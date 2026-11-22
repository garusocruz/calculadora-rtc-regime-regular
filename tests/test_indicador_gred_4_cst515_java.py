"""Paridade com Teste_indicador_gRed_4_cst515 (gRed + gDif CST 515)."""

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
_ENTRADA = "entradas/indicadores/Teste_indicador_gRed_4_cst515.json"

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


def test_testIndicadorGRedCST515(svc: CalculadoraService) -> None:
    item = _item0(svc)
    cbs = item.get_g_cbs()
    uf = item.get_g_ibs_uf()
    mun = item.get_g_ibs_mun()
    assert cbs is not None and uf is not None and mun is not None
    _assert_gred_presente(cbs, label="CBS gRed (CST 515)")
    _assert_gred_presente(uf, label="IBS UF gRed (CST 515)")
    _assert_gred_presente(mun, label="IBS Mun gRed (CST 515)")
    assert cbs.g_dif is not None, "CBS deve conter gDif (CST 515 diferimento)"
    assert uf.g_dif is not None, "IBS UF deve conter gDif"
    assert mun.g_dif is not None, "IBS Mun deve conter gDif"