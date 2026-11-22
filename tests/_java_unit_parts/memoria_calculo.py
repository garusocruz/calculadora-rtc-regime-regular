"""Identidade JUnit — ``MemoriaCalculoServiceTest``."""

from __future__ import annotations

_FQCN = "br.gov.serpro.rtc.domain.service.MemoriaCalculoServiceTest"
_MOD = "test_memoria_calculo_servico_java"

JAVA_UNIT_IDENTITY: dict[str, tuple[str, str]] = {
    f"{_MOD}::test_deveFormatarNuloComoZero": (_FQCN, "deveFormatarNuloComoZero"),
    f"{_MOD}::test_deveFormatarMoedaEmPtBr[1]": (
        _FQCN,
        "deveFormatarMoedaEmPtBr(BigDecimal, String)[1]",
    ),
    f"{_MOD}::test_deveFormatarMoedaEmPtBr[2]": (
        _FQCN,
        "deveFormatarMoedaEmPtBr(BigDecimal, String)[2]",
    ),
    f"{_MOD}::test_deveFormatarPercentualEmPtBr[1]": (
        _FQCN,
        "deveFormatarPercentualEmPtBr(BigDecimal, String)[1]",
    ),
    f"{_MOD}::test_deveFormatarPercentualEmPtBr[2]": (
        _FQCN,
        "deveFormatarPercentualEmPtBr(BigDecimal, String)[2]",
    ),
    f"{_MOD}::test_deveFormatarPercentualEmPtBr[3]": (
        _FQCN,
        "deveFormatarPercentualEmPtBr(BigDecimal, String)[3]",
    ),
}