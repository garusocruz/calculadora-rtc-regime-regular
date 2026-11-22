"""Paridade com Teste_indicador_gRed_3_tributacaoRegular."""

from __future__ import annotations

import json
import os
from pathlib import Path

import pytest

os.environ.setdefault(
    "CALC_DB",
    "/home/garusotec/projects/lynko/libs/calculadora-rtc-regime-regular/.cache/oficial/java/calculadora/db/calculadora-pro.db",
)

from calculadora_rtc_regime_regular.consumo import CalculadoraService
from calculadora_rtc_regime_regular.observabilidade import operacao_from_json

_CACHE = Path(__file__).resolve().parents[1] / ".cache/oficial/java/src/test/resources"
_ENTRADA = "entradas/indicadores/Teste_indicador_gRed_3_tributacaoRegular.json"

pytestmark = pytest.mark.skipif(not os.environ.get("CALC_DB"), reason="CALC_DB ausente")


def _item0(svc: CalculadoraService):
    payload = json.loads((_CACHE / _ENTRADA).read_text(encoding="utf-8"))
    roc = svc.calcularTributos(operacao_from_json(payload))
    assert roc is not None and roc.objetos
    return roc.objetos[0]


def _assert_gred_ausente(grupo, *, label: str) -> None:
    assert grupo is not None
    assert grupo.g_red is None, label


@pytest.fixture(scope="module")
def svc() -> CalculadoraService:
    return CalculadoraService(calculo_ibs_habilitado=True)


def test_testIndicadorGRedComTributacaoRegular(svc: CalculadoraService) -> None:
    item = _item0(svc)
    assert item.possui_tributacao_regular()
    assert item.get_tributacao_regular() is not None
    _assert_gred_ausente(item.get_g_cbs(), label="CBS sem gRed quando há tributação regular")
    _assert_gred_ausente(item.get_g_ibs_uf(), label="IBS UF sem gRed quando há tributação regular")
    _assert_gred_ausente(item.get_g_ibs_mun(), label="IBS Mun sem gRed quando há tributação regular")