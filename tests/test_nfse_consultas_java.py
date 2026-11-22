"""Teste_nfse_2 / Teste_nfse_5 — validação de parâmetros (pin f1eebd7, sem Spring)."""

from __future__ import annotations

import os

import pytest

os.environ.setdefault(
    "CALC_DB",
    "/home/garusotec/projects/lynko/libs/calculadora-rtc-regime-regular/.cache/oficial/java/calculadora/db/calculadora-pro.db",
)

from calculadora_rtc_regime_regular.base_calculo_service import CampoInvalido
from calculadora_rtc_regime_regular.consumo import NfseService

pytestmark = pytest.mark.skipif(not os.environ.get("CALC_DB"), reason="CALC_DB ausente")


@pytest.fixture(scope="module")
def servico() -> NfseService:
    return NfseService()


def teste_controller_consultarLocalOperacaoParametroInvalido(servico: NfseService) -> None:
    with pytest.raises(CampoInvalido, match="6 dígitos"):
        servico.consultarLocalOperacao("12345", "2026-01-01")


def teste_controller_consultarLocalOperacaoDataInvalida(servico: NfseService) -> None:
    with pytest.raises(CampoInvalido, match="dataOcorrenciaFatoGerador"):
        servico.consultarLocalOperacao("100301", "invalid-date")


def teste_controller_consultarLocalOperacaoSemParametrosObrigatorios(servico: NfseService) -> None:
    with pytest.raises(CampoInvalido, match="cIndOp"):
        servico.consultarLocalOperacao(None, None)


def teste_controller_consultarSituacoesClassificacoesSemParametros(servico: NfseService) -> None:
    with pytest.raises(CampoInvalido, match="nbs"):
        servico.consultarSituacoesClassificacoesPorNbs(None, None)


def teste_controller_consultarSituacoesClassificacoesDataInvalida(servico: NfseService) -> None:
    with pytest.raises(CampoInvalido, match="data"):
        servico.consultarSituacoesClassificacoesPorNbs("123456789", "invalid-date")


def teste_controller_consultarSituacoesClassificacoesNbsInvalido(servico: NfseService) -> None:
    with pytest.raises(CampoInvalido, match="9 dígitos"):
        servico.consultarSituacoesClassificacoesPorNbs("12345", "2026-01-01")