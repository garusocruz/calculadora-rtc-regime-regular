"""Paridade ViaController — Teste_validacao_AliquotasNominaisPorAnoFatoGerador (pin f1eebd7)."""

from __future__ import annotations

import json
import os
from dataclasses import replace
from datetime import date
from decimal import Decimal
from pathlib import Path

import pytest

os.environ.setdefault(
    "CALC_DB",
    "/home/garusotec/projects/lynko/libs/calculadora-rtc-regime-regular/.cache/oficial/java/calculadora/db/calculadora-pro.db",
)

from calculadora_rtc_regime_regular.calculadora import CalculadoraService
from calculadora_rtc_regime_regular.coletor import _problem_type_from
from calculadora_rtc_regime_regular.observabilidade import operacao_from_json
from calculadora_rtc_regime_regular.processamento_item import (
    AliquotaImpostoSeletivoNaoInformadaException,
    AliquotasNominaisInformadasIndevidamenteException,
    ImpostoSeletivoInput,
)

_RES = Path(__file__).resolve().parents[1] / ".cache/oficial/java/src/test/resources"
_ENTRADA = "entradas/validacoes/Teste_validacao_15_ImpostoSeletivoNaoInformadoException.json"

pytestmark = pytest.mark.skipif(
    not Path(os.environ["CALC_DB"]).is_file(),
    reason="calculadora-pro.db ausente",
)


@pytest.fixture(scope="module")
def calc() -> CalculadoraService:
    return CalculadoraService()


def _carregar_operacao():
    payload = json.loads((_RES / _ENTRADA).read_text(encoding="utf-8"))
    return operacao_from_json(payload)


def _mudar_2026(op):
    op.data_fato_gerador = date(2026, 8, 30)
    return op


def _informar_is(op):
    op.itens[0] = replace(
        op.itens[0],
        imposto_seletivo=ImpostoSeletivoInput(
            cst="000",
            c_class_trib="000001",
            base_calculo=Decimal("100"),
            quantidade=Decimal("1"),
            unidade="UN",
            imposto_informado=None,
        ),
    )
    return op


def _titulo_problem_detail(exc: Exception) -> str:
    """Espelha ``ApiExceptionHandler.createProblem`` → ``ProblemDetail.title``."""
    return _problem_type_from(exc).titulo


def test_deveCriticarAliquotasNominaisInformadasAte2026ViaController(
    calc: CalculadoraService,
) -> None:
    operacao = _mudar_2026(_carregar_operacao())
    with pytest.raises(AliquotasNominaisInformadasIndevidamenteException) as caught:
        calc.calcular_tributos(operacao)
    assert _titulo_problem_detail(caught.value) == (
        "Alíquotas nominais informadas indevidamente"
    )


def test_deveCriticarAliquotaImpostoSeletivoNaoResolvivelViaController(
    calc: CalculadoraService,
) -> None:
    operacao = _informar_is(_carregar_operacao())
    with pytest.raises(AliquotaImpostoSeletivoNaoInformadaException) as caught:
        calc.calcular_tributos(operacao)
    assert _titulo_problem_detail(caught.value) == (
        "Alíquota do Imposto Seletivo não informada"
    )