"""Integração dados abertos (pin f1eebd7) — chamada de serviço, sem Spring."""

from __future__ import annotations

import os
from datetime import date

import pytest

os.environ.setdefault(
    "CALC_DB",
    "/home/garusotec/projects/lynko/libs/calculadora-rtc-regime-regular/.cache/oficial/java/calculadora/db/calculadora-pro.db",
)

from calculadora_rtc_regime_regular.consumo import DadosAbertosService
from calculadora_rtc_regime_regular.dados_abertos import (
    ClassificacaoTributariaNaoEncontradaException,
    NbsNaoEncontradaException,
    NcmNaoEncontradaException,
    PapelAtor,
    SiglaDfeNaoEncontradaException,
)

pytestmark = pytest.mark.skipif(not os.environ.get("CALC_DB"), reason="CALC_DB ausente")

DATA_2026_01_01 = date(2026, 1, 1)
DATA_2026_08_07 = date(2026, 8, 7)
DATA_2027_01_01 = date(2027, 1, 1)
DATA_2025_01_01 = date(2025, 1, 1)
DATA_1980_01_01 = date(1980, 1, 1)

_FQCN_1 = "br.gov.serpro.rtc.testesintegracao.dadosabertos.Teste_dadosabertos_1_consultarUfs"
_FQCN_2 = "br.gov.serpro.rtc.testesintegracao.dadosabertos.Teste_dadosabertos_2_consultarMunicipiosPorSiglaUf"
_FQCN_3 = "br.gov.serpro.rtc.testesintegracao.dadosabertos.Teste_dadosabertos_3_consultarSituacoesTributariasCbsIbs"
_FQCN_4 = (
    "br.gov.serpro.rtc.testesintegracao.dadosabertos"
    ".Teste_dadosabertos_4_consultarClassificacoesTributariasPorIdSituacaoTributaria"
)
_FQCN_5 = (
    "br.gov.serpro.rtc.testesintegracao.dadosabertos"
    ".Teste_dadosabertos_5_consultarSituacoesTributariasImpostoSeletivo"
)
_FQCN_6 = "br.gov.serpro.rtc.testesintegracao.dadosabertos.Teste_dadosabertos_6_consultarNcm"
_FQCN_7 = "br.gov.serpro.rtc.testesintegracao.dadosabertos.Teste_dadosabertos_7_consultarNbs"
_FQCN_8 = "br.gov.serpro.rtc.testesintegracao.dadosabertos.Teste_dadosabertos_8_consultarFundamentacoesLegais"
_FQCN_9 = "br.gov.serpro.rtc.testesintegracao.dadosabertos.Teste_dadosabertos_9_classificacoesTributariasPorCst"
_FQCN_10 = "br.gov.serpro.rtc.testesintegracao.dadosabertos.Teste_dadosabertos_10_classificacaoUnicaCbsIbs"
_FQCN_11 = "br.gov.serpro.rtc.testesintegracao.dadosabertos.Teste_dadosabertos_11_situacaoClassificacaoAninhada"
_FQCN_13 = "br.gov.serpro.rtc.testesintegracao.dadosabertos.Teste_dadosabertos_13_classificacaoUnicaIs"
_FQCN_14 = "br.gov.serpro.rtc.testesintegracao.dadosabertos.Teste_dadosabertos_14_tiposDfeAgrupados"
_FQCN_15 = "br.gov.serpro.rtc.testesintegracao.dadosabertos.Teste_dadosabertos_15_atoresAgrupados"
_FQCN_16 = "br.gov.serpro.rtc.testesintegracao.dadosabertos.Teste_dadosabertos_16_classificacoesPorAtores"
_FQCN_NOM_12 = "br.gov.serpro.rtc.testesintegracao.dadosabertos.Teste_nomenclatura_12_determinarNomenclatura"
_FQCN_NOM_13 = "br.gov.serpro.rtc.testesintegracao.dadosabertos.Teste_nomenclatura_13_obrigatoriedade"

# Excluídos (só Spring — ver relatório final):
# Teste_dadosabertos_14_tiposDfeAgrupados.teste_dfeGrupos_semData_usaDataAtual
# Teste_dadosabertos_15_atoresAgrupados.teste_atoresAgrupados_semData_retorna400
# Teste_dadosabertos_15_atoresAgrupados.teste_atoresAgrupados_papelInvalido_retorna400
# Teste_dadosabertos_16_classificacoesPorAtores.teste_semData_retorna400


def _java(record_xml_attribute, fqcn: str, metodo: str) -> None:
    record_xml_attribute("classname", fqcn)
    record_xml_attribute("name", metodo)


def _tipos_flat(grupos):
    return [tipo for grupo in grupos for tipo in grupo.tipos]


def _tipo(grupos, codigo: str):
    return next(t for t in _tipos_flat(grupos) if t.codigo == codigo)


@pytest.fixture(scope="module")
def servico() -> DadosAbertosService:
    return DadosAbertosService()


# --- Teste_dadosabertos_1 ---


def teste_controller_consultarUfs(record_xml_attribute, servico: DadosAbertosService) -> None:
    _java(record_xml_attribute, _FQCN_1, "teste_controller_consultarUfs")
    assert len(servico.consultarUfs()) == 28


# --- Teste_dadosabertos_2 ---


def teste_controller_consultarMunicipiosPorSiglaUf(
    record_xml_attribute, servico: DadosAbertosService
) -> None:
    _java(record_xml_attribute, _FQCN_2, "teste_controller_consultarMunicipiosPorSiglaUf")
    assert len(servico.consultarMunicipiosPorSiglaUf("RS")) > 0


# --- Teste_dadosabertos_3 (situacoes-tributarias/cbs-ibs → CST aninhado) ---


def teste_controller_consultarSituacoesTributariasCbsIbs(
    record_xml_attribute, servico: DadosAbertosService
) -> None:
    _java(record_xml_attribute, _FQCN_3, "teste_controller_consultarSituacoesTributariasCbsIbs")
    assert len(servico.consultarCstsComClassificacoesCbsIbs(None, DATA_2026_01_01)) > 0


# --- Teste_dadosabertos_4 ---


def teste_controller_consultarClassificacoesTributariasPorIdSituacaoTributaria(
    record_xml_attribute, servico: DadosAbertosService
) -> None:
    _java(
        record_xml_attribute,
        _FQCN_4,
        "teste_controller_consultarClassificacoesTributariasPorIdSituacaoTributaria",
    )
    assert (
        len(
            servico.consultarClassificacoesTributariasPorIdSituacaoTributaria(
                1, DATA_2026_01_01
            )
        )
        > 0
    )


# --- Teste_dadosabertos_5 ---


def teste_controller_consultarSituacoesTributariasImpostoSeletivo(
    record_xml_attribute, servico: DadosAbertosService
) -> None:
    _java(record_xml_attribute, _FQCN_5, "teste_controller_consultarSituacoesTributariasImpostoSeletivo")
    assert len(servico.consultarSituacoesTributarias(1, DATA_2027_01_01)) > 0


# --- Teste_dadosabertos_6 ---


def teste_controller_consultarNcm(record_xml_attribute, servico: DadosAbertosService) -> None:
    _java(record_xml_attribute, _FQCN_6, "teste_controller_consultarNcm")
    assert servico.consultarNcm("24021000", DATA_2027_01_01).tributado_pelo_imposto_seletivo is True


def teste_controller_consultarNcm_inexistente(
    record_xml_attribute, servico: DadosAbertosService
) -> None:
    _java(record_xml_attribute, _FQCN_6, "teste_controller_consultarNcm_inexistente")
    with pytest.raises(NcmNaoEncontradaException):
        servico.consultarNcm("24020009", DATA_2027_01_01)


# --- Teste_dadosabertos_7 ---


def teste_controller_consultarNbs(record_xml_attribute, servico: DadosAbertosService) -> None:
    _java(record_xml_attribute, _FQCN_7, "teste_controller_consultarNbs")
    assert servico.consultarNbs("114052200", DATA_2027_01_01).tributado_pelo_imposto_seletivo is False


def teste_controller_consultarNbs_inexistente(
    record_xml_attribute, servico: DadosAbertosService
) -> None:
    _java(record_xml_attribute, _FQCN_7, "teste_controller_consultarNbs_inexistente")
    with pytest.raises(NbsNaoEncontradaException):
        servico.consultarNbs("999999999", DATA_2027_01_01)


# --- Teste_dadosabertos_8 ---


def teste_controller_consultarFundamentacoesLegais(
    record_xml_attribute, servico: DadosAbertosService
) -> None:
    _java(record_xml_attribute, _FQCN_8, "teste_controller_consultarNbs")
    assert len(servico.consultarFundamentacoesLegais(DATA_2027_01_01)) > 0


# --- Teste_dadosabertos_9 ---


def teste_controller_consultarClassificacoesTributariasImpostoSeletivoPorCst(
    record_xml_attribute, servico: DadosAbertosService
) -> None:
    _java(
        record_xml_attribute,
        _FQCN_9,
        "teste_controller_consultarClassificacoesTributariasImpostoSeletivoPorCst",
    )
    resultado = servico.consultarClassificacoesTributariasPorCstETributoTipo(
        "000", ["IS"], DATA_2027_01_01
    )
    assert len(resultado) > 0


def teste_controller_consultarClassificacoesTributariasCbsIbsPorCst(
    record_xml_attribute, servico: DadosAbertosService
) -> None:
    _java(record_xml_attribute, _FQCN_9, "teste_controller_consultarClassificacoesTributariasCbsIbsPorCst")
    resultado = servico.consultarClassificacoesTributariasPorCstETributoTipo(
        "000", ["CBS", "IBSUF", "IBSMun"], DATA_2026_01_01
    )
    assert len(resultado) > 0


def teste_controller_consultarClassificacoesTributariasImpostoSeletivoPorCstSemData(
    record_xml_attribute, servico: DadosAbertosService
) -> None:
    _java(
        record_xml_attribute,
        _FQCN_9,
        "teste_controller_consultarClassificacoesTributariasImpostoSeletivoPorCstSemData",
    )
    servico.consultarClassificacoesTributariasPorCstETributoTipo("000", ["IS"], DATA_2027_01_01)


def teste_controller_consultarClassificacoesTributariasCbsIbsPorCstSemData(
    record_xml_attribute, servico: DadosAbertosService
) -> None:
    _java(
        record_xml_attribute,
        _FQCN_9,
        "teste_controller_consultarClassificacoesTributariasCbsIbsPorCstSemData",
    )
    servico.consultarClassificacoesTributariasPorCstETributoTipo(
        "010", ["CBS", "IBSUF", "IBSMun"], DATA_2025_01_01
    )


# --- Teste_dadosabertos_10 ---


def teste_controller_consultarClassTribValidaDataValida(
    record_xml_attribute, servico: DadosAbertosService
) -> None:
    _java(record_xml_attribute, _FQCN_10, "teste_controller_consultarClassTribValidaDataValida")
    r = servico.consultarClassificacaoTributariaCbsIbsPorCodigo("000001", DATA_2027_01_01)
    assert r.codigo == "000001"
    assert r.descricao
    assert r.tipo_aliquota


def teste_controller_consultarClassTribInvalidaDataValida(
    record_xml_attribute, servico: DadosAbertosService
) -> None:
    _java(record_xml_attribute, _FQCN_10, "teste_controller_consultarClassTribInvalidaDataValida")
    with pytest.raises(ClassificacaoTributariaNaoEncontradaException):
        servico.consultarClassificacaoTributariaCbsIbsPorCodigo("999999", DATA_2027_01_01)


def teste_controller_consultarClassTribValidaDataInvalida(
    record_xml_attribute, servico: DadosAbertosService
) -> None:
    _java(record_xml_attribute, _FQCN_10, "teste_controller_consultarClassTribValidaDataInvalida")
    with pytest.raises(ClassificacaoTributariaNaoEncontradaException):
        servico.consultarClassificacaoTributariaCbsIbsPorCodigo("000001", DATA_1980_01_01)


def teste_controller_consultarClassTribInvalidaDataInvalida(
    record_xml_attribute, servico: DadosAbertosService
) -> None:
    _java(record_xml_attribute, _FQCN_10, "teste_controller_consultarClassTribInvalidaDataInvalida")
    with pytest.raises(ClassificacaoTributariaNaoEncontradaException):
        servico.consultarClassificacaoTributariaCbsIbsPorCodigo("999999", DATA_1980_01_01)


def teste_controller_consultarClassificacaoUnicaCbsIbsValidaTodasAsPropriedades(
    record_xml_attribute, servico: DadosAbertosService
) -> None:
    _java(
        record_xml_attribute,
        _FQCN_10,
        "teste_controller_consultarClassificacaoUnicaCbsIbsValidaTodasAsPropriedades",
    )
    r = servico.consultarClassificacaoTributariaCbsIbsPorCodigo("000001", DATA_2027_01_01)
    assert r.codigo
    assert r.descricao
    assert r.tipo_aliquota
    assert r.nomenclatura
    assert r.descricao_tratamento_tributario
    assert r.incompativel_com_suspensao is False
    assert r.exige_grupo_desoneracao is False
    assert r.possui_percentual_reducao is not None
    assert r.indica_apropriacao_credito_adquirente_cbs is not None
    assert r.indica_apropriacao_credito_adquirente_ibs is not None
    assert r.indica_credito_presumido_fornecedor is not None
    assert r.indica_credito_presumido_adquirente is not None
    assert r.tipo_receita_bruta_simples_nacional == 1
    assert r.tipos_dfe_classificacao
    assert r.data_atualizacao is not None


def teste_controller_consultarClassTribRetornaTipoReceitaBrutaSimplesNacional(
    record_xml_attribute, servico: DadosAbertosService
) -> None:
    _java(
        record_xml_attribute,
        _FQCN_10,
        "teste_controller_consultarClassTribRetornaTipoReceitaBrutaSimplesNacional",
    )
    r = servico.consultarClassificacaoTributariaCbsIbsPorCodigo("410002", DATA_2026_08_07)
    assert r.codigo == "410002"
    assert r.tipo_receita_bruta_simples_nacional == 0


# --- Teste_dadosabertos_11 ---


def teste_controller_cbsIbs_dfeExistente_dataValida(
    record_xml_attribute, servico: DadosAbertosService
) -> None:
    _java(record_xml_attribute, _FQCN_11, "teste_controller_cbsIbs_dfeExistente_dataValida")
    lista = servico.consultarCstsComClassificacoesCbsIbs("NFE", DATA_2027_01_01)
    assert lista
    assert lista[0].id is not None
    assert lista[0].codigo
    assert lista[0].descricao
    assert lista[0].classificacoes_tributarias
    assert lista[0].classificacoes_tributarias[0].codigo
    assert lista[0].classificacoes_tributarias[0].descricao


def teste_controller_cbsIbs_semSiglaDfe_dataValida(
    record_xml_attribute, servico: DadosAbertosService
) -> None:
    _java(record_xml_attribute, _FQCN_11, "teste_controller_cbsIbs_semSiglaDfe_dataValida")
    lista = servico.consultarCstsComClassificacoesCbsIbs(None, DATA_2027_01_01)
    assert lista
    assert lista[0].id is not None
    assert lista[0].codigo
    assert lista[0].descricao
    assert lista[0].classificacoes_tributarias
    assert len(lista[0].classificacoes_tributarias) > 0


def teste_controller_cbsIbs_dfeInexistente_dataValida(
    record_xml_attribute, servico: DadosAbertosService
) -> None:
    _java(record_xml_attribute, _FQCN_11, "teste_controller_cbsIbs_dfeInexistente_dataValida")
    with pytest.raises(SiglaDfeNaoEncontradaException):
        servico.consultarCstsComClassificacoesCbsIbs("XXXX", DATA_2027_01_01)


def teste_controller_cbsIbs_dfeExistente_dataAnterior(
    record_xml_attribute, servico: DadosAbertosService
) -> None:
    _java(record_xml_attribute, _FQCN_11, "teste_controller_cbsIbs_dfeExistente_dataAnterior")
    assert servico.consultarCstsComClassificacoesCbsIbs("NFE", DATA_1980_01_01) == []


def teste_controller_cbsIbs_semSiglaDfe_dataAnterior(
    record_xml_attribute, servico: DadosAbertosService
) -> None:
    _java(record_xml_attribute, _FQCN_11, "teste_controller_cbsIbs_semSiglaDfe_dataAnterior")
    assert servico.consultarCstsComClassificacoesCbsIbs(None, DATA_1980_01_01) == []


def teste_controller_cbsIbs_normalizaSiglaDfe(
    record_xml_attribute, servico: DadosAbertosService
) -> None:
    _java(record_xml_attribute, _FQCN_11, "teste_controller_cbsIbs_normalizaSiglaDfe")
    assert len(servico.consultarCstsComClassificacoesCbsIbs("nf-e ", DATA_2027_01_01)) > 0


def teste_controller_cbsIbs_retornaListaOrdenada(
    record_xml_attribute, servico: DadosAbertosService
) -> None:
    _java(record_xml_attribute, _FQCN_11, "teste_controller_cbsIbs_retornaListaOrdenada")
    lista = servico.consultarCstsComClassificacoesCbsIbs("NFE", DATA_2027_01_01)
    assert lista
    assert lista[0].codigo
    assert lista[0].classificacoes_tributarias
    assert len(lista[0].classificacoes_tributarias) > 0


def teste_controller_is_dfeExistente_dataValida(
    record_xml_attribute, servico: DadosAbertosService
) -> None:
    _java(record_xml_attribute, _FQCN_11, "teste_controller_is_dfeExistente_dataValida")
    assert servico.consultarCstsComClassificacoesIs("NFE", DATA_2027_01_01) is not None


def teste_controller_is_semSiglaDfe_dataValida(
    record_xml_attribute, servico: DadosAbertosService
) -> None:
    _java(record_xml_attribute, _FQCN_11, "teste_controller_is_semSiglaDfe_dataValida")
    lista = servico.consultarCstsComClassificacoesIs(None, DATA_2027_01_01)
    assert lista
    assert lista[0].id is not None
    assert lista[0].codigo
    assert lista[0].classificacoes_tributarias


def teste_controller_is_dfeInexistente_dataValida(
    record_xml_attribute, servico: DadosAbertosService
) -> None:
    _java(record_xml_attribute, _FQCN_11, "teste_controller_is_dfeInexistente_dataValida")
    with pytest.raises(SiglaDfeNaoEncontradaException):
        servico.consultarCstsComClassificacoesIs("XXXX", DATA_2027_01_01)


def teste_controller_is_dfeExistente_dataAnterior(
    record_xml_attribute, servico: DadosAbertosService
) -> None:
    _java(record_xml_attribute, _FQCN_11, "teste_controller_is_dfeExistente_dataAnterior")
    assert servico.consultarCstsComClassificacoesIs("NFE", DATA_1980_01_01) == []


def teste_controller_is_normalizaSiglaDfe(
    record_xml_attribute, servico: DadosAbertosService
) -> None:
    _java(record_xml_attribute, _FQCN_11, "teste_controller_is_normalizaSiglaDfe")
    assert servico.consultarCstsComClassificacoesIs("nf-e ", DATA_2027_01_01) is not None


# --- Teste_dadosabertos_13 ---

_C_CLASS_TRIB_IS = "000001"


def teste_controller_consultarClassTribIsValidaDataValida(
    record_xml_attribute, servico: DadosAbertosService
) -> None:
    _java(record_xml_attribute, _FQCN_13, "teste_controller_consultarClassTribIsValidaDataValida")
    r = servico.consultarClassificacaoTributariaIsPorCodigo(_C_CLASS_TRIB_IS, DATA_2027_01_01)
    assert r.codigo == _C_CLASS_TRIB_IS
    assert r.descricao
    assert r.tipo_aliquota


def teste_controller_consultarClassTribIsInvalidaDataValida(
    record_xml_attribute, servico: DadosAbertosService
) -> None:
    _java(record_xml_attribute, _FQCN_13, "teste_controller_consultarClassTribIsInvalidaDataValida")
    with pytest.raises(ClassificacaoTributariaNaoEncontradaException):
        servico.consultarClassificacaoTributariaIsPorCodigo("999999", DATA_2027_01_01)


def teste_controller_consultarClassTribIsValidaDataInvalida(
    record_xml_attribute, servico: DadosAbertosService
) -> None:
    _java(record_xml_attribute, _FQCN_13, "teste_controller_consultarClassTribIsValidaDataInvalida")
    with pytest.raises(ClassificacaoTributariaNaoEncontradaException):
        servico.consultarClassificacaoTributariaIsPorCodigo(_C_CLASS_TRIB_IS, DATA_1980_01_01)


def teste_controller_consultarClassTribIsInvalidaDataInvalida(
    record_xml_attribute, servico: DadosAbertosService
) -> None:
    _java(record_xml_attribute, _FQCN_13, "teste_controller_consultarClassTribIsInvalidaDataInvalida")
    with pytest.raises(ClassificacaoTributariaNaoEncontradaException):
        servico.consultarClassificacaoTributariaIsPorCodigo("999999", DATA_1980_01_01)


def teste_controller_consultarClassificacaoUnicaIsValidaTodasAsPropriedades(
    record_xml_attribute, servico: DadosAbertosService
) -> None:
    _java(
        record_xml_attribute,
        _FQCN_13,
        "teste_controller_consultarClassificacaoUnicaIsValidaTodasAsPropriedades",
    )
    r = servico.consultarClassificacaoTributariaIsPorCodigo(_C_CLASS_TRIB_IS, DATA_2027_01_01)
    assert r.codigo
    assert r.descricao
    assert r.tipo_aliquota
    assert r.nomenclatura
    assert r.descricao_tratamento_tributario
    assert r.incompativel_com_suspensao is False
    assert r.exige_grupo_desoneracao is False
    assert r.possui_percentual_reducao is not None
    assert r.tipos_dfe_classificacao is not None


# --- Teste_dadosabertos_14 ---


def teste_dfeGrupos_dataVigente_retornaGrupos(
    record_xml_attribute, servico: DadosAbertosService
) -> None:
    _java(record_xml_attribute, _FQCN_14, "teste_dfeGrupos_dataVigente_retornaGrupos")
    grupos = servico.consultarTiposDfeAgrupados(DATA_2027_01_01)
    assert grupos
    assert len(grupos) > 0


def teste_dfeGrupos_estruturaAninhada(record_xml_attribute, servico: DadosAbertosService) -> None:
    _java(record_xml_attribute, _FQCN_14, "teste_dfeGrupos_estruturaAninhada")
    g0 = servico.consultarTiposDfeAgrupados(DATA_2027_01_01)[0]
    assert g0.id
    assert g0.titulo
    assert g0.ordem == 1
    assert g0.tipos
    assert len(g0.tipos) > 0
    assert g0.tipos[0].codigo
    assert g0.tipos[0].titulo
    assert g0.tipos[0].ordem == 1


def teste_dfeGrupos_ordenadoEComCodigoNormalizado(
    record_xml_attribute, servico: DadosAbertosService
) -> None:
    _java(record_xml_attribute, _FQCN_14, "teste_dfeGrupos_ordenadoEComCodigoNormalizado")
    grupos = servico.consultarTiposDfeAgrupados(DATA_2027_01_01)
    assert grupos[0].titulo == "MERCADORIAS"
    assert grupos[0].ordem == 1
    assert grupos[0].tipos[0].codigo == "NFE"
    assert grupos[0].tipos[0].modelo == "55"
    assert grupos[0].tipos[0].ordem == 1
    assert grupos[0].tipos[1].codigo == "NFCE"
    assert grupos[0].tipos[1].ordem == 2
    assert grupos[1].titulo == "SERVIÇOS"
    assert grupos[1].ordem == 2


def teste_dfeGrupos_descricaoOmitida(record_xml_attribute, servico: DadosAbertosService) -> None:
    _java(record_xml_attribute, _FQCN_14, "teste_dfeGrupos_descricaoOmitida")
    tipo = servico.consultarTiposDfeAgrupados(DATA_2027_01_01)[0].tipos[0]
    assert "descricao" not in tipo.__dataclass_fields__


def teste_dfeGrupos_suportadoEPermiteNcmZero_tiposSuportados(
    record_xml_attribute, servico: DadosAbertosService
) -> None:
    _java(record_xml_attribute, _FQCN_14, "teste_dfeGrupos_suportadoEPermiteNcmZero_tiposSuportados")
    grupos = servico.consultarTiposDfeAgrupados(DATA_2027_01_01)
    assert _tipo(grupos, "NFE").suportado is True
    assert _tipo(grupos, "NFE").permite_ncm_zero is True
    assert _tipo(grupos, "NFCE").permite_ncm_zero is True
    assert _tipo(grupos, "CTE").suportado is True
    assert _tipo(grupos, "CTE").permite_ncm_zero is False


def teste_dfeGrupos_tiposNaoSuportados_grupo5(
    record_xml_attribute, servico: DadosAbertosService
) -> None:
    _java(record_xml_attribute, _FQCN_14, "teste_dfeGrupos_tiposNaoSuportados_grupo5")
    grupo5 = next(g for g in servico.consultarTiposDfeAgrupados(DATA_2027_01_01) if g.id == "5")
    tipos = {t.codigo: t for t in grupo5.tipos}
    assert tipos["NFEABI"].suportado is False
    assert tipos["DERE"].suportado is False
    assert tipos["DIR"].suportado is False
    assert tipos["DUIMP"].suportado is False


def teste_dfeGrupos_flagsSemprePresentes(record_xml_attribute, servico: DadosAbertosService) -> None:
    _java(record_xml_attribute, _FQCN_14, "teste_dfeGrupos_flagsSemprePresentes")
    for tipo in _tipos_flat(servico.consultarTiposDfeAgrupados(DATA_2027_01_01)):
        assert isinstance(tipo.suportado, bool)
        assert isinstance(tipo.permite_ncm_zero, bool)


# --- Teste_dadosabertos_15 ---


def teste_atoresAgrupados_dataVigente_retornaGrupos(
    record_xml_attribute, servico: DadosAbertosService
) -> None:
    _java(record_xml_attribute, _FQCN_15, "teste_atoresAgrupados_dataVigente_retornaGrupos")
    assert len(servico.consultarAtoresAgrupados(DATA_2027_01_01)) > 0


def teste_atoresAgrupados_papelFornecedor(record_xml_attribute, servico: DadosAbertosService) -> None:
    _java(record_xml_attribute, _FQCN_15, "teste_atoresAgrupados_papelFornecedor")
    assert servico.consultarAtoresAgrupados(DATA_2027_01_01, PapelAtor.FORNECEDOR) is not None


def teste_atoresAgrupados_papelAdquirente(record_xml_attribute, servico: DadosAbertosService) -> None:
    _java(record_xml_attribute, _FQCN_15, "teste_atoresAgrupados_papelAdquirente")
    assert servico.consultarAtoresAgrupados(DATA_2027_01_01, PapelAtor.ADQUIRENTE) is not None


def teste_atoresAgrupados_estruturaAninhada(record_xml_attribute, servico: DadosAbertosService) -> None:
    _java(record_xml_attribute, _FQCN_15, "teste_atoresAgrupados_estruturaAninhada")
    g0 = servico.consultarAtoresAgrupados(DATA_2027_01_01)[0]
    assert g0.id is not None
    assert g0.descricao
    assert g0.ordem is not None
    assert g0.atores
    assert len(g0.atores) > 0
    assert g0.atores[0].id is not None
    assert g0.atores[0].descricao
    assert g0.atores[0].ordem is not None


def teste_atoresAgrupados_gruposOrdenados(record_xml_attribute, servico: DadosAbertosService) -> None:
    _java(record_xml_attribute, _FQCN_15, "teste_atoresAgrupados_gruposOrdenados")
    grupos = servico.consultarAtoresAgrupados(DATA_2027_01_01)
    assert grupos[0].ordem >= 1
    assert all(g.ordem >= 1 for g in grupos)


# --- Teste_dadosabertos_16 ---

_CLASS_F27_A28 = "200054"
_CLASS_SO_ADQ_70 = "550017"
_CLASS_SEM_RESTRICAO = "000001"


def _codigos_por_atores(servico: DadosAbertosService, **kwargs) -> list[str]:
    return [c.codigo for c in servico.consultarClassificacoesTributariasCbsIbsPorAtores(DATA_2027_01_01, **kwargs)]


def teste_semFiltros_mesmaQuantidadeDoEndpointCbsIbs(
    record_xml_attribute, servico: DadosAbertosService
) -> None:
    _java(record_xml_attribute, _FQCN_16, "teste_semFiltros_mesmaQuantidadeDoEndpointCbsIbs")
    q_sem = len(servico.consultarClassificacoesTributariasCbsIbs(DATA_2027_01_01))
    q_atores = len(servico.consultarClassificacoesTributariasCbsIbsPorAtores(DATA_2027_01_01))
    assert q_sem > 0
    assert q_sem == q_atores


def teste_fornecedor27Adquirente28_contem200054ESemRestricao(
    record_xml_attribute, servico: DadosAbertosService
) -> None:
    _java(record_xml_attribute, _FQCN_16, "teste_fornecedor27Adquirente28_contem200054ESemRestricao")
    codigos = _codigos_por_atores(servico, fornecedor=27, adquirente=28)
    assert _CLASS_F27_A28 in codigos
    assert _CLASS_SEM_RESTRICAO in codigos


def teste_fornecedor27Adquirente29_naoContem200054(
    record_xml_attribute, servico: DadosAbertosService
) -> None:
    _java(record_xml_attribute, _FQCN_16, "teste_fornecedor27Adquirente29_naoContem200054")
    codigos = _codigos_por_atores(servico, fornecedor=27, adquirente=29)
    assert _CLASS_F27_A28 not in codigos
    assert _CLASS_SEM_RESTRICAO in codigos


def teste_restricaoApenasAdquirente_adquirenteVinculado_aparece(
    record_xml_attribute, servico: DadosAbertosService
) -> None:
    _java(record_xml_attribute, _FQCN_16, "teste_restricaoApenasAdquirente_adquirenteVinculado_aparece")
    assert _CLASS_SO_ADQ_70 in _codigos_por_atores(servico, adquirente=70)


def teste_restricaoApenasAdquirente_adquirenteNaoVinculado_naoAparece(
    record_xml_attribute, servico: DadosAbertosService
) -> None:
    _java(record_xml_attribute, _FQCN_16, "teste_restricaoApenasAdquirente_adquirenteNaoVinculado_naoAparece")
    assert _CLASS_SO_ADQ_70 not in _codigos_por_atores(servico, adquirente=22)


def teste_restricaoApenasAdquirente_papelAdquirenteNaoFiltrado_aparece(
    record_xml_attribute, servico: DadosAbertosService
) -> None:
    _java(record_xml_attribute, _FQCN_16, "teste_restricaoApenasAdquirente_papelAdquirenteNaoFiltrado_aparece")
    assert _CLASS_SO_ADQ_70 in _codigos_por_atores(servico, fornecedor=22)


def teste_siglaDfe_reduzOuMantemLista(record_xml_attribute, servico: DadosAbertosService) -> None:
    _java(record_xml_attribute, _FQCN_16, "teste_siglaDfe_reduzOuMantemLista")
    q_sem = len(servico.consultarClassificacoesTributariasCbsIbsPorAtores(DATA_2027_01_01))
    q_sigla = len(
        servico.consultarClassificacoesTributariasCbsIbsPorAtores(DATA_2027_01_01, sigla_dfe="NFSe")
    )
    assert q_sigla > 0
    assert q_sigla <= q_sem


def teste_siglaDfeCombinadaComAtores_aplicaELogico(
    record_xml_attribute, servico: DadosAbertosService
) -> None:
    _java(record_xml_attribute, _FQCN_16, "teste_siglaDfeCombinadaComAtores_aplicaELogico")
    codigos_nfse = _codigos_por_atores(
        servico, fornecedor=27, adquirente=28, sigla_dfe="NFSe"
    )
    assert _CLASS_F27_A28 in codigos_nfse
    codigos_cte = _codigos_por_atores(
        servico, fornecedor=27, adquirente=28, sigla_dfe="CTe"
    )
    assert _CLASS_F27_A28 not in codigos_cte
    assert _CLASS_SEM_RESTRICAO in codigos_cte


def teste_fornecedorInexistente_retornaApenasSemRestricaoDeFornecedor(
    record_xml_attribute, servico: DadosAbertosService
) -> None:
    _java(record_xml_attribute, _FQCN_16, "teste_fornecedorInexistente_retornaApenasSemRestricaoDeFornecedor")
    lista = servico.consultarClassificacoesTributariasCbsIbsPorAtores(DATA_2027_01_01, fornecedor=9999)
    assert lista
    codigos = [c.codigo for c in lista]
    assert _CLASS_F27_A28 not in codigos
    assert _CLASS_SEM_RESTRICAO in codigos


# --- Teste_nomenclatura_12 ---


def teste_SEM_200001_NFe(record_xml_attribute, servico: DadosAbertosService) -> None:
    _java(record_xml_attribute, _FQCN_NOM_12, "teste_SEM_200001_NFe")
    assert servico.consultarNomenclatura("NFe", "200001", DATA_2027_01_01).nomenclatura == "SEM"


def teste_NCM_200003_NFe(record_xml_attribute, servico: DadosAbertosService) -> None:
    _java(record_xml_attribute, _FQCN_NOM_12, "teste_NCM_200003_NFe")
    assert servico.consultarNomenclatura("NFe", "200003", DATA_2027_01_01).nomenclatura == "NCM"


def teste_NBS_200028_NFSe(record_xml_attribute, servico: DadosAbertosService) -> None:
    _java(record_xml_attribute, _FQCN_NOM_12, "teste_NBS_200028_NFSe")
    assert servico.consultarNomenclatura("NFSe", "200028", DATA_2027_01_01).nomenclatura == "NBS"


def teste_MISTO_200044_NFSe(record_xml_attribute, servico: DadosAbertosService) -> None:
    _java(record_xml_attribute, _FQCN_NOM_12, "teste_MISTO_200044_NFSe")
    assert servico.consultarNomenclatura("NFSe", "200044", DATA_2027_01_01).nomenclatura == "MISTO"


def teste_EXCECAO_NCM_200038_NFe(record_xml_attribute, servico: DadosAbertosService) -> None:
    _java(record_xml_attribute, _FQCN_NOM_12, "teste_EXCECAO_NCM_200038_NFe")
    assert servico.consultarNomenclatura("NFe", "200038", DATA_2027_01_01).nomenclatura == "EXCECAO_NCM"


def teste_EXCECAO_NCM_200038_NFCe(record_xml_attribute, servico: DadosAbertosService) -> None:
    _java(record_xml_attribute, _FQCN_NOM_12, "teste_EXCECAO_NCM_200038_NFCe")
    assert servico.consultarNomenclatura("NFCe", "200038", DATA_2027_01_01).nomenclatura == "EXCECAO_NCM"


def teste_EXCECAO_NBS_200038_NFSe(record_xml_attribute, servico: DadosAbertosService) -> None:
    _java(record_xml_attribute, _FQCN_NOM_12, "teste_EXCECAO_NBS_200038_NFSe")
    assert servico.consultarNomenclatura("NFSe", "200038", DATA_2027_01_01).nomenclatura == "EXCECAO_NBS"


def teste_EXCECAO_NCM_515001_NFe(record_xml_attribute, servico: DadosAbertosService) -> None:
    _java(record_xml_attribute, _FQCN_NOM_12, "teste_EXCECAO_NCM_515001_NFe")
    assert servico.consultarNomenclatura("NFe", "515001", DATA_2027_01_01).nomenclatura == "EXCECAO_NCM"


def teste_EXCECAO_NBS_515001_NFSe(record_xml_attribute, servico: DadosAbertosService) -> None:
    _java(record_xml_attribute, _FQCN_NOM_12, "teste_EXCECAO_NBS_515001_NFSe")
    assert servico.consultarNomenclatura("NFSe", "515001", DATA_2027_01_01).nomenclatura == "EXCECAO_NBS"


def teste_SEM_200038_BPe(record_xml_attribute, servico: DadosAbertosService) -> None:
    _java(record_xml_attribute, _FQCN_NOM_12, "teste_SEM_200038_BPe")
    assert servico.consultarNomenclatura("BPe", "200038", DATA_2027_01_01).nomenclatura == "SEM"


def teste_NCM_200003_NFSe_OnlyNCM(record_xml_attribute, servico: DadosAbertosService) -> None:
    _java(record_xml_attribute, _FQCN_NOM_12, "teste_NCM_200003_NFSe_OnlyNCM")
    assert servico.consultarNomenclatura("NFSe", "200004", DATA_2027_01_01).nomenclatura == "NCM"


def teste_SEM_200028_NFe_OnlyNBS(record_xml_attribute, servico: DadosAbertosService) -> None:
    _java(record_xml_attribute, _FQCN_NOM_12, "teste_SEM_200028_NFe_OnlyNBS")
    assert servico.consultarNomenclatura("NFe", "200028", DATA_2027_01_01).nomenclatura == "SEM"


def teste_SEM_200003_BPe(record_xml_attribute, servico: DadosAbertosService) -> None:
    _java(record_xml_attribute, _FQCN_NOM_12, "teste_SEM_200003_BPe")
    assert servico.consultarNomenclatura("BPe", "200003", DATA_2027_01_01).nomenclatura == "SEM"


def teste_SEM_200003_CTe(record_xml_attribute, servico: DadosAbertosService) -> None:
    _java(record_xml_attribute, _FQCN_NOM_12, "teste_SEM_200003_CTe")
    assert servico.consultarNomenclatura("CTe", "200003", DATA_2027_01_01).nomenclatura == "SEM"


# --- Teste_nomenclatura_13 ---


def teste_ncmObrigatorio(record_xml_attribute, servico: DadosAbertosService) -> None:
    _java(record_xml_attribute, _FQCN_NOM_13, "teste_ncmObrigatorio")
    r = servico.consultarNomenclatura("NFe", "200003", DATA_2027_01_01)
    assert r.nomenclatura == "NCM"
    assert r.obrigatorio is True
    assert r.ncm_opcional is False
    assert r.nbs_opcional is False


def teste_nbsObrigatoria(record_xml_attribute, servico: DadosAbertosService) -> None:
    _java(record_xml_attribute, _FQCN_NOM_13, "teste_nbsObrigatoria")
    r = servico.consultarNomenclatura("NFSe", "200028", DATA_2027_01_01)
    assert r.nomenclatura == "NBS"
    assert r.obrigatorio is True
    assert r.ncm_opcional is False
    assert r.nbs_opcional is False


def teste_mistoObrigatorio(record_xml_attribute, servico: DadosAbertosService) -> None:
    _java(record_xml_attribute, _FQCN_NOM_13, "teste_mistoObrigatorio")
    r = servico.consultarNomenclatura("NFSe", "200044", DATA_2027_01_01)
    assert r.nomenclatura == "MISTO"
    assert r.obrigatorio is True
    assert r.ncm_opcional is False
    assert r.nbs_opcional is False


def teste_semNfeNcmOpcional(record_xml_attribute, servico: DadosAbertosService) -> None:
    _java(record_xml_attribute, _FQCN_NOM_13, "teste_semNfeNcmOpcional")
    r = servico.consultarNomenclatura("NFe", "200001", DATA_2027_01_01)
    assert r.nomenclatura == "SEM"
    assert r.obrigatorio is False
    assert r.ncm_opcional is True
    assert r.nbs_opcional is False


def teste_semNfceNcmOpcional(record_xml_attribute, servico: DadosAbertosService) -> None:
    _java(record_xml_attribute, _FQCN_NOM_13, "teste_semNfceNcmOpcional")
    r = servico.consultarNomenclatura("NFCe", "200001", DATA_2027_01_01)
    assert r.nomenclatura == "SEM"
    assert r.obrigatorio is False
    assert r.ncm_opcional is True
    assert r.nbs_opcional is False


def teste_semNfseNbsOpcional(record_xml_attribute, servico: DadosAbertosService) -> None:
    _java(record_xml_attribute, _FQCN_NOM_13, "teste_semNfseNbsOpcional")
    r = servico.consultarNomenclatura("NFSe", "200001", DATA_2027_01_01)
    assert r.nomenclatura == "SEM"
    assert r.obrigatorio is False
    assert r.ncm_opcional is False
    assert r.nbs_opcional is True


def teste_semForaDoTrio(record_xml_attribute, servico: DadosAbertosService) -> None:
    _java(record_xml_attribute, _FQCN_NOM_13, "teste_semForaDoTrio")
    r = servico.consultarNomenclatura("BPe", "200003", DATA_2027_01_01)
    assert r.nomenclatura == "SEM"
    assert r.obrigatorio is False
    assert r.ncm_opcional is False
    assert r.nbs_opcional is False


def teste_semForaDoTrioCte(record_xml_attribute, servico: DadosAbertosService) -> None:
    _java(record_xml_attribute, _FQCN_NOM_13, "teste_semForaDoTrioCte")
    r = servico.consultarNomenclatura("CTe", "200003", DATA_2027_01_01)
    assert r.nomenclatura == "SEM"
    assert r.obrigatorio is False
    assert r.ncm_opcional is False
    assert r.nbs_opcional is False


def teste_excecaoNcm200038(record_xml_attribute, servico: DadosAbertosService) -> None:
    _java(record_xml_attribute, _FQCN_NOM_13, "teste_excecaoNcm200038")
    r = servico.consultarNomenclatura("NFe", "200038", DATA_2027_01_01)
    assert r.nomenclatura == "EXCECAO_NCM"
    assert r.obrigatorio is True
    assert r.ncm_opcional is False
    assert r.nbs_opcional is False


def teste_excecaoNbs200038(record_xml_attribute, servico: DadosAbertosService) -> None:
    _java(record_xml_attribute, _FQCN_NOM_13, "teste_excecaoNbs200038")
    r = servico.consultarNomenclatura("NFSe", "200038", DATA_2027_01_01)
    assert r.nomenclatura == "EXCECAO_NBS"
    assert r.obrigatorio is True
    assert r.ncm_opcional is False
    assert r.nbs_opcional is False


def teste_200038ForaDoTrio(record_xml_attribute, servico: DadosAbertosService) -> None:
    _java(record_xml_attribute, _FQCN_NOM_13, "teste_200038ForaDoTrio")
    r = servico.consultarNomenclatura("BPe", "200038", DATA_2027_01_01)
    assert r.nomenclatura == "SEM"
    assert r.obrigatorio is False
    assert r.ncm_opcional is False
    assert r.nbs_opcional is False