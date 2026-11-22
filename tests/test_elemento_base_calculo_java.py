"""Paridade com ``ElementoBaseCalculoTest`` (getValor em ``Componentes``)."""

from __future__ import annotations

from decimal import Decimal

from calculadora_rtc_regime_regular.base_calculo import Componentes, ElementoBaseCalculo


def _criar_componentes(*valores: Decimal | None) -> Componentes:
    nomes = (
        "vProd",
        "vFrete",
        "vSeg",
        "vOutro",
        "vII",
        "vIS",
        "vDesc",
        "vPIS",
        "vCOFINS",
        "vICMS",
        "vICMSUFDest",
        "vFCP",
        "vFCPUFDest",
        "vICMSMono",
        "vISSQN",
    )
    kwargs = {nome: valores[i] for i, nome in enumerate(nomes) if i < len(valores) and valores[i] is not None}
    return Componentes(**kwargs)


def test_deveMapearTodosOs15CamposCorretamente() -> None:
    comp = _criar_componentes(
        Decimal("1000"),
        Decimal("50"),
        Decimal("20"),
        Decimal("10"),
        Decimal("150"),
        Decimal("30"),
        Decimal("40"),
        Decimal("9.25"),
        Decimal("46.25"),
        Decimal("180"),
        Decimal("20"),
        Decimal("5"),
        Decimal("3"),
        Decimal("100"),
        Decimal("35"),
    )
    assert comp.get_valor(ElementoBaseCalculo.V_PROD) == Decimal("1000")
    assert comp.get_valor(ElementoBaseCalculo.V_FRETE) == Decimal("50")
    assert comp.get_valor(ElementoBaseCalculo.V_SEG) == Decimal("20")
    assert comp.get_valor(ElementoBaseCalculo.V_OUTRO) == Decimal("10")
    assert comp.get_valor(ElementoBaseCalculo.V_II) == Decimal("150")
    assert comp.get_valor(ElementoBaseCalculo.V_IS) == Decimal("30")
    assert comp.get_valor(ElementoBaseCalculo.V_DESC) == Decimal("40")
    assert comp.get_valor(ElementoBaseCalculo.V_PIS) == Decimal("9.25")
    assert comp.get_valor(ElementoBaseCalculo.V_COFINS) == Decimal("46.25")
    assert comp.get_valor(ElementoBaseCalculo.V_ICMS) == Decimal("180")
    assert comp.get_valor(ElementoBaseCalculo.V_ICMS_UF_DEST) == Decimal("20")
    assert comp.get_valor(ElementoBaseCalculo.V_FCP) == Decimal("5")
    assert comp.get_valor(ElementoBaseCalculo.V_FCP_UF_DEST) == Decimal("3")
    assert comp.get_valor(ElementoBaseCalculo.V_ICMS_MONO) == Decimal("100")
    assert comp.get_valor(ElementoBaseCalculo.V_ISSQN) == Decimal("35")


def test_deveRetornarNullQuandoCampoNaoInformado() -> None:
    comp = Componentes()
    for elemento in ElementoBaseCalculo:
        assert comp.get_valor(elemento) is None