"""Identidade JUnit: DadosAbertosControllerTest (53 casos surefire)."""

from __future__ import annotations

_FQCN = "br.gov.serpro.rtc.testesintegracao.dadosabertos.controller.DadosAbertosControllerTest"
_MOD = "test_dados_abertos_controller_java"

_METODOS = (
    "consultarUfs",
    "consultarMunicipiosPorSiglaUf",
    "consultarSituacoesTributariasCbsIbs",
    "consultarClassificacoesTributariasPorIdSituacaoTributaria",
    "listarPorCstImpostoSeletivo",
    "listarPorCstCbsIbs",
    "consultarClassificacoesTributariasCbsIbs",
    "consultarClassificacoesTributariasImpostoSeletivo",
    "listarClassificacoesTributariasPorNbs",
    "consultarSituacoesTributariasImpostoSeletivo",
    "consultarNcm",
    "consultarNbs",
    "listarNbs",
    "listarNbsAplicaveisPorClassificacao",
    "consultarFundamentacoesLegais",
    "consultarAliquotaUniao",
    "consultarAliquotaUf",
    "consultarAliquotaMunicipio",
    "consultarAliquotaUniaoSemAliquotaDefinidaEmLei",
    "consultarAliquotaUfSemAliquotaDefinidaEmLei",
    "consultarAliquotaMunicipioSemAliquotaDefinidaEmLei",
    "consultarValidadeDfeClassificacaoTributaria",
    "consultarClassificacaoTributariaCbsIbsPorCodigoComSucesso",
    "consultarClassificacaoTributariaCbsIbsPorCodigoNaoEncontrado",
    "consultarClassificacaoTributariaCbsIbsPorCodigoValidaEstrutura",
    "consultarClassificacaoTributariaIsPorCodigoComSucesso",
    "consultarClassificacaoTributariaIsPorCodigoNaoEncontrado",
    "consultarCstsComClassificacoesCbsIbsPorSiglaDfe",
    "consultarCstsComClassificacoesIsPorSiglaDfe",
    "consultarCstsComClassificacoesIsSemSiglaDfe",
    "consultarVersao",
    "consultarRedutoresCompraGovernamental",
    "consultarTransferenciasCBS",
    "consultarTransferenciasIBS",
    "consultarNomenclatura",
    "consultarAtoresAgrupados",
)

JAVA_UNIT_IDENTITY: dict[str, tuple[str, str]] = {
    f"{_MOD}::test_{m}": (_FQCN, m) for m in _METODOS
}

_PARAM_JAVA = "quando_consultarValidadeDfeClassificacaoTributariaExigirGrupoIbcCbs"
_PARAM_PY = f"test_{_PARAM_JAVA}"
for i in range(1, 18):
    JAVA_UNIT_IDENTITY[f"{_MOD}::{_PARAM_PY}[{i}]"] = (
        _FQCN,
        f"{_PARAM_JAVA}(String, boolean)[{i}]",
    )