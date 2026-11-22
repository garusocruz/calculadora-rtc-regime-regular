"""Identidade JUnit: Teste_validacao_26_TipoDfeNaoTratadoException (surefire)."""

from __future__ import annotations

_FQCN = (
    "br.gov.serpro.rtc.testesintegracao.validacoes.negocio."
    "Teste_validacao_26_TipoDfeNaoTratadoException"
)
_MOD = "test_teste_validacao_26_tipo_dfe_nao_tratado_exception_java"
_INT = "(int)"

_PARAM_METHODS = (
    "servicoDeveCalcularTributosComSucessoParaDFeTratado",
    "servicoDeveLancarExcecaoParaDFeNaoTratado",
    "apiDeveRetornarOkParaDFeTratado",
    "apiDeveRetornarErro422ParaDFeNaoTratado",
    "observabilidadeServicoDeveProcessarComSucessoParaDFeTratado",
    "observabilidadeServicoDeveLancarExcecaoParaDFeNaoTratado",
    "observabilidadeApiDeveRetornarOkParaDFeTratado",
    "observabilidadeApiDeveRetornarErro422ParaDFeNaoTratado",
)

_COUNTS = {
    "servicoDeveCalcularTributosComSucessoParaDFeTratado": 11,
    "servicoDeveLancarExcecaoParaDFeNaoTratado": 4,
    "apiDeveRetornarOkParaDFeTratado": 11,
    "apiDeveRetornarErro422ParaDFeNaoTratado": 4,
    "observabilidadeServicoDeveProcessarComSucessoParaDFeTratado": 11,
    "observabilidadeServicoDeveLancarExcecaoParaDFeNaoTratado": 4,
    "observabilidadeApiDeveRetornarOkParaDFeTratado": 11,
    "observabilidadeApiDeveRetornarErro422ParaDFeNaoTratado": 4,
}


def _build_identity() -> dict[str, tuple[str, str]]:
    out: dict[str, tuple[str, str]] = {}
    for method in _PARAM_METHODS:
        n = _COUNTS[method]
        for i in range(1, n + 1):
            surefire = f"{method}{_INT}[{i}]"
            out[f"{_MOD}::test_{method}[{surefire}]"] = (_FQCN, surefire)
    return out


JAVA_UNIT_IDENTITY = _build_identity()