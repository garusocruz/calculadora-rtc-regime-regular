"""Identidade JUnit — ``OperacaoInputTest``."""

from __future__ import annotations

_FQCN = "br.gov.serpro.rtc.api.model.input.OperacaoInputTest"
_MOD = "test_operacao_input_java"

JAVA_UNIT_IDENTITY: dict[str, tuple[str, str]] = {
    f"{_MOD}::test_retornaDataDoDhFatoGeradorQuandoPresente": (
        _FQCN,
        "retornaDataDoDhFatoGeradorQuandoPresente",
    ),
    f"{_MOD}::test_retornaDataDoDataHoraEmissaoQuandoDhFatoGeradorNulo": (
        _FQCN,
        "retornaDataDoDataHoraEmissaoQuandoDhFatoGeradorNulo",
    ),
    f"{_MOD}::test_lancaExcecaoQuandoDatasSaoNulas": (
        _FQCN,
        "lancaExcecaoQuandoDatasSaoNulas",
    ),
}