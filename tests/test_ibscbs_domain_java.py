"""Paridade com ``Teste_IBSCBSDomain`` (domínio ROC)."""

from __future__ import annotations

from decimal import Decimal

from calculadora_rtc_regime_regular.roc import (
    CBSDomain,
    CreditoPresumidoOperacaoDomain,
    EstornoCreditoDomain,
    GrupoIBSCBSDomain,
    IBSCBSCreditoPresumidoDomain,
    IBSCBSDomain,
    IBSMunDomain,
    IBSUFDomain,
    MonofasiaDomain,
    TributacaoRegularDomain,
    ZERO,
)

def d(value: str | Decimal) -> Decimal:
    return value if isinstance(value, Decimal) else Decimal(value)

def test_teste_IBSCBSDomainVazio_retornaFalseENull() -> None:
    domain = IBSCBSDomain()
    assert not domain.possui_base_calculo_ibscbs()
    assert domain.get_valor_base_calculo_ibscbs() == ZERO
    assert not domain.possui_cbs()
    assert domain.get_g_cbs() is None
    assert domain.get_grupo_ibscbs() is None
    assert not domain.possui_ibs_uf()
    assert not domain.possui_ibs_mun()
    assert domain.get_g_ibs_uf() is None
    assert domain.get_g_ibs_mun() is None
    assert not domain.possui_tributacao_regular()
    assert domain.get_tributacao_regular() is None

def test_teste_IBSCBSDomainComGrupoIBSCBS_retornaDelegates() -> None:
    cbs = CBSDomain()
    ibs_uf = IBSUFDomain()
    ibs_mun = IBSMunDomain()
    trib_reg = TributacaoRegularDomain()
    grupo = GrupoIBSCBSDomain(g_cbs=cbs, g_ibs_uf=ibs_uf, g_ibs_mun=ibs_mun, g_trib_regular=trib_reg)
    domain = IBSCBSDomain(g_ibscbs=grupo)
    assert domain.possui_cbs()
    assert domain.get_g_cbs() is not None
    assert domain.possui_ibs_uf()
    assert domain.possui_ibs_mun()
    assert domain.get_g_ibs_uf() is not None
    assert domain.get_g_ibs_mun() is not None
    assert domain.possui_tributacao_regular()
    assert domain.get_tributacao_regular() is not None
    assert domain.get_grupo_ibscbs() is not None

def test_teste_possuiMonofasiaComGIBSCBSMono_retornaTrue() -> None:
    assert IBSCBSDomain(g_ibscbs_mono=MonofasiaDomain()).possui_monofasia()

def test_teste_possuiMonofasiaSemGIBSCBSMono_retornaFalse() -> None:
    assert not IBSCBSDomain().possui_monofasia()

def test_teste_possuiEstornoCreditoComEstorno_retornaTrue() -> None:
    assert IBSCBSDomain(g_estorno_cred=EstornoCreditoDomain()).possui_estorno_credito()

def test_teste_possuiEstornoCreditoSemEstorno_retornaFalse() -> None:
    assert not IBSCBSDomain().possui_estorno_credito()

def test_teste_IBSCBSDomainSemCredPresOper_retornaFalse() -> None:
    domain = IBSCBSDomain()
    assert not domain.possui_cred_pres_cbs()
    assert domain.get_cred_pres_cbs() is None
    assert not domain.possui_cred_pres_ibs()
    assert domain.get_v_cred_pres_ibs() == ZERO
    assert not domain.possui_cred_pres_cond_sus_ibs()
    assert domain.get_v_cred_pres_cond_sus_ibs() == ZERO

def test_teste_IBSCBSDomainComCredPresOper_retornaTrue() -> None:
    cred_pres = CreditoPresumidoOperacaoDomain(g_cbs_cred_pres=IBSCBSCreditoPresumidoDomain())
    domain = IBSCBSDomain(g_cred_pres_oper=cred_pres)
    assert domain.possui_cred_pres_cbs()
    assert domain.get_cred_pres_cbs() is not None

def test_teste_IBSCBSDomainComCredPresOperEValor_retornaTrueEValor() -> None:
    ibs_cred = IBSCBSCreditoPresumidoDomain(v_cred_pres=d("25.00"))
    cred_pres = CreditoPresumidoOperacaoDomain(g_ibs_cred_pres=ibs_cred)
    domain = IBSCBSDomain(g_cred_pres_oper=cred_pres)
    assert domain.possui_cred_pres_ibs()
    assert domain.get_v_cred_pres_ibs() == d("25.00")
