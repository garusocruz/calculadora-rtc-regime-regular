"""Identidade JUnit — consultas NFS-e (Teste_nfse_2 / Teste_nfse_5, validação de query)."""

from __future__ import annotations

_FQCN_2 = "br.gov.serpro.rtc.testesintegracao.nfse.Teste_nfse_2_consultarLocalOperacao"
_FQCN_5 = "br.gov.serpro.rtc.testesintegracao.nfse.Teste_nfse_5_consultarSituacoesClassificacoes"
_MOD = "test_nfse_consultas_java"

JAVA_UNIT_IDENTITY: dict[str, tuple[str, str]] = {
    f"{_MOD}::teste_controller_consultarLocalOperacaoParametroInvalido": (
        _FQCN_2,
        "teste_controller_consultarLocalOperacaoParametroInvalido",
    ),
    f"{_MOD}::teste_controller_consultarLocalOperacaoDataInvalida": (
        _FQCN_2,
        "teste_controller_consultarLocalOperacaoDataInvalida",
    ),
    f"{_MOD}::teste_controller_consultarLocalOperacaoSemParametrosObrigatorios": (
        _FQCN_2,
        "teste_controller_consultarLocalOperacaoSemParametrosObrigatorios",
    ),
    f"{_MOD}::teste_controller_consultarSituacoesClassificacoesSemParametros": (
        _FQCN_5,
        "teste_controller_consultarSituacoesClassificacoesSemParametros",
    ),
    f"{_MOD}::teste_controller_consultarSituacoesClassificacoesDataInvalida": (
        _FQCN_5,
        "teste_controller_consultarSituacoesClassificacoesDataInvalida",
    ),
    f"{_MOD}::teste_controller_consultarSituacoesClassificacoesNbsInvalido": (
        _FQCN_5,
        "teste_controller_consultarSituacoesClassificacoesNbsInvalido",
    ),
}