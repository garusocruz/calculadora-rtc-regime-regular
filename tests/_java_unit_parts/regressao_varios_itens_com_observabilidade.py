"""Identidade JUnit: TesteRegressaoVariosItensComObservabilidade (surefire)."""

from __future__ import annotations

_FQCN = (
    "br.gov.serpro.rtc.testesintegracao.calculoscorretos.regressao."
    "TesteRegressaoVariosItensComObservabilidade"
)
_MOD = "test_regressao_varios_itens_com_observabilidade_java"

JAVA_UNIT_IDENTITY: dict[str, tuple[str, str]] = {
    f"{_MOD}::test_testRegressaoCalculoVariosItens": (
        _FQCN,
        "testRegressaoCalculoVariosItens",
    ),
}