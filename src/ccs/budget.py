"""Shared cumulative cost reservations, using integer nano-USD and SQLite transactions."""
from decimal import Decimal, ROUND_CEILING
from pathlib import Path
from contextlib import contextmanager
import sqlite3
import uuid

class BudgetExceeded(RuntimeError):
    pass

def nanos(value: Decimal) -> int:
    if not value.is_finite() or value < 0: raise ValueError("Invalid cost")
    return int((value * Decimal(10**9)).to_integral_value(rounding=ROUND_CEILING))

def token_cost(profile, input_tokens: int, output_tokens: int, cached_tokens: int = 0, cache_write_tokens: int = 0) -> Decimal:
    if min(input_tokens,output_tokens,cached_tokens,cache_write_tokens)<0 or cached_tokens+cache_write_tokens>input_tokens:
        raise ValueError("Invalid token usage")
    return ((input_tokens-cached_tokens-cache_write_tokens)*profile.input_rate + cached_tokens*profile.cached_rate + cache_write_tokens*profile.cache_write_rate + output_tokens*profile.output_rate) / Decimal(1000000)

class BudgetLedger:
    def __init__(self,path: Path,limit_usd: Decimal):
        self.path=Path(path); self.path.parent.mkdir(parents=True,exist_ok=True)
        self.limit=nanos(limit_usd)
        with self.connect() as db:
            db.execute("CREATE TABLE IF NOT EXISTS calls (id TEXT PRIMARY KEY, reserved INTEGER NOT NULL, actual INTEGER, status TEXT NOT NULL, model TEXT NOT NULL, role TEXT NOT NULL)")

    @contextmanager
    def connect(self):
        connection=sqlite3.connect(self.path,timeout=20)
        try:
            with connection:yield connection
        finally:connection.close()

    def reserve(self,estimate: Decimal,model: str,role: str) -> str:
        amount=nanos(estimate); identity=uuid.uuid4().hex
        with self.connect() as db:
            db.execute("BEGIN IMMEDIATE")
            used=db.execute("SELECT COALESCE(SUM(COALESCE(actual,reserved)),0) FROM calls").fetchone()[0]
            if used+amount>self.limit:
                raise BudgetExceeded("Cumulative API budget would be exceeded; no request was sent")
            db.execute("INSERT INTO calls VALUES(?,?,NULL,'reserved',?,?)",(identity,amount,model,role))
        return identity

    def settle(self,identity: str,cost: Decimal | None,status: str="completed"):
        with self.connect() as db:
            db.execute("BEGIN IMMEDIATE")
            row=db.execute("SELECT reserved,status FROM calls WHERE id=?",(identity,)).fetchone()
            if not row or row[1]!="reserved": raise ValueError("Unknown or already settled reservation")
            # Unknown provider acceptance retains the full reservation across restarts.
            db.execute("UPDATE calls SET actual=?,status=? WHERE id=?",(None if cost is None else nanos(cost),status,identity))

    def summary(self) -> dict:
        with self.connect() as db:
            count,total,unknown=db.execute("SELECT COUNT(*),COALESCE(SUM(COALESCE(actual,reserved)),0),COALESCE(SUM(CASE WHEN actual IS NULL THEN 1 ELSE 0 END),0) FROM calls").fetchone()
        return {"calls":count,"accounted_usd":str(Decimal(total)/Decimal(10**9)),"limit_usd":str(Decimal(self.limit)/Decimal(10**9)),"unconfirmed_calls":unknown}
