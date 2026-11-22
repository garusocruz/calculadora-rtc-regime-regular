"""Identidade JUnit — ``ComponentesBaseCalculoInputTest`` (ficheiro IntegrationTest)."""

from __future__ import annotations

# O ficheiro chama-se IntegrationTest; a classe Java, e o surefire, são ComponentesBaseCalculoInputTest.
_FQCN = "br.gov.serpro.rtc.api.model.input.ComponentesBaseCalculoInputTest"
_MOD = "test_componentes_base_calculo_input_integration_java"

JAVA_UNIT_IDENTITY: dict[str, tuple[str, str]] = {
    f"{_MOD}::test_deveSerializarECarregarPayloadCenario1_JSON": (
        _FQCN,
        "deveSerializarECarregarPayloadCenario1_JSON",
    ),
    f"{_MOD}::test_deveSerializarECarregarPayloadCenario2_JSON": (
        _FQCN,
        "deveSerializarECarregarPayloadCenario2_JSON",
    ),
    f"{_MOD}::test_deveSerializarECarregarPayloadCenario3_JSON": (
        _FQCN,
        "deveSerializarECarregarPayloadCenario3_JSON",
    ),
    f"{_MOD}::test_deveSerializarECarregarPayloadCenario2Inconsistencia_JSON": (
        _FQCN,
        "deveSerializarECarregarPayloadCenario2Inconsistencia_JSON",
    ),
    f"{_MOD}::test_deveManterComponentesNulosQuandoAusentes": (
        _FQCN,
        "deveManterComponentesNulosQuandoAusentes",
    ),
    f"{_MOD}::test_deveSerializarComponentesComTodosOs15Campos": (
        _FQCN,
        "deveSerializarComponentesComTodosOs15Campos",
    ),
    f"{_MOD}::test_deveSerializarPayloadRetornandoValorCorretoBaseCalculo": (
        _FQCN,
        "deveSerializarPayloadRetornandoValorCorretoBaseCalculo",
    ),
}