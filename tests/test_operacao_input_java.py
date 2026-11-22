"""Paridade com ``OperacaoInputTest`` (``getFatoGeradorAplicavel``)."""

from __future__ import annotations

from datetime import date, datetime

import pytest

from calculadora_rtc_regime_regular.processamento_item import (
    DataFatoGeradorNaoInformadaException,
    OperacaoInput,
)


def test_retornaDataDoDhFatoGeradorQuandoPresente() -> None:
    entrada = OperacaoInput()
    dh = datetime.fromisoformat("2026-01-05T11:42:49.95-03:00")
    entrada.dh_fato_gerador = dh
    assert entrada.fato_gerador_aplicavel() == dh.date()


def test_retornaDataDoDataHoraEmissaoQuandoDhFatoGeradorNulo() -> None:
    entrada = OperacaoInput()
    data_hora = datetime.fromisoformat("2026-01-10T09:00:00-03:00")
    entrada.data_hora_emissao = data_hora
    assert entrada.fato_gerador_aplicavel() == date(2026, 1, 10)


def test_lancaExcecaoQuandoDatasSaoNulas() -> None:
    entrada = OperacaoInput()
    with pytest.raises(DataFatoGeradorNaoInformadaException):
        entrada.fato_gerador_aplicavel()