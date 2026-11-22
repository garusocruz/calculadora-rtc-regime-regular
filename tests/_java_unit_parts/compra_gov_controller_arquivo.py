"""Identidade JUnit: CompraGovControllerArquivoTest (surefire)."""

from __future__ import annotations

_FQCN = (
    "br.gov.serpro.rtc.testesintegracao.calculoscorretos.comprasgovernamentais."
    "CompraGovControllerArquivoTest"
)
_MOD = "test_compra_gov_controller_arquivo_java"

JAVA_UNIT_IDENTITY: dict[str, tuple[str, str]] = {
    **{
        f"{_MOD}::test_deveCalcularTributosCompraGovViaEndpoint[deveCalcularTributosCompraGovViaEndpoint(String, String)[{i}]]": (
            _FQCN,
            f"deveCalcularTributosCompraGovViaEndpoint(String, String)[{i}]",
        )
        for i in range(1, 7)
    },
    f"{_MOD}::test_deveFalharComValoresInvalidos[deveFalharComValoresInvalidos(String)[1]]": (
        _FQCN,
        "deveFalharComValoresInvalidos(String)[1]",
    ),
    f"{_MOD}::test_deveFalharComValoresInvalidos[deveFalharComValoresInvalidos(String)[2]]": (
        _FQCN,
        "deveFalharComValoresInvalidos(String)[2]",
    ),
}