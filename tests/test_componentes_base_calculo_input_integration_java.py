"""Paridade com ``ComponentesBaseCalculoInputTest`` (JSON via ``OperacaoInput``)."""

from __future__ import annotations

from decimal import Decimal

from calculadora_rtc_regime_regular.processamento_item import (
    OperacaoInput,
    item_operacao_input_to_json_dict,
    operacao_input_from_json,
    possui_componentes,
)


def _carregar(item: dict, *, tp_doc: int | None = None) -> OperacaoInput:
    payload: dict = {
        "id": "ROC001",
        "versao": "1",
        "dhFatoGerador": "2026-06-15T12:00:00Z",
        "municipio": 3550308,
        "itens": [item],
    }
    if tp_doc is not None:
        payload["tpDoc"] = tp_doc
    return operacao_input_from_json(payload)


def test_deveSerializarECarregarPayloadCenario1_JSON() -> None:
    item = {
        "numero": 1,
        "cst": "000",
        "cClassTrib": "000001",
        "baseCalculo": "850.00",
    }
    operacao = _carregar(item)
    assert len(operacao.itens) == 1
    assert operacao.itens[0].base_calculo == Decimal("850.00")
    assert operacao.itens[0].g_componentes_bc is None


def test_deveSerializarECarregarPayloadCenario2_JSON() -> None:
    item = {
        "numero": 1,
        "cst": "000",
        "cClassTrib": "000001",
        "baseCalculo": "850.00",
        "gComponentesBC": {
            "vProd": "1000.00",
            "vFrete": "50.00",
            "vSeg": "20.00",
            "vDesc": "40.00",
            "vICMS": "180.00",
        },
    }
    operacao = _carregar(item)
    assert operacao.itens[0].base_calculo == Decimal("850.00")
    comps = operacao.itens[0].g_componentes_bc
    assert comps is not None
    assert comps.vProd == Decimal("1000.00")
    assert comps.vFrete == Decimal("50.00")
    assert comps.vSeg == Decimal("20.00")
    assert comps.vDesc == Decimal("40.00")
    assert comps.vICMS == Decimal("180.00")
    assert possui_componentes(comps) is True


def test_deveSerializarECarregarPayloadCenario3_JSON() -> None:
    item = {
        "numero": 1,
        "cst": "000",
        "cClassTrib": "000001",
        "gComponentesBC": {
            "vProd": "1000.00",
            "vFrete": "50.00",
            "vSeg": "20.00",
            "vDesc": "40.00",
            "vICMS": "180.00",
        },
    }
    operacao = _carregar(item)
    assert operacao.itens[0].base_calculo is None
    comps = operacao.itens[0].g_componentes_bc
    assert comps is not None
    assert comps.vProd == Decimal("1000.00")


def test_deveSerializarECarregarPayloadCenario2Inconsistencia_JSON() -> None:
    item = {
        "numero": 1,
        "cst": "000",
        "cClassTrib": "000001",
        "baseCalculo": "900.00",
        "gComponentesBC": {
            "vProd": "1000.00",
            "vFrete": "50.00",
            "vSeg": "20.00",
            "vDesc": "40.00",
            "vICMS": "180.00",
        },
    }
    operacao = _carregar(item)
    assert operacao.itens[0].base_calculo == Decimal("900.00")
    comps = operacao.itens[0].g_componentes_bc
    assert comps is not None
    assert possui_componentes(comps) is True


def test_deveManterComponentesNulosQuandoAusentes() -> None:
    item = {
        "numero": 1,
        "cst": "000",
        "cClassTrib": "000001",
        "baseCalculo": "850.00",
        "gComponentesBC": {},
    }
    operacao = _carregar(item)
    comps = operacao.itens[0].g_componentes_bc
    assert comps is not None
    assert possui_componentes(comps) is False


def test_deveSerializarComponentesComTodosOs15Campos() -> None:
    item = {
        "numero": 1,
        "cst": "000",
        "cClassTrib": "000001",
        "gComponentesBC": {
            "vProd": "1000.00",
            "vFrete": "50.00",
            "vSeg": "20.00",
            "vOutro": "10.00",
            "vII": "150.00",
            "vIS": "30.00",
            "vDesc": "40.00",
            "vPIS": "9.25",
            "vCOFINS": "46.25",
            "vICMS": "180.00",
            "vICMSUFDest": "20.00",
            "vFCP": "10.00",
            "vFCPUFDest": "5.00",
            "vICMSMono": "100.00",
            "vISSQN": "30.00",
        },
    }
    operacao = _carregar(item, tp_doc=55)
    comps = operacao.itens[0].g_componentes_bc
    assert comps is not None
    assert comps.vProd == Decimal("1000.00")
    assert comps.vFrete == Decimal("50.00")
    assert comps.vSeg == Decimal("20.00")
    assert comps.vOutro == Decimal("10.00")
    assert comps.vII == Decimal("150.00")
    assert comps.vIS == Decimal("30.00")
    assert comps.vDesc == Decimal("40.00")
    assert comps.vPIS == Decimal("9.25")
    assert comps.vCOFINS == Decimal("46.25")
    assert comps.vICMS == Decimal("180.00")
    assert comps.vICMSUFDest == Decimal("20.00")
    assert comps.vFCP == Decimal("10.00")
    assert comps.vFCPUFDest == Decimal("5.00")
    assert comps.vICMSMono == Decimal("100.00")
    assert comps.vISSQN == Decimal("30.00")
    assert possui_componentes(comps) is True


def test_deveSerializarPayloadRetornandoValorCorretoBaseCalculo() -> None:
    item = {
        "numero": 1,
        "cst": "000",
        "cClassTrib": "000001",
        "baseCalculo": "850.00",
        "gComponentesBC": {
            "vProd": "1000.00",
            "vFrete": "50.00",
            "vSeg": "20.00",
            "vDesc": "40.00",
            "vICMS": "180.00",
        },
    }
    operacao = _carregar(item, tp_doc=55)
    assert operacao.tp_doc == 55
    assert len(operacao.itens) == 1
    assert operacao.itens[0].base_calculo == Decimal("850.00")
    round_trip = item_operacao_input_to_json_dict(operacao.itens[0])
    assert Decimal(str(round_trip["baseCalculo"])) == Decimal("850.00")