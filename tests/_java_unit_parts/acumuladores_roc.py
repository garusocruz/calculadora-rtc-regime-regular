"""Identidade JUnit para acumuladores ROC (reduce.*TotalAccumulatorTest)."""

from __future__ import annotations

_MOD = "test_acumuladores_roc_java"

_CBS_FQCN = "br.gov.serpro.rtc.api.model.roc.reduce.CBSTotalAccumulatorTest"
_IBS_UF_FQCN = "br.gov.serpro.rtc.api.model.roc.reduce.IBSUFTotalAccumulatorTest"
_IBS_MUN_FQCN = "br.gov.serpro.rtc.api.model.roc.reduce.IBSMunTotalAccumulatorTest"
_MONO_FQCN = "br.gov.serpro.rtc.api.model.roc.reduce.MonofasiaTotalAccumulatorTest"


def _k(py_suffix: str) -> str:
    return f"{_MOD}::test_{py_suffix}"


def _six(fqcn: str, prefix: str, *, null_method: str) -> dict[str, tuple[str, str]]:
    return {
        _k(f"{prefix}_testDefaultConstructor"): (fqcn, "testDefaultConstructor"),
        _k(f"{prefix}_testParameterizedConstructor"): (fqcn, "testParameterizedConstructor"),
        _k(f"{prefix}_{null_method}"): (fqcn, null_method),
        _k(f"{prefix}_testFromMethodWithValues"): (fqcn, "testFromMethodWithValues"),
        _k(f"{prefix}_testAddMethod"): (fqcn, "testAddMethod"),
        _k(f"{prefix}_testAddWithNull"): (fqcn, "testAddWithNull"),
    }


JAVA_UNIT_IDENTITY: dict[str, tuple[str, str]] = {
    **_six(_CBS_FQCN, "cbs", null_method="testFromMethodWithNulls"),
    **_six(_IBS_UF_FQCN, "ibs_uf", null_method="testFromMethodWithNull"),
    **_six(_IBS_MUN_FQCN, "ibs_mun", null_method="testFromMethodWithNull"),
    **_six(_MONO_FQCN, "mono", null_method="testFromMethodWithNull"),
}