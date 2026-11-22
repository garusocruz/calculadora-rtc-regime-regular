"""Identidade JUnit para MonofasiaDomainTest e IBSCBSTotalDomainTest (surefire)."""

from __future__ import annotations

_MOD = "test_monofasia_totais_java"
_MONOFASIA_FQCN = "br.gov.serpro.rtc.api.model.roc.MonofasiaDomainTest"
_IBSCBS_TOTAL_FQCN = "br.gov.serpro.rtc.api.model.roc.IBSCBSTotalDomainTest"

_MONOFASIA_METHODS = (
    "testGettersMonofasiaPadrao",
    "testGettersMonofasiaRetencao",
    "testGettersMonofasiaDiferimento",
    "testTotalizadoresSemDiferimento",
    "testTotalizadoresComDiferimento",
    "testTotalizadoresZero",
)

JAVA_UNIT_IDENTITY: dict[str, tuple[str, str]] = {
    **{f"{_MOD}::test_{m}": (_MONOFASIA_FQCN, m) for m in _MONOFASIA_METHODS},
    f"{_MOD}::test_testMonofasiaSemTributacaoRegular_DeveConterCamposObrigatoriosZerados": (
        _IBSCBS_TOTAL_FQCN,
        "testMonofasiaSemTributacaoRegular_DeveConterCamposObrigatoriosZerados",
    ),
}