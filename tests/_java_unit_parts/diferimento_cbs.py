"""Identidade JUnit: Teste_CalculoCbsIbsService_Diferimento (3 casos surefire)."""

from __future__ import annotations

_FQCN = (
    "br.gov.serpro.rtc.domain.service.calculotributo."
    "Teste_CalculoCbsIbsService_Diferimento"
)
_MOD = "test_diferimento_cbs_java"

_METHODS = (
    "diferimentoDe50PorCento_descontadoUmaVez",
    "diferimentoDe100PorCento_devidoZero",
    "diferimentoParcial_vDifArredondadoUmaVez",
)

JAVA_UNIT_IDENTITY: dict[str, tuple[str, str]] = {
    **{f"{_MOD}::test_{m}": (_FQCN, m) for m in _METHODS},
}