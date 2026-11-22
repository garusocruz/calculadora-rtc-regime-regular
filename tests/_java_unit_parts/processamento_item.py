"""Identidade JUnit: ``ProcessamentoItemServiceTest``."""

from __future__ import annotations

_FQCN = "br.gov.serpro.rtc.domain.service.ProcessamentoItemServiceTest"
_MOD = "test_processamento_item_servico_java"


def _k(sufixo: str) -> str:
    return f"{_MOD}::test_{sufixo}"


JAVA_UNIT_IDENTITY: dict[str, tuple[str, str]] = {
    _k("deve_lancar_erro_quando_quantidade_nao_informada"): (
        _FQCN,
        "deveLancarErroQuandoQuantidadeNaoInformada",
    ),
    _k("deve_lancar_erro_quando_quantidade_igual_a_zero"): (
        _FQCN,
        "deveLancarErroQuandoQuantidadeIgualAZero",
    ),
    _k("deve_lancar_erro_quando_quantidade_menor_que_zero"): (
        _FQCN,
        "deveLancarErroQuandoQuantidadeMenorQueZero",
    ),
    _k("deve_lancar_erro_quando_unidade_nao_informada"): (
        _FQCN,
        "deveLancarErroQuandoUnidadeNaoInformada",
    ),
    _k("nao_deve_criticar_unidade_diferente_da_aliquota"): (
        _FQCN,
        "naoDeveCriticarUnidadeDiferenteDaAliquota",
    ),
    _k("nao_deve_lancar_erro_quando_nao_houver_aliquota_ad_rem"): (
        _FQCN,
        "naoDeveLancarErroQuandoNaoHouverAliquotaAdRem",
    ),
    _k("nao_deve_lancar_erro_quando_tudo_valido"): (_FQCN, "naoDeveLancarErroQuandoTudoValido"),
    _k("deve_calcular_bc_automaticamente_quando_somente_componentes_informados"): (
        _FQCN,
        "deveCalcularBCAutomaticamenteQuandoSomenteComponentesInformados",
    ),
    _k("deve_rejeitar_bc_divergente_dos_componentes"): (
        _FQCN,
        "deveRejeitarBCDivergenteDosComponentes",
    ),
    _k("deve_aceitar_bc_consistente_com_componentes"): (
        _FQCN,
        "deveAceitarBCConsistenteComComponentes",
    ),
    _k("deve_rejeitar_quando_tp_doc_nao_informado_com_componentes"): (
        _FQCN,
        "deveRejeitarQuandoTpDocNaoInformadoComComponentes",
    ),
    _k("deve_rejeitar_quando_tp_doc_invalido_com_componentes"): (
        _FQCN,
        "deveRejeitarQuandoTpDocInvalidoComComponentes",
    ),
    _k("deve_manter_comportamento_legado_quando_sem_componentes"): (
        _FQCN,
        "deveManterComportamentoLegadoQuandoSemComponentes",
    ),
    _k("deve_calcular_base_is_automaticamente_quando_imposto_seletivo_informado_sem_base_is"): (
        _FQCN,
        "deveCalcularBaseISAutomaticamenteQuandoImpostoSeletivoInformadoSemBaseIS",
    ),
    _k("deve_lancar_excecao_quando_base_is_declarada_inconsistente_com_componentes"): (
        _FQCN,
        "deveLancarExcecaoQuandoBaseISDeclaradaInconsistenteComComponentes",
    ),
    _k("deve_aceitar_quando_base_is_declarada_consistente_com_componentes"): (
        _FQCN,
        "deveAceitarQuandoBaseISDeclaradaConsistenteComComponentes",
    ),
}