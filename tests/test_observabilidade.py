"""Testes de ``ObservabilidadeService`` (pin f1eebd7)."""

from __future__ import annotations

import json
import os
from pathlib import Path

import pytest

os.environ.setdefault(
    "CALC_DB",
    "/home/garusotec/projects/lynko/libs/calculadora-rtc-regime-regular/.cache/oficial/java/calculadora/db/calculadora-pro.db",
)

from calculadora_rtc_regime_regular.coletor import ErrosCalculoException, EstadoItemEnum
from calculadora_rtc_regime_regular.observabilidade import (
    ObservabilidadeService,
    operacao_from_json,
)

_BASE_URL = "http://localhost:8080"
_RES = Path(__file__).resolve().parents[1] / ".cache/oficial/java/src/test/resources"
_ENTRADA = _RES / "entradas/calculoscorretos/observabilidade/entrada.json"
_ERRO_GLOBAL = _RES / "entradas/calculoscorretos/observabilidade/entrada_com_erro_global.json"
_ERRO_422 = _RES / "entradas/calculoscorretos/observabilidade/entrada_com_erro_422.json"


def _carregar(path: Path):
    return operacao_from_json(json.loads(path.read_text(encoding="utf-8")))


def test_processa_entrada_oficial_seis_itens() -> None:
    svc = ObservabilidadeService()
    roc = svc.processar_operacao(_carregar(_ENTRADA), _BASE_URL)
    assert roc.objetos is not None
    assert len(roc.objetos) == 6

    estados = [o.estado_item for o in roc.objetos]
    assert estados == [
        EstadoItemEnum.INCONSISTENCIA_ENTRADA,
        EstadoItemEnum.NAO_IMPLEMENTADO,
        EstadoItemEnum.INCONSISTENCIA_ENTRADA,
        EstadoItemEnum.INCONSISTENCIA_ENTRADA,
        EstadoItemEnum.CALCULADO,
        EstadoItemEnum.CALCULO_SIMULADO,
    ]

    assert [o.n_obj for o in roc.objetos] == [1, 2, 3, 4, 5, 6]
    assert roc.objetos[4].trib_calc is not None
    assert roc.objetos[5].trib_calc is not None
    assert roc.total is not None


def test_erro_global_municipio_uf_interrompe() -> None:
    svc = ObservabilidadeService()
    with pytest.raises(ErrosCalculoException) as exc:
        svc.processar_operacao(_carregar(_ERRO_GLOBAL), _BASE_URL)
    erros = exc.value.get_erros()
    assert len(erros) == 1
    assert erros[0].code == "REG-018"


def test_erro_global_municipio_invalido_interrompe() -> None:
    svc = ObservabilidadeService()
    with pytest.raises(ErrosCalculoException) as exc:
        svc.processar_operacao(_carregar(_ERRO_422), _BASE_URL)
    erros = exc.value.get_erros()
    assert len(erros) == 1
    assert erros[0].code == "VAL-006"


def test_validacao_estrutural_id_ausente() -> None:
    payload = json.loads(_ENTRADA.read_text(encoding="utf-8"))
    payload.pop("id")
    svc = ObservabilidadeService()
    with pytest.raises(ErrosCalculoException) as exc:
        svc.processar_operacao(operacao_from_json(payload), _BASE_URL)
    assert exc.value.get_erros()[0].code == "VAL-001"
    assert exc.value.get_erros()[0].pointer == "#/id"


def test_itens_vazios_val_003() -> None:
    payload = json.loads(_ENTRADA.read_text(encoding="utf-8"))
    payload["itens"] = []
    svc = ObservabilidadeService()
    with pytest.raises(ErrosCalculoException) as exc:
        svc.processar_operacao(operacao_from_json(payload), _BASE_URL)
    assert exc.value.get_erros()[0].code == "VAL-003"