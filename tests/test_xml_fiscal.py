"""Testes de domínio XML fiscal (XmlUtilTest + XmlService* sem HTTP)."""

from __future__ import annotations

import json
from io import BytesIO
from pathlib import Path

import pytest
from lxml import etree

from calculadora_rtc_regime_regular.xml_fiscal import (
    ErroXmlException,
    TipoDocumento,
    TipoXml,
    XmlService,
    XmlUtil,
    canonicalizar_xml,
    gerar_xml_invalido,
    tag_obrigatoria_do_grupo,
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

_ARQUIVO_ENTRADA = _JAVA_TEST_RESOURCES / "entradas" / "xml" / "entrada.json"

_ARQUIVO_POR_TIPO = {
    TipoDocumento.NFE: "nfe.xml",
    TipoDocumento.NFCE: "nfce.xml",
    TipoDocumento.CTE: "cte.xml",
    TipoDocumento.CTE_SIMPLIFICADO: "cte-simplificado.xml",
    TipoDocumento.BPE: "bpe.xml",
    TipoDocumento.BPE_TM: "bpe-tm.xml",
    TipoDocumento.NF3E: "nf3e.xml",
}


def _ler_xml(relativo: str) -> str:
    caminho = _JAVA_TEST_RESOURCES / relativo
    assert caminho.is_file(), f"Arquivo não encontrado: {relativo}"
    return caminho.read_text(encoding="utf-8")


@pytest.fixture
def xml_util() -> XmlUtil:
    return XmlUtil()


@pytest.fixture
def xml_service() -> XmlService:
    return XmlService()


@pytest.fixture
def roc_entrada() -> dict:
    return json.loads(_ARQUIVO_ENTRADA.read_text(encoding="utf-8"))


@pytest.mark.parametrize("caminho,tipo_documento,tipo_xml", _EXEMPLOS_VALIDOS)
def test_deve_validar_xmls_de_exemplo(
    xml_util: XmlUtil, caminho: str, tipo_documento: TipoDocumento, tipo_xml: TipoXml
) -> None:
    schema = xml_util.get_schema(tipo_documento, tipo_xml)
    documento = etree.parse(BytesIO(_ler_xml(caminho).encode("utf-8")))
    schema.assertValid(documento)


@pytest.mark.parametrize("caminho,tipo_documento,tipo_xml", _EXEMPLOS_VALIDOS)
def test_deve_rejeitar_xml_invalido_derivado(
    xml_util: XmlUtil, caminho: str, tipo_documento: TipoDocumento, tipo_xml: TipoXml
) -> None:
    schema = xml_util.get_schema(tipo_documento, tipo_xml)
    xml_valido = _ler_xml(caminho)
    xml_invalido = gerar_xml_invalido(xml_valido, tipo_documento, tipo_xml)
    documento = etree.parse(BytesIO(xml_invalido.encode("utf-8")))
    with pytest.raises(etree.DocumentInvalid):
        schema.assertValid(documento)


@pytest.mark.parametrize("tipo_documento", list(TipoDocumento))
@pytest.mark.parametrize("tipo_xml", list(TipoXml))
def test_deve_resolver_schema_para_todas_combinacoes(
    xml_util: XmlUtil, tipo_documento: TipoDocumento, tipo_xml: TipoXml
) -> None:
    schema = xml_util.get_schema(tipo_documento, tipo_xml)
    assert schema is not None


@pytest.mark.parametrize("caminho,tipo,subtipo", _ENTRADAS_VALIDACAO)
def test_deve_validar_xml_via_service(
    xml_service: XmlService, caminho: str, tipo: TipoDocumento, subtipo: TipoXml
) -> None:
    xml = _ler_xml(caminho)
    assert xml_service.validar_xml(xml, tipo, subtipo) is True


@pytest.mark.parametrize("tipo", _TIPOS_GERACAO)
def test_deve_gerar_xml_nao_vazio(xml_service: XmlService, roc_entrada: dict, tipo: TipoDocumento) -> None:
    xml = xml_service.gerar_xml(roc_entrada, tipo)
    assert xml.strip()


@pytest.mark.parametrize("tipo", _TIPOS_GERACAO)
def test_deve_gerar_xml_igual_fixture_java(
    xml_service: XmlService, roc_entrada: dict, tipo: TipoDocumento
) -> None:
    gerado = xml_service.gerar_xml(roc_entrada, tipo)
    esperado = _ler_xml(f"entradas/xml/{_ARQUIVO_POR_TIPO[tipo]}")
    assert canonicalizar_xml(gerado) == canonicalizar_xml(esperado)


@pytest.mark.parametrize("tipo", _TIPOS_GERACAO)
def test_xml_gerado_valida_contra_grupo(
    xml_service: XmlService, roc_entrada: dict, tipo: TipoDocumento
) -> None:
    xml = xml_service.gerar_xml(roc_entrada, tipo)
    assert xml_service.validar_xml(xml, tipo, TipoXml.GRUPO) is True


def test_tag_obrigatoria_do_grupo_mapeia_como_java() -> None:
    assert tag_obrigatoria_do_grupo(TipoDocumento.NFE) == "det"
    assert tag_obrigatoria_do_grupo(TipoDocumento.NFSE) == "IBSCBS"
    assert tag_obrigatoria_do_grupo(TipoDocumento.BPE_TM) == "detBPeTM"


def test_validar_xml_lanca_erro_xml_exception(xml_service: XmlService) -> None:
    with pytest.raises(ErroXmlException) as exc:
        xml_service.validar_xml("<infNFe/>", TipoDocumento.NFE, TipoXml.GRUPO)
    assert "Erro na validação do XML:" in str(exc.value)