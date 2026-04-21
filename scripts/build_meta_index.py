from __future__ import annotations

import ast
import json
import re
from collections import defaultdict
from dataclasses import dataclass
from datetime import date
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
SRC_DIR = ROOT / "src"
TESTS_DIR = ROOT / "tests"
FRONTEND_DIR = ROOT / "frontend"
META_DIR = ROOT / "meta"
TODAY = date.today().isoformat()

MARKDOWN_DIRS = [
    ROOT / "docs",
    ROOT / "specs",
    ROOT / "tasks",
    ROOT / "agents",
]
ROOT_MARKDOWN_FILES = [
    ROOT / "README.md",
    ROOT / "AGENTS.md",
]

TASK_REF_RE = re.compile(r"(tasks/[A-Za-z0-9_./-]+\.md)")
DOC_REF_RE = re.compile(r"((?:docs|specs|agents|meta|reviews)/[A-Za-z0-9_./-]+\.md|README\.md|AGENTS\.md)")
ENDPOINT_RE = re.compile(r"(?:GET|POST|PUT|PATCH|DELETE)\s+(/api/[A-Za-z0-9_./{-}:-]+)|(/api/[A-Za-z0-9_./{-}:-]+)")
HEADING_RE = re.compile(r"^(#{1,6})\s+(.+?)\s*$")


@dataclass
class EntityRef:
    entity_id: str
    entity_type: str
    path: str | None = None
    symbol_path: str | None = None
    feature_tags: list[str] | None = None
    task_ids: list[str] | None = None
    api_endpoints: list[str] | None = None


def relative(path: Path) -> str:
    return path.relative_to(ROOT).as_posix()


def slugify(text: str) -> str:
    text = text.lower().strip()
    text = re.sub(r"`+", "", text)
    text = re.sub(r"[^a-z0-9가-힣\s/-]", "", text)
    text = re.sub(r"[\s/]+", "-", text)
    text = re.sub(r"-{2,}", "-", text).strip("-")
    return text or "section"


def module_name_for_path(path: Path) -> str:
    rel = path.relative_to(SRC_DIR).with_suffix("")
    return ".".join(rel.parts)


def infer_feature_tags(path_str: str) -> list[str]:
    tags: list[str] = []
    if path_str.startswith("frontend/"):
        tags.extend(["frontend", "runtime"])
    if "/engine/" in f"/{path_str}/" or path_str.startswith("src/engine") or path_str.startswith("tests/unit/engine") or path_str.startswith("tests/integration/engine"):
        tags.append("engine")
    if "/training/" in f"/{path_str}/" or path_str.startswith("src/training") or path_str.startswith("tests/unit/training"):
        tags.append("training")
    if "/runtime/" in f"/{path_str}/" or path_str.startswith("src/api") or path_str.startswith("tests/unit/runtime") or "fastapi" in path_str:
        tags.append("runtime")
    if "self-play" in path_str or "self_play" in path_str:
        tags.append("self-play")
    if "checkpoint" in path_str:
        tags.append("checkpoint")
    if "trainer" in path_str or "training-pipeline" in path_str or "training_pipeline" in path_str:
        tags.append("trainer-loop")
    if "dashboard" in path_str:
        tags.append("training-dashboard")
    if "api" in path_str:
        tags.append("api")
    return sorted(set(tags))


def infer_owner(path_str: str) -> str:
    if path_str.startswith("frontend/"):
        return "runtime-agent"
    if path_str.startswith("src/engine") or "/engine/" in path_str:
        return "engine-agent"
    if path_str.startswith("src/api") or "/runtime/" in path_str or "fastapi" in path_str:
        return "runtime-agent"
    if path_str.startswith("src/training") or "/training/" in path_str:
        data_markers = (
            "self-play",
            "self_play",
            "episode",
            "checkpoint",
            "cnn",
            "rl-components",
            "policy",
            "predict-api",
            "action_mask",
            "state_encoder",
        )
        if any(marker in path_str for marker in data_markers):
            return "training-data-agent"
        return "training-loop-agent"
    if path_str.startswith("tasks/specs") or path_str.startswith("tasks/review") or path_str.startswith("meta/") or path_str.startswith("agents/"):
        return "governance-agent"
    if path_str in {"README.md", "AGENTS.md"}:
        return "governance-agent"
    return "governance-agent"


def discover_python_files(base: Path) -> list[Path]:
    return sorted(
        path for path in base.rglob("*.py")
        if "__pycache__" not in path.parts
    )


def discover_frontend_files() -> list[Path]:
    if not FRONTEND_DIR.exists():
        return []
    extensions = {".js", ".jsx", ".ts", ".tsx", ".css", ".html"}
    return sorted(
        path for path in FRONTEND_DIR.rglob("*")
        if path.is_file() and path.suffix in extensions
    )


def discover_markdown_files() -> list[Path]:
    files = list(ROOT_MARKDOWN_FILES)
    for directory in MARKDOWN_DIRS:
        files.extend(sorted(directory.rglob("*.md")))
    return sorted(set(files))


def dotted_name(node: ast.AST) -> str | None:
    if isinstance(node, ast.Name):
        return node.id
    if isinstance(node, ast.Attribute):
        base = dotted_name(node.value)
        if base is None:
            return node.attr
        return f"{base}.{node.attr}"
    if isinstance(node, ast.Call):
        return dotted_name(node.func)
    return None


def resolve_relative_import(module: str, level: int, current_module: str) -> str:
    if level == 0:
        return module
    package_parts = current_module.split(".")[:-1]
    if level > len(package_parts) + 1:
        return module
    prefix = package_parts[: len(package_parts) - level + 1]
    if module:
        return ".".join(prefix + module.split("."))
    return ".".join(prefix)


def local_symbol_target(symbol: str, alias_map: dict[str, str], current_module: str, local_defs: set[str], current_class: str | None) -> str:
    parts = symbol.split(".")
    head = parts[0]
    if head in alias_map:
        resolved = alias_map[head]
        if len(parts) > 1:
            return ".".join([resolved, *parts[1:]])
        return resolved
    if head == "self" and current_class:
        return ".".join([current_module, current_class, *parts[1:]]) if len(parts) > 1 else f"{current_module}.{current_class}"
    if head in local_defs:
        return ".".join([current_module, *parts])
    if symbol.startswith(("engine.", "training.", "api.")):
        return symbol
    return symbol


def detect_status(text: str) -> str:
    lowered = text.lower()
    if "deprecated" in lowered or "폐기" in lowered:
        return "deprecated"
    if "draft" in lowered or "초안" in lowered:
        return "draft"
    return "active"


class FunctionAnalyzer(ast.NodeVisitor):
    def __init__(self) -> None:
        self.calls: list[str] = []
        self.raises: list[str] = []

    def visit_Call(self, node: ast.Call) -> Any:
        name = dotted_name(node.func)
        if name:
            self.calls.append(name)
        self.generic_visit(node)

    def visit_Raise(self, node: ast.Raise) -> Any:
        if node.exc is None:
            return
        name = dotted_name(node.exc)
        if name:
            self.raises.append(name)
        elif isinstance(node.exc, ast.Constant) and isinstance(node.exc.value, str):
            self.raises.append(node.exc.value)
        self.generic_visit(node)


def build_code_entities() -> tuple[list[dict[str, Any]], list[dict[str, Any]], dict[str, str]]:
    entities: list[dict[str, Any]] = []
    edges: list[dict[str, Any]] = []
    symbol_to_entity: dict[str, str] = {}

    for path in discover_python_files(SRC_DIR):
        rel_path = relative(path)
        module_name = module_name_for_path(path)
        source = path.read_text(encoding="utf-8")
        tree = ast.parse(source, filename=rel_path)
        alias_map: dict[str, str] = {}
        module_imports: list[str] = []
        local_defs: set[str] = set()
        decorators: list[str] = []
        endpoints_for_function: dict[str, list[str]] = defaultdict(list)

        for node in tree.body:
            if isinstance(node, ast.Import):
                for alias in node.names:
                    alias_name = alias.asname or alias.name.split(".")[0]
                    alias_map[alias_name] = alias.name
                    module_imports.append(alias.name)
            elif isinstance(node, ast.ImportFrom):
                resolved_module = resolve_relative_import(node.module or "", node.level, module_name)
                for alias in node.names:
                    alias_name = alias.asname or alias.name
                    alias_map[alias_name] = f"{resolved_module}.{alias.name}" if resolved_module else alias.name
                    module_imports.append(alias_map[alias_name])
            elif isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
                local_defs.add(node.name)

        module_uses_config_env = any(
            item.startswith("os") or "dotenv" in item for item in module_imports
        ) and any(token in source for token in ("os.environ", "os.getenv", "environ[", "getenv("))
        module_references_db_model = any(
            token in source for token in ("sqlalchemy", "declarative_base", "Base =", "models.")
        )
        module_calls_external_api = any(
            token in source for token in ("requests.", "httpx.", "urllib.request", "aiohttp.", "openai.")
        )
        module_feature_tags = infer_feature_tags(rel_path)
        module_owner = infer_owner(rel_path)
        module_entity = {
            "entity_id": f"code:{rel_path}",
            "entity_type": "code.module",
            "module_path": rel_path,
            "symbol_path": module_name,
            "class_name": None,
            "function_name": None,
            "decorators": [],
            "imports": sorted(set(module_imports)),
            "calls": [],
            "raises": [],
            "uses_config_env": module_uses_config_env,
            "references_db_model": module_references_db_model,
            "calls_external_api": module_calls_external_api,
            "feature_tags": module_feature_tags,
            "task_ids": [],
            "api_endpoints": [],
            "owner": module_owner,
            "last_updated": TODAY,
        }
        entities.append(module_entity)
        symbol_to_entity[module_name] = module_entity["entity_id"]

        for node in tree.body:
            if isinstance(node, ast.ClassDef):
                class_symbol = f"{module_name}.{node.name}"
                class_entity_id = f"code:{rel_path}:{node.name}"
                class_decorators = [dotted_name(dec) or ast.unparse(dec) for dec in node.decorator_list]
                entities.append(
                    {
                        "entity_id": class_entity_id,
                        "entity_type": "code.class",
                        "module_path": rel_path,
                        "symbol_path": class_symbol,
                        "class_name": node.name,
                        "function_name": None,
                        "decorators": class_decorators,
                        "imports": sorted(set(module_imports)),
                        "calls": [],
                        "raises": [],
                        "uses_config_env": module_uses_config_env,
                        "references_db_model": module_references_db_model,
                        "calls_external_api": module_calls_external_api,
                        "feature_tags": module_feature_tags,
                        "task_ids": [],
                        "api_endpoints": [],
                        "owner": module_owner,
                        "last_updated": TODAY,
                    }
                )
                symbol_to_entity[class_symbol] = class_entity_id
                edges.append({"from": f"code:{rel_path}", "relation": "defines", "to": class_entity_id})
                for child in node.body:
                    if isinstance(child, (ast.FunctionDef, ast.AsyncFunctionDef)):
                        local_defs.add(child.name)

            elif isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                if module_name == "api.fastapi_app":
                    for decorator in node.decorator_list:
                        decorator_name = dotted_name(decorator)
                        if decorator_name in {"app.get", "app.post", "app.put", "app.patch", "app.delete"} and isinstance(decorator, ast.Call):
                            if decorator.args and isinstance(decorator.args[0], ast.Constant) and isinstance(decorator.args[0].value, str):
                                method = decorator_name.split(".")[-1].upper()
                                endpoints_for_function[node.name].append(f"{method} {decorator.args[0].value}")

        for node in tree.body:
            if not isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
                continue

            if isinstance(node, ast.ClassDef):
                current_class = node.name
                function_nodes = [child for child in node.body if isinstance(child, (ast.FunctionDef, ast.AsyncFunctionDef))]
            else:
                current_class = None
                function_nodes = [node]

            for func in function_nodes:
                analyzer = FunctionAnalyzer()
                analyzer.visit(func)
                function_symbol = ".".join(part for part in [module_name, current_class, func.name] if part)
                function_entity_id = f"code:{rel_path}:{'.'.join(part for part in [current_class, func.name] if part)}"
                raw_calls = [local_symbol_target(call, alias_map, module_name, local_defs, current_class) for call in analyzer.calls]
                raw_raises = [local_symbol_target(name, alias_map, module_name, local_defs, current_class) for name in analyzer.raises]
                function_decorators = [dotted_name(dec) or ast.unparse(dec) for dec in func.decorator_list]
                api_endpoints = endpoints_for_function.get(func.name, [])
                entity = {
                    "entity_id": function_entity_id,
                    "entity_type": "code.function",
                    "module_path": rel_path,
                    "symbol_path": function_symbol,
                    "class_name": current_class,
                    "function_name": func.name,
                    "decorators": function_decorators,
                    "imports": sorted(set(module_imports)),
                    "calls": sorted(set(raw_calls)),
                    "raises": sorted(set(raw_raises)),
                    "uses_config_env": module_uses_config_env,
                    "references_db_model": module_references_db_model,
                    "calls_external_api": module_calls_external_api,
                    "feature_tags": module_feature_tags,
                    "task_ids": [],
                    "api_endpoints": api_endpoints,
                    "owner": module_owner,
                    "last_updated": TODAY,
                }
                entities.append(entity)
                symbol_to_entity[function_symbol] = function_entity_id
                parent_id = f"code:{rel_path}:{current_class}" if current_class else f"code:{rel_path}"
                edges.append({"from": parent_id, "relation": "defines", "to": function_entity_id})

                for call in entity["calls"]:
                    if call.startswith(("engine.", "training.", "api.")):
                        edges.append({"from": function_entity_id, "relation": "calls", "to": call})
                for raised in entity["raises"]:
                    target = raised if raised.startswith("exception:") else f"exception:{raised}"
                    edges.append({"from": function_entity_id, "relation": "raises", "to": target})
                for endpoint in api_endpoints:
                    edges.append({"from": function_entity_id, "relation": "exposes", "to": f"endpoint:{endpoint}"})

    return entities, edges, symbol_to_entity


def build_frontend_entities() -> list[dict[str, Any]]:
    entities: list[dict[str, Any]] = []
    import_re = re.compile(r'^\s*import\s+(?:.+?\s+from\s+)?["\']([^"\']+)["\']', re.MULTILINE)

    for path in discover_frontend_files():
        rel_path = relative(path)
        source = path.read_text(encoding="utf-8")
        imports = sorted(set(import_re.findall(source)))
        api_endpoints = sorted(
            set(
                endpoint.group(1) or endpoint.group(2)
                for endpoint in ENDPOINT_RE.finditer(source)
                if endpoint.group(1) or endpoint.group(2)
            )
        )
        symbol_path = rel_path.replace("/", ".")
        entities.append(
            {
                "entity_id": f"code:{rel_path}",
                "entity_type": "code.module",
                "module_path": rel_path,
                "symbol_path": symbol_path,
                "class_name": None,
                "function_name": None,
                "decorators": [],
                "imports": imports,
                "calls": [],
                "raises": [],
                "uses_config_env": "import.meta.env" in source,
                "references_db_model": False,
                "calls_external_api": "fetch(" in source,
                "feature_tags": infer_feature_tags(rel_path),
                "task_ids": [],
                "api_endpoints": api_endpoints,
                "owner": infer_owner(rel_path),
                "last_updated": TODAY,
            }
        )

    return entities


def parse_markdown_entities() -> tuple[list[dict[str, Any]], list[dict[str, Any]], dict[str, str]]:
    entities: list[dict[str, Any]] = []
    edges: list[dict[str, Any]] = []
    path_to_entity: dict[str, str] = {}

    for path in discover_markdown_files():
        rel_path = relative(path)
        text = path.read_text(encoding="utf-8")
        feature_tags = infer_feature_tags(rel_path)
        task_ids = sorted(set(TASK_REF_RE.findall(text)))
        api_endpoints = sorted(
            set(
                endpoint.group(1) or endpoint.group(2)
                for endpoint in ENDPOINT_RE.finditer(text)
                if endpoint.group(1) or endpoint.group(2)
            )
        )
        file_entity_id = f"doc:{rel_path}"
        file_entity = {
            "entity_id": file_entity_id,
            "entity_type": "doc.file",
            "path": rel_path,
            "section_id": None,
            "title": path.stem,
            "feature_tags": feature_tags,
            "task_ids": task_ids,
            "api_endpoints": api_endpoints,
            "owner": infer_owner(rel_path),
            "last_updated": TODAY,
            "status": detect_status(text),
        }
        entities.append(file_entity)
        path_to_entity[rel_path] = file_entity_id

        for line in text.splitlines():
            match = HEADING_RE.match(line)
            if not match:
                continue
            heading = match.group(2).strip()
            section_id = slugify(heading)
            section_entity_id = f"doc:{rel_path}#{section_id}"
            entities.append(
                {
                    "entity_id": section_entity_id,
                    "entity_type": "doc.section",
                    "path": rel_path,
                    "section_id": section_id,
                    "title": heading,
                    "feature_tags": feature_tags,
                    "task_ids": task_ids,
                    "api_endpoints": api_endpoints,
                    "owner": infer_owner(rel_path),
                    "last_updated": TODAY,
                    "status": detect_status(text),
                }
            )
            edges.append({"from": file_entity_id, "relation": "defines", "to": section_entity_id})

        for ref in sorted(set(DOC_REF_RE.findall(text))):
            if ref == rel_path:
                continue
            edges.append({"from": file_entity_id, "relation": "references", "to": f"doc:{ref}"})
        for task_ref in task_ids:
            edges.append({"from": file_entity_id, "relation": "references", "to": f"doc:{task_ref}"})
        if rel_path.startswith("tasks/"):
            for ref in sorted(set(DOC_REF_RE.findall(text))):
                if ref.startswith("specs/"):
                    edges.append({"from": file_entity_id, "relation": "implements", "to": f"doc:{ref}"})
                elif ref.startswith(("docs/", "agents/", "meta/")) or ref in {"README.md", "AGENTS.md"}:
                    edges.append({"from": file_entity_id, "relation": "references", "to": f"doc:{ref}"})

    return entities, edges, path_to_entity


def build_test_entities(symbol_to_entity: dict[str, str]) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    entities: list[dict[str, Any]] = []
    edges: list[dict[str, Any]] = []

    for path in discover_python_files(TESTS_DIR):
        rel_path = relative(path)
        source = path.read_text(encoding="utf-8")
        tree = ast.parse(source, filename=rel_path)
        alias_map: dict[str, str] = {}
        module_imports: list[str] = []

        for node in tree.body:
            if isinstance(node, ast.Import):
                for alias in node.names:
                    alias_name = alias.asname or alias.name.split(".")[0]
                    alias_map[alias_name] = alias.name
                    module_imports.append(alias.name)
            elif isinstance(node, ast.ImportFrom):
                module = node.module or ""
                for alias in node.names:
                    alias_name = alias.asname or alias.name
                    alias_map[alias_name] = f"{module}.{alias.name}" if module else alias.name
                    module_imports.append(alias_map[alias_name])

        test_level = "integration" if "/integration/" in rel_path else "unit"
        if "/e2e/" in rel_path:
            test_level = "e2e"

        for node in tree.body:
            if not isinstance(node, ast.FunctionDef) or not node.name.startswith("test_"):
                continue

            fixtures = [arg.arg for arg in node.args.args]
            referenced_symbols: set[str] = set()
            for child in ast.walk(node):
                if isinstance(child, ast.Call):
                    call_name = dotted_name(child.func)
                    if call_name:
                        referenced_symbols.add(call_name)
                elif isinstance(child, ast.Name):
                    referenced_symbols.add(child.id)
                elif isinstance(child, ast.Attribute):
                    attr_name = dotted_name(child)
                    if attr_name:
                        referenced_symbols.add(attr_name)

            target_symbols = sorted(
                {
                    local_symbol_target(symbol, alias_map, "tests", set(), None)
                    for symbol in referenced_symbols
                    if local_symbol_target(symbol, alias_map, "tests", set(), None).startswith(("engine.", "training.", "api."))
                }
            )
            entity_id = f"test:{rel_path}:{node.name}"
            entity = {
                "entity_id": entity_id,
                "entity_type": f"test.{test_level}",
                "path": rel_path,
                "target_symbols": target_symbols,
                "test_level": test_level,
                "fixtures": fixtures,
                "uses_db": False,
                "uses_mock": "monkeypatch" in fixtures or any(token in source for token in ("unittest.mock", "mock.", "SimpleNamespace")),
                "uses_external_dependency": any(token in source for token in ("TestClient", "requests.", "httpx.", "subprocess", "docker")),
                "feature_tags": infer_feature_tags(rel_path),
                "owner": infer_owner(rel_path),
                "last_updated": TODAY,
            }
            entities.append(entity)

            for symbol in target_symbols:
                edges.append({"from": entity_id, "relation": "verifies", "to": symbol_to_entity.get(symbol, symbol)})

    return entities, edges


def build_nodes(*entity_groups: list[dict[str, Any]]) -> list[dict[str, Any]]:
    nodes: list[dict[str, Any]] = []
    seen: set[str] = set()
    for entities in entity_groups:
        for entity in entities:
            entity_id = entity["entity_id"]
            if entity_id in seen:
                continue
            seen.add(entity_id)
            node = {
                "entity_id": entity_id,
                "entity_type": entity["entity_type"],
            }
            if "path" in entity:
                node["path"] = entity["path"]
            if "module_path" in entity:
                node["path"] = entity["module_path"]
            if "symbol_path" in entity:
                node["symbol_path"] = entity["symbol_path"]
            nodes.append(node)
    return sorted(nodes, key=lambda item: item["entity_id"])


def build_indexes(
    code_entities: list[dict[str, Any]],
    doc_entities: list[dict[str, Any]],
    test_entities: list[dict[str, Any]],
) -> tuple[dict[str, list[str]], dict[str, list[str]], dict[str, list[str]], dict[str, list[str]]]:
    by_symbol: dict[str, list[str]] = defaultdict(list)
    by_feature: dict[str, list[str]] = defaultdict(list)
    by_task: dict[str, list[str]] = defaultdict(list)
    by_endpoint: dict[str, list[str]] = defaultdict(list)

    for entity in [*code_entities, *doc_entities, *test_entities]:
        entity_id = entity["entity_id"]
        symbol = entity.get("symbol_path")
        if symbol:
            by_symbol[symbol].append(entity_id)
            by_symbol[symbol.split(".")[-1]].append(entity_id)
        for tag in entity.get("feature_tags", []):
            by_feature[tag].append(entity_id)
        for task_id in entity.get("task_ids", []):
            by_task[task_id].append(entity_id)
        for endpoint in entity.get("api_endpoints", []):
            by_endpoint[endpoint].append(entity_id)

    def finalize(index: dict[str, list[str]]) -> dict[str, list[str]]:
        return {key: sorted(set(value)) for key, value in sorted(index.items())}

    return finalize(by_symbol), finalize(by_feature), finalize(by_task), finalize(by_endpoint)


def parse_checklist_section(lines: list[str]) -> dict[str, Any]:
    items: list[tuple[str, str]] = []
    current_item: tuple[str, str] | None = None
    for line in lines:
        stripped = line.strip()
        match = re.match(r"- \[([x -])\] (.+)", stripped)
        if match:
            status_char = match.group(1)
            status = {"x": "done", "-": "partial", " ": "todo"}[status_char]
            current_item = (status, match.group(2).strip())
            items.append(current_item)
    return {"items": items}


def build_compressed_states() -> dict[str, dict[str, Any]]:
    checklist = (ROOT / "tasks" / "implementation-checklist.md").read_text(encoding="utf-8").splitlines()
    sections: dict[str, list[str]] = {"engine": [], "training": [], "runtime": []}
    current: str | None = None
    for line in checklist:
        if line.startswith("## Engine"):
            current = "engine"
            continue
        if line.startswith("## Training"):
            current = "training"
            continue
        if line.startswith("## Runtime"):
            current = "runtime"
            continue
        if line.startswith("## ") and current is not None:
            current = None
        if current is not None:
            sections[current].append(line)

    states: dict[str, dict[str, Any]] = {}
    for axis, lines in sections.items():
        parsed = parse_checklist_section(lines)
        partial_or_todo = [item for item in parsed["items"] if item[0] in {"partial", "todo"}]
        focus = [text for _, text in partial_or_todo[:5]]
        risk_summary = [text for status, text in partial_or_todo if status == "partial"][:5]
        open_checks = [text for status, text in partial_or_todo if status == "todo"][:8]
        direct_tasks = sorted(set(TASK_REF_RE.findall("\n".join(lines))))
        states[axis] = {
            "axis": axis,
            "focus_entities": focus,
            "direct_specs": [],
            "direct_tasks": direct_tasks,
            "direct_tests": [],
            "neighbors": [],
            "risk_summary": risk_summary,
            "open_checks": open_checks,
            "last_updated": TODAY,
        }
    return states


def write_json(path: Path, payload: Any) -> None:
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def write_jsonl(path: Path, rows: list[dict[str, Any]]) -> None:
    text = "".join(json.dumps(row, ensure_ascii=False, sort_keys=True) + "\n" for row in rows)
    path.write_text(text, encoding="utf-8")


def main() -> None:
    code_entities, code_edges, symbol_to_entity = build_code_entities()
    frontend_entities = build_frontend_entities()
    doc_entities, doc_edges, _ = parse_markdown_entities()
    test_entities, test_edges = build_test_entities(symbol_to_entity)
    nodes = build_nodes(code_entities, frontend_entities, doc_entities, test_entities)
    edges = sorted(
        {
            (edge["from"], edge["relation"], edge["to"]): edge
            for edge in [*code_edges, *doc_edges, *test_edges]
        }.values(),
        key=lambda item: (item["from"], item["relation"], item["to"]),
    )
    by_symbol, by_feature, by_task, by_endpoint = build_indexes([*code_entities, *frontend_entities], doc_entities, test_entities)
    states = build_compressed_states()

    write_jsonl(META_DIR / "entities" / "code.jsonl", sorted([*code_entities, *frontend_entities], key=lambda item: item["entity_id"]))
    write_jsonl(META_DIR / "entities" / "docs.jsonl", sorted(doc_entities, key=lambda item: item["entity_id"]))
    write_jsonl(META_DIR / "entities" / "tests.jsonl", sorted(test_entities, key=lambda item: item["entity_id"]))
    write_jsonl(META_DIR / "graph" / "nodes.jsonl", nodes)
    write_jsonl(META_DIR / "graph" / "edges.jsonl", edges)
    write_json(META_DIR / "index" / "by_symbol.json", by_symbol)
    write_json(META_DIR / "index" / "by_feature.json", by_feature)
    write_json(META_DIR / "index" / "by_task.json", by_task)
    write_json(META_DIR / "index" / "by_endpoint.json", by_endpoint)
    write_json(META_DIR / "state" / "compressed" / "engine.json", states["engine"])
    write_json(META_DIR / "state" / "compressed" / "training.json", states["training"])
    write_json(META_DIR / "state" / "compressed" / "runtime.json", states["runtime"])


if __name__ == "__main__":
    main()
