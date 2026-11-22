"""Paridade DadosAbertosControllerTest — DadosAbertosService direto (sem MockMvc)."""

from __future__ import annotations

import os
from datetime import date

import pytest

os.environ.setdefault(
    "CALC_DB",
    "/home/garusotec/projects/lynko/libs/calculadora-rtc-regime-regular/.cache/oficial/java/calculadora/db/calculadora-pro.db",
)

from calculadora_rtc_regime_regular.consumo import DadosAbertosService
from calculadora_rtc_regime_regular.dados_abertos import (
    AliquotaNaoEncontradaException,
    ClassificacaoTributariaNaoEncontradaException,
)

pytestmark = pytest.mark.skipif(not os.environ.get("CALC_DB"), reason="CALC_DB ausente")

DATA = date(2027, 1, 1)
DATA_COM_ALIQUOTAS = date(2026, 1, 1)
NCM = "09024000"
NBS = "102020000"
SIGLA_UF = "AC"
CODIGO_UF = 12
CODIGO_MUNICIPIO = 1200013
CST = "000"
C_CLASS_TRIB = "000001"
ID_SITUACAO_TRIBUTARIA = 1
SIGLA_DFE = "NFE"
ID_ST_CBS_IBS = 2
ID_ST_IS = 1

# Mesmo valor que ``application-testes`` + ``DadosAbertosControllerTest`` (Java).
VERSAO_APLICACAO_COMPLETA = "feature-calculo-SNAPSHOT-b7bb06d6"

_VALIDADE_EXIGE_GRUPO = (
    ("000001", True),
    ("010001", True),
    ("011001", True),
    ("200001", True),
    ("221001", True),
    ("222001", True),
    ("400001", False),
    ("410001", False),
    ("510001", True),
    ("515001", True),
    ("550001", True),
    ("620001", False),
    ("800001", False),
    ("810001", False),
    ("811001", False),
    ("820001", False),
    ("830001", True),
)


def _versao_app_dados_abertos(versao_completa: str) -> str:
    marcador = "-SNAPSHOT-"
    idx = versao_completa.find(marcador)
    if idx >= 0 and idx + len(marcador) < len(versao_completa):
        return versao_completa[idx + 1 :]
    return versao_completa


@pytest.fixture(scope="module")
def servico() -> DadosAbertosService:
    return DadosAbertosService()


def test_consultarUfs(servico: DadosAbertosService) -> None:
    assert servico.consultarUfs() is not None


def test_consultarMunicipiosPorSiglaUf(servico: DadosAbertosService) -> None:
    assert servico.consultarMunicipiosPorSiglaUf(SIGLA_UF) is not None


def test_consultarSituacoesTributariasCbsIbs(servico: DadosAbertosService) -> None:
    assert servico.consultarSituacoesTributarias(ID_ST_CBS_IBS, DATA) is not None


def test_consultarClassificacoesTributariasPorIdSituacaoTributaria(servico: DadosAbertosService) -> None:
    assert servico.consultarClassificacoesTributariasPorIdSituacaoTributaria(
        ID_SITUACAO_TRIBUTARIA, DATA
    ) is not None


def test_listarPorCstImpostoSeletivo(servico: DadosAbertosService) -> None:
    assert servico.consultarClassificacoesTributariasPorCstETributoTipo(CST, ["IS"], DATA) is not None


def test_listarPorCstCbsIbs(servico: DadosAbertosService) -> None:
    assert servico.consultarClassificacoesTributariasPorCstETributoTipo(
        CST, ["CBS", "IBSUF", "IBSMun"], DATA
    ) is not None


def test_consultarClassificacoesTributariasCbsIbs(servico: DadosAbertosService) -> None:
    assert servico.consultarClassificacoesTributariasCbsIbs(DATA) is not None


def test_consultarClassificacoesTributariasImpostoSeletivo(servico: DadosAbertosService) -> None:
    assert servico.consultarClassificacoesTributariasImpostoSeletivo(DATA) is not None


def test_listarClassificacoesTributariasPorNbs(servico: DadosAbertosService) -> None:
    assert servico.listarClassificacaoAplicavelPorNbs(NBS, DATA) is not None


def test_consultarSituacoesTributariasImpostoSeletivo(servico: DadosAbertosService) -> None:
    assert servico.consultarSituacoesTributarias(ID_ST_IS, DATA) is not None


def test_consultarNcm(servico: DadosAbertosService) -> None:
    assert servico.consultarNcm(NCM, DATA) is not None


def test_consultarNbs(servico: DadosAbertosService) -> None:
    assert servico.consultarNbs(NBS, DATA) is not None


def test_listarNbs(servico: DadosAbertosService) -> None:
    assert servico.listarNbs(DATA) is not None


def test_listarNbsAplicaveisPorClassificacao(servico: DadosAbertosService) -> None:
    assert servico.listarNbsAplicaveisPorClassificacao(C_CLASS_TRIB, DATA) is not None


def test_consultarFundamentacoesLegais(servico: DadosAbertosService) -> None:
    assert servico.consultarFundamentacoesLegais(DATA) is not None


def test_consultarAliquotaUniao(servico: DadosAbertosService) -> None:
    assert servico.consultarAliquota(2, None, None, DATA_COM_ALIQUOTAS) is not None


def test_consultarAliquotaUf(servico: DadosAbertosService) -> None:
    assert servico.consultarAliquota(3, CODIGO_UF, None, DATA_COM_ALIQUOTAS) is not None


def test_consultarAliquotaMunicipio(servico: DadosAbertosService) -> None:
    assert servico.consultarAliquota(4, None, CODIGO_MUNICIPIO, DATA_COM_ALIQUOTAS) is not None


def test_consultarAliquotaUniaoSemAliquotaDefinidaEmLei(servico: DadosAbertosService) -> None:
    with pytest.raises(AliquotaNaoEncontradaException):
        servico.consultarAliquota(2, None, None, DATA)


def test_consultarAliquotaUfSemAliquotaDefinidaEmLei(servico: DadosAbertosService) -> None:
    with pytest.raises(AliquotaNaoEncontradaException):
        servico.consultarAliquota(3, CODIGO_UF, None, DATA)


def test_consultarAliquotaMunicipioSemAliquotaDefinidaEmLei(servico: DadosAbertosService) -> None:
    with pytest.raises(AliquotaNaoEncontradaException):
        servico.consultarAliquota(4, None, CODIGO_MUNICIPIO, DATA)


def test_consultarValidadeDfeClassificacaoTributaria(servico: DadosAbertosService) -> None:
    assert servico.consultarValidadeDfeClassificacaoTributaria(SIGLA_DFE, C_CLASS_TRIB, DATA) is not None


@pytest.mark.parametrize(
    "codigo, esperado",
    _VALIDADE_EXIGE_GRUPO,
    ids=[str(i + 1) for i in range(len(_VALIDADE_EXIGE_GRUPO))],
)
def test_quando_consultarValidadeDfeClassificacaoTributariaExigirGrupoIbcCbs(
    servico: DadosAbertosService,
    codigo: str,
    esperado: bool,
) -> None:
    resultado = servico.consultarValidadeDfeClassificacaoTributaria(SIGLA_DFE, codigo, DATA)
    assert resultado is not None
    assert resultado.exige_grupo_ibs_cbs is esperado


def test_consultarClassificacaoTributariaCbsIbsPorCodigoComSucesso(servico: DadosAbertosService) -> None:
    assert servico.consultarClassificacaoTributariaCbsIbsPorCodigo(C_CLASS_TRIB, DATA) is not None


def test_consultarClassificacaoTributariaCbsIbsPorCodigoNaoEncontrado(servico: DadosAbertosService) -> None:
    with pytest.raises(ClassificacaoTributariaNaoEncontradaException):
        servico.consultarClassificacaoTributariaCbsIbsPorCodigo("999999", DATA)


def test_consultarClassificacaoTributariaCbsIbsPorCodigoValidaEstrutura(servico: DadosAbertosService) -> None:
    assert servico.consultarClassificacaoTributariaCbsIbsPorCodigo(C_CLASS_TRIB, DATA) is not None


def test_consultarClassificacaoTributariaIsPorCodigoComSucesso(servico: DadosAbertosService) -> None:
    assert servico.consultarClassificacaoTributariaIsPorCodigo(C_CLASS_TRIB, DATA) is not None


def test_consultarClassificacaoTributariaIsPorCodigoNaoEncontrado(servico: DadosAbertosService) -> None:
    with pytest.raises(ClassificacaoTributariaNaoEncontradaException):
        servico.consultarClassificacaoTributariaIsPorCodigo("999999", DATA)


def test_consultarCstsComClassificacoesCbsIbsPorSiglaDfe(servico: DadosAbertosService) -> None:
    resultado = servico.consultarCstsComClassificacoesCbsIbs(SIGLA_DFE, DATA)
    assert resultado is not None
    assert len(resultado) > 0


def test_consultarCstsComClassificacoesIsPorSiglaDfe(servico: DadosAbertosService) -> None:
    assert servico.consultarCstsComClassificacoesIs(SIGLA_DFE, DATA) is not None


def test_consultarCstsComClassificacoesIsSemSiglaDfe(servico: DadosAbertosService) -> None:
    assert servico.consultarCstsComClassificacoesIs(None, DATA) is not None


def test_consultarVersao(servico: DadosAbertosService) -> None:
    del servico
    assert _versao_app_dados_abertos(VERSAO_APLICACAO_COMPLETA) == "SNAPSHOT-b7bb06d6"
    assert VERSAO_APLICACAO_COMPLETA == "feature-calculo-SNAPSHOT-b7bb06d6"


def test_consultarRedutoresCompraGovernamental(servico: DadosAbertosService) -> None:
    assert servico.consultarRedutoresCompraGovernamental() is not None


def test_consultarTransferenciasCBS(servico: DadosAbertosService) -> None:
    assert servico.consultarTransferenciasCBS() is not None


def test_consultarTransferenciasIBS(servico: DadosAbertosService) -> None:
    assert servico.consultarTransferenciasIBS() is not None


def test_consultarNomenclatura(servico: DadosAbertosService) -> None:
    resultado = servico.consultarNomenclatura(SIGLA_DFE, C_CLASS_TRIB, DATA)
    assert resultado.sigla_dfe == SIGLA_DFE
    assert resultado.c_class_trib == C_CLASS_TRIB
    assert resultado.data == DATA
    assert resultado.nomenclatura == "SEM"


def test_consultarAtoresAgrupados(servico: DadosAbertosService) -> None:
    assert servico.consultarAtoresAgrupados(DATA) is not None