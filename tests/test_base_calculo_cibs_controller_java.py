"""Paridade com ``Teste_BaseCalculoCibs_Controller`` — ``BaseCalculoService`` direto."""

from __future__ import annotations

from decimal import Decimal

from calculadora_rtc_regime_regular.base_calculo_service import EntradaCibs, calcular_cibs


def teste_calculoBasicoComSucesso() -> None:
    base = calcular_cibs(
        EntradaCibs(2027, Decimal("100.00"), Decimal("10.00"), Decimal("5.00"), icms=Decimal("15.00"))
    )
    assert base == Decimal("100.00")


def teste_todosCamposQueIntegram() -> None:
    base = calcular_cibs(
        EntradaCibs(
            2027,
            Decimal("1000.00"),
            Decimal("50.00"),
            Decimal("20.00"),
            Decimal("10.00"),
            Decimal("30.00"),
            Decimal("40.00"),
            Decimal("100.00"),
            Decimal("25.00"),
            Decimal("15.00"),
        )
    )
    assert base == Decimal("1290.00")


def teste_todosCamposQueNaoIntegram() -> None:
    base = calcular_cibs(
        EntradaCibs(
            2026,
            Decimal("1000.00"),
            icms=Decimal("100.00"),
            iss=Decimal("50.00"),
            pis=Decimal("16.50"),
            pis_importacao=Decimal("10.00"),
            cofins=Decimal("76.00"),
            cofins_importacao=Decimal("20.00"),
            cosip=Decimal("5.00"),
            ipi=Decimal("150.00"),
            desconto_incondicional=Decimal("50.00"),
        )
    )
    assert base == Decimal("522.50")


def teste_valoresZeroRetornaZero() -> None:
    assert calcular_cibs(EntradaCibs(2027)) == Decimal("0.00")


def teste_impostoSeletivoIntegraBase() -> None:
    base = calcular_cibs(
        EntradaCibs(2027, Decimal("500.00"), imposto_seletivo=Decimal("100.00"), icms=Decimal("50.00"))
    )
    assert base == Decimal("550.00")


def teste_novosCamposLC214() -> None:
    base = calcular_cibs(
        EntradaCibs(
            2027,
            Decimal("500.00"),
            cosip=Decimal("5.00"),
            ipi=Decimal("50.00"),
            desconto_incondicional=Decimal("15.00"),
        )
    )
    assert base == Decimal("430.00")


def teste_camposRemovidosNaoExistemMais() -> None:
    base = calcular_cibs(EntradaCibs(2027, Decimal("100.00"), Decimal("10.00"), icms=Decimal("10.00")))
    assert base == Decimal("100.00")