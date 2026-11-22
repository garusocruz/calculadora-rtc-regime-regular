"""Identidade JUnit: Teste_BaseCalculoIS_Controller (surefire, sem HTTP)."""

from __future__ import annotations

_FQCN = "br.gov.serpro.rtc.testesintegracao.basecalculo.Teste_BaseCalculoIS_Controller"
_MOD = "test_base_calculo_is_controller_java"

JAVA_UNIT_IDENTITY: dict[str, tuple[str, str]] = {
    f"{_MOD}::teste_calculoBasicoComSucesso": (_FQCN, "teste_calculoBasicoComSucesso"),
    f"{_MOD}::teste_todosCamposQueIntegram_SemImpostoSeletivo": (
        _FQCN,
        "teste_todosCamposQueIntegram_SemImpostoSeletivo",
    ),
    f"{_MOD}::teste_todosCamposQueNaoIntegram_ComBonificacaoEDevolucao": (
        _FQCN,
        "teste_todosCamposQueNaoIntegram_ComBonificacaoEDevolucao",
    ),
    f"{_MOD}::teste_valoresZeroRetornaZero": (_FQCN, "teste_valoresZeroRetornaZero"),
    f"{_MOD}::teste_bonificacaoReduzBase_Art417": (_FQCN, "teste_bonificacaoReduzBase_Art417"),
    f"{_MOD}::teste_devolucaoVendasReduzBase_Art418": (_FQCN, "teste_devolucaoVendasReduzBase_Art418"),
    f"{_MOD}::teste_bonificacaoEDevolucaoJuntos": (_FQCN, "teste_bonificacaoEDevolucaoJuntos"),
}