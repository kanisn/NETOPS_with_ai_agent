"""Deterministic, stateful wired network backed by SQLite."""
from __future__ import annotations

import hashlib
import ipaddress
import json
import sqlite3
import threading
from pathlib import Path
from typing import Any, Callable

from .errors import ChangeConflictError, ContractError, IdempotencyConflictError, NotFoundError, UnknownToolError, VersionConflictError

BACKEND_ID = "sqlite-wired-v1"
SCHEMA_VERSION = "2"

def _json(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False)

def _decode(value: str) -> Any:
    return json.loads(value)

def _hash(value: Any) -> str:
    return hashlib.sha256(_json(value).encode("utf-8")).hexdigest()

class SQLiteBackend:
    """Implement the stable NetworkBackend contract over a wired world DB."""
    _READ_LIMIT = 50

    def __init__(self, path: Path):
        self.path = Path(path)
        if not self.path.is_file(): raise FileNotFoundError(self.path)
        self._lock = threading.RLock()
        self._connection = sqlite3.connect(self.path, isolation_level=None, check_same_thread=False)
        self._connection.row_factory = sqlite3.Row
        self._connection.execute("PRAGMA foreign_keys=ON")
        self._connection.execute("PRAGMA busy_timeout=5000")
        try:
            metadata = dict(self._connection.execute("SELECT key,value FROM metadata"))
        except sqlite3.Error:
            self.close(); raise ContractError(f"database does not implement {BACKEND_ID} schema version {SCHEMA_VERSION}") from None
        if metadata.get("backend_id") != BACKEND_ID or metadata.get("schema_version") != SCHEMA_VERSION:
            self.close(); raise ContractError(f"database does not implement {BACKEND_ID} schema version {SCHEMA_VERSION}")

    def __enter__(self) -> "SQLiteBackend": return self
    def __exit__(self, *_: object) -> None: self.close()
    def close(self) -> None:
        connection = getattr(self, "_connection", None)
        if connection is not None: connection.close(); self._connection = None

    @property
    def _db(self) -> sqlite3.Connection:
        if self._connection is None: raise RuntimeError("backend is closed")
        return self._connection

    def _meta_int(self, key: str) -> int:
        row = self._db.execute("SELECT value FROM metadata WHERE key=?", (key,)).fetchone()
        if row is None: raise ContractError(f"missing database metadata: {key}")
        return int(row[0])

    def _set_meta_int(self, key: str, value: int) -> None:
        self._db.execute("UPDATE metadata SET value=? WHERE key=?", (str(value), key))

    def _state_version(self) -> int: return self._meta_int("state_version")

    @staticmethod
    def _arguments(arguments: dict[str, Any], *, required: set[str], allowed: set[str]) -> None:
        if not isinstance(arguments, dict): raise ContractError("tool arguments must be an object")
        missing, extra = required - arguments.keys(), arguments.keys() - allowed
        if missing: raise ContractError(f"missing required arguments: {sorted(missing)}")
        if extra: raise ContractError(f"unknown arguments: {sorted(extra)}")

    @staticmethod
    def _text(value: Any, name: str, *, maximum: int = 256) -> str:
        if not isinstance(value, str) or not value.strip(): raise ContractError(f"{name} must be a non-empty string")
        result = value.strip()
        if len(result) > maximum: raise ContractError(f"{name} exceeds {maximum} characters")
        return result

    @staticmethod
    def _limit(value: Any, default: int, maximum: int) -> int:
        if value is None: return default
        if isinstance(value, bool) or not isinstance(value, int) or not 1 <= value <= maximum: raise ContractError(f"limit must be an integer from 1 through {maximum}")
        return value

    def call(self, tool: str, arguments: dict[str, Any]) -> dict[str, Any]:
        if not isinstance(tool, str): raise UnknownToolError("tool name must be a string")
        handlers: dict[str, Callable[[dict[str, Any]], dict[str, Any]]] = {
            "list_alarms": self._list_alarms, "get_kpi": self._get_kpi, "get_logs": self._get_logs,
            "get_config": self._get_config, "get_topology": self._get_topology, "lookup_flows": self._lookup_flows,
            "preview_change": self._preview_change, "apply_change": self._apply_change, "get_change_status": self._get_change_status,
            "rollback_change": self._rollback_change, "verify_service": self._verify_service, "update_ticket": self._update_ticket,
        }
        try: handler = handlers[tool]
        except KeyError as exc: raise UnknownToolError(f"unknown network tool: {tool}") from exc
        with self._lock: return handler(arguments)

    def _list_alarms(self, arguments: dict[str, Any]) -> dict[str, Any]:
        self._arguments(arguments, required=set(), allowed={"scope", "window", "limit"})
        scope = self._text(arguments["scope"], "scope").upper() if arguments.get("scope") is not None else None
        window = self._limit(arguments.get("window"), 100, 1000); limit = self._limit(arguments.get("limit"), 20, self._READ_LIMIT)
        query = "SELECT alarm_id,ts,target,severity,code,summary,status FROM alarms WHERE ts>=?"; params: list[Any] = [self._meta_int("logical_clock") - window]
        if scope: query += " AND target=?"; params.append(scope)
        query += " ORDER BY CASE status WHEN 'active' THEN 0 ELSE 1 END,ts DESC,alarm_id LIMIT ?"; params.append(limit)
        alarms = [dict(row) for row in self._db.execute(query, params)]
        return {"alarms": alarms, "count": len(alarms), "state_version": self._state_version()}

    def _get_logs(self, arguments: dict[str, Any]) -> dict[str, Any]:
        self._arguments(arguments, required={"target"}, allowed={"target", "window", "severity", "limit"})
        target = self._text(arguments["target"], "target").upper(); window = self._limit(arguments.get("window"), 100, 1000); limit = self._limit(arguments.get("limit"), 20, self._READ_LIMIT)
        severity = arguments.get("severity")
        if severity is not None:
            severity = self._text(severity, "severity").upper()
            if severity not in {"DEBUG", "INFO", "WARN", "ERROR"}: raise ContractError("severity must be DEBUG, INFO, WARN, or ERROR")
        query = "SELECT log_id,ts,target,severity,message FROM logs WHERE ts>=? AND target=?"; params: list[Any] = [self._meta_int("logical_clock") - window, target]
        if severity: query += " AND severity=?"; params.append(severity)
        query += " ORDER BY ts DESC,log_id DESC LIMIT ?"; params.append(limit)
        logs = [dict(row) for row in self._db.execute(query, params)]
        return {"logs": logs, "count": len(logs), "state_version": self._state_version()}

    def _get_config(self, arguments: dict[str, Any]) -> dict[str, Any]:
        self._arguments(arguments, required={"target"}, allowed={"target", "params"})
        target = self._text(arguments["target"], "target").upper(); requested = arguments.get("params")
        if requested is not None and (not isinstance(requested, list) or len(requested) > 20 or not all(isinstance(v, str) for v in requested)): raise ContractError("params must be an array of at most 20 strings")
        rows = self._db.execute("SELECT param,value_json,reference_json,version FROM config_items WHERE target=? ORDER BY param", (target,)).fetchall()
        if not rows: raise NotFoundError(f"no configuration for target {target}")
        wanted = set(requested or []); items = []
        for row in rows:
            if wanted and row["param"] not in wanted: continue
            current, reference = _decode(row["value_json"]), _decode(row["reference_json"])
            items.append({"param": row["param"], "current_value": current, "reference_value": reference, "version": row["version"], "is_at_reference": current == reference})
        return {"target": target, "items": items, "state_version": self._state_version()}

    @staticmethod
    def _node(row: sqlite3.Row) -> dict[str, Any]:
        return {"node_id": row["node_id"], "node_type": row["node_type"], "label": row["label"], "management_ip": row["management_ip"], "status": row["status"]}

    @staticmethod
    def _interface(row: sqlite3.Row) -> dict[str, Any]:
        return {"interface_id": row["interface_id"], "node_id": row["node_id"], "name": row["name"], "mac_address": row["mac_address"], "ipv4_cidr": row["ipv4_cidr"], "admin_state": row["admin_state"]}

    @staticmethod
    def _link(row: sqlite3.Row) -> dict[str, Any]:
        return {"link_id": row["link_id"], "source_interface": row["source_interface"], "target_interface": row["target_interface"], "path": row["path"], "capacity_mbps": row["capacity_mbps"], "delay_ms": row["delay_ms"], "loss_pct": row["loss_pct"], "status": row["status"]}

    @staticmethod
    def _flow(row: sqlite3.Row) -> dict[str, Any]:
        return {"flow_id": row["flow_id"], "src_host": row["src_host"], "dst_host": row["dst_host"], "src_ip": row["src_ip"], "dst_ip": row["dst_ip"], "protocol": row["protocol"], "dst_port": row["dst_port"], "status": row["status"]}

    def _get_topology(self, arguments: dict[str, Any]) -> dict[str, Any]:
        self._arguments(arguments, required={"target"}, allowed={"target", "depth"})
        target = self._text(arguments["target"], "target").upper(); depth = arguments.get("depth", 1)
        if isinstance(depth, bool) or not isinstance(depth, int) or not 0 <= depth <= 2: raise ContractError("depth must be an integer from 0 through 2")
        if self._db.execute("SELECT 1 FROM nodes WHERE node_id=?", (target,)).fetchone() is None: raise NotFoundError(f"unknown topology target {target}")
        nodes = [self._node(row) for row in self._db.execute("SELECT node_id,node_type,label,management_ip,status FROM nodes ORDER BY node_id")]
        interfaces = [self._interface(row) for row in self._db.execute("SELECT interface_id,node_id,name,mac_address,ipv4_cidr,admin_state FROM interfaces ORDER BY interface_id")]
        links = [self._link(row) for row in self._db.execute("SELECT link_id,source_interface,target_interface,path,capacity_mbps,delay_ms,loss_pct,status FROM links ORDER BY link_id")]
        flows = [self._flow(row) for row in self._db.execute("SELECT flow_id,src_host,dst_host,src_ip,dst_ip,protocol,dst_port,status FROM traffic_flows WHERE src_host=? OR dst_host=? ORDER BY flow_id LIMIT 25", (target, target))]
        return {"target": target, "depth": depth, "nodes": nodes, "interfaces": interfaces, "links": links, "flows": flows, "state_version": self._state_version()}

    def _lookup_flows(self, arguments: dict[str, Any]) -> dict[str, Any]:
        self._arguments(arguments, required=set(), allowed={"host", "src_ip", "dst_ip", "limit"})
        filters = {key: arguments.get(key) for key in ("host", "src_ip", "dst_ip") if arguments.get(key) is not None}
        if not filters: raise ContractError("one of host, src_ip, or dst_ip is required")
        if len(filters) != 1: raise ContractError("use exactly one flow lookup selector")
        field, raw = next(iter(filters.items())); value = self._text(raw, field); limit = self._limit(arguments.get("limit"), 10, 25)
        if field == "host":
            value = value.upper(); query = "SELECT flow_id,src_host,dst_host,src_ip,dst_ip,protocol,dst_port,status FROM traffic_flows WHERE src_host=? OR dst_host=? ORDER BY flow_id LIMIT ?"; params = (value, value, limit)
        else:
            query = f"SELECT flow_id,src_host,dst_host,src_ip,dst_ip,protocol,dst_port,status FROM traffic_flows WHERE {field}=? ORDER BY flow_id LIMIT ?"; params = (value, limit)
        flows = [self._flow(row) for row in self._db.execute(query, params)]
        return {"flows": flows, "count": len(flows), "state_version": self._state_version()}

    def _config_value(self, target: str, param: str) -> Any:
        row = self._db.execute("SELECT value_json FROM config_items WHERE target=? AND param=?", (target, param)).fetchone()
        if row is None: raise NotFoundError(f"unknown configuration {target}.{param}")
        return _decode(row[0])

    def _config_reference(self, target: str, param: str) -> Any:
        row = self._db.execute("SELECT reference_json FROM config_items WHERE target=? AND param=?", (target, param)).fetchone()
        if row is None: raise NotFoundError(f"unknown configuration {target}.{param}")
        return _decode(row[0])

    def _normalize_change(self, target: str, param: str, value: Any) -> tuple[str, Any, Any]:
        current = self._config_value(target, param)
        if param == "active_path":
            if value not in {"primary", "backup"}: raise ContractError("active_path must be primary or backup")
        elif param == "admin_state":
            if value not in {"up", "down"}: raise ContractError("admin_state must be up or down")
        elif param == "default_gateway":
            if not isinstance(value, str): raise ContractError("default_gateway must be an IPv4 address")
            try: value = str(ipaddress.IPv4Address(value))
            except ipaddress.AddressValueError: raise ContractError("default_gateway must be an IPv4 address") from None
        elif param in {"loss_pct", "bandwidth_mbps", "delay_ms"}:
            if isinstance(value, bool) or not isinstance(value, (int, float)): raise ContractError(f"{param} must be numeric")
            lower, upper = {"loss_pct": (0, 100), "bandwidth_mbps": (0.1, 10000), "delay_ms": (0, 10000)}[param]
            if not lower <= value <= upper: raise ContractError(f"{param} must be from {lower} through {upper}")
            value = float(value)
        return param, current, value

    def _preview_change(self, arguments: dict[str, Any]) -> dict[str, Any]:
        self._arguments(arguments, required={"target", "param", "value", "reason"}, allowed={"target", "param", "value", "reason"})
        target = self._text(arguments["target"], "target").upper(); param = self._text(arguments["param"], "param", maximum=64); reason = self._text(arguments["reason"], "reason", maximum=500)
        canonical, before, after = self._normalize_change(target, param, arguments["value"]); base_version = self._state_version()
        number = self._db.execute("SELECT COALESCE(MAX(preview_id),0)+1 FROM previews").fetchone()[0]
        token = "PRE-" + _hash({"preview": number, "target": target, "param": canonical, "before": before, "after": after, "reason": reason, "base_version": base_version})[:32]
        self._db.execute("INSERT INTO previews(token,target,param,before_json,after_json,reason,base_version,used_by_change) VALUES(?,?,?,?,?,?,?,NULL)", (token, target, canonical, _json(before), _json(after), reason, base_version))
        return {"change_token": token, "diff": {"target": target, "param": canonical, "before": before, "after": after}, "base_version": base_version, "expires_at_version": base_version}

    def _idempotent_response(self, key: str, operation: str, request: dict[str, Any]) -> dict[str, Any] | None:
        row = self._db.execute("SELECT operation,request_hash,response_json FROM idempotency WHERE idempotency_key=?", (key,)).fetchone()
        if row is None: return None
        if row["operation"] != operation or row["request_hash"] != _hash(request): raise IdempotencyConflictError(f"idempotency key {key!r} was already used for a different request")
        return _decode(row["response_json"])

    def _store_idempotency(self, key: str, operation: str, request: dict[str, Any], response: dict[str, Any]) -> None:
        self._db.execute("INSERT INTO idempotency(idempotency_key,operation,request_hash,response_json) VALUES(?,?,?,?)", (key, operation, _hash(request), _json(response)))

    def _sync_host_egress(self, target: str, param: str, value: float) -> None:
        """Bind shared host TC configuration to both real dual-homed egress links."""
        column = {"loss_pct": "loss_pct", "bandwidth_mbps": "capacity_mbps", "delay_ms": "delay_ms"}[param]
        cursor = self._db.execute(
            f"UPDATE links SET {column}=? WHERE source_interface IN "
            "(SELECT interface_id FROM interfaces WHERE node_id=?)",
            (value, target),
        )
        if cursor.rowcount != 2:
            raise ContractError(f"wired schema invariant failed: expected two {target} egress links, updated {cursor.rowcount}")

    def _write_config(self, target: str, param: str, value: Any) -> int:
        row = self._db.execute("SELECT version FROM config_items WHERE target=? AND param=?", (target, param)).fetchone()
        if row is None: raise NotFoundError(f"unknown configuration {target}.{param}")
        version = int(row[0]) + 1
        self._db.execute("UPDATE config_items SET value_json=?,version=? WHERE target=? AND param=?", (_json(value), version, target, param))
        if target == "HOST-001" and param == "admin_state":
            self._db.execute("UPDATE interfaces SET admin_state=? WHERE node_id='HOST-001'", (value,))
        elif target == "HOST-001" and param in {"loss_pct", "bandwidth_mbps", "delay_ms"}:
            self._sync_host_egress(target, param, float(value))
        return version

    def _apply_change(self, arguments: dict[str, Any]) -> dict[str, Any]:
        self._arguments(arguments, required={"change_token", "idempotency_key"}, allowed={"change_token", "idempotency_key"})
        token = self._text(arguments["change_token"], "change_token"); key = self._text(arguments["idempotency_key"], "idempotency_key", maximum=128); request = {"change_token": token}
        existing = self._idempotent_response(key, "apply_change", request)
        if existing is not None: return existing
        self._db.execute("BEGIN IMMEDIATE")
        try:
            preview = self._db.execute("SELECT * FROM previews WHERE token=?", (token,)).fetchone()
            if preview is None: raise NotFoundError("unknown change token")
            if preview["used_by_change"] is not None: raise ChangeConflictError("change token has already been consumed")
            state_version = self._state_version()
            if preview["base_version"] != state_version: raise VersionConflictError(f"stale preview: based on version {preview['base_version']}, current version is {state_version}")
            before, after = _decode(preview["before_json"]), _decode(preview["after_json"])
            if self._config_value(preview["target"], preview["param"]) != before: raise VersionConflictError("configuration changed after preview")
            version = self._write_config(preview["target"], preview["param"], after); state_version += 1; self._set_meta_int("state_version", state_version)
            clock = self._meta_int("logical_clock") + 1; self._set_meta_int("logical_clock", clock); number = self._db.execute("SELECT COALESCE(MAX(change_number),0)+1 FROM changes").fetchone()[0]; change_id = f"CHG-{number:06d}"
            self._db.execute("INSERT INTO changes(change_number,change_id,target,param,before_json,after_json,reason,status,applied_state_version,rolled_back_state_version,ts) VALUES(?,?,?,?,?,?,?,?,?,NULL,?)", (number, change_id, preview["target"], preview["param"], preview["before_json"], preview["after_json"], preview["reason"], "applied", state_version, clock))
            self._db.execute("UPDATE previews SET used_by_change=? WHERE token=?", (change_id, token))
            response = {"change_id": change_id, "status": "applied", "target": preview["target"], "param": preview["param"], "before": before, "after": after, "version": version, "state_version": state_version}
            self._store_idempotency(key, "apply_change", request, response); self._refresh_alarm_status(preview["target"]); self._db.execute("COMMIT"); return response
        except Exception:
            self._db.execute("ROLLBACK"); raise

    def _get_change_status(self, arguments: dict[str, Any]) -> dict[str, Any]:
        self._arguments(arguments, required={"idempotency_key"}, allowed={"idempotency_key"}); key = self._text(arguments["idempotency_key"], "idempotency_key", maximum=128)
        row = self._db.execute("SELECT operation,response_json FROM idempotency WHERE idempotency_key=?", (key,)).fetchone()
        if row is None: return {"found": False, "idempotency_key": key}
        response = _decode(row["response_json"]); return {"found": True, "idempotency_key": key, "operation": row["operation"], "status": response.get("status", "completed"), "response": response}

    def _rollback_change(self, arguments: dict[str, Any]) -> dict[str, Any]:
        self._arguments(arguments, required={"change_id", "idempotency_key"}, allowed={"change_id", "idempotency_key"})
        change_id = self._text(arguments["change_id"], "change_id"); key = self._text(arguments["idempotency_key"], "idempotency_key", maximum=128); request = {"change_id": change_id}
        existing = self._idempotent_response(key, "rollback_change", request)
        if existing is not None: return existing
        self._db.execute("BEGIN IMMEDIATE")
        try:
            change = self._db.execute("SELECT * FROM changes WHERE change_id=?", (change_id,)).fetchone()
            if change is None: raise NotFoundError(f"unknown change {change_id}")
            if change["status"] != "applied": raise ChangeConflictError(f"change {change_id} is {change['status']}")
            state_version = self._state_version()
            if state_version != change["applied_state_version"]: raise VersionConflictError("a later network mutation prevents safe rollback")
            after, before = _decode(change["after_json"]), _decode(change["before_json"])
            if self._config_value(change["target"], change["param"]) != after: raise VersionConflictError("current configuration no longer matches the applied change")
            version = self._write_config(change["target"], change["param"], before); state_version += 1; self._set_meta_int("state_version", state_version); clock = self._meta_int("logical_clock") + 1; self._set_meta_int("logical_clock", clock)
            self._db.execute("UPDATE changes SET status='rolled_back',rolled_back_state_version=? WHERE change_id=?", (state_version, change_id))
            response = {"change_id": change_id, "status": "rolled_back", "target": change["target"], "param": change["param"], "before": after, "after": before, "version": version, "state_version": state_version}
            self._store_idempotency(key, "rollback_change", request, response); self._refresh_alarm_status(change["target"]); self._db.execute("COMMIT"); return response
        except Exception:
            self._db.execute("ROLLBACK"); raise

    def _metrics(self, target: str) -> dict[str, float]:
        if self._db.execute("SELECT 1 FROM nodes WHERE node_id=? AND node_type='host'", (target,)).fetchone() is None: raise NotFoundError(f"unknown service target {target}")
        active_path = self._config_value(target, "active_path"); gateway = self._config_value(target, "default_gateway")
        egress = self._db.execute(
            "SELECT i.admin_state,l.capacity_mbps,l.delay_ms,l.loss_pct FROM interfaces i "
            "JOIN links l ON l.source_interface=i.interface_id WHERE i.node_id=? AND l.path=?",
            (target, active_path),
        ).fetchone()
        if egress is None: raise ContractError(f"wired schema invariant failed: no {target} egress link for path {active_path}")
        admin = egress["admin_state"]; bandwidth = float(egress["capacity_mbps"]); delay = float(egress["delay_ms"]); loss = float(egress["loss_pct"])
        path_links = self._db.execute("SELECT status FROM links WHERE path=?", (active_path,)).fetchall()
        switch_id = "SWITCH-PRIMARY" if active_path == "primary" else "SWITCH-BACKUP"
        switch = self._db.execute("SELECT status FROM nodes WHERE node_id=?", (switch_id,)).fetchone()
        path_healthy = bool(path_links) and all(row["status"] == "up" for row in path_links) and switch is not None and switch["status"] == "up"
        connected = admin == "up" and gateway == self._config_reference(target, "default_gateway") and path_healthy
        if not connected: return {"throughput_mbps": 0.0, "latency_ms": 1000.0, "packet_loss_pct": 100.0, "reachability_pct": 0.0}
        throughput = min(90.0, bandwidth * 0.9) * max(0.0, 1.0 - loss / 100.0)
        if delay > 30.0: throughput *= 0.85
        return {"throughput_mbps": round(throughput, 3), "latency_ms": round(delay + 8.0, 3), "packet_loss_pct": round(loss, 3), "reachability_pct": round(max(0.0, 100.0-loss), 3)}

    def _service_checks(self, target: str) -> list[dict[str, Any]]:
        metrics = self._metrics(target)
        config_ok = all(row["value_json"] == row["reference_json"] for row in self._db.execute("SELECT value_json,reference_json FROM config_items WHERE target=? AND param<>'active_path'", (target,)))
        active_path = self._config_value(target, "active_path")
        switch_id = "SWITCH-PRIMARY" if active_path == "primary" else "SWITCH-BACKUP"
        path_ok = self._db.execute("SELECT status FROM nodes WHERE node_id=?", (switch_id,)).fetchone()[0] == "up" and all(row[0] == "up" for row in self._db.execute("SELECT status FROM links WHERE path=?", (active_path,)))
        expected_tc = {
            "capacity_mbps": float(self._config_value(target, "bandwidth_mbps")),
            "delay_ms": float(self._config_value(target, "delay_ms")),
            "loss_pct": float(self._config_value(target, "loss_pct")),
        }
        egress_rows = self._db.execute(
            "SELECT l.capacity_mbps,l.delay_ms,l.loss_pct FROM links l JOIN interfaces i ON l.source_interface=i.interface_id WHERE i.node_id=?",
            (target,),
        ).fetchall()
        tc_bound = len(egress_rows) == 2 and all(all(float(row[field]) == value for field, value in expected_tc.items()) for row in egress_rows)
        return [
            {"name": "configuration_reference", "passed": config_ok},
            {"name": "active_path_health", "passed": path_ok, "path": active_path, "intermediate_switch": switch_id},
            {"name": "host_egress_tc_binding", "passed": tc_bound, "egress_links": len(egress_rows)},
            {"name": "throughput", "passed": metrics["throughput_mbps"] >= 80.0, "value": metrics["throughput_mbps"], "threshold": 80.0},
            {"name": "latency", "passed": metrics["latency_ms"] <= 30.0, "value": metrics["latency_ms"], "threshold": 30.0},
            {"name": "packet_loss", "passed": metrics["packet_loss_pct"] <= 2.0, "value": metrics["packet_loss_pct"], "threshold": 2.0},
            {"name": "reachability", "passed": metrics["reachability_pct"] >= 99.0, "value": metrics["reachability_pct"], "threshold": 99.0},
        ]

    def _verify_service(self, arguments: dict[str, Any]) -> dict[str, Any]:
        self._arguments(arguments, required={"target"}, allowed={"target", "checks"}); target = self._text(arguments["target"], "target").upper(); requested = arguments.get("checks")
        if requested is not None and (not isinstance(requested, list) or len(requested) > 12 or not all(isinstance(v, str) for v in requested)): raise ContractError("checks must be an array of at most 12 strings")
        checks = self._service_checks(target)
        if requested:
            names, known = set(requested), {check["name"] for check in checks}; unknown = names - known
            if unknown: raise ContractError(f"unknown service checks: {sorted(unknown)}")
            checks = [check for check in checks if check["name"] in names]
        return {"target": target, "passed": bool(checks) and all(check["passed"] for check in checks), "checks": checks, "state_version": self._state_version()}

    def _get_kpi(self, arguments: dict[str, Any]) -> dict[str, Any]:
        self._arguments(arguments, required={"target"}, allowed={"target", "metrics", "window"}); target = self._text(arguments["target"], "target").upper(); requested = arguments.get("metrics")
        if requested is not None and (not isinstance(requested, list) or len(requested) > 12 or not all(isinstance(v, str) for v in requested)): raise ContractError("metrics must be an array of at most 12 strings")
        metrics = self._metrics(target); units = {"throughput_mbps": "Mbps", "latency_ms": "ms", "packet_loss_pct": "percent", "reachability_pct": "percent"}; healthy = {"throughput_mbps": lambda v: v >= 80, "latency_ms": lambda v: v <= 30, "packet_loss_pct": lambda v: v <= 2, "reachability_pct": lambda v: v >= 99}
        if requested:
            unknown = set(requested) - set(metrics)
            if unknown: raise ContractError(f"unknown metrics: {sorted(unknown)}")
        samples = [{"metric": name, "value": value, "unit": units[name], "status": "ok" if healthy[name](value) else "degraded"} for name, value in metrics.items() if not requested or name in set(requested)]
        return {"target": target, "samples": samples, "state_version": self._state_version()}

    def _refresh_alarm_status(self, changed_target: str) -> None:
        for row in self._db.execute("SELECT DISTINCT target FROM alarms WHERE status='active'").fetchall():
            try: healthy = all(item["passed"] for item in self._service_checks(row[0]))
            except NotFoundError: healthy = False
            if healthy: self._db.execute("UPDATE alarms SET status='cleared' WHERE target=? AND status='active'", (row[0],))
        self._db.execute("INSERT INTO logs(ts,target,severity,message) VALUES(?,?,?,?)", (self._meta_int("logical_clock"), changed_target, "INFO", f"Configuration transaction completed for {changed_target}; service verification is available."))

    def _update_ticket(self, arguments: dict[str, Any]) -> dict[str, Any]:
        self._arguments(arguments, required={"ticket_id", "status", "note"}, allowed={"ticket_id", "status", "note", "idempotency_key"})
        ticket_id = self._text(arguments["ticket_id"], "ticket_id").upper(); status = self._text(arguments["status"], "status").lower(); note = arguments["note"]
        if status not in {"open", "investigating", "resolved", "escalated"}: raise ContractError("invalid ticket status")
        if not isinstance(note, str) or len(note) > 1000: raise ContractError("note must be a string of at most 1000 characters")
        key = self._text(arguments.get("idempotency_key") or "TICKET-" + _hash({"ticket_id": ticket_id, "status": status, "note": note})[:32], "idempotency_key", maximum=128); request = {"ticket_id": ticket_id, "status": status, "note": note}
        existing = self._idempotent_response(key, "update_ticket", request)
        if existing is not None: return existing
        if self._db.execute("SELECT 1 FROM tickets WHERE ticket_id=?", (ticket_id,)).fetchone() is None: raise NotFoundError(f"unknown ticket {ticket_id}")
        self._db.execute("BEGIN IMMEDIATE")
        try:
            clock = self._meta_int("logical_clock") + 1; self._set_meta_int("logical_clock", clock); self._db.execute("UPDATE tickets SET status=?,note=?,updated_at=? WHERE ticket_id=?", (status, note, clock, ticket_id))
            response = {"ticket_id": ticket_id, "status": status, "note": note, "updated_at": clock}; self._store_idempotency(key, "update_ticket", request, response); self._db.execute("COMMIT"); return response
        except Exception:
            self._db.execute("ROLLBACK"); raise

    def snapshot(self) -> dict[str, Any]:
        """Return the canonical offline wired state; this is not a Network Tool."""
        with self._lock:
            nodes = [self._node(row) for row in self._db.execute("SELECT node_id,node_type,label,management_ip,status FROM nodes ORDER BY node_id")]
            interfaces = [self._interface(row) for row in self._db.execute("SELECT interface_id,node_id,name,mac_address,ipv4_cidr,admin_state FROM interfaces ORDER BY interface_id")]
            links = [self._link(row) for row in self._db.execute("SELECT link_id,source_interface,target_interface,path,capacity_mbps,delay_ms,loss_pct,status FROM links ORDER BY link_id")]
            flows = [self._flow(row) for row in self._db.execute("SELECT flow_id,src_host,dst_host,src_ip,dst_ip,protocol,dst_port,status FROM traffic_flows ORDER BY flow_id")]
            configuration = []
            for row in self._db.execute("SELECT target,param,value_json,reference_json,version FROM config_items ORDER BY target,param"):
                current, reference = _decode(row["value_json"]), _decode(row["reference_json"])
                configuration.append({"target": row["target"], "param": row["param"], "current_value": current, "reference_value": reference, "version": row["version"], "is_at_reference": current == reference})
            changes = [{"change_id": row["change_id"], "target": row["target"], "param": row["param"], "before_value": _decode(row["before_json"]), "after_value": _decode(row["after_json"]), "status": row["status"], "applied_state_version": row["applied_state_version"], "rolled_back_state_version": row["rolled_back_state_version"], "ts": row["ts"]} for row in self._db.execute("SELECT change_id,target,param,before_json,after_json,status,applied_state_version,rolled_back_state_version,ts FROM changes ORDER BY change_number")]
            network_state = {"nodes": nodes, "interfaces": interfaces, "links": links, "flows": flows, "configuration": configuration}
            return {"backend_id": BACKEND_ID, "schema_version": SCHEMA_VERSION, "state_version": self._state_version(), "logical_clock": self._meta_int("logical_clock"), **network_state, "changes": changes, "state_hash": _hash(network_state)}
