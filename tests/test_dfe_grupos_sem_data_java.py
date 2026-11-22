"""Consulta de tipos de DFe sem data: o serviço usa a data de hoje."""

from __future__ import annotations

import os

import pytest

os.environ.setdefault(
    "CALC_DB",
    "/home/garusotec/projects/lynko/libs/calculadora-rtc-regime-regular/.cache/oficial/java/calculadora/db/calculadora-pro.db",
)

from calculadora_rtc_regime_regular.consumo import DadosAbertosService

pytestmark = pytest.mark.skipif(not os.environ.get("CALC_DB"), reason="CALC_DB ausente")


def test_dfeGrupos_semData_usaDataAtual() -> None:
    grupos = DadosAbertosService().consultarTiposDfeAgrupados(None)
    assert grupos
    assert grupos[0].tipos
