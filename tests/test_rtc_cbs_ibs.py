from decimal import Decimal

from calculadora_rtc_regime_regular.cbs_ibs import Classificacao, Tratamento, calcular_cbs_ibs


def _tratamento(fracao: str) -> Tratamento:
    return Tratamento(
        expressao_aliquota="aliquota",
        expressao_base_calculo="baseCalculoInformada-impostoSeletivoInformado+impostoSeletivoCalculado",
        expressao_aliquota_efetiva="aliquota*(1-percentualReducao)*(1-pRedutorCompraGov/100)",
        expressao_tributo_calculado="baseCalculo*aliquotaEfetiva",
        expressao_tributo_devido="tributoCalculado",
        expressao_percentual_diferimento=fracao,
        expressao_valor_diferimento=f"tributoCalculado*{fracao}",
    )


def _calcular(fracao: str, base: str, aliquota: str):
    return calcular_cbs_ibs(
        aliquota_informada=Decimal(aliquota),
        base_informada=Decimal(base),
        imposto_seletivo_calculado=Decimal(0),
        imposto_seletivo_informado=None,
        redutor_compra_gov=Decimal(0),
        tratamento=_tratamento(fracao),
        classificacao=Classificacao(1, "510001", "Padrão"),
    )


def test_diferimento_de_50_por_cento() -> None:
    cbs = _calcular("0.50", "1000.00", "1")
    assert cbs is not None and cbs.diferimento is not None
    assert cbs.base_calculo == Decimal("1000.00")
    assert cbs.aliquota == Decimal("1.0000")
    assert cbs.diferimento.percentual == Decimal("50.0000")
    assert cbs.diferimento.valor == Decimal("5.00")
    assert cbs.tributo_devido == Decimal("5.00")


def test_diferimento_de_100_por_cento() -> None:
    cbs = _calcular("1.00", "1234.57", "8.8123")
    assert cbs is not None and cbs.diferimento is not None
    assert cbs.diferimento.percentual == Decimal("100.0000")
    assert cbs.diferimento.valor == Decimal("108.79")
    assert cbs.tributo_devido == Decimal("0.00")


def test_diferimento_parcial_arredonda_o_valor_uma_vez() -> None:
    cbs = _calcular("0.50", "2.90", "1")
    assert cbs is not None and cbs.diferimento is not None
    assert cbs.diferimento.valor == Decimal("0.01")
    assert cbs.tributo_devido == Decimal("0.02")
    assert cbs.tributo_devido + cbs.diferimento.valor == Decimal("0.03")
