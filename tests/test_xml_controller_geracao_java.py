"""Paridade XmlControllerGeracaoTest — XmlService (sem MockMvc)."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from calculadora_rtc_regime_regular.xml_fiscal import TipoDocumento, XmlService

_CACHE = Path(__file__).resolve().parents[1] / ".cache/oficial/java/src/test/resources"
_ENTRADA = _CACHE / "entradas/xml/entrada.json"

_TIPOS = (
    TipoDocumento.NFE,
    TipoDocumento.NFCE,
    TipoDocumento.CTE,
    TipoDocumento.CTE_SIMPLIFICADO,
    TipoDocumento.BPE,
    TipoDocumento.BPE_TM,
    TipoDocumento.NF3E,
)


def _surefire_ids() -> list[str]:
    return [f"deveGerarXmlViaEndpoint(TipoDocumento)[{i}]" for i in range(1, 8)]


@pytest.fixture(scope="module")
def xml_service() -> XmlService:
    return XmlService()


@pytest.fixture(scope="module")
def roc_entrada() -> dict:
    return json.loads(_ENTRADA.read_text(encoding="utf-8"))


@pytest.mark.parametrize("indice,tipo", list(enumerate(_TIPOS, start=1)), ids=_surefire_ids())
def test_deveGerarXmlViaEndpoint(indice: int, tipo: TipoDocumento, xml_service: XmlService, roc_entrada: dict) -> None:
    del indice
    xml = xml_service.gerar_xml(roc_entrada, tipo)
    assert xml.strip()