"""Identidade JUnit — ``TesteCalculadoraNcmZero`` (surefire, sem expandir a classe)."""

from __future__ import annotations

_FQCN = "br.gov.serpro.rtc.testesintegracao.calculadora.TesteCalculadoraNcmZero"
_MOD = "test_calculadora_ncm_zero_java"

JAVA_UNIT_IDENTITY: dict[str, tuple[str, str]] = {}

for i in range(1, 39):
    JAVA_UNIT_IDENTITY[f"{_MOD}::teste_ncm_zero_conforme_tipo_documento[{i}]"] = (
        _FQCN,
        f"teste_ncm_zero_conforme_tipo_documento(Integer, String, HttpStatus)[{i}]",
    )
    JAVA_UNIT_IDENTITY[
        f"{_MOD}::teste_ncm_zero_conforme_tipo_documento_observabilidade[{i}]"
    ] = (
        _FQCN,
        "teste_ncm_zero_conforme_tipo_documento_observabilidade"
        f"(Integer, String, HttpStatus, EstadoItemEnum)[{i}]",
    )