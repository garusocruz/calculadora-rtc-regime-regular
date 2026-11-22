"""Paridade com ``BaseCalculoUnificadaServiceTest`` (componentes / exato)."""

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


def _comp(
    v_prod: Decimal | None = None,
    v_frete: Decimal | None = None,
    v_seg: Decimal | None = None,
    v_outro: Decimal | None = None,
    v_ii: Decimal | None = None,
    v_is: Decimal | None = None,
    v_desc: Decimal | None = None,
    v_pis: Decimal | None = None,
    v_cofins: Decimal | None = None,
    v_icms: Decimal | None = None,
    v_icms_uf_dest: Decimal | None = None,
    v_fcp: Decimal | None = None,
    v_fcp_uf_dest: Decimal | None = None,
    v_icms_mono: Decimal | None = None,
    v_issqn: Decimal | None = None,
) -> Componentes:
    return Componentes(
        vProd=v_prod,
        vFrete=v_frete,
        vSeg=v_seg,
        vOutro=v_outro,
        vII=v_ii,
        vIS=v_is,
        vDesc=v_desc,
        vPIS=v_pis,
        vCOFINS=v_cofins,
        vICMS=v_icms,
        vICMSUFDest=v_icms_uf_dest,
        vFCP=v_fcp,
        vFCPUFDest=v_fcp_uf_dest,
        vICMSMono=v_icms_mono,
        vISSQN=v_issqn,
    )


def test_deveCalcularBCParaNFe() -> None:
    componentes = _comp(
        v_prod=Decimal("1000"),
        v_frete=Decimal("50"),
        v_seg=Decimal("20"),
        v_desc=Decimal("40"),
        v_icms=Decimal("180"),
    )
    resultado = _SERVICE.calcular(componentes, 2026, Natureza.BEM, 55)
    assert resultado.getBaseRG() == Decimal("850")


def test_deveCalcularBCParaNFCe() -> None:
    componentes = _comp(
        v_prod=Decimal("1000"),
        v_frete=Decimal("50"),
        v_ii=Decimal("150"),
        v_desc=Decimal("40"),
        v_icms=Decimal("180"),
        v_icms_uf_dest=Decimal("20"),
    )
    resultado = _SERVICE.calcular(componentes, 2026, Natureza.BEM, 65)
    assert resultado.getBaseRG() == Decimal("830")


def test_deveIgnorarCamposNaoAplicaveis() -> None:
    componentes = _comp(v_prod=Decimal("1000"), v_issqn=Decimal("20"))
    resultado_bem = _SERVICE.calcular(componentes, 2026, Natureza.BEM, 55).getBaseRG()
    resultado_servico = _SERVICE.calcular(componentes, 2026, Natureza.SERVICO, 55).getBaseRG()
    assert resultado_bem == Decimal("1000")
    assert resultado_servico == Decimal("980")


def test_deveTratarNullsComoZero() -> None:
    resultado = _SERVICE.calcular(_comp(), 2026, Natureza.BEM, 55).getBaseRG()
    assert resultado == Decimal("0")


def test_deveCalcularBCNegativa() -> None:
    componentes = _comp(v_prod=Decimal("100"), v_desc=Decimal("200"))
    resultado = _SERVICE.calcular(componentes, 2026, Natureza.BEM, 55).getBaseRG()
    assert resultado == Decimal("-100")


def test_deveCalcularViaInputDTO() -> None:
    entrada = BaseCalculoUnificadaInput()
    entrada.setAnoFatoGerador(2026)
    entrada.setTipoDocumento(55)
    entrada.setNatureza(Natureza.BEM)
    entrada.getComponentes().vProd = Decimal("1000")
    entrada.getComponentes().vDesc = Decimal("40")
    entrada.getComponentes().vICMS = Decimal("180")

    resultado = _SERVICE.calcular(entrada)
    assert resultado.getBaseRG() == Decimal("780.00")


def test_deveLancarExcecaoParaTipoDocumentoInvalido() -> None:
    entrada = BaseCalculoUnificadaInput()
    entrada.setAnoFatoGerador(2026)
    entrada.setTipoDocumento(57)
    entrada.setNatureza(Natureza.BEM)
    entrada.getComponentes().vProd = Decimal("1000")

    with pytest.raises(CampoInvalido, match="55"):
        _SERVICE.calcular(entrada)


def test_deveRetornarAvisosQuandoCamposIgnorados() -> None:
    componentes = _comp(v_prod=Decimal("1000"), v_issqn=Decimal("20"))
    resultado = _SERVICE.calcular(componentes, 2026, Natureza.BEM, 55)
    assert resultado.getAvisos()
    assert "vISSQN" in resultado.getAvisos()[0]


def test_deveLancarExcecaoParaTipoDocumentoInvalidoViaComponentes() -> None:
    componentes = _comp(v_prod=Decimal("1000"))
    with pytest.raises(CampoInvalido):
        _SERVICE.calcular(componentes, 2026, Natureza.BEM, None)
    with pytest.raises(CampoInvalido):
        _SERVICE.calcular(componentes, 2026, Natureza.BEM, 57)