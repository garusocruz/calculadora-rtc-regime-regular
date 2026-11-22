"""Casos CalcularCibs ainda não mapeados em test_base_calculo_service."""

from decimal import Decimal

import pytest

from calculadora_rtc_regime_regular.base_calculo_service import CampoInvalido, EntradaCibs, calcular_cibs


def teste_ano2027_PisCofinsMultiplosLancaExcecao() -> None:
    with pytest.raises(CampoInvalido):
        calcular_cibs(
            EntradaCibs(
                2027,
                Decimal("1000.00"),
                pis=Decimal("10.00"),
                cofins=Decimal("20.00"),
                pis_importacao=Decimal("5.00"),
            )
        )


def teste_ano2032_IssDeduzido() -> None:
    assert calcular_cibs(EntradaCibs(2032, Decimal("1000.00"), iss=Decimal("50.00"))) == Decimal("950.00")


def teste_ano2033_IssLancaExcecao() -> None:
    with pytest.raises(CampoInvalido, match="a partir de 2033: ISS"):
        calcular_cibs(EntradaCibs(2033, Decimal("1000.00"), iss=Decimal("50.00")))


def teste_ano2033_IssZeroNaoLancaExcecao() -> None:
    assert calcular_cibs(EntradaCibs(2033, Decimal("1000.00"), iss=Decimal(0))) == Decimal("1000.00")


def teste_ano2027_TodosCamposPisCofinsLancaExcecao() -> None:
    with pytest.raises(CampoInvalido) as erro:
        calcular_cibs(
            EntradaCibs(
                2027,
                Decimal("1000.00"),
                pis=Decimal("16.50"),
                cofins=Decimal("76.00"),
                pis_importacao=Decimal("5.00"),
                cofins_importacao=Decimal("10.00"),
            )
        )
    msg = str(erro.value)
    assert "a partir de 2027" in msg
    assert "PIS" in msg and "COFINS" in msg


def teste_ano2027_CamposPisZeroNaoLancaExcecao() -> None:
    assert calcular_cibs(
        EntradaCibs(
            2027,
            Decimal("1000.00"),
            pis=Decimal(0),
            cofins=Decimal(0),
            pis_importacao=Decimal(0),
            cofins_importacao=Decimal(0),
        )
    ) == Decimal("1000.00")


def teste_icmsNaoIntegraBase_2026() -> None:
    assert calcular_cibs(EntradaCibs(2026, Decimal("1000.00"), icms=Decimal("150.00"))) == Decimal("850.00")


def teste_icmsNaoIntegraBase_2027() -> None:
    assert calcular_cibs(EntradaCibs(2027, Decimal("1000.00"), icms=Decimal("180.00"))) == Decimal("820.00")


def teste_icmsNaoIntegraBase_2032() -> None:
    assert calcular_cibs(
        EntradaCibs(2032, Decimal("1000.00"), icms=Decimal("120.00"), iss=Decimal("50.00"))
    ) == Decimal("830.00")


def teste_ano2033_IcmsLancaExcecao() -> None:
    with pytest.raises(CampoInvalido, match="a partir de 2033: ICMS"):
        calcular_cibs(EntradaCibs(2033, Decimal("1000.00"), icms=Decimal("100.00")))


def teste_ano2033_IcmsZeroNaoLancaExcecao() -> None:
    assert calcular_cibs(EntradaCibs(2033, Decimal("1000.00"), icms=Decimal(0))) == Decimal("1000.00")


def teste_ano2033_IcmsIssAmbosLancamExcecao() -> None:
    with pytest.raises(CampoInvalido) as erro:
        calcular_cibs(EntradaCibs(2033, Decimal("1000.00"), icms=Decimal("100.00"), iss=Decimal("50.00")))
    assert str(erro.value).index("ICMS") < str(erro.value).index("ISS")


def teste_icmsComOutrosCamposQueNaoIntegram() -> None:
    base = calcular_cibs(
        EntradaCibs(
            2027,
            Decimal("2000.00"),
            icms=Decimal("200.00"),
            cosip=Decimal("10.00"),
            ipi=Decimal("100.00"),
            desconto_incondicional=Decimal("50.00"),
        )
    )
    assert base == Decimal("1640.00")


def teste_ano2034_IcmsLancaExcecao() -> None:
    with pytest.raises(CampoInvalido, match="ICMS"):
        calcular_cibs(EntradaCibs(2034, Decimal("1000.00"), icms=Decimal("50.00")))


def teste_icmsComPisCofinsSomenteIcmsDeveSerDeduzido2027() -> None:
    assert calcular_cibs(EntradaCibs(2027, Decimal("1000.00"), icms=Decimal("180.00"))) == Decimal("820.00")


def teste_mensagemErroOrdenadaAlfabeticamente_IcmsIss() -> None:
    with pytest.raises(CampoInvalido) as erro:
        calcular_cibs(EntradaCibs(2033, Decimal("1000.00"), icms=Decimal("100.00"), iss=Decimal("50.00")))
    assert str(erro.value).index("ICMS") < str(erro.value).index("ISS")


def teste_todosOsCamposDeducaoSimultanea() -> None:
    base = calcular_cibs(
        EntradaCibs(
            2026,
            Decimal("3000.00"),
            pis=Decimal("20.00"),
            pis_importacao=Decimal("10.00"),
            cofins=Decimal("80.00"),
            cofins_importacao=Decimal("15.00"),
            icms=Decimal("150.00"),
            iss=Decimal("60.00"),
            cosip=Decimal("5.00"),
            ipi=Decimal("200.00"),
            desconto_incondicional=Decimal("30.00"),
        )
    )
    assert base == Decimal("2430.00")


def teste_duasValidacoesSeparadas() -> None:
    with pytest.raises(CampoInvalido, match="2027"):
        calcular_cibs(EntradaCibs(2033, Decimal("1000.00"), pis=Decimal("10.00")))

