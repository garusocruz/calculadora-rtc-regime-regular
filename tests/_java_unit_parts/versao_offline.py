"""Identidade JUnit — VersaoOfflineOutputTest (63) e Teste_VersaoOfflineService (13)."""

from __future__ import annotations

_FQCN_OUTPUT = "br.gov.serpro.rtc.api.model.output.versaooffline.VersaoOfflineOutputTest"
_FQCN_SERVICE = "br.gov.serpro.rtc.testesunitarios.service.Teste_VersaoOfflineService"
_MOD = "test_versao_offline_java"

JAVA_UNIT_IDENTITY: dict[str, tuple[str, str]] = {
    f"{_MOD}::test_deveRetornarTudoAtualizadoQuandoVersoesIguais": (
        _FQCN_OUTPUT,
        "deveRetornarTudoAtualizadoQuandoVersoesIguais",
    ),
    f"{_MOD}::test_deveRetornarDesatualizadoQuandoVersoesDiferentes": (
        _FQCN_OUTPUT,
        "deveRetornarDesatualizadoQuandoVersoesDiferentes",
    ),
    f"{_MOD}::test_deveRetornarTudoDesatualizadoQuandoRemotaNula": (
        _FQCN_OUTPUT,
        "deveRetornarTudoDesatualizadoQuandoRemotaNula",
    ),
    f"{_MOD}::test_deveRetornarNaoAtualizadaQuandoVersaoAppLocalNull": (
        _FQCN_OUTPUT,
        "deveRetornarNaoAtualizadaQuandoVersaoAppLocalNull",
    ),
    f"{_MOD}::test_naoDeveGerarFalsePositiveQuandoSemverNullEmAmbosLados": (
        _FQCN_OUTPUT,
        "naoDeveGerarFalsePositiveQuandoSemverNullEmAmbosLados",
    ),
    f"{_MOD}::test_deveReconhecerNumerosGrandes": (
        _FQCN_OUTPUT,
        "deveReconhecerNumerosGrandes",
    ),
    f"{_MOD}::test_leAVersaoPublicadaPelaInstalacaoOnlineECompara": (
        _FQCN_SERVICE,
        "leAVersaoPublicadaPelaInstalacaoOnlineECompara",
    ),
    f"{_MOD}::test_campoDesconhecidoNaRespostaRemotaNaoImpedeALeitura": (
        _FQCN_SERVICE,
        "campoDesconhecidoNaRespostaRemotaNaoImpedeALeitura",
    ),
    f"{_MOD}::test_naSubidaAFalhaDaConsultaRemotaAcionaNovaTentativa": (
        _FQCN_SERVICE,
        "naSubidaAFalhaDaConsultaRemotaAcionaNovaTentativa",
    ),
    f"{_MOD}::test_naSubidaAComparacaoERegistradaQuandoAConsultaResponde": (
        _FQCN_SERVICE,
        "naSubidaAComparacaoERegistradaQuandoAConsultaResponde",
    ),
    f"{_MOD}::test_instalacaoOnlineQueNaoRespondeEsgotaOTempoLimiteDeLeitura": (
        _FQCN_SERVICE,
        "instalacaoOnlineQueNaoRespondeEsgotaOTempoLimiteDeLeitura",
    ),
    f"{_MOD}::test_conexaoRecusadaDevolveComparacaoSemVersaoRemota": (
        _FQCN_SERVICE,
        "conexaoRecusadaDevolveComparacaoSemVersaoRemota",
    ),
}

for i in range(1, 10):
    JAVA_UNIT_IDENTITY[f"{_MOD}::test_deveExtrairPrefixoIgnorandoSufixo[{i}]"] = (
        _FQCN_OUTPUT,
        f"deveExtrairPrefixoIgnorandoSufixo(String)[{i}]",
    )
for i in range(1, 7):
    JAVA_UNIT_IDENTITY[f"{_MOD}::test_deveReconhecerVersoesValidasSimples[{i}]"] = (
        _FQCN_OUTPUT,
        f"deveReconhecerVersoesValidasSimples(String)[{i}]",
    )
for i in range(1, 20):
    JAVA_UNIT_IDENTITY[f"{_MOD}::test_deveReconhecerVersoesValidasComplexas[{i}]"] = (
        _FQCN_OUTPUT,
        f"deveReconhecerVersoesValidasComplexas(String)[{i}]",
    )
for i in range(1, 4):
    JAVA_UNIT_IDENTITY[f"{_MOD}::test_deveRejeitarZerosAEsquerda[{i}]"] = (
        _FQCN_OUTPUT,
        f"deveRejeitarZerosAEsquerda(String)[{i}]",
    )
for i in range(1, 21):
    JAVA_UNIT_IDENTITY[f"{_MOD}::test_deveRejeitarStringsSemFormatoSemver[{i}]"] = (
        _FQCN_OUTPUT,
        f"deveRejeitarStringsSemFormatoSemver(String)[{i}]",
    )
for i in range(1, 8):
    JAVA_UNIT_IDENTITY[
        f"{_MOD}::test_falhaDaConsultaRemotaDevolveComparacaoSemVersaoRemota[{i}]"
    ] = (
        _FQCN_SERVICE,
        f"falhaDaConsultaRemotaDevolveComparacaoSemVersaoRemota(String, ResponseCreator)[{i}]",
    )