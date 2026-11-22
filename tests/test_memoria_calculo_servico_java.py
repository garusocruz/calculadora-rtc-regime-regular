"""Paridade com ``MemoriaCalculoServiceTest`` (formatação pt-BR via serviço)."""

from __future__ import annotations

from decimal import Decimal

import pytest

from calculadora_rtc_regime_regular.memoria import MemoriaCalculoService


def _formatar(metodo: str, valor: Decimal | None) -> str:
    return getattr(MemoriaCalculoService, metodo)(valor)


@pytest.mark.parametrize(
    ("valor", "esperado"),
    [
        (Decimal("247.30000000"), "247,30"),
        (Decimal("1234.5"), "1.234,50"),
    ],
    ids=["1", "2"],
)
def test_deveFormatarMoedaEmPtBr(valor: Decimal, esperado: str) -> None:
    assert _formatar("formatarMoeda", valor) == esperado


@pytest.mark.parametrize(
    ("valor", "esperado"),
    [
        (Decimal("8.4"), "8,40"),
        (Decimal("0.05"), "0,05"),
        (Decimal("0.0375"), "0,0375"),
    ],
    ids=["1", "2", "3"],
)
def test_deveFormatarPercentualEmPtBr(valor: Decimal, esperado: str) -> None:
    assert _formatar("formatarPercentual", valor) == esperado


def test_deveFormatarNuloComoZero() -> None:
    assert _formatar("formatarMoeda", None) == "0,00"
    assert _formatar("formatarPercentual", None) == "0,00"