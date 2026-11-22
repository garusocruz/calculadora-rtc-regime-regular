"""Identidade JUnit — surefire Teste_CasosFixosArredondamento (@DisplayName na classe)."""

from __future__ import annotations

# testcase @classname no XML Java (não é o FQCN da suite).
_CLASSNAME = "Casos fixos de arredondamento do regime geral"
_MOD = "test_casos_fixos_arredondamento_java"

JAVA_UNIT_IDENTITY: dict[str, tuple[str, str]] = {
    f"{_MOD}::test_t1EmpateParaOPar": (_CLASSNAME, "t1EmpateParaOPar"),
    f"{_MOD}::test_t2VIbsSomaDasPartesPublicadas": (_CLASSNAME, "t2VIbsSomaDasPartesPublicadas"),
    f"{_MOD}::test_t3TotaisSomaDosItensPublicados": (_CLASSNAME, "t3TotaisSomaDosItensPublicados"),
    f"{_MOD}::test_t4ValorPelaAliquotaEfetivaPublicada": (_CLASSNAME, "t4ValorPelaAliquotaEfetivaPublicada"),
    f"{_MOD}::test_t5CompraDaUniao": (_CLASSNAME, "t5CompraDaUniao"),
    f"{_MOD}::test_issueTotalCbsSomaDosItens": (_CLASSNAME, "issueTotalCbsSomaDosItens"),
}