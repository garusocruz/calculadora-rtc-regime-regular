"""Paridade com ``Teste_CreditoPresumidoOperacaoDomain`` (domínio ROC)."""

from __future__ import annotations

from decimal import Decimal

from calculadora_rtc_regime_regular.roc import (
    CreditoPresumidoOperacaoDomain,
    IBSCBSCreditoPresumidoDomain,
    ZERO,
)

def d(value: str | Decimal) -> Decimal:
    return value if isinstance(value, Decimal) else Decimal(value)

def test_teste_possuiCredPresCbsSemDados_retornaFalse() -> None:
    assert not CreditoPresumidoOperacaoDomain().possui_cred_pres_cbs()

def test_teste_possuiCredPresCbsComDados_retornaTrue() -> None:
    domain = CreditoPresumidoOperacaoDomain(g_cbs_cred_pres=IBSCBSCreditoPresumidoDomain())
    assert domain.possui_cred_pres_cbs()

def test_teste_possuiCredPresIbsSemDados_retornaFalse() -> None:
    assert not CreditoPresumidoOperacaoDomain().possui_cred_pres_ibs()

def test_teste_possuiCredPresIbsComDadosVazios_retornaFalse() -> None:
    domain = CreditoPresumidoOperacaoDomain(g_ibs_cred_pres=IBSCBSCreditoPresumidoDomain())
    assert not domain.possui_cred_pres_ibs()

def test_teste_possuiCredPresIbsComValor_retornaTrue() -> None:
    domain = CreditoPresumidoOperacaoDomain(
        g_ibs_cred_pres=IBSCBSCreditoPresumidoDomain(v_cred_pres=d("10.00"))
    )
    assert domain.possui_cred_pres_ibs()

def test_teste_getVCredPresIbsSemDados_retornaZero() -> None:
    assert CreditoPresumidoOperacaoDomain().get_v_cred_pres_ibs() == ZERO

def test_teste_getVCredPresIbsComDados_retornaValor() -> None:
    domain = CreditoPresumidoOperacaoDomain(
        g_ibs_cred_pres=IBSCBSCreditoPresumidoDomain(v_cred_pres=d("42.50"))
    )
    assert domain.get_v_cred_pres_ibs() == d("42.50")

def test_teste_possuiCredPresCondSusIbsSemDados_retornaFalse() -> None:
    assert not CreditoPresumidoOperacaoDomain().possui_cred_pres_cond_sus_ibs()

def test_teste_possuiCredPresCondSusIbsComValor_retornaTrue() -> None:
    domain = CreditoPresumidoOperacaoDomain(
        g_ibs_cred_pres=IBSCBSCreditoPresumidoDomain(v_cred_pres_cond_sus=d("5.00"))
    )
    assert domain.possui_cred_pres_cond_sus_ibs()

def test_teste_getVCredPresCondSusIbsSemDados_retornaZero() -> None:
    assert CreditoPresumidoOperacaoDomain().get_v_cred_pres_cond_sus_ibs() == ZERO

def test_teste_getVCredPresCondSusIbsComDados_retornaValor() -> None:
    domain = CreditoPresumidoOperacaoDomain(
        g_ibs_cred_pres=IBSCBSCreditoPresumidoDomain(v_cred_pres_cond_sus=d("7.75"))
    )
    assert domain.get_v_cred_pres_cond_sus_ibs() == d("7.75")
