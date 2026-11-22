"""Indicador gRed — espelho dos testes Java (pin f1eebd7). Sem MockMvc."""

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
_FQCN = "br.gov.serpro.rtc.testesintegracao.indicadores"

pytestmark = pytest.mark.skipif(not os.environ.get("CALC_DB"), reason="CALC_DB ausente")


def _java(record_xml_attribute, classname: str, method: str) -> None:
    record_xml_attribute("classname", f"{_FQCN}.{classname}")
    record_xml_attribute("name", method)


def _dec(value: object) -> Decimal:
    return Decimal(str(value))


def _load_json(rel: str) -> dict:
    return json.loads((_CACHE / rel).read_text(encoding="utf-8"))


def _operacao(rel: str):
    return operacao_from_json(_load_json(rel))


@pytest.fixture(scope="module")
def svc() -> CalculadoraService:
    return CalculadoraService(calculo_ibs_habilitado=True)


def _item0(svc: CalculadoraService, rel: str):
    roc = svc.calcularTributos(_operacao(rel))
    assert roc is not None
    assert roc.objetos
    return roc.objetos[0]


def _assert_gred_presente(grupo, *, label: str) -> None:
    assert grupo is not None, label
    red = grupo.g_red
    assert red is not None, label
    assert red.p_red_aliq is not None
    assert _dec(red.p_red_aliq) > 0
    assert red.p_aliq_efet is not None


def _assert_gred_ausente(grupo, *, label: str) -> None:
    assert grupo is not None
    assert grupo.g_red is None, label


def test_testIndicadorGRedPresente(record_xml_attribute, svc: CalculadoraService) -> None:
    _java(record_xml_attribute, "Teste_indicador_gRed_1_presente", "testIndicadorGRedPresente(Resource)")
    item = _item0(svc, "entradas/indicadores/Teste_indicador_gRed_1_presente.json")
    _assert_gred_presente(item.get_g_cbs(), label="CBS deve conter grupo gRed (CST 200, SITR_IND_GRED=1)")
    _assert_gred_presente(item.get_g_ibs_uf(), label="IBS UF deve conter grupo gRed")
    _assert_gred_presente(item.get_g_ibs_mun(), label="IBS Mun deve conter grupo gRed")


def test_testIndicadorGRedAusente(record_xml_attribute, svc: CalculadoraService) -> None:
    _java(record_xml_attribute, "Teste_indicador_gRed_2_ausente", "testIndicadorGRedAusente(Resource)")
    item = _item0(svc, "entradas/indicadores/Teste_indicador_gRed_2_ausente.json")
    _assert_gred_ausente(item.get_g_cbs(), label="CBS NÃO deve conter gRed (CST 000, SITR_IND_GRED=0)")
    _assert_gred_ausente(item.get_g_ibs_uf(), label="IBS UF NÃO deve conter gRed")
    _assert_gred_ausente(item.get_g_ibs_mun(), label="IBS Mun NÃO deve conter gRed")


def test_testIndicadorGRedComTributacaoRegular(record_xml_attribute, svc: CalculadoraService) -> None:
    _java(
        record_xml_attribute,
        "Teste_indicador_gRed_3_tributacaoRegular",
        "testIndicadorGRedComTributacaoRegular(Resource)",
    )
    item = _item0(svc, "entradas/indicadores/Teste_indicador_gRed_3_tributacaoRegular.json")
    assert item.possui_tributacao_regular()
    assert item.get_tributacao_regular() is not None
    _assert_gred_ausente(item.get_g_cbs(), label="CBS sem gRed quando há tributação regular")
    _assert_gred_ausente(item.get_g_ibs_uf(), label="IBS UF sem gRed quando há tributação regular")
    _assert_gred_ausente(item.get_g_ibs_mun(), label="IBS Mun sem gRed quando há tributação regular")


def test_testIndicadorGRedCST515(record_xml_attribute, svc: CalculadoraService) -> None:
    _java(record_xml_attribute, "Teste_indicador_gRed_4_cst515", "testIndicadorGRedCST515(Resource)")
    item = _item0(svc, "entradas/indicadores/Teste_indicador_gRed_4_cst515.json")
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