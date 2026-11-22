"""Integração NFS-e (pin f1eebd7) — chamada de serviço, sem Spring."""

from __future__ import annotations

import os
from datetime import date
from decimal import Decimal

import pytest

os.environ.setdefault(
    "CALC_DB",
    "/home/garusotec/projects/lynko/libs/calculadora-rtc-regime-regular/.cache/oficial/java/calculadora/db/calculadora-pro.db",
)

from calculadora_rtc_regime_regular.base_calculo_service import CampoInvalido
from calculadora_rtc_regime_regular.consumo import NfseBaseCalculoInput, NfseService
from calculadora_rtc_regime_regular.dados_abertos import NbsNaoEncontradaException
from calculadora_rtc_regime_regular.nfse_servico import (
    IndicadorOperacaoNaoEncontradoException,
    NfseValidacaoIndicadorOperacaoEntrada,
)

pytestmark = pytest.mark.skipif(not os.environ.get("CALC_DB"), reason="CALC_DB ausente")

DATA_2026_01_01 = date(2026, 1, 1)
DATA_2024_12_31 = date(2024, 12, 31)

_FQCN_1 = "br.gov.serpro.rtc.testesintegracao.nfse.Teste_nfse_1_consultarIndicadoresOperacao"
_FQCN_2 = "br.gov.serpro.rtc.testesintegracao.nfse.Teste_nfse_2_consultarLocalOperacao"
_FQCN_3 = "br.gov.serpro.rtc.testesintegracao.nfse.Teste_nfse_3_calcularBaseCalculo"
_FQCN_4 = "br.gov.serpro.rtc.testesintegracao.nfse.Teste_nfse_4_validarIndicadorOperacao"
_FQCN_5 = "br.gov.serpro.rtc.testesintegracao.nfse.Teste_nfse_5_consultarSituacoesClassificacoes"

# Excluídos (só Spring — ver relatório):
# Teste_nfse_1: teste_controller_consultarIndicadoresOperacaoDataInvalida, SemDataObrigatoria
# Teste_nfse_2: ParametroInvalido, DataInvalida, SemParametrosObrigatorios
# Teste_nfse_3: teste_controller_calcularBaseCalculoValoresNulos
# Teste_nfse_4: teste_controller_validarIndicadorOperacaoDadosObrigatoriosNulos
# Teste_nfse_5: SemParametros, DataInvalida, NbsInvalido (formato)


def _java(record_xml_attribute, fqcn: str, metodo: str) -> None:
    record_xml_attribute("classname", fqcn)
    record_xml_attribute("name", metodo)


@pytest.fixture(scope="module")
def servico() -> NfseService:
    return NfseService()


# --- Teste_nfse_1 ---


def teste_controller_consultarIndicadoresOperacaoSemNbs(
    record_xml_attribute, servico: NfseService
) -> None:
    _java(record_xml_attribute, _FQCN_1, "teste_controller_consultarIndicadoresOperacaoSemNbs")
    resultado = servico.consultarIndicadorOperacao(DATA_2026_01_01)
    assert isinstance(resultado, list)


def teste_controller_consultarIndicadoresOperacaoComNbs(
    record_xml_attribute, servico: NfseService
) -> None:
    _java(record_xml_attribute, _FQCN_1, "teste_controller_consultarIndicadoresOperacaoComNbs")
    assert isinstance(servico.consultarIndicadorOperacao(DATA_2026_01_01, "115021000"), list)


def teste_controller_consultarIndicadoresOperacaoComNbsInvalido(
    record_xml_attribute, servico: NfseService
) -> None:
    _java(record_xml_attribute, _FQCN_1, "teste_controller_consultarIndicadoresOperacaoComNbsInvalido")
    with pytest.raises(NbsNaoEncontradaException):
        servico.consultarIndicadorOperacao(DATA_2026_01_01, "999999999")


# --- Teste_nfse_2 ---


def teste_controller_consultarLocalOperacaoComSucesso(
    record_xml_attribute, servico: NfseService
) -> None:
    _java(record_xml_attribute, _FQCN_2, "teste_controller_consultarLocalOperacaoComSucesso")
    saida = servico.consultarLocalOperacao("100301", DATA_2026_01_01)
    assert saida.c_ind_op == "100301"
    assert saida.data_ocorrencia_fato_gerador == DATA_2026_01_01
    assert saida.codigo_local_fornecimento is not None
    assert saida.codigo_local_incidencia is not None


def teste_controller_consultarLocalOperacaoIndicadorInexistente(
    record_xml_attribute, servico: NfseService
) -> None:
    _java(record_xml_attribute, _FQCN_2, "teste_controller_consultarLocalOperacaoIndicadorInexistente")
    with pytest.raises(IndicadorOperacaoNaoEncontradoException):
        servico.consultarLocalOperacao("999999", DATA_2026_01_01)


# --- Teste_nfse_3 ---


def teste_controller_calcularBaseCalculoComSucesso(
    record_xml_attribute, servico: NfseService
) -> None:
    _java(record_xml_attribute, _FQCN_3, "teste_controller_calcularBaseCalculoComSucesso")
    saida = servico.calcularBaseCalculo(
        NfseBaseCalculoInput(
            ano_fato_gerador=2026,
            valor_servico=Decimal("100.00"),
            desconto_incondicional=Decimal("5.00"),
            v_calc_ree_rep_res=Decimal("6.00"),
            v_calc_ded_red_ibscbs=Decimal("4.00"),
            iss=Decimal("5.00"),
            pis=Decimal("1.65"),
            cofins=Decimal("7.60"),
        )
    )
    assert saida.base_calculo == Decimal("70.75")


def teste_controller_calcularBaseCalculoDataApartir2033(
    record_xml_attribute, servico: NfseService
) -> None:
    _java(record_xml_attribute, _FQCN_3, "teste_controller_calcularBaseCalculoDataApartir2033")
    saida = servico.calcularBaseCalculo(
        NfseBaseCalculoInput(
            ano_fato_gerador=2033,
            valor_servico=Decimal("100.00"),
            desconto_incondicional=Decimal("5.00"),
            v_calc_ree_rep_res=Decimal("3.00"),
            v_calc_ded_red_ibscbs=Decimal("2.00"),
        )
    )
    assert saida.base_calculo == Decimal("90.00")


def teste_controller_calcularBaseCalculoBaseNegativa(
    record_xml_attribute, servico: NfseService
) -> None:
    _java(record_xml_attribute, _FQCN_3, "teste_controller_calcularBaseCalculoBaseNegativa")
    with pytest.raises(CampoInvalido, match="Base de cálculo não pode ser negativa"):
        servico.calcularBaseCalculo(
            NfseBaseCalculoInput(
                ano_fato_gerador=2026,
                valor_servico=Decimal("10.00"),
                desconto_incondicional=Decimal("50.00"),
            )
        )


# --- Teste_nfse_4 ---


def teste_controller_validarIndicadorOperacaoComCTribNac(
    record_xml_attribute, servico: NfseService
) -> None:
    _java(record_xml_attribute, _FQCN_4, "teste_controller_validarIndicadorOperacaoComCTribNac")
    saida = servico.validarIndicadorOperacao(
        NfseValidacaoIndicadorOperacaoEntrada(
            nbs="123456789",
            c_class_trib="620001",
            c_ind_op="100301",
            c_trib_nac="0101",
            data_ocorrencia_fato_gerador=DATA_2026_01_01,
        )
    )
    assert saida.c_ind_op == "100301"
    assert saida.c_class_trib == "620001"
    assert saida.nbs == "123456789"
    assert saida.data_ocorrencia_fato_gerador == DATA_2026_01_01
    assert isinstance(saida.valido, bool)


def teste_controller_validarIndicadorOperacaoSemCTribNac(
    record_xml_attribute, servico: NfseService
) -> None:
    _java(record_xml_attribute, _FQCN_4, "teste_controller_validarIndicadorOperacaoSemCTribNac")
    saida = servico.validarIndicadorOperacao(
        NfseValidacaoIndicadorOperacaoEntrada(
            nbs="123456789",
            c_class_trib="620001",
            c_ind_op="100301",
            data_ocorrencia_fato_gerador=DATA_2026_01_01,
        )
    )
    assert saida.c_ind_op == "100301"
    assert saida.c_class_trib == "620001"
    assert saida.nbs == "123456789"
    assert saida.data_ocorrencia_fato_gerador == DATA_2026_01_01
    assert isinstance(saida.valido, bool)


def teste_controller_validarIndicadorOperacaoCombinacaoInvalida(
    record_xml_attribute, servico: NfseService
) -> None:
    _java(record_xml_attribute, _FQCN_4, "teste_controller_validarIndicadorOperacaoCombinacaoInvalida")
    saida = servico.validarIndicadorOperacao(
        NfseValidacaoIndicadorOperacaoEntrada(
            nbs="999999999",
            c_class_trib="999999",
            c_ind_op="999999",
            c_trib_nac="9999",
            data_ocorrencia_fato_gerador=DATA_2026_01_01,
        )
    )
    assert isinstance(saida.valido, bool)


# --- Teste_nfse_5 ---


def teste_controller_consultarSituacoesClassificacoesPorNbs(
    record_xml_attribute, servico: NfseService
) -> None:
    _java(record_xml_attribute, _FQCN_5, "teste_controller_consultarSituacoesClassificacoesPorNbs")
    resultado = servico.consultarSituacoesClassificacoesPorNbs("115021000", DATA_2026_01_01)
    assert isinstance(resultado, list)


def teste_controller_consultarSituacoesClassificacoes_DeveRetornar404QuandoNbsInvalido(
    record_xml_attribute, servico: NfseService
) -> None:
    _java(
        record_xml_attribute,
        _FQCN_5,
        "teste_controller_consultarSituacoesClassificacoes_DeveRetornar404QuandoNbsInvalido",
    )
    with pytest.raises(NbsNaoEncontradaException):
        servico.consultarSituacoesClassificacoesPorNbs("999999999", DATA_2026_01_01)


def teste_controller_consultarSituacoesClassificacoes_DeveRetornar404QuandoNbsForaDaVigencia(
    record_xml_attribute, servico: NfseService
) -> None:
    _java(
        record_xml_attribute,
        _FQCN_5,
        "teste_controller_consultarSituacoesClassificacoes_DeveRetornar404QuandoNbsForaDaVigencia",
    )
    with pytest.raises(NbsNaoEncontradaException):
        servico.consultarSituacoesClassificacoesPorNbs("126050000", DATA_2024_12_31)