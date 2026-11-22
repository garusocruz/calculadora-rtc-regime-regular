"""XML fiscal (pin f1eebd7) — XmlService/XmlUtil, identidade JUnit Surefire, sem HTTP."""

from __future__ import annotations

import json
from io import BytesIO
from pathlib import Path

import pytest
from lxml import etree

from calculadora_rtc_regime_regular.xml_fiscal import (
    TipoDocumento,
    TipoXml,
    XmlService,
    XmlUtil,
    gerar_xml_invalido,
)

_JAVA_TEST_RESOURCES = (
    Path(__file__).resolve().parent.parent / ".cache" / "oficial" / "java" / "src" / "test" / "resources"
)

_FQCN_GERACAO = "br.gov.serpro.rtc.testesintegracao.xml.XmlServiceGeracaoTest"
_FQCN_VALIDACAO = "br.gov.serpro.rtc.testesintegracao.xml.XmlServiceValidacaoTest"
_FQCN_UTIL = "br.gov.serpro.rtc.core.util.XmlUtilTest"

_ARQUIVO_ENTRADA = _JAVA_TEST_RESOURCES / "entradas" / "xml" / "entrada.json"

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

_ENTRADAS_VALIDACAO = [
    ("entradas/xml/nfe.xml", TipoDocumento.NFE, TipoXml.GRUPO),
    ("entradas/xml/nfce.xml", TipoDocumento.NFCE, TipoXml.GRUPO),
    ("entradas/xml/cte.xml", TipoDocumento.CTE, TipoXml.GRUPO),
    ("entradas/xml/cte-simplificado.xml", TipoDocumento.CTE_SIMPLIFICADO, TipoXml.GRUPO),
    ("entradas/xml/bpe.xml", TipoDocumento.BPE, TipoXml.GRUPO),
    ("entradas/xml/bpe-tm.xml", TipoDocumento.BPE_TM, TipoXml.GRUPO),
    ("entradas/xml/nf3e.xml", TipoDocumento.NF3E, TipoXml.GRUPO),
]

_TIPOS_GERACAO = [
    TipoDocumento.NFE,
    TipoDocumento.NFCE,
    TipoDocumento.CTE,
    TipoDocumento.CTE_SIMPLIFICADO,
    TipoDocumento.BPE,
    TipoDocumento.BPE_TM,
    TipoDocumento.NF3E,
]

_TODAS_COMBINACOES = [(doc, tx) for doc in TipoDocumento for tx in TipoXml]


def _surefire(metodo: str, indice: int) -> str:
    return f"{metodo}[{indice}]"


_GERACAO_CASES = [
    (_surefire("deveGerarXml(TipoDocumento)", i + 1), tipo)
    for i, tipo in enumerate(_TIPOS_GERACAO)
]

_VALIDACAO_CASES = [
    (_surefire("deveValidarXml(String, TipoDocumento, TipoXml)", i + 1), *row)
    for i, row in enumerate(_ENTRADAS_VALIDACAO)
]

_UTIL_VALIDAR_CASES = [
    (_surefire("deveValidarDemaisCenariosDeXmlDeExemplo(String, TipoDocumento, TipoXml)", i + 1), *row)
    for i, row in enumerate(_EXEMPLOS_VALIDOS)
]

_UTIL_SCHEMA_CASES = [
    (
        _surefire("deveResolverSchemaParaTodasAsCombinacoesDeDocumentoETipoXml(TipoDocumento, TipoXml)", i + 1),
        doc,
        tx,
    )
    for i, (doc, tx) in enumerate(_TODAS_COMBINACOES)
]

_UTIL_REJEITAR_CASES = [
    (_surefire("deveRejeitarCenariosInvalidosDerivadosDosExemplos(String, TipoDocumento, TipoXml)", i + 1), *row)
    for i, row in enumerate(_EXEMPLOS_VALIDOS)
]


def _java(record_xml_attribute, fqcn: str, metodo: str) -> None:
    record_xml_attribute("classname", fqcn)
    record_xml_attribute("name", metodo)


def _ler_xml(relativo: str) -> str:
    caminho = _JAVA_TEST_RESOURCES / relativo
    assert caminho.is_file(), f"Arquivo não encontrado: {relativo}"
    return caminho.read_text(encoding="utf-8")


@pytest.fixture(scope="module")
def xml_util() -> XmlUtil:
    return XmlUtil()


@pytest.fixture(scope="module")
def xml_service() -> XmlService:
    return XmlService()


@pytest.fixture(scope="module")
def roc_entrada() -> dict:
    return json.loads(_ARQUIVO_ENTRADA.read_text(encoding="utf-8"))


# --- XmlServiceGeracaoTest ---


@pytest.mark.parametrize("nome_java,tipo", _GERACAO_CASES)
def test_deve_gerar_xml(
    record_xml_attribute,
    xml_service: XmlService,
    roc_entrada: dict,
    nome_java: str,
    tipo: TipoDocumento,
) -> None:
    _java(record_xml_attribute, _FQCN_GERACAO, nome_java)
    xml = xml_service.gerar_xml(roc_entrada, tipo)
    assert xml.strip()


# --- XmlServiceValidacaoTest ---


@pytest.mark.parametrize("nome_java,caminho,tipo,subtipo", _VALIDACAO_CASES)
def test_deve_validar_xml_via_service(
    record_xml_attribute,
    xml_service: XmlService,
    nome_java: str,
    caminho: str,
    tipo: TipoDocumento,
    subtipo: TipoXml,
) -> None:
    _java(record_xml_attribute, _FQCN_VALIDACAO, nome_java)
    xml = _ler_xml(caminho)
    assert xml_service.validar_xml(xml, tipo, subtipo) is True


# --- XmlUtilTest ---


@pytest.mark.parametrize("nome_java,caminho,tipo_documento,tipo_xml", _UTIL_VALIDAR_CASES)
def test_deve_validar_demais_cenarios_de_xml_de_exemplo(
    record_xml_attribute,
    xml_util: XmlUtil,
    nome_java: str,
    caminho: str,
    tipo_documento: TipoDocumento,
    tipo_xml: TipoXml,
) -> None:
    _java(record_xml_attribute, _FQCN_UTIL, nome_java)
    schema = xml_util.get_schema(tipo_documento, tipo_xml)
    documento = etree.parse(BytesIO(_ler_xml(caminho).encode("utf-8")))
    schema.assertValid(documento)


@pytest.mark.parametrize("nome_java,tipo_documento,tipo_xml", _UTIL_SCHEMA_CASES)
def test_deve_resolver_schema_para_todas_combinacoes(
    record_xml_attribute,
    xml_util: XmlUtil,
    nome_java: str,
    tipo_documento: TipoDocumento,
    tipo_xml: TipoXml,
) -> None:
    _java(record_xml_attribute, _FQCN_UTIL, nome_java)
    schema = xml_util.get_schema(tipo_documento, tipo_xml)
    assert schema is not None


@pytest.mark.parametrize("nome_java,caminho,tipo_documento,tipo_xml", _UTIL_REJEITAR_CASES)
def test_deve_rejeitar_cenarios_invalidos_derivados_dos_exemplos(
    record_xml_attribute,
    xml_util: XmlUtil,
    nome_java: str,
    caminho: str,
    tipo_documento: TipoDocumento,
    tipo_xml: TipoXml,
) -> None:
    _java(record_xml_attribute, _FQCN_UTIL, nome_java)
    schema = xml_util.get_schema(tipo_documento, tipo_xml)
    xml_valido = _ler_xml(caminho)
    xml_invalido = gerar_xml_invalido(xml_valido, tipo_documento, tipo_xml)
    documento = etree.parse(BytesIO(xml_invalido.encode("utf-8")))
    with pytest.raises(etree.DocumentInvalid):
        schema.assertValid(documento)