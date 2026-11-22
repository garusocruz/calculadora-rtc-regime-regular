"""Paridade JUnit com ``XmlUtilTest`` (validação XSD, pin f1eebd7), sem Spring."""

from __future__ import annotations

from io import BytesIO
from pathlib import Path

import pytest
from lxml import etree

from calculadora_rtc_regime_regular.xml_fiscal import (
    TipoDocumento,
    TipoXml,
    XmlUtil,
    gerar_xml_invalido,
)

_JAVA_TEST_RESOURCES = (
    Path(__file__).resolve().parent.parent / ".cache" / "oficial" / "java" / "src" / "test" / "resources"
)

_EXEMPLOS_VALIDOS = [
    ("xml/nfe/valido/grupo/nfe_valido.xml", TipoDocumento.NFE, TipoXml.GRUPO),
    ("xml/nfe/valido/nota/nfe_valido.xml", TipoDocumento.NFE, TipoXml.NOTA),
    ("xml/nfce/valido/grupo/nfce_valido.xml", TipoDocumento.NFCE, TipoXml.GRUPO),
    ("xml/nfce/valido/nota/nfce_valido.xml", TipoDocumento.NFCE, TipoXml.NOTA),
    ("xml/nfse/valido/grupo/nfse_valido.xml", TipoDocumento.NFSE, TipoXml.GRUPO),
    ("xml/nfse/valido/nota/nfse_valido_com_IBSCBS.xml", TipoDocumento.NFSE, TipoXml.NOTA),
    ("xml/nfse/valido/nota/nfse_valido_sem_IBSCBS.xml", TipoDocumento.NFSE, TipoXml.NOTA),
    ("xml/cte/valido/grupo/cte_valido.xml", TipoDocumento.CTE, TipoXml.GRUPO),
    ("xml/cte/valido/nota/cte_valido.xml", TipoDocumento.CTE, TipoXml.NOTA),
    ("xml/cte-simplificado/valido/grupo/cte_simplificado_valido.xml", TipoDocumento.CTE_SIMPLIFICADO, TipoXml.GRUPO),
    ("xml/cte-simplificado/valido/nota/cte_simplificado_valido.xml", TipoDocumento.CTE_SIMPLIFICADO, TipoXml.NOTA),
    ("xml/bpe/valido/grupo/bpe_valido.xml", TipoDocumento.BPE, TipoXml.GRUPO),
    ("xml/bpe/valido/nota/bpe_valido.xml", TipoDocumento.BPE, TipoXml.NOTA),
    ("xml/bpe-tm/valido/grupo/bpe_tm_valido.xml", TipoDocumento.BPE_TM, TipoXml.GRUPO),
    ("xml/bpe-tm/valido/nota/bpe_tm_valido.xml", TipoDocumento.BPE_TM, TipoXml.NOTA),
    ("xml/nf3e/valido/grupo/nf3e_valido.xml", TipoDocumento.NF3E, TipoXml.GRUPO),
    ("xml/nf3e/valido/nota/nf3e_valido.xml", TipoDocumento.NF3E, TipoXml.NOTA),
]

_TODAS_COMBINACOES = [(doc, tx) for doc in TipoDocumento for tx in TipoXml]

_PARAM_IDS_17 = [str(i) for i in range(1, 18)]
_PARAM_IDS_16 = [str(i) for i in range(1, 17)]


def _ler_xml(relativo: str) -> str:
    caminho = _JAVA_TEST_RESOURCES / relativo
    assert caminho.is_file(), f"Arquivo não encontrado: {relativo}"
    return caminho.read_text(encoding="utf-8")


@pytest.fixture(scope="module")
def xml_util() -> XmlUtil:
    return XmlUtil()


@pytest.mark.parametrize(
    "caminho,tipo_documento,tipo_xml",
    _EXEMPLOS_VALIDOS,
    ids=_PARAM_IDS_17,
)
def test_deve_validar_demais_cenarios_de_xml_de_exemplo(
    xml_util: XmlUtil,
    caminho: str,
    tipo_documento: TipoDocumento,
    tipo_xml: TipoXml,
) -> None:
    schema = xml_util.get_schema(tipo_documento, tipo_xml)
    documento = etree.parse(BytesIO(_ler_xml(caminho).encode("utf-8")))
    schema.assertValid(documento)


@pytest.mark.parametrize(
    "tipo_documento,tipo_xml",
    _TODAS_COMBINACOES,
    ids=_PARAM_IDS_16,
)
def test_deve_resolver_schema_para_todas_combinacoes(
    xml_util: XmlUtil,
    tipo_documento: TipoDocumento,
    tipo_xml: TipoXml,
) -> None:
    schema = xml_util.get_schema(tipo_documento, tipo_xml)
    assert schema is not None


@pytest.mark.parametrize(
    "caminho,tipo_documento,tipo_xml",
    _EXEMPLOS_VALIDOS,
    ids=_PARAM_IDS_17,
)
def test_deve_rejeitar_cenarios_invalidos_derivados_dos_exemplos(
    xml_util: XmlUtil,
    caminho: str,
    tipo_documento: TipoDocumento,
    tipo_xml: TipoXml,
) -> None:
    schema = xml_util.get_schema(tipo_documento, tipo_xml)
    xml_valido = _ler_xml(caminho)
    xml_invalido = gerar_xml_invalido(xml_valido, tipo_documento, tipo_xml)
    documento = etree.parse(BytesIO(xml_invalido.encode("utf-8")))
    with pytest.raises(etree.DocumentInvalid):
        schema.assertValid(documento)