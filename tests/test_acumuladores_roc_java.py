"""Paridade com reduce.*TotalAccumulatorTest (pin oficial Java)."""

from __future__ import annotations

from decimal import Decimal

from calculadora_rtc_regime_regular.roc import (
    CBSTotalAccumulator,
    CBSTotalDomain,
    CBSDomain,
    DevolucaoTributosDomain,
    DiferimentoDomain,
    IBSCBSCreditoPresumidoDomain,
    IBSMunDomain,
    IBSMunTotalAccumulator,
    IBSMunTotalDomain,
    IBSUFDomain,
    IBSUFTotalAccumulator,
    IBSUFTotalDomain,
    MonofasiaDomain,
    MonofasiaPadraoDomain,
    MonofasiaRetencaoDomain,
    MonofasiaRetidoAnteriormenteDomain,
    MonofasiaTotalAccumulator,
    MonofasiaTotalDomain,
    ZERO,
)

ONE = Decimal(1)
TWO = Decimal(2)
TEN = Decimal(10)


def d(value: str) -> Decimal:
    return Decimal(value)


def _cmp(actual: Decimal, expected: Decimal) -> None:
    assert actual is not None
    assert expected is not None
    assert actual.compare(expected) == 0


def _assert_cbs_total(total: CBSTotalDomain, *expected: Decimal) -> None:
    v_dif, v_dev_trib, v_cbs, v_cred_pres, v_cred_pres_cond_sus = expected
    _cmp(total.v_dif, v_dif)
    _cmp(total.v_dev_trib, v_dev_trib)
    _cmp(total.v_cbs, v_cbs)
    _cmp(total.v_cred_pres, v_cred_pres)
    _cmp(total.v_cred_pres_cond_sus, v_cred_pres_cond_sus)


def _assert_ibs_uf_total(total: IBSUFTotalDomain, v_dif: Decimal, v_dev_trib: Decimal, v_ibs_uf: Decimal) -> None:
    _cmp(total.v_dif, v_dif)
    _cmp(total.v_dev_trib, v_dev_trib)
    _cmp(total.v_ibs_uf, v_ibs_uf)


def _assert_ibs_mun_total(total: IBSMunTotalDomain, v_dif: Decimal, v_dev_trib: Decimal, v_ibs_mun: Decimal) -> None:
    _cmp(total.v_dif, v_dif)
    _cmp(total.v_dev_trib, v_dev_trib)
    _cmp(total.v_ibs_mun, v_ibs_mun)


def _assert_monofasia_total(
    total: MonofasiaTotalDomain,
    v_ibs_mono: Decimal,
    v_cbs_mono: Decimal,
    v_ibs_mono_reten: Decimal,
    v_cbs_mono_reten: Decimal,
    v_ibs_mono_ret: Decimal,
    v_cbs_mono_ret: Decimal,
) -> None:
    _cmp(total.v_ibs_mono, v_ibs_mono)
    _cmp(total.v_cbs_mono, v_cbs_mono)
    _cmp(total.v_ibs_mono_reten, v_ibs_mono_reten)
    _cmp(total.v_cbs_mono_reten, v_cbs_mono_reten)
    _cmp(total.v_ibs_mono_ret, v_ibs_mono_ret)
    _cmp(total.v_cbs_mono_ret, v_cbs_mono_ret)


# --- CBSTotalAccumulatorTest ---


def test_cbs_testDefaultConstructor() -> None:
    _assert_cbs_total(CBSTotalAccumulator().to_cbs_total(), ZERO, ZERO, ZERO, ZERO, ZERO)


def test_cbs_testParameterizedConstructor() -> None:
    _assert_cbs_total(
        CBSTotalAccumulator(ONE, ONE, ONE, ONE, ONE).to_cbs_total(),
        ONE,
        ONE,
        ONE,
        ONE,
        ONE,
    )


def test_cbs_testFromMethodWithNulls() -> None:
    _assert_cbs_total(CBSTotalAccumulator.from_(None, None).to_cbs_total(), ZERO, ZERO, ZERO, ZERO, ZERO)


def test_cbs_testFromMethodWithValues() -> None:
    cbs = CBSDomain(
        g_dif=DiferimentoDomain(v_dif=TEN),
        g_dev_trib=DevolucaoTributosDomain(v_dev_trib=ONE),
        v_cbs=d("5.00"),
    )
    cred = IBSCBSCreditoPresumidoDomain(v_cred_pres=TWO, v_cred_pres_cond_sus=d("3.97"))
    _assert_cbs_total(
        CBSTotalAccumulator.from_(cbs, cred).to_cbs_total(),
        TEN,
        ONE,
        d("5.00"),
        TWO,
        d("3.97"),
    )


def test_cbs_testAddMethod() -> None:
    onze = d("11.00")
    _assert_cbs_total(
        CBSTotalAccumulator(ONE, ONE, ONE, ONE, ONE)
        .add(CBSTotalAccumulator(TEN, TEN, TEN, TEN, TEN))
        .to_cbs_total(),
        onze,
        onze,
        onze,
        onze,
        onze,
    )


def test_cbs_testAddWithNull() -> None:
    _assert_cbs_total(
        CBSTotalAccumulator(ONE, ONE, ONE, ONE, ONE).add(None).to_cbs_total(),
        ONE,
        ONE,
        ONE,
        ONE,
        ONE,
    )


# --- IBSUFTotalAccumulatorTest ---


def test_ibs_uf_testDefaultConstructor() -> None:
    _assert_ibs_uf_total(IBSUFTotalAccumulator().to_ibs_uf_total(), ZERO, ZERO, ZERO)


def test_ibs_uf_testParameterizedConstructor() -> None:
    _assert_ibs_uf_total(IBSUFTotalAccumulator(ONE, ONE, ONE).to_ibs_uf_total(), ONE, ONE, ONE)


def test_ibs_uf_testFromMethodWithNull() -> None:
    _assert_ibs_uf_total(IBSUFTotalAccumulator.from_(None).to_ibs_uf_total(), ZERO, ZERO, ZERO)


def test_ibs_uf_testFromMethodWithValues() -> None:
    ibs_uf = IBSUFDomain(
        g_dif=DiferimentoDomain(v_dif=TEN),
        g_dev_trib=DevolucaoTributosDomain(v_dev_trib=ONE),
        v_ibs_uf=Decimal(5),
    )
    _assert_ibs_uf_total(IBSUFTotalAccumulator.from_(ibs_uf).to_ibs_uf_total(), TEN, ONE, Decimal(5))


def test_ibs_uf_testAddMethod() -> None:
    onze = d("11.00")
    _assert_ibs_uf_total(
        IBSUFTotalAccumulator(ONE, ONE, ONE).add(IBSUFTotalAccumulator(TEN, TEN, TEN)).to_ibs_uf_total(),
        onze,
        onze,
        onze,
    )


def test_ibs_uf_testAddWithNull() -> None:
    _assert_ibs_uf_total(IBSUFTotalAccumulator(ONE, ONE, ONE).add(None).to_ibs_uf_total(), ONE, ONE, ONE)


# --- IBSMunTotalAccumulatorTest ---


def test_ibs_mun_testDefaultConstructor() -> None:
    _assert_ibs_mun_total(IBSMunTotalAccumulator().to_ibs_mun_total(), ZERO, ZERO, ZERO)


def test_ibs_mun_testParameterizedConstructor() -> None:
    _assert_ibs_mun_total(IBSMunTotalAccumulator(ONE, ONE, ONE).to_ibs_mun_total(), ONE, ONE, ONE)


def test_ibs_mun_testFromMethodWithNull() -> None:
    _assert_ibs_mun_total(IBSMunTotalAccumulator.from_(None).to_ibs_mun_total(), ZERO, ZERO, ZERO)


def test_ibs_mun_testFromMethodWithValues() -> None:
    ibs_mun = IBSMunDomain(
        g_dif=DiferimentoDomain(v_dif=TEN),
        g_dev_trib=DevolucaoTributosDomain(v_dev_trib=ONE),
        v_ibs_mun=Decimal(5),
    )
    _assert_ibs_mun_total(IBSMunTotalAccumulator.from_(ibs_mun).to_ibs_mun_total(), TEN, ONE, Decimal(5))


def test_ibs_mun_testAddMethod() -> None:
    onze = d("11.00")
    _assert_ibs_mun_total(
        IBSMunTotalAccumulator(ONE, ONE, ONE).add(IBSMunTotalAccumulator(TEN, TEN, TEN)).to_ibs_mun_total(),
        onze,
        onze,
        onze,
    )


def test_ibs_mun_testAddWithNull() -> None:
    _assert_ibs_mun_total(IBSMunTotalAccumulator(ONE, ONE, ONE).add(None).to_ibs_mun_total(), ONE, ONE, ONE)


# --- MonofasiaTotalAccumulatorTest ---


def test_mono_testDefaultConstructor() -> None:
    _assert_monofasia_total(
        MonofasiaTotalAccumulator().to_monofasia_total(),
        ZERO,
        ZERO,
        ZERO,
        ZERO,
        ZERO,
        ZERO,
    )


def test_mono_testParameterizedConstructor() -> None:
    _assert_monofasia_total(
        MonofasiaTotalAccumulator(ONE, ONE, ONE, ONE, ONE, ONE).to_monofasia_total(),
        ONE,
        ONE,
        ONE,
        ONE,
        ONE,
        ONE,
    )


def test_mono_testFromMethodWithNull() -> None:
    _assert_monofasia_total(
        MonofasiaTotalAccumulator.from_(None).to_monofasia_total(),
        ZERO,
        ZERO,
        ZERO,
        ZERO,
        ZERO,
        ZERO,
    )


def test_mono_testFromMethodWithValues() -> None:
    monofasia = MonofasiaDomain(
        g_mono_padrao=MonofasiaPadraoDomain(v_ibs_mono=TEN, v_cbs_mono=ONE),
        g_mono_reten=MonofasiaRetencaoDomain(v_ibs_mono_reten=TWO, v_cbs_mono_reten=Decimal(3)),
        g_mono_ret=MonofasiaRetidoAnteriormenteDomain(v_ibs_mono_ret=Decimal(4), v_cbs_mono_ret=Decimal(5)),
    )
    _assert_monofasia_total(
        MonofasiaTotalAccumulator.from_(monofasia).to_monofasia_total(),
        TEN,
        ONE,
        TWO,
        Decimal(3),
        Decimal(4),
        Decimal(5),
    )


def test_mono_testAddMethod() -> None:
    onze = d("11.00")
    _assert_monofasia_total(
        MonofasiaTotalAccumulator(ONE, ONE, ONE, ONE, ONE, ONE)
        .add(MonofasiaTotalAccumulator(TEN, TEN, TEN, TEN, TEN, TEN))
        .to_monofasia_total(),
        onze,
        onze,
        onze,
        onze,
        onze,
        onze,
    )


def test_mono_testAddWithNull() -> None:
    _assert_monofasia_total(
        MonofasiaTotalAccumulator(ONE, ONE, ONE, ONE, ONE, ONE).add(None).to_monofasia_total(),
        ONE,
        ONE,
        ONE,
        ONE,
        ONE,
        ONE,
    )