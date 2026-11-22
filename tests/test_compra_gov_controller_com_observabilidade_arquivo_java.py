"""Paridade CompraGovControllerComObservabilidadeArquivoTest — ObservabilidadeService."""

from __future__ import annotations

import os
from pathlib import Path

import pytest

os.environ.setdefault(
    "CALC_DB",
    "/home/garusotec/projects/lynko/libs/calculadora-rtc-regime-regular/.cache/oficial/java/calculadora/db/calculadora-pro.db",
)

from calculadora_rtc_regime_regular.observabilidade import ObservabilidadeService

from test_compra_gov_controller_arquivo_java import assert_gabarito_compra_gov, operacao_arquivo

_CACHE = Path(__file__).resolve().parents[1] / ".cache/oficial/java/src/test/resources"
_TESTES = "entradas/calculoscorretos/compras-governamentais/testes"
_BASE_URL = "http://localhost:8080"

pytestmark = pytest.mark.skipif(not os.environ.get("CALC_DB"), reason="CALC_DB ausente")

_SUCESSO = (
    ("cenario_01_uniao_input.json", "cenario_01_uniao_output_observabilidade.json"),
    ("cenario_02_estado_input.json", "cenario_02_estado_output_observabilidade.json"),
    ("cenario_03_distrito_federal_input.json", "cenario_03_distrito_federal_output_observabilidade.json"),
    ("cenario_04_municipio_input.json", "cenario_04_municipio_output_observabilidade.json"),
    ("cenario_05_consorcio_input.json", "cenario_05_consorcio_output_observabilidade.json"),
    ("cenario_06_comite_gestor_input.json", "cenario_06_comite_gestor_output_observabilidade.json"),
)

_FALHA = (
    "cenario_00_tipo_ente_invalido_input.json",
    "cenario_00_tipo_operacao_invalido_input.json",
)


def _surefire_calc_ids() -> list[str]:
    return [f"deveCalcularTributosCompraGovViaEndpoint(String, String)[{i}]" for i in range(1, 7)]


def _surefire_fail_ids() -> list[str]:
    return [f"deveFalharComValoresInvalidos(String)[{i}]" for i in range(1, 3)]


@pytest.fixture(scope="module")
def svc() -> ObservabilidadeService:
    return ObservabilidadeService()


@pytest.mark.parametrize("par", _SUCESSO, ids=_surefire_calc_ids())
def test_deveCalcularTributosCompraGovViaEndpoint(par: tuple[str, str], svc: ObservabilidadeService) -> None:
    entrada, saida = par
    roc = svc.processar_operacao(operacao_arquivo(entrada), _BASE_URL)
    assert_gabarito_compra_gov(roc, f"{_TESTES}/{saida}")


@pytest.mark.parametrize("arquivo", _FALHA, ids=_surefire_fail_ids())
def test_deveFalharComValoresInvalidos(arquivo: str) -> None:
    with pytest.raises(ValueError):
        operacao_arquivo(arquivo)