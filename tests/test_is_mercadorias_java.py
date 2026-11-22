"""Paridade com Teste_BaseCalculoService_CalcularISMercadorias."""

from decimal import Decimal

import pytest

from calculadora_rtc_regime_regular.base_calculo_service import (
    CampoInvalido,
    MENSAGEM_BASE_NEGATIVA,
    EntradaIsMercadorias,
    calcular_is_mercadorias,
)


def teste_logicaCalculoCorreta() -> None:
    base = calcular_is_mercadorias(
        EntradaIsMercadorias(
            2027,
            Decimal("1000.00"),
            Decimal("50.00"),
            Decimal("20.00"),
            Decimal("10.00"),
            Decimal("30.00"),
            Decimal("40.00"),
            Decimal("25.00"),
            Decimal("15.00"),
            icms=Decimal("100.00"),
            iss=Decimal("50.00"),
            bonificacao=Decimal("20.00"),
        )
    )
    assert base == Decimal("1020.00")


def teste_baseNegativaLancaExcecao() -> None:
    with pytest.raises(CampoInvalido, match=MENSAGEM_BASE_NEGATIVA):
        calcular_is_mercadorias(
            EntradaIsMercadorias(2027, Decimal("100.00"), bonificacao=Decimal("50.00"), devolucao_vendas=Decimal("60.00"))
        )


def teste_todosCamposZeroRetornaZero() -> None:
    assert calcular_is_mercadorias(EntradaIsMercadorias(2027)) == Decimal(0)


def teste_camposIndividuaisIntegram() -> None:
    assert calcular_is_mercadorias(EntradaIsMercadorias(2027, Decimal("100.00"))) == Decimal("100.00")
    assert calcular_is_mercadorias(
        EntradaIsMercadorias(2027, Decimal("100.00"), frete_cobrado=Decimal("50.00"))
    ) == Decimal("150.00")


def teste_bonificacaoReduzBase_Art417() -> None:
    assert calcular_is_mercadorias(
        EntradaIsMercadorias(2027, Decimal("1000.00"), bonificacao=Decimal("20.00"))
    ) == Decimal("980.00")


def teste_devolucaoVendasReduzBase_Art418() -> None:
    assert calcular_is_mercadorias(
        EntradaIsMercadorias(2027, Decimal("1000.00"), devolucao_vendas=Decimal("30.00"))
    ) == Decimal("970.00")


def teste_camposIndividuaisNaoIntegram() -> None:
    assert calcular_is_mercadorias(
        EntradaIsMercadorias(2027, Decimal("1000.00"), cosip=Decimal("5.00"))
    ) == Decimal("995.00")
    assert calcular_is_mercadorias(
        EntradaIsMercadorias(2027, Decimal("1000.00"), ipi=Decimal("150.00"))
    ) == Decimal("850.00")
    assert calcular_is_mercadorias(
        EntradaIsMercadorias(2027, Decimal("1000.00"), desconto_incondicional=Decimal("50.00"))
    ) == Decimal("950.00")
    assert calcular_is_mercadorias(
        EntradaIsMercadorias(2027, Decimal("1000.00"), bonificacao=Decimal("100.00"), devolucao_vendas=Decimal("50.00"))
    ) == Decimal("850.00")


def teste_ano2026_PisCofinsDeduzidos() -> None:
    assert calcular_is_mercadorias(
        EntradaIsMercadorias(2027, Decimal("1000.00"), icms=Decimal("50.00"), iss=Decimal("30.00"))
    ) == Decimal("920.00")


def teste_anoAnterior2027_LancaExcecao() -> None:
    with pytest.raises(CampoInvalido, match="Para IS, o ano do fato gerador deve ser 2027 ou superior"):
        calcular_is_mercadorias(EntradaIsMercadorias(2026, Decimal("1000.00")))


def teste_ano2032_IssDeduzido() -> None:
    assert calcular_is_mercadorias(EntradaIsMercadorias(2032, Decimal("1000.00"), iss=Decimal("50.00"))) == Decimal(
        "950.00"
    )


def teste_ano2033_IssLancaExcecao() -> None:
    with pytest.raises(CampoInvalido, match="a partir de 2033: ISS"):
        calcular_is_mercadorias(EntradaIsMercadorias(2033, Decimal("1000.00"), iss=Decimal("50.00")))


def teste_ano2033_IssZeroNaoLancaExcecao() -> None:
    assert calcular_is_mercadorias(EntradaIsMercadorias(2033, Decimal("1000.00"), iss=Decimal(0))) == Decimal("1000.00")


def teste_icmsNaoIntegraBase_2027() -> None:
    assert calcular_is_mercadorias(
        EntradaIsMercadorias(2027, Decimal("1000.00"), icms=Decimal("180.00"))
    ) == Decimal("820.00")


def teste_icmsNaoIntegraBase_2032() -> None:
    assert calcular_is_mercadorias(
        EntradaIsMercadorias(2032, Decimal("1000.00"), icms=Decimal("120.00"), iss=Decimal("50.00"))
    ) == Decimal("830.00")


def teste_ano2033_IcmsLancaExcecao() -> None:
    with pytest.raises(CampoInvalido, match="a partir de 2033: ICMS"):
        calcular_is_mercadorias(EntradaIsMercadorias(2033, Decimal("1000.00"), icms=Decimal("100.00")))


def teste_ano2033_IcmsZeroNaoLancaExcecao() -> None:
    assert calcular_is_mercadorias(EntradaIsMercadorias(2033, Decimal("1000.00"), icms=Decimal(0))) == Decimal("1000.00")


def teste_ano2033_IcmsIssAmbosLancamExcecao() -> None:
    with pytest.raises(CampoInvalido) as erro:
        calcular_is_mercadorias(
            EntradaIsMercadorias(2033, Decimal("1000.00"), icms=Decimal("100.00"), iss=Decimal("50.00"))
        )
    assert str(erro.value).index("ICMS") < str(erro.value).index("ISS")


def teste_icmsComOutrosCamposQueNaoIntegram() -> None:
    assert calcular_is_mercadorias(
        EntradaIsMercadorias(
            2027,
            Decimal("2000.00"),
            icms=Decimal("200.00"),
            cosip=Decimal("10.00"),
            ipi=Decimal("100.00"),
            desconto_incondicional=Decimal("50.00"),
        )
    ) == Decimal("1640.00")


def teste_ano2034_IcmsLancaExcecao() -> None:
    with pytest.raises(CampoInvalido, match="ICMS"):
        calcular_is_mercadorias(EntradaIsMercadorias(2034, Decimal("1000.00"), icms=Decimal("50.00")))


def teste_mensagemErroOrdenadaAlfabeticamente() -> None:
    with pytest.raises(CampoInvalido) as erro:
        calcular_is_mercadorias(
            EntradaIsMercadorias(2033, Decimal("1000.00"), icms=Decimal("100.00"), iss=Decimal("50.00"))
        )
    assert str(erro.value).index("ICMS") < str(erro.value).index("ISS")


def teste_validacaoAntesDaSoma() -> None:
    with pytest.raises(CampoInvalido, match="2033"):
        calcular_is_mercadorias(EntradaIsMercadorias(2033, Decimal("1000.00"), icms=Decimal("100.00")))


def teste_todosOsCamposDeducaoSimultanea() -> None:
    base = calcular_is_mercadorias(
        EntradaIsMercadorias(
            2027,
            Decimal("2000.00"),
            icms=Decimal("100.00"),
            iss=Decimal("50.00"),
            cosip=Decimal("10.00"),
            ipi=Decimal("150.00"),
            desconto_incondicional=Decimal("30.00"),
            bonificacao=Decimal("20.00"),
            devolucao_vendas=Decimal("40.00"),
        )
    )
    assert base == Decimal("1600.00")