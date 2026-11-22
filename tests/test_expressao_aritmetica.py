"""Paridade com Teste_AvaliadorExpressaoAritmetica (identidade JUnit via teste_*)."""

from decimal import Decimal

from calculadora_rtc_regime_regular.expressao import avaliar


def teste_DivisaoInteiros_DevolveFracao() -> None:
    resultado = avaliar("5/100", {})
    assert resultado == Decimal("0.05")


def teste_ExpressaoComVariaveis() -> None:
    variables = {
        "quantidade": Decimal("7720"),
        "aliquotaAdRemSecundaria": Decimal("0.1922"),
    }
    resultado = avaliar(
        "(5/100)*quantidade*0.4285714*aliquotaAdRemSecundaria",
        variables,
    )
    esperado = (
        Decimal("0.05")
        * Decimal("7720")
        * Decimal("0.4285714")
        * Decimal("0.1922")
    )
    assert resultado == esperado
    assert resultado == Decimal("31.79536930888")


def teste_DivisaoDecimaisExplicitos() -> None:
    variables = {
        "quantidade": Decimal("7720"),
        "aliquotaAdRemSecundaria": Decimal("0.1922"),
    }
    resultado = avaliar("0.05*quantidade*0.4285714*aliquotaAdRemSecundaria", variables)
    esperado = (
        Decimal("0.05")
        * Decimal("7720")
        * Decimal("0.4285714")
        * Decimal("0.1922")
    )
    assert resultado == esperado


def teste_DivisaoSimples() -> None:
    assert avaliar("1/2", {}) == Decimal("0.5")


def teste_DivisaoComplexaComVariaveis() -> None:
    assert avaliar("valor * (3/4)", {"valor": Decimal("100")}) == Decimal("75")


def teste_DivisaoQueNaoTermina_Usa34DigitosSignificativos() -> None:
    resultado = avaliar("1/3", {})
    assert len(resultado.as_tuple().digits) == 34


def teste_MultiplicacaoNaoArredonda() -> None:
    resultado = avaliar(
        "a*b",
        {
            "a": Decimal("0.12345678901"),
            "b": Decimal("0.10987654321"),
        },
    )
    assert resultado == Decimal("0.0135650052122251181221")


def teste_AliquotaEfetiva_ContaExata() -> None:
    resultado = avaliar(
        "aliquota*(1-percentualReducao)*(1-pRedutorCompraGov/100)",
        {
            "aliquota": Decimal("0.088123"),
            "percentualReducao": Decimal("0.60"),
            "pRedutorCompraGov": Decimal(0),
        },
    )
    assert resultado == Decimal("0.0352492")