"""Paridade com ``Teste_TributosDomain`` (domínio ROC)."""

from __future__ import annotations

from decimal import Decimal

from calculadora_rtc_regime_regular.roc import (
    CBSDomain,
    EstornoCreditoDomain,
    GrupoIBSCBSDomain,
    IBSCBSDomain,
    IBSMunDomain,
    IBSUFDomain,
    ImpostoSeletivoDomain,
    MonofasiaDomain,
    TributacaoRegularDomain,
    TributosDomain,
    ZERO,
)

def d(value: str | Decimal) -> Decimal:
    return value if isinstance(value, Decimal) else Decimal(value)

def test_teste_inicializacaoSemImpostoSeletivo_retornaFalse() -> None:
    tributos = TributosDomain()
    assert not tributos.possui_imposto_seletivo()
    assert tributos.get_valor_imposto_seletivo() == ZERO

def test_teste_inicializacaoComImpostoSeletivo_retornaTrue() -> None:
    tributos = TributosDomain(IS=ImpostoSeletivoDomain(v_is=d("100")))
    assert tributos.possui_imposto_seletivo()
    assert tributos.get_valor_imposto_seletivo() == d("100")

def test_teste_inicializacaoSemIBSCBS_retornaDefaultsNullEZero() -> None:
    tributos = TributosDomain()
    assert not tributos.possui_base_calculo_ibscbs()
    assert tributos.get_valor_base_calculo_ibscbs() == ZERO
    assert not tributos.possui_cbs()
    assert tributos.get_g_cbs() is None
    assert not tributos.possui_cred_pres_cbs()
    assert tributos.get_cred_pres_cbs() is None
    assert not tributos.possui_cred_pres_ibs()
    assert tributos.get_v_cred_pres_ibs() == ZERO
    assert not tributos.possui_cred_pres_cond_sus_ibs()
    assert tributos.get_v_cred_pres_cond_sus_ibs() == ZERO
    assert tributos.get_grupo_ibscbs() is None
    assert not tributos.possui_ibs_uf()
    assert not tributos.possui_ibs_mun()
    assert tributos.get_g_ibs_uf() is None
    assert tributos.get_g_ibs_mun() is None
    assert not tributos.possui_monofasia()
    assert tributos.get_g_ibscbs_mono() is None
    assert not tributos.possui_tributacao_regular()
    assert tributos.get_tributacao_regular() is None
    assert not tributos.possui_estorno_credito()
    assert tributos.get_g_estorno_cred() is None

def test_teste_inicializacaoComIBSCBSComGrupo_retornaDelegates() -> None:
    grupo = GrupoIBSCBSDomain(
        g_cbs=CBSDomain(),
        g_ibs_uf=IBSUFDomain(),
        g_ibs_mun=IBSMunDomain(),
        g_trib_regular=TributacaoRegularDomain(),
    )
    ibscbs = IBSCBSDomain(g_ibscbs=grupo)
    tributos = TributosDomain(IBSCBS=ibscbs)
    assert tributos.possui_cbs()
    assert tributos.get_g_cbs() is not None
    assert tributos.possui_ibs_uf()
    assert tributos.get_g_ibs_uf() is not None
    assert tributos.possui_ibs_mun()
    assert tributos.get_g_ibs_mun() is not None
    assert tributos.possui_tributacao_regular()
    assert tributos.get_tributacao_regular() is not None
    assert tributos.get_grupo_ibscbs() is not None

def test_teste_inicializacaoComMonofasia_retornaTrue() -> None:
    tributos = TributosDomain(IBSCBS=IBSCBSDomain(g_ibscbs_mono=MonofasiaDomain()))
    assert tributos.possui_monofasia()
    assert tributos.get_g_ibscbs_mono() is not None

def test_teste_inicializacaoComEstornoCredito_retornaTrue() -> None:
    tributos = TributosDomain(IBSCBS=IBSCBSDomain(g_estorno_cred=EstornoCreditoDomain()))
    assert tributos.possui_estorno_credito()
    assert tributos.get_g_estorno_cred() is not None
