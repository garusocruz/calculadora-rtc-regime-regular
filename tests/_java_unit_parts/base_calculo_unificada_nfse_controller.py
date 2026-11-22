"""Identidade JUnit: Teste_BaseCalculoUnificadaNfse_Controller (surefire)."""

from __future__ import annotations

_FQCN = "br.gov.serpro.rtc.testesintegracao.basecalculo.Teste_BaseCalculoUnificadaNfse_Controller"
_MOD = "test_base_calculo_unificada_nfse_controller_java"

_METH = (
    "cenario1_comum_nao_optante",
    "cenario2_salaoParceiro_nao_optante",
    "cenario3_locacao_nao_optante",
    "cenario4_baseNegativa",
    "cenario5_locacao_optante_com_erro",
    "cenario6_salaoParceiro_regAp3",
    "cenario7_salaoParceiro_docTipo102",
    "cenario8_salaoParceiro_docTipo102_e_9",
    "camposZerados",
    "ano2027_pisCofinsForaVigencia",
    "ano2033_issqnExtinto",
    "e1534_somaAjustesExcedeServico",
    "regApObrigatorio",
    "tipo199SemDescricao",
    "tipo199ComDescricao",
    "camposNulos_tratadosComoZero",
    "cenario_sucesso_comum_optante_regAp1",
    "cenario_sucesso_comum_optante_regAp2_docTipo9",
    "cenario_sucesso_salaoParceiro_regAp1_docTipo9",
    "cenario_sucesso_optante_pendente",
    "cenario_sucesso_locacao_optante_regAp1_vs_2",
    "cenario_sucesso_todos_cinzeros",
    "cenario_sucesso_multiplos_docs",
    "cenario_sucesso_locacao_optante_docs_ignored",
    "cenario_sucesso_tipo0_ajuste",
    "cenario_sucesso_arredondamento_3_decimais",
)

JAVA_UNIT_IDENTITY: dict[str, tuple[str, str]] = {
    f"{_MOD}::teste_{m}": (_FQCN, m) for m in _METH
}