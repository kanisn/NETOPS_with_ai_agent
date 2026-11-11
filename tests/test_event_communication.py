from ccs.monitor import _normalize_event


def event(component, action, status="started", **details):
    return _normalize_event({"event_id": "e1", "component": component, "action": action,
                             "status": status, "writer_id": "operation", "details": details})


def comm(record):
    return record["presentation"]["communication"]


def test_handoff_shows_actual_fields_and_values_without_credentials():
    request = {"task_id": "episode-1", "incident": {"target": "HOST-001", "summary": "Cannot reach server"},
               "context": {"runbooks": [{"doc_id": "RB-W2", "content": "Inspect route table"}],
                           "history": [], "observations": {"gateway": "10.0.1.254"}},
               "constraints": {"tool_budget": 8}, "api_key": "not-for-screen"}
    record = event("a2a", "delegate_diagnosis", request=request)
    value = comm(record)
    assert (value["source"], value["destination"], value["protocol"], value["kind"]) == ("operation", "diagnosis", "A2A", "request")
    fields = {part["key"]: part["value"] for part in value["sections"]}
    assert fields["incident"] == request["incident"]
    assert fields["runbooks"] == request["context"]["runbooks"]
    assert fields["history"] == []
    assert fields["context"] == {"observations": {"gateway": "10.0.1.254"}}
    assert fields["constraints"] == {"tool_budget": 8}
    assert fields["envelope"]["api_key"] == "[redacted by monitor]"
    assert "not-for-screen" not in str(record)


def test_response_and_client_server_mcp_directions_are_distinct():
    a2a = comm(event("a2a", "delegate_diagnosis", "succeeded", response={"root_cause": "incorrect_default_gateway"}))
    assert (a2a["source"], a2a["destination"], a2a["kind"]) == ("diagnosis", "operation", "response")
    call = comm(event("mcp", "call", role="diagnosis", tool="get_config", arguments={"target": "HOST-001"}))
    reply = comm(event("mcp", "call", "succeeded", role="diagnosis", result={"items": []}))
    backend = comm(event("mcp", "execute", caller_role="diagnosis", tool="get_config"))
    backend_reply = comm(event("mcp", "execute", "succeeded", caller_role="diagnosis", result={"items": []}))
    assert (call["source"], call["destination"]) == ("diagnosis", "tools")
    assert (reply["source"], reply["destination"]) == ("tools", "diagnosis")
    assert (backend["source"], backend["destination"]) == ("tools", "network")
    assert (backend_reply["source"], backend_reply["destination"]) == ("network", "tools")


def test_failed_transport_is_not_claimed_to_be_a_response():
    value = comm(event("mcp", "call", "failed", role="operation", error_type="TimeoutError"))
    assert value["kind"] == "request_failed"
    assert (value["source"], value["destination"]) == ("operation", "tools")
    value = comm(event("a2a", "delegate_diagnosis", "failed", error_type="TimeoutError"))
    assert value["kind"] == "request_failed"


def test_model_copy_has_no_removed_notice_and_keeps_scrubbing():
    record = event("model", "request", "succeeded", role="diagnosis", model="example-model",
                   selected_tools=[{"name": "finish", "arguments": {"root_cause": "link_down"}}],
                   raw_response={"thinking": "not-for-screen"})
    assert comm(record)["source"] == "model"
    assert comm(record)["destination"] == "diagnosis"
    assert "비공개" not in record["presentation"]["detail"]["ko"]
    assert "Private reasoning" not in record["presentation"]["detail"]["en"]
    assert "not-for-screen" not in str(record)


def test_internal_stage_and_disabled_retrieval_do_not_invent_communication():
    for record in (event("runner", "workflow", "info"), event("runbook", "search", "skipped", disabled=True)):
        value = comm(record)
        assert value["kind"] == "internal"
        assert value["source"] == value["destination"]
