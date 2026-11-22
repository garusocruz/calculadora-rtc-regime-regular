"""Paridade com br.gov.serpro.rtc.domain.service.CalculadoraServiceTest (surefire)."""

from __future__ import annotations

from datetime import date
from types import SimpleNamespace

import pytest

from calculadora_rtc_regime_regular.aviso import TipoWarningDadosSimulados, aviso_dados_simulados

_CST_FICTICIA = ("010", "220", "221")

_DATAS_ALIQUOTAS = (
    (date(2026, 1, 1), TipoWarningDadosSimulados.CASO_ALIQUOTAS_FICTICIAS),
    (date(2026, 12, 31), TipoWarningDadosSimulados.CASO_ALIQUOTAS_FICTICIAS),
    (date(2027, 1, 1), TipoWarningDadosSimulados.CASO_CALCULOS_SIMULADOS),
    (date(2028, 5, 10), TipoWarningDadosSimulados.CASO_CALCULOS_SIMULADOS),
)


def _item(cst: str | None = None, *, seletivo: bool = False) -> SimpleNamespace:
    return SimpleNamespace(
        cst=cst,
        imposto_seletivo=object() if seletivo else None,
    )


def test_deveRetornarNullQuandoDataAnteriorA2027() -> None:
    resultado = aviso_dados_simulados(date(2026, 12, 31), [_item()])
    assert resultado is None


@pytest.mark.parametrize("cst", _CST_FICTICIA, ids=["1", "2", "3"])
def test_deveRetornarCasoAliquotasFicticiasParaQualquerData(cst: str) -> None:
    for data, esperado in _DATAS_ALIQUOTAS:
        resultado = aviso_dados_simulados(data, [_item(cst)])
        assert resultado is esperado, f"CST {cst} na data {data}"
        assert resultado is not None
        assert resultado.value == esperado.value


def test_deveRetornarCasoImpostoSeletivo() -> None:
    resultado = aviso_dados_simulados(
        date(2027, 1, 1),
        [_item("000", seletivo=True)],
    )
    assert resultado is TipoWarningDadosSimulados.CASO_CALCULOS_SIMULADOS
    assert resultado.value == 6


def test_deveRetornarCasoGeral() -> None:
    resultado = aviso_dados_simulados(date(2027, 1, 1), [_item("000")])
    assert resultado is TipoWarningDadosSimulados.CASO_CALCULOS_SIMULADOS
    assert resultado.value == 6