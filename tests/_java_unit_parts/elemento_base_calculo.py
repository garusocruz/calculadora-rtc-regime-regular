"""Identidade JUnit — ``ElementoBaseCalculoTest``."""

from __future__ import annotations

_FQCN = "br.gov.serpro.rtc.api.model.input.basecalculo.enumeration.ElementoBaseCalculoTest"
_MOD = "test_elemento_base_calculo_java"

JAVA_UNIT_IDENTITY: dict[str, tuple[str, str]] = {
    f"{_MOD}::test_deveRetornarNullQuandoCampoNaoInformado": (
        _FQCN,
        "deveRetornarNullQuandoCampoNaoInformado",
    ),
    f"{_MOD}::test_deveMapearTodosOs15CamposCorretamente": (
        _FQCN,
        "deveMapearTodosOs15CamposCorretamente",
    ),
}