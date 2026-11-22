"""Identidade JUnit — Teste_tpdoc_5_TpDocInvalido (4 casos controller/catálogo)."""

from __future__ import annotations

_FQCN = "br.gov.serpro.rtc.testesintegracao.tpdoc.Teste_tpdoc_5_TpDocInvalido"
_MOD = "test_tpdoc_invalido_java"

_METHODS = (
    "teste_controller_tpDocInexistente",
    "teste_controllerObservabilidade_tpDocInexistente",
    "teste_catalogoErros_REG028",
    "teste_catalogoErros_novosCodigos",
)

JAVA_UNIT_IDENTITY: dict[str, tuple[str, str]] = {
    **{f"{_MOD}::{m}": (_FQCN, m) for m in _METHODS},
}