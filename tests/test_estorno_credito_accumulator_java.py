"""Paridade com ``Teste_EstornoCreditoAccumulator`` (domínio ROC)."""

from __future__ import annotations

from decimal import Decimal

from calculadora_rtc_regime_regular.roc import (
    EstornoCreditoAccumulator,
    EstornoCreditoDomain,
    ZERO,
)

ONE = Decimal(1)
TEN = Decimal(10)

def d(value: str | Decimal) -> Decimal:
    return value if isinstance(value, Decimal) else Decimal(value)

def test_teste_construtorPadrao_inicializaComZeros() -> None:
    total = EstornoCreditoAccumulator().to_estorno_credito_domain_total()
    assert total.v_ibs_est_cred == ZERO
    assert total.v_cbs_est_cred == ZERO

def test_teste_construtorComValores_preservaValores() -> None:
    total = EstornoCreditoAccumulator(TEN, ONE).to_estorno_credito_domain_total()
    assert total.v_ibs_est_cred == TEN
    assert total.v_cbs_est_cred == ONE

def test_teste_construtorComNulls_substituiPorZeros() -> None:
    total = EstornoCreditoAccumulator(None, None).to_estorno_credito_domain_total()
    assert total.v_ibs_est_cred == ZERO
    assert total.v_cbs_est_cred == ZERO

def test_teste_fromNull_inicializaComZeros() -> None:
    total = EstornoCreditoAccumulator.from_fields(None).to_estorno_credito_domain_total()
    assert total.v_ibs_est_cred == ZERO
    assert total.v_cbs_est_cred == ZERO

def test_teste_fromDomain_extraiValores() -> None:
    domain = EstornoCreditoDomain(v_ibs_est_cred=d("5.50"), v_cbs_est_cred=d("3.25"))
    total = EstornoCreditoAccumulator.from_fields(domain).to_estorno_credito_domain_total()
    assert total.v_ibs_est_cred == d("5.50")
    assert total.v_cbs_est_cred == d("3.25")

def test_teste_fromDomainComCamposNulos_inicializaComZeros() -> None:
    total = EstornoCreditoAccumulator.from_fields(EstornoCreditoDomain()).to_estorno_credito_domain_total()
    assert total.v_ibs_est_cred == ZERO
    assert total.v_cbs_est_cred == ZERO

def test_teste_addNull_adicionaZero() -> None:
    total = EstornoCreditoAccumulator(TEN, ONE).add(None).to_estorno_credito_domain_total()
    assert total.v_ibs_est_cred == TEN
    assert total.v_cbs_est_cred == ONE

def test_teste_addValor_somaCorretamente() -> None:
    result = EstornoCreditoAccumulator(TEN, ONE).add(EstornoCreditoAccumulator(d("5"), d("2")))
    total = result.to_estorno_credito_domain_total()
    assert total.v_ibs_est_cred == d("15")
    assert total.v_cbs_est_cred == d("3")
