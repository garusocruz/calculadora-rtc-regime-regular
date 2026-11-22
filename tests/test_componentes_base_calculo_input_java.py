"""Paridade com ``ComponentesBaseCalculoInputTest`` (getValor / ElementoBaseCalculo)."""

from __future__ import annotations

from decimal import Decimal

import pytest

from calculadora_rtc_regime_regular.base_calculo import ElementoBaseCalculo
from calculadora_rtc_regime_regular.consumo import ComponentesBaseCalculoInput

_PARAM_IDS = [str(i) for i in range(1, 16)]


def test_getValor_deveRetornarVProd() -> None:
    comp = ComponentesBaseCalculoInput()
    comp.setVProd(Decimal("1000.00"))
    assert comp.getValor(ElementoBaseCalculo.V_PROD) == Decimal("1000.00")


def test_getValor_deveRetornarVFrete() -> None:
    comp = ComponentesBaseCalculoInput()
    comp.setVFrete(Decimal("50.00"))
    assert comp.getValor(ElementoBaseCalculo.V_FRETE) == Decimal("50.00")


def test_getValor_deveRetornarVSeg() -> None:
    comp = ComponentesBaseCalculoInput()
    comp.setVSeg(Decimal("20.00"))
    assert comp.getValor(ElementoBaseCalculo.V_SEG) == Decimal("20.00")


def test_getValor_deveRetornarVOutro() -> None:
    comp = ComponentesBaseCalculoInput()
    comp.setVOutro(Decimal("10.00"))
    assert comp.getValor(ElementoBaseCalculo.V_OUTRO) == Decimal("10.00")


def test_getValor_deveRetornarVII() -> None:
    comp = ComponentesBaseCalculoInput()
    comp.setVII(Decimal("150.00"))
    assert comp.getValor(ElementoBaseCalculo.V_II) == Decimal("150.00")


def test_getValor_deveRetornarVIS() -> None:
    comp = ComponentesBaseCalculoInput()
    comp.setVIS(Decimal("30.00"))
    assert comp.getValor(ElementoBaseCalculo.V_IS) == Decimal("30.00")


def test_getValor_deveRetornarVDesc() -> None:
    comp = ComponentesBaseCalculoInput()
    comp.setVDesc(Decimal("50.00"))
    assert comp.getValor(ElementoBaseCalculo.V_DESC) == Decimal("50.00")


def test_getValor_deveRetornarVPIS() -> None:
    comp = ComponentesBaseCalculoInput()
    comp.setVPIS(Decimal("9.25"))
    assert comp.getValor(ElementoBaseCalculo.V_PIS) == Decimal("9.25")


def test_getValor_deveRetornarVCOFINS() -> None:
    comp = ComponentesBaseCalculoInput()
    comp.setVCOFINS(Decimal("46.25"))
    assert comp.getValor(ElementoBaseCalculo.V_COFINS) == Decimal("46.25")


def test_getValor_deveRetornarVICMS() -> None:
    comp = ComponentesBaseCalculoInput()
    comp.setVICMS(Decimal("180.00"))
    assert comp.getValor(ElementoBaseCalculo.V_ICMS) == Decimal("180.00")


def test_getValor_deveRetornarVICMSUFDest() -> None:
    comp = ComponentesBaseCalculoInput()
    comp.setVICMSUFDest(Decimal("20.00"))
    assert comp.getValor(ElementoBaseCalculo.V_ICMS_UF_DEST) == Decimal("20.00")


def test_getValor_deveRetornarVFCP() -> None:
    comp = ComponentesBaseCalculoInput()
    comp.setVFCP(Decimal("10.00"))
    assert comp.getValor(ElementoBaseCalculo.V_FCP) == Decimal("10.00")


def test_getValor_deveRetornarVFCPUFDest() -> None:
    comp = ComponentesBaseCalculoInput()
    comp.setVFCPUFDest(Decimal("5.00"))
    assert comp.getValor(ElementoBaseCalculo.V_FCP_UF_DEST) == Decimal("5.00")


def test_getValor_deveRetornarVICMSMono() -> None:
    comp = ComponentesBaseCalculoInput()
    comp.setVICMSMono(Decimal("100.00"))
    assert comp.getValor(ElementoBaseCalculo.V_ICMS_MONO) == Decimal("100.00")


def test_getValor_deveRetornarVISSQN() -> None:
    comp = ComponentesBaseCalculoInput()
    comp.setVISSQN(Decimal("30.00"))
    assert comp.getValor(ElementoBaseCalculo.V_ISSQN) == Decimal("30.00")


@pytest.mark.parametrize("elemento", list(ElementoBaseCalculo), ids=_PARAM_IDS)
def test_getValor_deveRetornarNullQuandoCampoNaoInformado(elemento: ElementoBaseCalculo) -> None:
    comp = ComponentesBaseCalculoInput()
    assert comp.getValor(elemento) is None