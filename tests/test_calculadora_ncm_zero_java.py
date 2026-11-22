"""NCM zero por tipo de documento — espelho ``TesteCalculadoraNcmZero`` (sem MockMvc)."""

from __future__ import annotations

import copy
import json
import os
from pathlib import Path
from typing import Literal

import pytest

os.environ.setdefault(
    "CALC_DB",
    "/home/garusotec/projects/lynko/libs/calculadora-rtc-regime-regular/.cache/oficial/java/calculadora/db/calculadora-pro.db",
)

from calculadora_rtc_regime_regular.coletor import ErrosCalculoException, EstadoItemEnum
from calculadora_rtc_regime_regular.consultas import TipoDfeNaoTratadoException
from calculadora_rtc_regime_regular.consumo import CalculadoraService
from calculadora_rtc_regime_regular.observabilidade import ObservabilidadeService, operacao_from_json
from calculadora_rtc_regime_regular.processamento_item import NcmNaoEncontradaException

pytestmark = pytest.mark.skipif(not os.environ.get("CALC_DB"), reason="CALC_DB ausente")

_CACHE = Path(__file__).resolve().parents[1] / ".cache/oficial/java/src/test/resources"
_BASE_URL = "http://localhost:8080"
_NCM_CURTO = "00"
_NCM_LONGO = "00000000"

HttpExpect = Literal["OK", "NOT_FOUND", "UNPROCESSABLE"]

CENARIOS_CALC: list[tuple[int | None, str, HttpExpect]] = [
    (55, _NCM_CURTO, "OK"),
    (55, _NCM_LONGO, "OK"),
    (65, _NCM_CURTO, "OK"),
    (65, _NCM_LONGO, "OK"),
    (57, _NCM_CURTO, "NOT_FOUND"),
    (57, _NCM_LONGO, "NOT_FOUND"),
    (62, _NCM_CURTO, "NOT_FOUND"),
    (62, _NCM_LONGO, "NOT_FOUND"),
    (63, _NCM_CURTO, "NOT_FOUND"),
    (63, _NCM_LONGO, "NOT_FOUND"),
    (66, _NCM_CURTO, "NOT_FOUND"),
    (66, _NCM_LONGO, "NOT_FOUND"),
    (67, _NCM_CURTO, "NOT_FOUND"),
    (67, _NCM_LONGO, "NOT_FOUND"),
    (75, _NCM_CURTO, "NOT_FOUND"),
    (75, _NCM_LONGO, "NOT_FOUND"),
    (76, _NCM_CURTO, "NOT_FOUND"),
    (76, _NCM_LONGO, "NOT_FOUND"),
    (77, _NCM_CURTO, "UNPROCESSABLE"),
    (77, _NCM_LONGO, "UNPROCESSABLE"),
    (83, _NCM_CURTO, "NOT_FOUND"),
    (83, _NCM_LONGO, "NOT_FOUND"),
    (91, _NCM_CURTO, "NOT_FOUND"),
    (91, _NCM_LONGO, "NOT_FOUND"),
    (92, _NCM_CURTO, "NOT_FOUND"),
    (92, _NCM_LONGO, "NOT_FOUND"),
    (93, _NCM_CURTO, "NOT_FOUND"),
    (93, _NCM_LONGO, "NOT_FOUND"),
    (94, _NCM_CURTO, "UNPROCESSABLE"),
    (94, _NCM_LONGO, "UNPROCESSABLE"),
    (95, _NCM_CURTO, "UNPROCESSABLE"),
    (95, _NCM_LONGO, "UNPROCESSABLE"),
    (96, _NCM_CURTO, "UNPROCESSABLE"),
    (96, _NCM_LONGO, "UNPROCESSABLE"),
    (97, _NCM_CURTO, "NOT_FOUND"),
    (97, _NCM_LONGO, "NOT_FOUND"),
    (None, _NCM_CURTO, "NOT_FOUND"),
    (None, _NCM_LONGO, "NOT_FOUND"),
]

EstadoExpect = Literal["CALCULADO", "INCONSISTENCIA_ENTRADA"] | None

CENARIOS_OBS: list[tuple[int | None, str, HttpExpect, EstadoExpect]] = [
    (55, _NCM_CURTO, "OK", "CALCULADO"),
    (55, _NCM_LONGO, "OK", "CALCULADO"),
    (65, _NCM_CURTO, "OK", "CALCULADO"),
    (65, _NCM_LONGO, "OK", "CALCULADO"),
    (57, _NCM_CURTO, "OK", "INCONSISTENCIA_ENTRADA"),
    (57, _NCM_LONGO, "OK", "INCONSISTENCIA_ENTRADA"),
    (62, _NCM_CURTO, "OK", "INCONSISTENCIA_ENTRADA"),
    (62, _NCM_LONGO, "OK", "INCONSISTENCIA_ENTRADA"),
    (63, _NCM_CURTO, "OK", "INCONSISTENCIA_ENTRADA"),
    (63, _NCM_LONGO, "OK", "INCONSISTENCIA_ENTRADA"),
    (66, _NCM_CURTO, "OK", "INCONSISTENCIA_ENTRADA"),
    (66, _NCM_LONGO, "OK", "INCONSISTENCIA_ENTRADA"),
    (67, _NCM_CURTO, "OK", "INCONSISTENCIA_ENTRADA"),
    (67, _NCM_LONGO, "OK", "INCONSISTENCIA_ENTRADA"),
    (75, _NCM_CURTO, "OK", "INCONSISTENCIA_ENTRADA"),
    (75, _NCM_LONGO, "OK", "INCONSISTENCIA_ENTRADA"),
    (76, _NCM_CURTO, "OK", "INCONSISTENCIA_ENTRADA"),
    (76, _NCM_LONGO, "OK", "INCONSISTENCIA_ENTRADA"),
    (77, _NCM_CURTO, "UNPROCESSABLE", None),
    (77, _NCM_LONGO, "UNPROCESSABLE", None),
    (83, _NCM_CURTO, "OK", "INCONSISTENCIA_ENTRADA"),
    (83, _NCM_LONGO, "OK", "INCONSISTENCIA_ENTRADA"),
    (91, _NCM_CURTO, "OK", "INCONSISTENCIA_ENTRADA"),
    (91, _NCM_LONGO, "OK", "INCONSISTENCIA_ENTRADA"),
    (92, _NCM_CURTO, "OK", "INCONSISTENCIA_ENTRADA"),
    (92, _NCM_LONGO, "OK", "INCONSISTENCIA_ENTRADA"),
    (93, _NCM_CURTO, "OK", "INCONSISTENCIA_ENTRADA"),
    (93, _NCM_LONGO, "OK", "INCONSISTENCIA_ENTRADA"),
    (94, _NCM_CURTO, "UNPROCESSABLE", None),
    (94, _NCM_LONGO, "UNPROCESSABLE", None),
    (95, _NCM_CURTO, "UNPROCESSABLE", None),
    (95, _NCM_LONGO, "UNPROCESSABLE", None),
    (96, _NCM_CURTO, "UNPROCESSABLE", None),
    (96, _NCM_LONGO, "UNPROCESSABLE", None),
    (97, _NCM_CURTO, "OK", "INCONSISTENCIA_ENTRADA"),
    (97, _NCM_LONGO, "OK", "INCONSISTENCIA_ENTRADA"),
    (None, _NCM_CURTO, "OK", "INCONSISTENCIA_ENTRADA"),
    (None, _NCM_LONGO, "OK", "INCONSISTENCIA_ENTRADA"),
]


def _operacao(tp_doc: int | None, ncm: str):
    base = json.loads(
        (_CACHE / "entradas/calculadora/ncm-zero/base_operacao.json").read_text(encoding="utf-8")
    )
    op = operacao_from_json(copy.deepcopy(base))
    op.tp_doc = tp_doc
    op.itens[0].ncm = ncm
    return op


@pytest.fixture(scope="module")
def calculadora() -> CalculadoraService:
    return CalculadoraService(calculo_ibs_habilitado=True)


@pytest.fixture(scope="module")
def observabilidade() -> ObservabilidadeService:
    return ObservabilidadeService()


@pytest.mark.parametrize(
    ("tp_doc", "ncm", "esperado"),
    CENARIOS_CALC,
    ids=[str(i) for i in range(1, len(CENARIOS_CALC) + 1)],
)
def teste_ncm_zero_conforme_tipo_documento(
    calculadora: CalculadoraService,
    tp_doc: int | None,
    ncm: str,
    esperado: HttpExpect,
) -> None:
    operacao = _operacao(tp_doc, ncm)
    if esperado == "OK":
        calculadora.calcularTributos(operacao)
        return
    if esperado == "NOT_FOUND":
        with pytest.raises(NcmNaoEncontradaException):
            calculadora.calcularTributos(operacao)
        return
    with pytest.raises(TipoDfeNaoTratadoException):
        calculadora.calcularTributos(operacao)


@pytest.mark.parametrize(
    ("tp_doc", "ncm", "status_esperado", "estado_esperado"),
    CENARIOS_OBS,
    ids=[str(i) for i in range(1, len(CENARIOS_OBS) + 1)],
)
def teste_ncm_zero_conforme_tipo_documento_observabilidade(
    observabilidade: ObservabilidadeService,
    tp_doc: int | None,
    ncm: str,
    status_esperado: HttpExpect,
    estado_esperado: EstadoExpect,
) -> None:
    operacao = _operacao(tp_doc, ncm)
    if status_esperado == "UNPROCESSABLE":
        with pytest.raises(ErrosCalculoException):
            observabilidade.processar_operacao(operacao, _BASE_URL)
        return
    resultado = observabilidade.processar_operacao(operacao, _BASE_URL)
    assert resultado.objetos
    estado = resultado.objetos[0].estado_item
    assert estado == EstadoItemEnum[estado_esperado or "CALCULADO"]