"""Identidade JUnit — ``BaseCalculoUnificadaServiceTest``."""

from __future__ import annotations

_FQCN = "br.gov.serpro.rtc.domain.service.basecalculo.BaseCalculoUnificadaServiceTest"
_MOD = "test_base_calculo_unificada_servico_java"

JAVA_UNIT_IDENTITY: dict[str, tuple[str, str]] = {
    f"{_MOD}::test_deveCalcularBCParaNFe": (_FQCN, "deveCalcularBCParaNFe"),
    f"{_MOD}::test_deveLancarExcecaoParaTipoDocumentoInvalidoViaComponentes": (
        _FQCN,
        "deveLancarExcecaoParaTipoDocumentoInvalidoViaComponentes",
    ),
    f"{_MOD}::test_deveLancarExcecaoParaTipoDocumentoInvalido": (
        _FQCN,
        "deveLancarExcecaoParaTipoDocumentoInvalido",
    ),
    f"{_MOD}::test_deveIgnorarCamposNaoAplicaveis": (_FQCN, "deveIgnorarCamposNaoAplicaveis"),
    f"{_MOD}::test_deveTratarNullsComoZero": (_FQCN, "deveTratarNullsComoZero"),
    f"{_MOD}::test_deveRetornarAvisosQuandoCamposIgnorados": (
        _FQCN,
        "deveRetornarAvisosQuandoCamposIgnorados",
    ),
    f"{_MOD}::test_deveCalcularBCNegativa": (_FQCN, "deveCalcularBCNegativa"),
    f"{_MOD}::test_deveCalcularBCParaNFCe": (_FQCN, "deveCalcularBCParaNFCe"),
    f"{_MOD}::test_deveCalcularViaInputDTO": (_FQCN, "deveCalcularViaInputDTO"),
}