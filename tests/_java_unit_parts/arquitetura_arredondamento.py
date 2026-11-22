"""Identidade JUnit da política numérica e da cópia única."""

from __future__ import annotations

_MOD = "test_arquitetura_arredondamento_java"
_FQCN_POLITICA = "br.gov.serpro.rtc.testesunitarios.shared.Teste_ArquiteturaArredondamento"
_FQCN_COPIA = "br.gov.serpro.rtc.testesunitarios.shared.Teste_ArredondamentoUtilsCopiaUnica"

JAVA_UNIT_IDENTITY: dict[str, tuple[str, str]] = {
    f"{_MOD}::test_soAClasseDaPoliticaArredonda": (
        _FQCN_POLITICA,
        "soAClasseDaPoliticaArredonda",
    ),
    f"{_MOD}::test_asRegrasPegamOQueDevemPegar": (
        _FQCN_POLITICA,
        "asRegrasPegamOQueDevemPegar",
    ),
    f"{_MOD}::test_classe_eACopiaUnicaDosDoisProjetos": (
        _FQCN_COPIA,
        "classe_eACopiaUnicaDosDoisProjetos",
    ),
}
