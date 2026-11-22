"""Paridade com ``BaseCalculoUnificadaInputTest`` (endpoint / publicado)."""

from __future__ import annotations

from decimal import Decimal

import pytest

from calculadora_rtc_regime_regular.base_calculo import (
    BaseCalculoUnificadaInput,
    BaseCalculoUnificadaService,
    Componentes,
    Natureza,
)
from calculadora_rtc_regime_regular.base_calculo_service import CampoInvalido

_SERVICE = BaseCalculoUnificadaService()


def _input(ano: int, tipo_documento: int, natureza: str, valores: dict[str, str]) -> BaseCalculoUnificadaInput:
    comp = Componentes(
        **{nome: Decimal(valor) for nome, valor in valores.items()},
    )
    return BaseCalculoUnificadaInput(
        anoFatoGerador=ano,
        tipoDocumento=tipo_documento,
        natureza=Natureza[natureza],
        componentes=comp,
    )


def test_deveCalcularAsTresBasesComTodosOsCamposAtivos() -> None:
    output = _SERVICE.calcular(
        _input(
            2026,
            55,
            "BEM",
            {
                "vProd": "1000.00",
                "vFrete": "50.00",
                "vSeg": "20.00",
                "vOutro": "10.00",
                "vII": "150.00",
                "vDesc": "50.00",
                "vPIS": "9.25",
                "vCOFINS": "46.25",
                "vICMS": "180.00",
                "vICMSUFDest": "20.00",
                "vFCP": "10.00",
                "vFCPUFDest": "5.00",
                "vICMSMono": "100.00",
            },
        )
    )
    assert output.getBaseRG() == Decimal("809.50")
    assert output.getBaseIS() == Decimal("809.50")
    assert output.getBaseSN() == Decimal("1030.00")
    assert output.getAvisos() == []


def test_vPisEVCofinsDevemComporAsBasesEm2026() -> None:
    output = _SERVICE.calcular(
        _input(2026, 55, "BEM", {"vProd": "1000.00", "vPIS": "100.00", "vCOFINS": "50.00"})
    )
    assert output.getBaseRG() == Decimal("850.00")
    assert output.getBaseIS() == Decimal("850.00")
    assert output.getBaseSN() == Decimal("1000.00")
    assert output.getAvisos() == []


def test_vPisEVCofinsDevemSerIgnoradosComAvisoEm2027() -> None:
    output = _SERVICE.calcular(
        _input(2027, 55, "BEM", {"vProd": "1000.00", "vPIS": "100.00", "vCOFINS": "50.00"})
    )
    assert output.getBaseRG() == Decimal("1000.00")
    assert output.getBaseIS() == Decimal("1000.00")
    assert set(output.getAvisos()) == {
        "Campo vPIS não compõe as bases para o ano 2027 (vigência 2026–2026) e foi ignorado no cálculo",
        "Campo vCOFINS não compõe as bases para o ano 2027 (vigência 2026–2026) e foi ignorado no cálculo",
    }


def test_vIsDeveSerIgnoradoComAvisoEm2026() -> None:
    output = _SERVICE.calcular(_input(2026, 55, "BEM", {"vProd": "1000.00", "vIS": "30.00"}))
    assert output.getBaseRG() == Decimal("1000.00")
    assert output.getBaseSN() == Decimal("1000.00")
    assert output.getAvisos() == [
        "Campo vIS não compõe as bases para o ano 2026 (vigência 2027–2033) e foi ignorado no cálculo"
    ]


def test_vIsDeveComporAsBasesAPartirDe2027() -> None:
    output = _SERVICE.calcular(_input(2027, 55, "BEM", {"vProd": "1000.00", "vIS": "30.00"}))
    assert output.getBaseRG() == Decimal("1030.00")
    assert output.getBaseIS() == Decimal("1000.00")
    assert output.getBaseSN() == Decimal("1030.00")
    assert output.getAvisos() == []


def test_familiaIcmsDeveComporAsBasesAte2032() -> None:
    output = _SERVICE.calcular(
        _input(2032, 55, "BEM", {"vProd": "1000.00", "vICMS": "100.00", "vFCP": "10.00", "vICMSMono": "40.00"})
    )
    assert output.getBaseRG() == Decimal("850.00")
    assert output.getBaseIS() == Decimal("850.00")
    assert output.getBaseSN() == Decimal("1000.00")
    assert output.getAvisos() == []


def test_familiaIcmsDeveSerIgnoradaComAvisoEm2033() -> None:
    output = _SERVICE.calcular(
        _input(2033, 55, "BEM", {"vProd": "1000.00", "vICMS": "100.00", "vFCP": "10.00", "vICMSMono": "40.00"})
    )
    assert output.getBaseRG() == Decimal("1000.00")
    assert output.getBaseIS() == Decimal("1000.00")
    assert set(output.getAvisos()) == {
        "Campo vICMS não compõe as bases para o ano 2033 (vigência 2026–2032) e foi ignorado no cálculo",
        "Campo vFCP não compõe as bases para o ano 2033 (vigência 2026–2032) e foi ignorado no cálculo",
        "Campo vICMSMono não compõe as bases para o ano 2033 (vigência 2026–2032) e foi ignorado no cálculo",
    }


def test_vIssqnDeveComporAsBasesApenasComServico() -> None:
    com_servico = _SERVICE.calcular(_input(2026, 55, "SERVICO", {"vProd": "1000.00", "vISSQN": "50.00"}))
    assert com_servico.getBaseRG() == Decimal("950.00")
    assert com_servico.getBaseIS() == Decimal("950.00")
    assert com_servico.getBaseSN() == Decimal("1000.00")
    assert com_servico.getAvisos() == []

    com_bem = _SERVICE.calcular(_input(2026, 55, "BEM", {"vProd": "1000.00", "vISSQN": "50.00"}))
    assert com_bem.getBaseRG() == Decimal("1000.00")
    assert com_bem.getAvisos() == [
        "Campo vISSQN não compõe as bases para a natureza BEM (aplicável apenas a SERVICO) e foi ignorado no cálculo"
    ]


def test_camposDeBemDevemSerIgnoradosComAvisoParaServico() -> None:
    output = _SERVICE.calcular(
        _input(2026, 55, "SERVICO", {"vProd": "1000.00", "vII": "150.00", "vICMS": "100.00"})
    )
    assert output.getBaseRG() == Decimal("1000.00")
    assert output.getBaseIS() == Decimal("1000.00")
    assert output.getBaseSN() == Decimal("1000.00")
    assert set(output.getAvisos()) == {
        "Campo vII não compõe as bases para a natureza SERVICO (aplicável apenas a BEM) e foi ignorado no cálculo",
        "Campo vICMS não compõe as bases para a natureza SERVICO (aplicável apenas a BEM) e foi ignorado no cálculo",
    }


def test_camposExclusivosDoModelo55DevemSerIgnoradosComAvisoNoModelo65() -> None:
    output = _SERVICE.calcular(
        _input(2026, 65, "BEM", {"vProd": "1000.00", "vII": "150.00", "vICMSUFDest": "20.00", "vFCPUFDest": "5.00"})
    )
    assert output.getBaseRG() == Decimal("1000.00")
    assert output.getBaseIS() == Decimal("1000.00")
    assert output.getBaseSN() == Decimal("1000.00")
    assert set(output.getAvisos()) == {
        "Campo vII não compõe as bases para o documento modelo 65 e foi ignorado no cálculo",
        "Campo vICMSUFDest não compõe as bases para o documento modelo 65 e foi ignorado no cálculo",
        "Campo vFCPUFDest não compõe as bases para o documento modelo 65 e foi ignorado no cálculo",
    }


def test_campoIgnoradoComValorZeroOuAusenteNaoDeveGerarAviso() -> None:
    output = _SERVICE.calcular(_input(2027, 55, "BEM", {"vProd": "1000.00", "vPIS": "0.00"}))
    assert output.getBaseRG() == Decimal("1000.00")
    assert output.getAvisos() == []


def test_avisosNaoDevemAfetarOCalculoDasBases() -> None:
    sem_avisos = _SERVICE.calcular(_input(2027, 55, "BEM", {"vProd": "1000.00", "vDesc": "50.00"}))
    com_avisos = _SERVICE.calcular(
        _input(2027, 55, "BEM", {"vProd": "1000.00", "vDesc": "50.00", "vPIS": "100.00", "vCOFINS": "50.00"})
    )
    assert len(com_avisos.getAvisos()) == 2
    assert sem_avisos.getAvisos() == []
    assert com_avisos.getBaseRG() == sem_avisos.getBaseRG()
    assert com_avisos.getBaseIS() == sem_avisos.getBaseIS()
    assert com_avisos.getBaseSN() == sem_avisos.getBaseSN()


def test_tipoDocumentoDiferenteDe55E65DeveLancarExcecao() -> None:
    inp = _input(2026, 44, "BEM", {"vProd": "1000.00"})
    with pytest.raises(CampoInvalido, match="Tipo de documento deve ser 55 \\(NF-e\\) ou 65 \\(NFC-e\\)"):
        _SERVICE.calcular(inp)