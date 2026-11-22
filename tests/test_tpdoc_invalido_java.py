"""Teste_tpdoc_5_TpDocInvalido — controller/catálogo (pin f1eebd7, sem MockMvc)."""

from __future__ import annotations

import json
import os
from copy import deepcopy
from datetime import date
from pathlib import Path

import pytest

os.environ.setdefault(
    "CALC_DB",
    "/home/garusotec/projects/lynko/libs/calculadora-rtc-regime-regular/.cache/oficial/java/calculadora/db/calculadora-pro.db",
)

from calculadora_rtc_regime_regular.calculadora import ClassificacaoTributariaNaoVinculadaTipoDfeException
from calculadora_rtc_regime_regular.coletor import ErrosCalculoException, ItemCollector
from calculadora_rtc_regime_regular.consultas import TipoDfeNaoEncontradoException
from calculadora_rtc_regime_regular.consumo import CalculadoraService, ObservabilidadeService
from calculadora_rtc_regime_regular.nomenclatura import (
    NomenclaturaIncompativelTipoDfeException,
    NomenclaturaNaoPermitidaTipoDfeException,
    NomenclaturaObrigatoriaNaoInformadaException,
)
from calculadora_rtc_regime_regular.observabilidade import operacao_from_json
from calculadora_rtc_regime_regular.processamento_item import ImpostoSeletivoNaoAdmitidoTipoDfeException

_CACHE = Path(__file__).resolve().parents[1] / ".cache/oficial/java/src/test/resources"
_ENTRADA = "entradas/tpdoc/tpdoc_sem_anexo_000001.json"
_BASE_URL = "http://localhost:8080"
_DATA = date(2026, 1, 1)

pytestmark = pytest.mark.skipif(not os.environ.get("CALC_DB"), reason="CALC_DB ausente")


def _load_operacao() -> object:
    payload = json.loads((_CACHE / _ENTRADA).read_text(encoding="utf-8"))
    return operacao_from_json(payload)


def _erro_catalogo(codigo: str) -> dict[str, str]:
    """Espelha ``ErroService.buscarPorCodigo`` via mapeamento REG no coletor."""
    amostras = {
        "REG-028": TipoDfeNaoEncontradoException(99, _DATA),
        "REG-029": ClassificacaoTributariaNaoVinculadaTipoDfeException(
            "000001", 55, "CBS e IBS"
        ),
        "REG-030": NomenclaturaIncompativelTipoDfeException("NCM", "000001", "NFE"),
        "REG-031": NomenclaturaNaoPermitidaTipoDfeException("000001", "NFCOM"),
        "REG-032": ImpostoSeletivoNaoAdmitidoTipoDfeException(62, "NCM", "24021000"),
        "REG-033": NomenclaturaObrigatoriaNaoInformadaException("000001", "NFSE"),
    }
    exc = amostras[codigo]
    collector = ItemCollector(-1, _BASE_URL)
    collector.add_erro(exc)
    detalhe = collector.get_erros()[0]
    return {"codigo": detalhe.code, "titulo": detalhe.title}


@pytest.fixture(scope="module")
def calc() -> CalculadoraService:
    return CalculadoraService(calculo_ibs_habilitado=True)


@pytest.fixture(scope="module")
def obs() -> ObservabilidadeService:
    return ObservabilidadeService()


def teste_controller_tpDocInexistente(calc: CalculadoraService) -> None:
    operacao = deepcopy(_load_operacao())
    operacao.tp_doc = 99
    with pytest.raises(TipoDfeNaoEncontradoException):
        calc.calcularTributos(operacao)
    problema = ItemCollector(-1, _BASE_URL)
    problema.add_erro(
        TipoDfeNaoEncontradoException(99, operacao.fato_gerador_aplicavel())
    )
    assert problema.get_erros()[0].title == "Tipo de documento fiscal não encontrado"


def teste_controllerObservabilidade_tpDocInexistente(obs: ObservabilidadeService) -> None:
    operacao = deepcopy(_load_operacao())
    operacao.tp_doc = 99
    with pytest.raises(ErrosCalculoException) as excinfo:
        obs.processarOperacao(operacao, _BASE_URL)
    erros = excinfo.value.get_erros()
    assert erros and erros[0].code == "REG-028"


def teste_catalogoErros_REG028() -> None:
    descricao = _erro_catalogo("REG-028")
    assert descricao["titulo"] == "Tipo de documento fiscal não encontrado"


def teste_catalogoErros_novosCodigos() -> None:
    for codigo in ("REG-029", "REG-030", "REG-031", "REG-032", "REG-033"):
        descricao = _erro_catalogo(codigo)
        assert descricao["codigo"] == codigo