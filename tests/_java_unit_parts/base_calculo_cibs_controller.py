"""Identidade JUnit: Teste_BaseCalculoCibs_Controller (surefire, sem HTTP)."""

from __future__ import annotations

_FQCN = "br.gov.serpro.rtc.testesintegracao.basecalculo.Teste_BaseCalculoCibs_Controller"
_MOD = "test_base_calculo_cibs_controller_java"

JAVA_UNIT_IDENTITY: dict[str, tuple[str, str]] = {
    f"{_MOD}::teste_calculoBasicoComSucesso": (_FQCN, "teste_calculoBasicoComSucesso"),
    f"{_MOD}::teste_todosCamposQueIntegram": (_FQCN, "teste_todosCamposQueIntegram"),
    f"{_MOD}::teste_todosCamposQueNaoIntegram": (_FQCN, "teste_todosCamposQueNaoIntegram"),
    f"{_MOD}::teste_valoresZeroRetornaZero": (_FQCN, "teste_valoresZeroRetornaZero"),
    f"{_MOD}::teste_impostoSeletivoIntegraBase": (_FQCN, "teste_impostoSeletivoIntegraBase"),
    f"{_MOD}::teste_novosCamposLC214": (_FQCN, "teste_novosCamposLC214"),
    f"{_MOD}::teste_camposRemovidosNaoExistemMais": (_FQCN, "teste_camposRemovidosNaoExistemMais"),
}