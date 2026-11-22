"""Paridade XmlControllerValidacaoTest — XmlService (sem MockMvc)."""

from __future__ import annotations

from pathlib import Path

import pytest

from calculadora_rtc_regime_regular.xml_fiscal import TipoDocumento, TipoXml, XmlService

_CACHE = Path(__file__).resolve().parents[1] / ".cache/oficial/java/src/test/resources"

_CASOS = (
    ("entradas/xml/nfe.xml", TipoDocumento.NFE, TipoXml.GRUPO),
    ("entradas/xml/nfce.xml", TipoDocumento.NFCE, TipoXml.GRUPO),
    ("entradas/xml/cte.xml", TipoDocumento.CTE, TipoXml.GRUPO),
    ("entradas/xml/cte-simplificado.xml", TipoDocumento.CTE_SIMPLIFICADO, TipoXml.GRUPO),
    ("entradas/xml/bpe.xml", TipoDocumento.BPE, TipoXml.GRUPO),
    ("entradas/xml/bpe-tm.xml", TipoDocumento.BPE_TM, TipoXml.GRUPO),
    ("entradas/xml/nf3e.xml", TipoDocumento.NF3E, TipoXml.GRUPO),
)


def _surefire_ids() -> list[str]:
    return [f"deveValidarXmlViaEndpoint(String, TipoDocumento, TipoXml)[{i}]" for i in range(1, 8)]


@pytest.fixture(scope="module")
def xml_service() -> XmlService:
    return XmlService()


def _ler_xml(relativo: str) -> str:
    return (_CACHE / relativo).read_text(encoding="utf-8")


@pytest.mark.parametrize("indice,caso", list(enumerate(_CASOS, start=1)), ids=_surefire_ids())
def test_deveValidarXmlViaEndpoint(
    indice: int,
    caso: tuple[str, TipoDocumento, TipoXml],
    xml_service: XmlService,
) -> None:
    del indice
    relativo, tipo, subtipo = caso
    assert xml_service.validar_xml(_ler_xml(relativo), tipo, subtipo) is True