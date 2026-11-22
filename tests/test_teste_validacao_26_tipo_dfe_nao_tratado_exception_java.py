"""Paridade Teste_validacao_26_TipoDfeNaoTratadoException — Calculadora/Observabilidade (sem MockMvc)."""

from __future__ import annotations

import json
import os
from copy import deepcopy
from dataclasses import replace
from pathlib import Path

import pytest

os.environ.setdefault(
    "CALC_DB",
    "/home/garusotec/projects/lynko/libs/calculadora-rtc-regime-regular/.cache/oficial/java/calculadora/db/calculadora-pro.db",
)

from calculadora_rtc_regime_regular.calculadora import CalculadoraService
from calculadora_rtc_regime_regular.coletor import ErrosCalculoException
from calculadora_rtc_regime_regular.consultas import TipoDfeNaoTratadoException
from calculadora_rtc_regime_regular.observabilidade import ObservabilidadeService, operacao_from_json

_RES = Path(__file__).resolve().parents[1] / ".cache/oficial/java/src/test/resources"
_ENTRADA = "entradas/validacoes/Teste_validacao_26_TipoDfeNaoTratadoException.json"
_BASE_URL = "http://localhost:8080"
_ERRO_TITULO = "Tipo de documento fiscal não tratado"

_DFE_TRATADOS = (55, 57, 62, 63, 65, 66, 67, 75, 76, 83, 91)
_DFE_NAO_TRATADOS = (77, 94, 95, 96)

pytestmark = pytest.mark.skipif(not os.environ.get("CALC_DB"), reason="CALC_DB ausente")

_CALC = CalculadoraService()
_OBS = ObservabilidadeService()


def _operacao(tp_doc: int):
    op = operacao_from_json(json.loads((_RES / _ENTRADA).read_text(encoding="utf-8")))
    return replace(deepcopy(op), tp_doc=tp_doc)


def _surefire_ids(method: str, n: int) -> list[str]:
    return [f"{method}(int)[{i}]" for i in range(1, n + 1)]


@pytest.mark.parametrize("indice", range(1, 12), ids=_surefire_ids("servicoDeveCalcularTributosComSucessoParaDFeTratado", 11))
def test_servicoDeveCalcularTributosComSucessoParaDFeTratado(indice: int) -> None:
    _CALC.calcular_tributos(_operacao(_DFE_TRATADOS[indice - 1]))


@pytest.mark.parametrize("indice", range(1, 5), ids=_surefire_ids("servicoDeveLancarExcecaoParaDFeNaoTratado", 4))
def test_servicoDeveLancarExcecaoParaDFeNaoTratado(indice: int) -> None:
    with pytest.raises(TipoDfeNaoTratadoException):
        _CALC.calcular_tributos(_operacao(_DFE_NAO_TRATADOS[indice - 1]))


@pytest.mark.parametrize("indice", range(1, 12), ids=_surefire_ids("apiDeveRetornarOkParaDFeTratado", 11))
def test_apiDeveRetornarOkParaDFeTratado(indice: int) -> None:
    _CALC.calcular_tributos(_operacao(_DFE_TRATADOS[indice - 1]))


@pytest.mark.parametrize("indice", range(1, 5), ids=_surefire_ids("apiDeveRetornarErro422ParaDFeNaoTratado", 4))
def test_apiDeveRetornarErro422ParaDFeNaoTratado(indice: int) -> None:
    with pytest.raises(TipoDfeNaoTratadoException):
        _CALC.calcular_tributos(_operacao(_DFE_NAO_TRATADOS[indice - 1]))


@pytest.mark.parametrize(
    "indice",
    range(1, 12),
    ids=_surefire_ids("observabilidadeServicoDeveProcessarComSucessoParaDFeTratado", 11),
)
def test_observabilidadeServicoDeveProcessarComSucessoParaDFeTratado(indice: int) -> None:
    _OBS.processar_operacao(_operacao(_DFE_TRATADOS[indice - 1]), _BASE_URL)


@pytest.mark.parametrize(
    "indice",
    range(1, 5),
    ids=_surefire_ids("observabilidadeServicoDeveLancarExcecaoParaDFeNaoTratado", 4),
)
def test_observabilidadeServicoDeveLancarExcecaoParaDFeNaoTratado(indice: int) -> None:
    with pytest.raises(ErrosCalculoException) as excinfo:
        _OBS.processar_operacao(_operacao(_DFE_NAO_TRATADOS[indice - 1]), _BASE_URL)
    erros = excinfo.value.get_erros()
    assert len(erros) == 1
    assert erros[0].title == _ERRO_TITULO


@pytest.mark.parametrize(
    "indice",
    range(1, 12),
    ids=_surefire_ids("observabilidadeApiDeveRetornarOkParaDFeTratado", 11),
)
def test_observabilidadeApiDeveRetornarOkParaDFeTratado(indice: int) -> None:
    _OBS.processar_operacao(_operacao(_DFE_TRATADOS[indice - 1]), _BASE_URL)


@pytest.mark.parametrize(
    "indice",
    range(1, 5),
    ids=_surefire_ids("observabilidadeApiDeveRetornarErro422ParaDFeNaoTratado", 4),
)
def test_observabilidadeApiDeveRetornarErro422ParaDFeNaoTratado(indice: int) -> None:
    with pytest.raises(ErrosCalculoException) as excinfo:
        _OBS.processar_operacao(_operacao(_DFE_NAO_TRATADOS[indice - 1]), _BASE_URL)
    erros = excinfo.value.get_erros()
    assert any(e.title == _ERRO_TITULO for e in erros)