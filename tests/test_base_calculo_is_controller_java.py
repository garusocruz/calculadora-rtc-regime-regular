"""Paridade com ``Teste_BaseCalculoIS_Controller`` — serviço direto."""

from __future__ import annotations

from decimal import Decimal

from calculadora_rtc_regime_regular.base_calculo_service import EntradaIsMercadorias, calcular_is_mercadorias


def teste_calculoBasicoComSucesso() -> None:
    base = calcular_is_mercadorias(
        EntradaIsMercadorias(2027, Decimal("100.00"), Decimal("10.00"), Decimal("5.00"), icms=Decimal("15.00"))
    )
    assert base == Decimal("100.00")


def teste_todosCamposQueIntegram_SemImpostoSeletivo() -> None:
    base = calcular_is_mercadorias(
        EntradaIsMercadorias(
            2027,
            Decimal("1000.00"),
            Decimal("50.00"),
            Decimal("20.00"),
            Decimal("10.00"),
            Decimal("30.00"),
            Decimal("40.00"),
            Decimal("25.00"),
            Decimal("15.00"),
        )
    )
    assert base == Decimal("1190.00")


def teste_todosCamposQueNaoIntegram_ComBonificacaoEDevolucao() -> None:
    base = calcular_is_mercadorias(
        EntradaIsMercadorias(
            2027,
            Decimal("2000.00"),
            icms=Decimal("100.00"),
            iss=Decimal("50.00"),
            cosip=Decimal("5.00"),
            ipi=Decimal("150.00"),
            desconto_incondicional=Decimal("50.00"),
            bonificacao=Decimal("100.00"),
            devolucao_vendas=Decimal("200.00"),
        )
    )
    assert base == Decimal("1345.00")


def teste_valoresZeroRetornaZero() -> None:
    assert calcular_is_mercadorias(EntradaIsMercadorias(2027)) == Decimal("0.00")


def teste_bonificacaoReduzBase_Art417() -> None:
    assert calcular_is_mercadorias(
        EntradaIsMercadorias(2027, Decimal("1000.00"), bonificacao=Decimal("150.00"))
    ) == Decimal("850.00")


def teste_devolucaoVendasReduzBase_Art418() -> None:
    assert calcular_is_mercadorias(
        EntradaIsMercadorias(2027, Decimal("1000.00"), devolucao_vendas=Decimal("200.00"))
    ) == Decimal("800.00")


def teste_bonificacaoEDevolucaoJuntos() -> None:
    assert calcular_is_mercadorias(
        EntradaIsMercadorias(
            2027, Decimal("1000.00"), bonificacao=Decimal("100.00"), devolucao_vendas=Decimal("50.00")
        )
    ) == Decimal("850.00")