from concurrent.futures import ThreadPoolExecutor
from decimal import Decimal
from pathlib import Path
import json
import uuid
import pytest

from tests.support_paths import workspace_for
from ccs.config import load_ai,load_system,ConfigurationError
from ccs.budget import BudgetLedger,BudgetExceeded,token_cost

PROJECT=Path(__file__).resolve().parents[1]
WORK = workspace_for("test_config_budget")

def fresh():
    p=WORK/uuid.uuid4().hex; p.mkdir(parents=True); return p

def test_xml_profiles_and_secret_free_export():
    cfg=load_ai(PROJECT/'configs/ai.example.xml')
    assert cfg.active_profile=='luna6'
    assert cfg.profile('operation').model=='gpt-6-luna'
    assert cfg.profile('diagnosis').model=='gpt-6-luna'
    assert cfg.profile('diagnosis','sonnet5').provider=='anthropic'
    cfg.keys['openai']='SECRET_SENTINEL'
    assert 'SECRET_SENTINEL' not in repr(cfg)
    assert 'SECRET_SENTINEL' not in json.dumps(cfg.public())
    assert token_cost(cfg.profile('operation'),100000,10000)==Decimal('0.015')
    assert load_system(PROJECT/'configs/system.example.xml').approval=='auto'

@pytest.mark.parametrize('replacement',[
    ('active_profile="luna6"','active_profile="missing"'),
    ('input_usd_per_million="0.10"','input_usd_per_million="NaN"'),
    ('cache_write_usd_per_million="0.125"','cache_write_usd_per_million="NaN"'),
    ('max_output_tokens="1800"','max_output_tokens="0"'),
    ('cumulative_usd="5.00"','cumulative_usd="Infinity"'),
])
def test_bad_ai_fields_fail_without_secret_values(replacement):
    xml=(PROJECT/'configs/ai.example.xml').read_text(encoding='utf-8-sig').replace(*replacement).replace('</api_key>','SECRET_SENTINEL</api_key>')
    p=fresh()/'invalid.xml'; p.write_text(xml, encoding='utf-8')
    with pytest.raises(ConfigurationError) as error: load_ai(p)
    assert 'SECRET_SENTINEL' not in str(error.value)

def test_xml_external_entity_rejected():
    p=fresh()/'entity.xml'
    p.write_text('<!DOCTYPE ai [<!ENTITY secret SYSTEM "file:///secret">]><ai version="1">&secret;</ai>', encoding='utf-8')
    with pytest.raises(ConfigurationError):load_ai(p)

def test_luna_cache_reads_and_writes_are_disjoint_billing_categories():
    profile=load_ai(PROJECT/'configs/ai.example.xml').profile('operation')
    # 30 ordinary + 40 cached + 30 written input tokens, plus 20 output tokens.
    assert token_cost(profile,100,20,40,30)==Decimal('0.00001715')
    with pytest.raises(ValueError):token_cost(profile,100,20,40,61)
    with pytest.raises(ValueError):token_cost(profile,100,20,40,-1)

@pytest.mark.parametrize('old,new',[
    ('operation_profile=""','operation_profiel=""'),
    ('<requests ','<requests unknown="1" '),
    ('</providers>','</providers><providers/>'),
    ('<api_key env="OPENAI_API_KEY">','<api_key env="OPENAI_API_KEY" extra="ignored">'),
])
def test_ai_typos_and_duplicate_sections_fail(old,new):
    p=fresh()/'typo.xml';p.write_text((PROJECT/'configs/ai.example.xml').read_text(encoding='utf-8-sig').replace(old,new), encoding='utf-8')
    with pytest.raises(ConfigurationError):load_ai(p)

@pytest.mark.parametrize('old,new',[
    ('memory_enabled="true"','memory_enabled="true" memory_enabld="false"'),
    ('<protection mode="D0" />','<protection mode="D0" /><protection mode="D0" />'),
    ('<system version="1">','<system version="1" unknown="value">'),
])
def test_system_typos_and_duplicate_sections_fail(old,new):
    p=fresh()/'system.xml';p.write_text((PROJECT/'configs/system.example.xml').read_text(encoding='utf-8-sig').replace(old,new), encoding='utf-8')
    with pytest.raises(ConfigurationError):load_system(p)

def test_atomic_reservations_and_restart_retention():
    path=fresh()/'ledger.sqlite'
    ledger=BudgetLedger(path,Decimal('1'))
    def reserve(_):
        try:return BudgetLedger(path,Decimal('1')).reserve(Decimal('.3'),'model','agent')
        except BudgetExceeded:return None
    with ThreadPoolExecutor(max_workers=8) as pool: ids=list(pool.map(reserve,range(8)))
    ids=[x for x in ids if x]
    assert len(ids)==3
    ledger.settle(ids[0],Decimal('.1'))
    ledger.settle(ids[1],None,'network_unknown')
    assert BudgetLedger(path,Decimal('1')).summary()['accounted_usd']=='0.7'
    with pytest.raises(BudgetExceeded): ledger.reserve(Decimal('.31'),'model','agent')
    with pytest.raises(ValueError):ledger.settle(ids[0],Decimal('0'))

def test_failed_no_charge_request_releases_reservation():
    ledger=BudgetLedger(fresh()/'ledger.sqlite',Decimal('1'))
    identity=ledger.reserve(Decimal('1'),'model','agent')
    ledger.settle(identity,Decimal('0'),'failed')
    assert ledger.summary()['accounted_usd']=='0'

