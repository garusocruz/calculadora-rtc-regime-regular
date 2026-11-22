"""Fixtures e identidade JUnit para equivalencia.sh."""

from __future__ import annotations

import importlib.util
from pathlib import Path

import pytest

from _java_unit_map import JAVA_MODULE_CLASS, JAVA_STRIP_TESTE_PREFIX, JAVA_UNIT_IDENTITY


def _identidade_java() -> dict[str, tuple[str, str]]:
    """O mapa base mais um arquivo por módulo novo, para agentes em paralelo."""
    identidade = dict(JAVA_UNIT_IDENTITY)
    pasta = Path(__file__).parent / "_java_unit_parts"
    if not pasta.is_dir():
        return identidade
    for caminho in sorted(pasta.glob("*.py")):
        spec = importlib.util.spec_from_file_location(f"java_unit_part_{caminho.stem}", caminho)
        if spec is None or spec.loader is None:
            continue
        modulo = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(modulo)
        parte = getattr(modulo, "JAVA_UNIT_IDENTITY", None)
        if isinstance(parte, dict):
            identidade.update(parte)
    return identidade


def pytest_configure(config: pytest.Config) -> None:
    config.option.junit_family = "legacy"
    config.addinivalue_line(
        "markers",
        "java_unit(classname, name): classname+name no JUnit XML (equivalencia.sh)",
    )


def pytest_collection_modifyitems(items: list[pytest.Item]) -> None:
    identidade = _identidade_java()
    for item in items:
        mod = item.module.__name__
        leaf = item.nodeid.split("::")[-1]
        base = leaf.split("[")[0]
        keys = (
            f"{mod}::{leaf}",
            f"{mod}::{base}",
        )
        for key in keys:
            if key in identidade:
                fqcn, metodo = identidade[key]
                item.add_marker(pytest.mark.java_unit(classname=fqcn, name=metodo))
                break
        else:
            if mod in JAVA_MODULE_CLASS and base.startswith("teste_"):
                fqcn = JAVA_MODULE_CLASS[mod]
                metodo = base.removeprefix("teste_") if mod in JAVA_STRIP_TESTE_PREFIX else base
                item.add_marker(pytest.mark.java_unit(classname=fqcn, name=metodo))


@pytest.fixture(autouse=True)
def _registrar_identidade_java_no_junit(request: pytest.FixtureRequest, record_xml_attribute) -> None:
    marker = request.node.get_closest_marker("java_unit")
    if marker is None:
        return
    record_xml_attribute("classname", marker.kwargs["classname"])
    record_xml_attribute("name", marker.kwargs["name"])
