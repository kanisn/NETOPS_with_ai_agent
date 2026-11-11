"""Generate deterministic source/function reference pages without importing the app."""
from __future__ import annotations

import argparse
import ast
from collections import Counter
import hashlib
import json
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "docs" / "reference"


def module_name(path: Path) -> str:
    """Use import-like names, keeping __init__ files explicit for file coverage."""
    relative = path.relative_to(ROOT).with_suffix("")
    parts = list(relative.parts)
    if parts[0] == "src":
        parts = parts[1:]
    return ".".join(parts)


def anchor(prefix: str, name: str) -> str:
    """Return the explicit HTML anchor shared by folder README links."""
    return prefix + "-" + name.replace(".", "-")


def direct_calls(node: ast.AST) -> list[str]:
    """Collect syntactic call expressions, without claiming runtime dispatch resolution."""
    found = set()
    pending = list(ast.iter_child_nodes(node))
    while pending:
        child = pending.pop()
        if isinstance(child, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef, ast.Lambda)):
            continue
        if isinstance(child, ast.Call):
            try:
                expression = ast.unparse(child.func)
                if len(expression) <= 100:
                    found.add(expression)
            except (ValueError, TypeError):
                pass
        pending.extend(ast.iter_child_nodes(child))
    return sorted(found)


def symbols(tree: ast.AST, module: str) -> list[dict]:
    """Enumerate classes, functions, methods, and nested handlers from Python AST."""
    result = []

    def visit(node: ast.AST, parents: list[str], parent_kinds: list[str]) -> None:
        for child in ast.iter_child_nodes(node):
            if isinstance(child, (ast.ClassDef, ast.FunctionDef, ast.AsyncFunctionDef)):
                name = ".".join([module, *parents, child.name])
                kind = "class" if isinstance(child, ast.ClassDef) else "async" if isinstance(child, ast.AsyncFunctionDef) else "function"
                item = {"name": name, "short_name": ".".join([*parents, child.name]), "kind": kind,
                        "line": child.lineno, "end_line": child.end_lineno,
                        "nested": "function" in parent_kinds or "async" in parent_kinds,
                        "method": bool(parent_kinds and parent_kinds[-1] == "class"),
                        "docstring": ast.get_docstring(child) or ""}
                if kind == "class":
                    item["bases"] = [ast.unparse(base) for base in child.bases]
                    item["fields"] = [statement.target.id for statement in child.body
                                      if isinstance(statement, ast.AnnAssign) and isinstance(statement.target, ast.Name)]
                    item["arguments"] = ""
                    item["calls"] = []
                else:
                    item["arguments"] = ast.unparse(child.args)
                    item["returns"] = ast.unparse(child.returns) if child.returns else None
                    item["calls"] = direct_calls(child)
                result.append(item)
                visit(child, [*parents, child.name], [*parent_kinds, kind])
            else:
                visit(child, parents, parent_kinds)

    visit(tree, [], [])
    used = Counter()
    for item in result:
        key = anchor("class" if item["kind"] == "class" else "fn", item["name"])
        used[key] += 1
        item["anchor"] = key + (f"-{used[key]}" if used[key] > 1 else "")
    return result


def inventory() -> list[dict]:
    """Read only source, tests and repository tools; never load local configuration."""
    paths = sorted([*ROOT.joinpath("src").rglob("*.py"), *ROOT.joinpath("tests").glob("*.py"), *ROOT.joinpath("tools").glob("*.py")])
    modules = []
    for path in paths:
        if "__pycache__" in path.parts:
            continue
        text = path.read_text(encoding="utf-8-sig")
        tree = ast.parse(text, filename=str(path))
        modules.append({"module": module_name(path), "path": path.relative_to(ROOT).as_posix(),
                        "normalized_sha256": hashlib.sha256(text.encode("utf-8")).hexdigest(),
                        "module_docstring": ast.get_docstring(tree) or "", "symbols": symbols(tree, module_name(path))})
    return modules


def escape(text: str) -> str:
    return text.replace("|", "\\|").replace("\n", " ").replace("<", "&lt;").replace(">", "&gt;")


def build_python_reference(modules: list[dict]) -> str:
    functions = sum(item["kind"] != "class" for module in modules for item in module["symbols"])
    classes = sum(item["kind"] == "class" for module in modules for item in module["symbols"])
    lines = ["# Python 파일·함수 전체 참조", "", "[루트 안내](../../README.md) · [문서 목차](../README.md) · [참조 읽는 법](README.md)", "",
             f"현재 소스에서 **Python {len(modules)}개 파일, 함수·메서드 {functions}개, 클래스 {classes}개**를 읽어 만든 목록입니다. 테스트와 문서 관리 도구도 포함합니다.", "",
             "이 문서는 함수의 위치와 입력, 원문 설명을 찾는 사전입니다. 처음에는 [전체 실행 흐름](../ARCHITECTURE.md)을 읽고 해당 폴더 README에서 역할을 익힌 뒤 필요한 항목만 찾아보세요.", "",
             "- `async`: 다른 작업의 응답을 기다릴 수 있는 비동기 함수입니다.",
             "- `메서드`: 클래스 인스턴스의 동작입니다. `self`는 그 인스턴스를 뜻합니다.",
             "- `_`로 시작하는 이름은 내부용이라는 관례이며 접근 보안 장치는 아닙니다.",
             "- 중첩 함수는 다른 함수 안에서 만들어지는 callback/handler입니다.",
             "- 호출 표현은 AST에 직접 적힌 이름만 보여 줍니다. 동적 dispatch, HTTP/A2A/MCP 경계, 실행 순서를 자동으로 증명하지 않습니다.",
             "- docstring은 소스의 설명을 그대로 인용합니다. 설명이 없는 작은 내부 함수는 폴더 README의 상위 흐름과 소스를 함께 확인하세요.", ""]
    for group, prefix in [("애플리케이션", "src/"), ("tests", "tests/"), ("관리 도구", "tools/")]:
        lines += [f'<a id="{group if group == "tests" else "application" if prefix == "src/" else "tools"}"></a>', f"## {group}", "",
                  "| 모듈 | 함수·메서드 | 클래스 |", "|---|---:|---:|"]
        for module in modules:
            if not module["path"].startswith(prefix):
                continue
            funcs = sum(item["kind"] != "class" for item in module["symbols"])
            classes_count = len(module["symbols"]) - funcs
            lines.append(f"| [{module['module']}](#{anchor('module', module['module'])}) | {funcs} | {classes_count} |")
        lines.append("")
    for module in modules:
        source = "../../" + module["path"]
        parent = str(Path(source).parent).replace("\\", "/") + "/README.md"
        lines += [f'<a id="{anchor("module", module["module"])}"></a>', f"## `{module['module']}`", "",
                  f"[소스 파일]({source}) · [이 폴더 설명]({parent})", ""]
        if module["module_docstring"]:
            lines += ["> 소스의 모듈 설명: " + escape(module["module_docstring"]), ""]
        if not module["symbols"]:
            lines += ["이 파일에는 Python 함수/클래스 정의가 없습니다. 패키지 초기화, 실행 진입점 또는 데이터/화면 문자열을 담는 파일이며 역할은 폴더 README에서 설명합니다.", ""]
        for item in module["symbols"]:
            kind = "클래스" if item["kind"] == "class" else ("비동기 " if item["kind"] == "async" else "") + ("메서드" if item["method"] else "함수") + (" (중첩 handler)" if item["nested"] else "")
            lines += [f'<a id="{item["anchor"]}"></a>', f"### `{item['short_name']}`", "", f"**{kind}** · [정의 위치 L{item['line']}]({source}#L{item['line']})", ""]
            if item["kind"] == "class":
                lines += ["상속/계약: " + (", ".join(f"`{escape(base)}`" for base in item["bases"]) or "별도 상속 없음"), "",
                          "선언된 필드: " + (", ".join(f"`{field}`" for field in item["fields"]) or "없음. 생성자나 메서드에서 상태를 만들 수 있습니다."), ""]
            else:
                lines += ["```python", ("async " if item["kind"] == "async" else "") + f"{item['short_name']}({item['arguments']})" + (f" -> {item['returns']}" if item.get("returns") else ""), "```", ""]
            if item["docstring"]:
                lines += ["> " + escape(item["docstring"]), ""]
            elif item["short_name"].split(".")[-1].startswith("test_"):
                lines += ["테스트 함수입니다. 어떤 정상/실패 조건을 확인하는지는 [테스트 안내](../../tests/README.md)와 assertion을 함께 읽으세요.", ""]
            else:
                lines += ["상세 동작은 위 정의 위치와 이 폴더의 파일별 역할 설명을 함께 확인하세요.", ""]
            if item["calls"]:
                lines += ["<details><summary>본문에 직접 적힌 호출 표현</summary>", "", ", ".join(f"`{escape(call)}`" for call in item["calls"]), "", "</details>", ""]
    return "\n".join(lines)


def web_inventory() -> list[dict]:
    """Catalog named JS declarations/assigned arrows embedded in the three UI sources."""
    result = []
    patterns = [re.compile(r"\b(?:async\s+)?function\s+([A-Za-z_$][\w$]*)\s*\(([^)]*)\)"),
                re.compile(r"\b(?:const|let|var)\s+([A-Za-z_$][\w$]*)\s*=\s*(?:async\s+)?(?:\(([^)]*)\)|([A-Za-z_$][\w$]*))\s*=>")]
    for name in ["studio_script.py", "monitor.py", "monitor_i18n.py"]:
        path = ROOT / "src" / "ccs" / name
        text = path.read_text(encoding="utf-8")
        functions = []
        for kind, pattern in zip(["function 선언", "이름에 할당한 arrow function"], patterns):
            for match in pattern.finditer(text):
                functions.append({"name": match.group(1), "arguments": match.group(2) if match.group(2) is not None else match.group(3),
                                  "line": text[:match.start()].count("\n") + 1, "kind": kind})
        result.append({"path": path.relative_to(ROOT).as_posix(), "functions": sorted(functions, key=lambda item: item["line"])})
    return result


def build_web_reference(groups: list[dict]) -> str:
    count = sum(len(group["functions"]) for group in groups)
    lines = ["# 웹 JavaScript 함수 참조", "", "[참조 목차](README.md) · [브라우저 코드 설명](../../src/ccs/README.md)", "",
             f"Python 파일 안에 문자열로 들어 있는 **이름 있는 JavaScript 함수 {count}개**의 선언 위치입니다. Python AST 함수 목록과 별개입니다.", "",
             "이 목록은 `function 이름(...)`과 이름에 할당한 arrow function 선언을 찾습니다. 익명 이벤트 callback과 객체 method를 모두 나열한 JavaScript AST 그래프는 아닙니다. 클릭/입력/주기 갱신의 전체 연결은 [웹 화면 구조](../ARCHITECTURE.md#web-flow)와 각 파일 설명을 함께 보세요.", ""]
    for group in groups:
        name = Path(group["path"]).stem
        lines += [f'<a id="module-{name}"></a>', f"## `{name}.py`에 포함된 JavaScript", "",
                  "| 함수 | 입력 | 선언 형태 | 소스 위치 |", "|---|---|---|---|"]
        for item in group["functions"]:
            lines.append(f"| `{item['name']}` | `{escape(item['arguments'])}` | {item['kind']} | [L{item['line']}](../../{group['path']}#L{item['line']}) |")
        lines.append("")
    return "\n".join(lines)


def generate(check: bool = False) -> bool:
    modules = inventory()
    web = web_inventory()
    outputs = {"python_functions.md": build_python_reference(modules), "web_functions.md": build_web_reference(web),
               "function_inventory.json": json.dumps({"python": modules, "javascript_named": web}, ensure_ascii=False, indent=2) + "\n"}
    mismatches = []
    for name, content in outputs.items():
        target = OUTPUT / name
        if check:
            if not target.exists() or target.read_text(encoding="utf-8") != content:
                mismatches.append(name)
        else:
            OUTPUT.mkdir(parents=True, exist_ok=True)
            target.write_text(content, encoding="utf-8", newline="\n")
    print(json.dumps({"check": check, "python_files": len(modules),
                      "python_functions": sum(item["kind"] != "class" for module in modules for item in module["symbols"]),
                      "javascript_named_functions": sum(len(group["functions"]) for group in web), "stale": mismatches}, ensure_ascii=False))
    return not mismatches


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true", help="Validate generated references without writing files")
    raise SystemExit(0 if generate(parser.parse_args().check) else 1)
