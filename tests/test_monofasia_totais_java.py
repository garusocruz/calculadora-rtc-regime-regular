"""Paridade com MonofasiaDomainTest e IBSCBSTotalDomainTest (roc)."""

from __future__ import annotations

from decimal import Decimal

from calculadora_rtc_regime_regular.roc import (
    IBSCBSDomain,
    IBSCBSTotalDomain,
    MonofasiaDiferimentoDomain,
    MonofasiaDomain,
    MonofasiaPadraoDomain,
    MonofasiaRetencaoDomain,
    ObjetoDomain,
    TributosDomain,
    ZERO,
)


def d(value: str) -> Decimal:
    return Decimal(value)


def _cmp(actual: Decimal, expected: Decimal) -> None:
    assert actual.compare(expected) == 0


# --- MonofasiaDomainTest ---


def test_testGettersMonofasiaPadrao() -> None:
    monofasia = MonofasiaDomain(
        g_mono_padrao=MonofasiaPadraoDomain(v_ibs_mono=d("792.50"), v_cbs_mono=d("792.50")),
    )
    _cmp(monofasia.get_v_ibs_mono(), d("792.50"))
    _cmp(monofasia.get_v_cbs_mono(), d("792.50"))
    _cmp(monofasia.get_v_ibs_mono_reten(), ZERO)
    _cmp(monofasia.get_v_cbs_mono_reten(), ZERO)
    _cmp(monofasia.get_v_ibs_mono_dif(), ZERO)
    _cmp(monofasia.get_v_cbs_mono_dif(), ZERO)


def test_testGettersMonofasiaRetencao() -> None:
    monofasia = MonofasiaDomain(
        g_mono_reten=MonofasiaRetencaoDomain(v_ibs_mono_reten=d("82.37"), v_cbs_mono_reten=d("82.37")),
    )
    _cmp(monofasia.get_v_ibs_mono(), ZERO)
    _cmp(monofasia.get_v_cbs_mono(), ZERO)
    _cmp(monofasia.get_v_ibs_mono_reten(), d("82.37"))
    _cmp(monofasia.get_v_cbs_mono_reten(), d("82.37"))


def test_testGettersMonofasiaDiferimento() -> None:
    monofasia = MonofasiaDomain(
        g_mono_dif=MonofasiaDiferimentoDomain(v_ibs_mono_dif=d("100.00"), v_cbs_mono_dif=d("100.00")),
    )
    _cmp(monofasia.get_v_ibs_mono_dif(), d("100.00"))
    _cmp(monofasia.get_v_cbs_mono_dif(), d("100.00"))


def test_testTotalizadoresSemDiferimento() -> None:
    monofasia = MonofasiaDomain(
        g_mono_padrao=MonofasiaPadraoDomain(v_ibs_mono=d("792.50"), v_cbs_mono=d("792.50")),
        g_mono_reten=MonofasiaRetencaoDomain(v_ibs_mono_reten=d("82.37"), v_cbs_mono_reten=d("82.37")),
        v_tot_ibs_mono_item=d("874.87"),
        v_tot_cbs_mono_item=d("874.87"),
    )
    _cmp(monofasia.get_v_tot_ibs_mono_item(), d("874.87"))
    _cmp(monofasia.get_v_tot_cbs_mono_item(), d("874.87"))


def test_testTotalizadoresComDiferimento() -> None:
    monofasia = MonofasiaDomain(
        g_mono_padrao=MonofasiaPadraoDomain(v_ibs_mono=d("792.50"), v_cbs_mono=d("792.50")),
        g_mono_reten=MonofasiaRetencaoDomain(v_ibs_mono_reten=d("82.37"), v_cbs_mono_reten=d("82.37")),
        g_mono_dif=MonofasiaDiferimentoDomain(v_ibs_mono_dif=d("50.00"), v_cbs_mono_dif=d("50.00")),
        v_tot_ibs_mono_item=d("824.87"),
        v_tot_cbs_mono_item=d("824.87"),
    )
    _cmp(monofasia.get_v_tot_ibs_mono_item(), d("824.87"))
    _cmp(monofasia.get_v_tot_cbs_mono_item(), d("824.87"))


def test_testTotalizadoresZero() -> None:
    monofasia = MonofasiaDomain()
    _cmp(monofasia.get_v_tot_ibs_mono_item(), ZERO)
    _cmp(monofasia.get_v_tot_cbs_mono_item(), ZERO)


# --- IBSCBSTotalDomainTest ---


def test_testMonofasiaSemTributacaoRegular_DeveConterCamposObrigatoriosZerados() -> None:
    objeto = ObjetoDomain(
        n_obj=1,
        trib_calc=TributosDomain(
            IBSCBS=IBSCBSDomain(
                CST="620",
                c_class_trib="620001",
                g_ibscbs_mono=MonofasiaDomain(
                    g_mono_padrao=MonofasiaPadraoDomain(
                        q_bc_mono=d("1000"),
                        ad_rem_ibs=d("0.7925"),
                        ad_rem_cbs=d("0.7925"),
                        v_ibs_mono=d("792.50"),
                        v_cbs_mono=d("792.50"),
                    ),
                    v_tot_ibs_mono_item=d("792.50"),
                    v_tot_cbs_mono_item=d("792.50"),
                ),
            ),
        ),
    )
    total = IBSCBSTotalDomain.create([objeto])
    assert total is not None
    _cmp(total.v_bc_ibscbs or ZERO, ZERO)

    assert total.g_ibs is not None
    _cmp(total.g_ibs.v_ibs or ZERO, ZERO)
    _cmp(total.g_ibs.v_cred_pres or ZERO, ZERO)
    _cmp(total.g_ibs.v_cred_pres_cond_sus or ZERO, ZERO)

    assert total.g_ibs.g_ibs_uf is not None
    _cmp(total.g_ibs.g_ibs_uf.v_dif, ZERO)
    _cmp(total.g_ibs.g_ibs_uf.v_dev_trib, ZERO)
    _cmp(total.g_ibs.g_ibs_uf.v_ibs_uf, ZERO)

    assert total.g_ibs.g_ibs_mun is not None
    _cmp(total.g_ibs.g_ibs_mun.v_dif, ZERO)
    _cmp(total.g_ibs.g_ibs_mun.v_dev_trib, ZERO)
    _cmp(total.g_ibs.g_ibs_mun.v_ibs_mun, ZERO)

    assert total.g_cbs is not None
    _cmp(total.g_cbs.v_dif, ZERO)
    _cmp(total.g_cbs.v_dev_trib, ZERO)
    _cmp(total.g_cbs.v_cbs, ZERO)
    _cmp(total.g_cbs.v_cred_pres, ZERO)
    _cmp(total.g_cbs.v_cred_pres_cond_sus, ZERO)

    assert total.g_mono is not None
    _cmp(total.g_mono.v_ibs_mono, d("792.50"))
    _cmp(total.g_mono.v_cbs_mono, d("792.50"))