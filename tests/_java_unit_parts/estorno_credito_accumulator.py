"""Identidade JUnit: Teste_EstornoCreditoAccumulator (surefire)."""

from __future__ import annotations

_FQCN = "br.gov.serpro.rtc.testesunitarios.domain.Teste_EstornoCreditoAccumulator"
_MOD = "test_estorno_credito_accumulator_java"

JAVA_UNIT_IDENTITY: dict[str, tuple[str, str]] = {
    "test_estorno_credito_accumulator_java::test_teste_construtorPadrao_inicializaComZeros": (_FQCN, "teste_construtorPadrao_inicializaComZeros"),
    "test_estorno_credito_accumulator_java::test_teste_construtorComValores_preservaValores": (_FQCN, "teste_construtorComValores_preservaValores"),
    "test_estorno_credito_accumulator_java::test_teste_construtorComNulls_substituiPorZeros": (_FQCN, "teste_construtorComNulls_substituiPorZeros"),
    "test_estorno_credito_accumulator_java::test_teste_fromNull_inicializaComZeros": (_FQCN, "teste_fromNull_inicializaComZeros"),
    "test_estorno_credito_accumulator_java::test_teste_fromDomain_extraiValores": (_FQCN, "teste_fromDomain_extraiValores"),
    "test_estorno_credito_accumulator_java::test_teste_fromDomainComCamposNulos_inicializaComZeros": (_FQCN, "teste_fromDomainComCamposNulos_inicializaComZeros"),
    "test_estorno_credito_accumulator_java::test_teste_addNull_adicionaZero": (_FQCN, "teste_addNull_adicionaZero"),
    "test_estorno_credito_accumulator_java::test_teste_addValor_somaCorretamente": (_FQCN, "teste_addValor_somaCorretamente"),
}
