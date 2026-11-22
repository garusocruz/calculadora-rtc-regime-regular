"""Identidade JUnit: Teste_TributosDomain (surefire)."""

from __future__ import annotations

_FQCN = "br.gov.serpro.rtc.testesunitarios.domain.Teste_TributosDomain"
_MOD = "test_tributos_domain_java"

JAVA_UNIT_IDENTITY: dict[str, tuple[str, str]] = {
    "test_tributos_domain_java::test_teste_inicializacaoSemImpostoSeletivo_retornaFalse": (_FQCN, "teste_inicializacaoSemImpostoSeletivo_retornaFalse"),
    "test_tributos_domain_java::test_teste_inicializacaoComImpostoSeletivo_retornaTrue": (_FQCN, "teste_inicializacaoComImpostoSeletivo_retornaTrue"),
    "test_tributos_domain_java::test_teste_inicializacaoSemIBSCBS_retornaDefaultsNullEZero": (_FQCN, "teste_inicializacaoSemIBSCBS_retornaDefaultsNullEZero"),
    "test_tributos_domain_java::test_teste_inicializacaoComIBSCBSComGrupo_retornaDelegates": (_FQCN, "teste_inicializacaoComIBSCBSComGrupo_retornaDelegates"),
    "test_tributos_domain_java::test_teste_inicializacaoComMonofasia_retornaTrue": (_FQCN, "teste_inicializacaoComMonofasia_retornaTrue"),
    "test_tributos_domain_java::test_teste_inicializacaoComEstornoCredito_retornaTrue": (_FQCN, "teste_inicializacaoComEstornoCredito_retornaTrue"),
}
