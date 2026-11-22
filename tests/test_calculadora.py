"""Testes de orquestração ``CalculadoraService`` (pin f1eebd7)."""

from __future__ import annotations

import os
from datetime import date
from decimal import Decimal

import pytest

os.environ.setdefault(
    "CALC_DB",
    "/home/garusotec/projects/lynko/libs/calculadora-rtc-regime-regular/.cache/oficial/java/calculadora/db/calculadora-pro.db",
)

from calculadora_rtc_regime_regular.calculadora import CalculadoraService, OperacaoCalculadoraInput
from calculadora_rtc_regime_regular.consultas import (
    MunicipioNaoPertencenteException,
    TipoDfeNaoEncontradoException,
    UfNaoEncontradaException,
)
from calculadora_rtc_regime_regular.processamento_item import ItemOperacaoInput

DATA = date(2026, 1, 15)
SERVICO = CalculadoraService()


def _item_minimo() -> ItemOperacaoInput:
    return ItemOperacaoInput(
        numero=1,
        ncm="24021000",
        cst="000",
        c_class_trib="000001",
        base_calculo=Decimal("200"),
        quantidade=Decimal("1"),
        unidade="VN",
    )


def _operacao(**kwargs: object) -> OperacaoCalculadoraInput:
    base = dict(
        id="test",
        versao="0.0.1",
        municipio=4314902,
        data_fato_gerador=DATA,
        tp_doc=55,
        itens=[_item_minimo()],
    )
    base.update(kwargs)
    return OperacaoCalculadoraInput(**base)  # type: ignore[arg-type]


def test_uf_ausente_resolvida_pelo_municipio() -> None:
    op = _operacao(uf=None)
    roc = SERVICO.calcular_tributos(op)
    assert op.uf == "RS"
    assert roc.objetos


def test_uf_inexistente() -> None:
    op = _operacao(uf="RX")
    with pytest.raises(UfNaoEncontradaException):
        SERVICO.calcular_tributos(op)


def test_municipio_de_outra_uf() -> None:
    op = _operacao(uf="RJ", municipio=4314902)
    with pytest.raises(MunicipioNaoPertencenteException):
        SERVICO.calcular_tributos(op)


def test_tp_doc_inexistente() -> None:
    op = _operacao(tp_doc=99999)
    with pytest.raises(TipoDfeNaoEncontradoException):
        SERVICO.calcular_tributos(op)


def test_item_minimo_valida_e_calcula_cbs() -> None:
    roc = SERVICO.calcular_tributos(_operacao())
    assert len(roc.objetos) == 1
    obj = roc.objetos[0]
    assert obj.n_obj == 1
    assert obj.trib_calc is not None
    assert obj.trib_calc.possui_base_calculo_ibscbs()
    assert obj.trib_calc.possui_cbs()
    assert obj.trib_calc.get_valor_base_calculo_ibscbs() == Decimal("200")
    assert roc.total is not None
    assert roc.oper is None
    assert obj.trib_calc.IBSCBS is not None
    assert obj.trib_calc.IBSCBS.memoria_calculo is not None
    assert obj.trib_calc.IBSCBS.memoria_calculo.cbs