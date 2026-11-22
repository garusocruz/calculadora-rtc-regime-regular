"""Identidade JUnit: Teste_IBSCBSDomain (surefire)."""

from __future__ import annotations

_FQCN = "br.gov.serpro.rtc.testesunitarios.domain.Teste_IBSCBSDomain"
_MOD = "test_ibscbs_domain_java"

JAVA_UNIT_IDENTITY: dict[str, tuple[str, str]] = {
    "test_ibscbs_domain_java::test_teste_IBSCBSDomainVazio_retornaFalseENull": (_FQCN, "teste_IBSCBSDomainVazio_retornaFalseENull"),
    "test_ibscbs_domain_java::test_teste_IBSCBSDomainComGrupoIBSCBS_retornaDelegates": (_FQCN, "teste_IBSCBSDomainComGrupoIBSCBS_retornaDelegates"),
    "test_ibscbs_domain_java::test_teste_possuiMonofasiaComGIBSCBSMono_retornaTrue": (_FQCN, "teste_possuiMonofasiaComGIBSCBSMono_retornaTrue"),
    "test_ibscbs_domain_java::test_teste_possuiMonofasiaSemGIBSCBSMono_retornaFalse": (_FQCN, "teste_possuiMonofasiaSemGIBSCBSMono_retornaFalse"),
    "test_ibscbs_domain_java::test_teste_possuiEstornoCreditoComEstorno_retornaTrue": (_FQCN, "teste_possuiEstornoCreditoComEstorno_retornaTrue"),
    "test_ibscbs_domain_java::test_teste_possuiEstornoCreditoSemEstorno_retornaFalse": (_FQCN, "teste_possuiEstornoCreditoSemEstorno_retornaFalse"),
    "test_ibscbs_domain_java::test_teste_IBSCBSDomainSemCredPresOper_retornaFalse": (_FQCN, "teste_IBSCBSDomainSemCredPresOper_retornaFalse"),
    "test_ibscbs_domain_java::test_teste_IBSCBSDomainComCredPresOper_retornaTrue": (_FQCN, "teste_IBSCBSDomainComCredPresOper_retornaTrue"),
    "test_ibscbs_domain_java::test_teste_IBSCBSDomainComCredPresOperEValor_retornaTrueEValor": (_FQCN, "teste_IBSCBSDomainComCredPresOperEValor_retornaTrueEValor"),
}
