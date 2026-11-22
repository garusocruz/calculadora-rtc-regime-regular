"""Identidade JUnit: CalculadoraServiceTest (classname surefire)."""

from __future__ import annotations

_FQCN = "br.gov.serpro.rtc.domain.service.CalculadoraServiceTest"
_MOD = "test_calculadora_service_java"

JAVA_UNIT_IDENTITY: dict[str, tuple[str, str]] = {
    f"{_MOD}::test_deveRetornarNullQuandoDataAnteriorA2027": (
        _FQCN,
        "deveRetornarNullQuandoDataAnteriorA2027",
    ),
    f"{_MOD}::test_deveRetornarCasoAliquotasFicticiasParaQualquerData[1]": (
        _FQCN,
        "deveRetornarCasoAliquotasFicticiasParaQualquerData(String)[1]",
    ),
    f"{_MOD}::test_deveRetornarCasoAliquotasFicticiasParaQualquerData[2]": (
        _FQCN,
        "deveRetornarCasoAliquotasFicticiasParaQualquerData(String)[2]",
    ),
    f"{_MOD}::test_deveRetornarCasoAliquotasFicticiasParaQualquerData[3]": (
        _FQCN,
        "deveRetornarCasoAliquotasFicticiasParaQualquerData(String)[3]",
    ),
    f"{_MOD}::test_deveRetornarCasoImpostoSeletivo": (
        _FQCN,
        "deveRetornarCasoImpostoSeletivo",
    ),
    f"{_MOD}::test_deveRetornarCasoGeral": (_FQCN, "deveRetornarCasoGeral"),
}