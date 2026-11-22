"""Paridade com Teste_indicador_gRed_1_presente (indicador gRed presente)."""

from __future__ import annotations

import json
import os
from decimal import Decimal
from pathlib import Path

import pytest

os.environ.setdefault(
    "CALC_DB",
    "/home/garusotec/projects/lynko/libs/calculadora-rtc-regime-regular/.cache/oficial/java/calculadora/db/calculadora-pro.db",
)

from calculadora_rtc_regime_regular.consumo import CalculadoraService
from calculadora_rtc_regime_regular.observabilidade import operacao_from_json

_CACHE = Path(__file__).resolve().parents[1] / ".cache/oficial/java/src/test/resources"
_ENTRADA = "entradas/indicadores/Teste_indicador_gRed_1_presente.json"

pytestmark = pytest.mark.skipif(not os.environ.get("CALC_DB"), reason="CALC_DB ausente")


def _dec(value: object) -> Decimal:
    return Decimal(str(value))


def _item0(svc: CalculadoraService):
    payload = json.loads((_CACHE / _ENTRADA).read_text(encoding="utf-8"))
    roc = svc.calcularTributos(operacao_from_json(payload))
    assert roc is not None and roc.objetos
    return roc.objetos[0]


def _assert_gred_presente(grupo, *, label: str) -> None:
    assert grupo is not None, label
    red = grupo.g_red
    assert red is not None, label
    assert red.p_red_aliq is not None
    assert _dec(red.p_red_aliq) > 0
    assert red.p_aliq_efet is not None


@pytest.fixture(scope="module")
def svc() -> CalculadoraService:
    return CalculadoraService(calculo_ibs_habilitado=True)


def test_testIndicadorGRedPresente(svc: CalculadoraService) -> None:
    item = _item0(svc)
    _assert_gred_presente(item.get_g_cbs(), label="CBS deve conter grupo gRed (CST 200, SITR_IND_GRED=1)")
    _assert_gred_presente(item.get_g_ibs_uf(), label="IBS UF deve conter grupo gRed")
    _assert_gred_presente(item.get_g_ibs_mun(), label="IBS Mun deve conter grupo gRed")