"""Strict XML configuration; secret contents never appear in validation errors."""
from dataclasses import asdict, dataclass, field
from decimal import Decimal, InvalidOperation
from pathlib import Path
from typing import Any
import os
from defusedxml import ElementTree as ET

class ConfigurationError(ValueError):
    pass

@dataclass(frozen=True)
class Profile:
    id: str
    provider: str
    model: str
    reasoning_effort: str
    max_output_tokens: int
    input_rate: Decimal
    cached_rate: Decimal
    output_rate: Decimal
    cache_write_rate: Decimal

@dataclass
class AIConfig:
    active_profile: str
    profiles: dict[str, Profile]
    keys: dict[str, str] = field(repr=False)
    agent_profiles: dict[str, str] = field(default_factory=dict)
    timeout: float = 90
    schema_retries: int = 2
    max_input_bytes: int = 60000
    budget_usd: Decimal = Decimal("5")
    ledger_path: Path = Path("cost-ledger.sqlite")

    def profile(self, role: str, override: str | None = None) -> Profile:
        name = override or self.agent_profiles.get(role) or self.active_profile
        if name not in self.profiles:
            raise ConfigurationError("Unknown AI profile; review profile identifiers")
        return self.profiles[name]

    def public(self) -> dict:
        return {"active_profile": self.active_profile,
                "profiles": {k: {n: str(v) if isinstance(v, Decimal) else v for n,v in asdict(p).items()} for k,p in self.profiles.items()},
                "agent_profiles": self.agent_profiles, "timeout": self.timeout,
                "schema_retries": self.schema_retries, "max_input_bytes": self.max_input_bytes,
                "budget_usd": str(self.budget_usd)}

@dataclass
class SystemConfig:
    project_root: Path
    output_root: Path
    runbooks: Path
    prompts: Path
    host: str = "127.0.0.1"
    tool_port: int = 0
    diagnosis_port: int = 0
    startup_timeout: float = 30
    request_timeout: float = 120
    diagnosis_tool_budget: int = 8
    context_steps: int = 6
    max_agent_steps: int = 12
    read_retries: int = 2
    approval: str = "auto"
    memory_enabled: bool = True
    memory_k: int = 3
    runbook_k: int = 3
    seeds: tuple[int, ...] = (1,2,3,4,5)
    faults: tuple[str, ...] = ("W1","W2","W3","W4","W5","N0")
    difficulty: str = "L1"
    target: str = "HOST-001"

    def public(self) -> dict:
        return {k: str(v) if isinstance(v, Path) else v for k,v in asdict(self).items()}

def _root(path: Path, tag: str):
    try:
        node = ET.parse(path).getroot()
        if node.tag != tag or node.get("version") != "1":
            raise ValueError()
        return node
    except Exception:
        raise ConfigurationError(f"Invalid or unreadable {tag} XML; expected version 1") from None

def _path(value: str, base: Path) -> Path:
    path = Path(value).expanduser()
    return path if path.is_absolute() else (base / path).resolve()

def _shape(element, attributes, children=(), optional_attributes=()):
    """Reject typos and duplicate singleton elements before reading any values."""
    if element is None or not set(attributes)<=set(element.attrib) or set(element.attrib)-set(attributes)-set(optional_attributes):
        raise ValueError('Invalid XML attributes')
    if sorted(child.tag for child in element)!=sorted(children):
        raise ValueError('Invalid XML child elements')

def load_ai(path: Path) -> AIConfig:
    root = _root(Path(path), "ai")
    try:
        _shape(root,['version','active_profile'],['providers','profiles','agents','requests','budget'])
        provider_nodes=list(root.find('providers'))
        profile_nodes=list(root.find('profiles'))
        _shape(root.find('providers'),[],['provider']*len(provider_nodes))
        _shape(root.find('profiles'),[],['profile']*len(profile_nodes))
        _shape(root.find('agents'),[],optional_attributes=['operation_profile','diagnosis_profile'])
        _shape(root.find('requests'),['timeout_seconds','schema_retries','max_input_bytes'])
        _shape(root.find('budget'),['cumulative_usd','ledger_path'])
        keys = {}
        for provider in provider_nodes:
            _shape(provider,['id'],['api_key'])
            _shape(provider.find('api_key'),[],optional_attributes=['env'])
            identity = provider.attrib["id"]
            if identity not in {"openai", "anthropic"} or identity in keys:
                raise ValueError()
            key = provider.find("api_key")
            keys[identity] = (key.text or "").strip() or os.environ.get(key.get("env", ""), "")
        profiles = {}
        for item in profile_nodes:
            _shape(item,['id','provider','model','max_output_tokens','input_usd_per_million','cached_input_usd_per_million','output_usd_per_million'],optional_attributes=['reasoning_effort','cache_write_usd_per_million'])
            a = item.attrib
            input_rate = Decimal(a["input_usd_per_million"])
            # Preserve the existing legacy OpenAI / Anthropic prices when omitted.
            default_write_rate = input_rate * (Decimal('1.25') if a['provider']=='anthropic' else Decimal(1))
            profile = Profile(a["id"],a["provider"],a["model"],a.get("reasoning_effort","low"),int(a["max_output_tokens"]),input_rate,Decimal(a["cached_input_usd_per_million"]),Decimal(a["output_usd_per_million"]),Decimal(a.get('cache_write_usd_per_million',str(default_write_rate))))
            if profile.id in profiles or profile.provider not in keys or not profile.model or profile.reasoning_effort not in {"none","low","medium","high","xhigh"}:
                raise ValueError()
            if not 256 <= profile.max_output_tokens <= 16000 or any(not n.is_finite() or n < 0 for n in [profile.input_rate,profile.cached_rate,profile.output_rate,profile.cache_write_rate]):
                raise ValueError()
            if profile.input_rate == 0 or profile.output_rate == 0 or profile.cached_rate > profile.input_rate:
                raise ValueError()
            profiles[profile.id] = profile
        request = root.find("requests").attrib
        budget = root.find("budget").attrib
        agents = root.find("agents").attrib
        config = AIConfig(root.attrib["active_profile"],profiles,keys,
            {r: agents.get(r+"_profile", "") for r in ["operation","diagnosis"]},
            float(request["timeout_seconds"]),int(request["schema_retries"]),int(request["max_input_bytes"]),
            Decimal(budget["cumulative_usd"]),_path(budget["ledger_path"],Path(path).resolve().parent))
        if not config.budget_usd.is_finite() or config.budget_usd <= 0 or not 1 <= config.timeout <= 600 or not 0 <= config.schema_retries <= 3 or not 1024 <= config.max_input_bytes <= 120000:
            raise ValueError()
        for role in ["operation","diagnosis"]: config.profile(role)
        return config
    except Exception:
        raise ConfigurationError("Invalid AI configuration fields; check identifiers, limits and non-negative prices") from None

def load_system(path: Path) -> SystemConfig:
    root = _root(Path(path), "system")
    # Source/package root remains stable when a user keeps a configuration elsewhere.
    base = Path(__file__).resolve().parents[2]
    try:
        _shape(root,['version'],['paths','network','workflow','experiment','protection'])
        _shape(root.find('paths'),['output_root','runbooks','prompts'])
        _shape(root.find('network'),['host','tool_port','diagnosis_port','startup_timeout_seconds','request_timeout_seconds'])
        _shape(root.find('workflow'),['diagnosis_tool_budget','operation_context_steps','max_agent_steps','read_retries','approval','memory_enabled','memory_k','runbook_k'])
        _shape(root.find('experiment'),['seeds','faults','difficulty','target'])
        _shape(root.find('protection'),['mode'])
        if root.find("protection").get("mode") != "D0":
            raise ValueError()
        p,n,w,e = (root.find(k).attrib for k in ["paths","network","workflow","experiment"])
        result = SystemConfig(base,_path(p["output_root"],base),_path(p["runbooks"],base),_path(p["prompts"],base),
            n["host"],int(n["tool_port"]),int(n["diagnosis_port"]),float(n["startup_timeout_seconds"]),float(n["request_timeout_seconds"]),
            int(w["diagnosis_tool_budget"]),int(w["operation_context_steps"]),int(w["max_agent_steps"]),int(w["read_retries"]),w["approval"],w["memory_enabled"]=="true",int(w["memory_k"]),int(w["runbook_k"]),tuple(int(x) for x in e["seeds"].split(",")),tuple(e["faults"].split(",")),e["difficulty"],e["target"])
        if result.host not in {"127.0.0.1","localhost"} or result.approval not in {"auto","deny","interactive"} or w["memory_enabled"] not in {"true","false"}:
            raise ValueError()
        if result.difficulty not in {"L1","L2","L3"} or not set(result.faults) <= {"W1","W2","W3","W4","W5","N0"}:
            raise ValueError()
        if any(not 0 <= x <= 65535 for x in [result.tool_port,result.diagnosis_port]) or not result.seeds or not result.faults:
            raise ValueError()
        if any(x<=0 for x in [result.startup_timeout,result.request_timeout,result.diagnosis_tool_budget,result.context_steps,result.max_agent_steps,result.memory_k,result.runbook_k]) or not 0<=result.read_retries<=3:
            raise ValueError()
        return result
    except Exception:
        raise ConfigurationError("Invalid system configuration fields") from None
