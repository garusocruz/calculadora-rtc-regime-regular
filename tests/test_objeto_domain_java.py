"""Paridade com ``Teste_ObjetoDomain`` (domínio ROC)."""

from __future__ import annotations

from decimal import Decimal

from calculadora_rtc_regime_regular.roc import (
    CBSDomain,
    GrupoIBSCBSDomain,
    IBSCBSDomain,
    ImpostoSeletivoDomain,
    ObjetoDomain,
    TributosDomain,
    ZERO,
)

ONE = Decimal(1)
TEN = Decimal(10)

def d(value: str | Decimal) -> Decimal:
    return value if isinstance(value, Decimal) else Decimal(value)

def test_teste_inicializarObjetoDomainVazio_retornaDefaultsEFalse() -> None:
    obj = ObjetoDomain(n_obj=1)
    assert not obj.possui_imposto_seletivo()
    assert obj.get_imposto_seletivo() is None
    assert obj.get_valor_imposto_seletivo() == ZERO
    assert not obj.possui_base_calculo_ibscbs()
    assert obj.get_valor_base_calculo_ibscbs() == ZERO
    assert not obj.possui_cbs()
    assert obj.get_g_cbs() is None
    assert not obj.possui_cred_pres_cbs()
    assert obj.get_cred_pres_cbs() is None
    assert not obj.possui_cred_pres_ibs()
    assert not obj.possui_cred_pres_cond_sus_ibs()
    assert obj.get_v_cred_pres_ibs() == ZERO
    assert obj.get_v_cred_pres_cond_sus_ibs() == ZERO
    assert obj.get_grupo_ibscbs() is None
    assert not obj.possui_ibs_uf()
    assert obj.get_g_ibs_uf() is None
    assert not obj.possui_ibs_mun()
    assert obj.get_g_ibs_mun() is None
    assert not obj.possui_monofasia()
    assert obj.get_g_ibscbs_mono() is None
    assert not obj.possui_tributacao_regular()
    assert obj.get_tributacao_regular() is None
    assert not obj.possui_estorno_credito()
    assert obj.get_g_estorno_cred() is None

def test_teste_objetoDomainComTribCalc_delegaCorretamente() -> None:
    is_dom = ImpostoSeletivoDomain(v_is=d("50"))
    cbs = CBSDomain()
    grupo = GrupoIBSCBSDomain(g_cbs=cbs)
    ibscbs = IBSCBSDomain(g_ibscbs=grupo)
    tributos = TributosDomain(IS=is_dom, IBSCBS=ibscbs)
    obj = ObjetoDomain(n_obj=1, trib_calc=tributos)
    assert obj.possui_imposto_seletivo()
    assert obj.get_imposto_seletivo() is not None
    assert obj.get_valor_imposto_seletivo() == d("50")
    assert obj.possui_cbs()
    assert obj.get_g_cbs() is not None

def test_teste_compareTo_comparaCorretamente() -> None:
    obj1 = ObjetoDomain(n_obj=1)
    obj2 = ObjetoDomain(n_obj=2)
    obj3 = ObjetoDomain(n_obj=1)
    assert obj1 < obj2
    assert obj2 > obj1
    assert (obj1 < obj3) is False and (obj1 > obj3) is False

def test_teste_compareToComNull_objNullMenor() -> None:
    obj_null = ObjetoDomain(n_obj=None)
    obj1 = ObjetoDomain(n_obj=1)
    assert obj_null < obj1
    assert obj1 > obj_null

def test_teste_equalsEHashCode_consideraApenasNumeroDeObj() -> None:
    obj1 = ObjetoDomain(n_obj=1)
    obj2 = ObjetoDomain(n_obj=1, trib_calc=TributosDomain())
    assert obj1 == obj2
    assert hash(obj1) == hash(obj2)
