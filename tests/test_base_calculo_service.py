from decimal import Decimal

import pytest

from calculadora_rtc_regime_regular.base_calculo_service import (
    MENSAGEM_BASE_NEGATIVA,
    CampoInvalido,
    EntradaCibs,
    EntradaIsMercadorias,
    calcular_cibs,
    calcular_is_mercadorias,
)


def test_cibs_soma_o_que_integra_e_deduz_icms_e_iss() -> None:
    base = calcular_cibs(
        EntradaCibs(
            2027,
            Decimal("1000.00"),
            Decimal("50.00"),
            Decimal("20.00"),
            Decimal("10.00"),
            Decimal("30.00"),
            Decimal("40.00"),
            Decimal("100.00"),
            Decimal("25.00"),
            Decimal("15.00"),
            icms=Decimal("100.00"),
            iss=Decimal("50.00"),
        )
    )
    assert base == Decimal("1140.00")


def test_cibs_negativa_rejeita() -> None:
    with pytest.raises(CampoInvalido, match=MENSAGEM_BASE_NEGATIVA):
        calcular_cibs(EntradaCibs(2027, Decimal("100.00"), icms=Decimal("200.00")))


def test_cibs_zerada() -> None:
    assert calcular_cibs(EntradaCibs(2027)) == Decimal(0)


def test_cibs_cada_campo_que_integra() -> None:
    assert calcular_cibs(EntradaCibs(2027, Decimal("100.00"))) == Decimal("100.00")
    assert calcular_cibs(EntradaCibs(2027, Decimal("100.00"), imposto_seletivo=Decimal("50.00"))) == Decimal("150.00")


def test_cibs_cada_campo_que_nao_integra() -> None:
    assert calcular_cibs(EntradaCibs(2027, Decimal("1000.00"), cosip=Decimal("5.00"))) == Decimal("995.00")
    assert calcular_cibs(EntradaCibs(2027, Decimal("1000.00"), ipi=Decimal("150.00"))) == Decimal("850.00")
    assert calcular_cibs(EntradaCibs(2027, Decimal("1000.00"), desconto_incondicional=Decimal("50.00"))) == Decimal("950.00")


def test_cibs_em_2026_deduz_pis_e_cofins() -> None:
    base = calcular_cibs(
        EntradaCibs(
            2026,
            Decimal("1000.00"),
            pis=Decimal("16.50"),
            cofins=Decimal("76.00"),
            pis_importacao=Decimal("5.00"),
            cofins_importacao=Decimal("10.00"),
        )
    )
    assert base == Decimal("892.50")


def test_cibs_antes_de_2026_rejeita() -> None:
    with pytest.raises(CampoInvalido, match="Para CBS/IBS, o ano do fato gerador deve ser 2026 ou superior"):
        calcular_cibs(EntradaCibs(2025, Decimal("1000.00")))


@pytest.mark.parametrize(
    "campo",
    ["pis", "cofins", "pis_importacao", "cofins_importacao"],
)
def test_cibs_em_2027_rejeita_pis_e_cofins(campo: str) -> None:
    with pytest.raises(CampoInvalido, match="2027"):
        calcular_cibs(EntradaCibs(2027, Decimal("1000.00"), **{campo: Decimal("10.00")}))


def test_cibs_iss_ate_2032_deduz_e_em_2033_rejeita() -> None:
    assert calcular_cibs(EntradaCibs(2032, Decimal("1000.00"), iss=Decimal("50.00"))) == Decimal("950.00")
    with pytest.raises(CampoInvalido, match="a partir de 2033: ISS"):
        calcular_cibs(EntradaCibs(2033, Decimal("1000.00"), iss=Decimal("50.00")))
    assert calcular_cibs(EntradaCibs(2033, Decimal("1000.00"), iss=Decimal(0))) == Decimal("1000.00")


def test_cibs_icms_deduz_ate_2032_e_rejeita_em_2033() -> None:
    assert calcular_cibs(EntradaCibs(2026, Decimal("1000.00"), icms=Decimal("150.00"))) == Decimal("850.00")
    assert calcular_cibs(EntradaCibs(2027, Decimal("1000.00"), icms=Decimal("180.00"))) == Decimal("820.00")
    assert calcular_cibs(EntradaCibs(2032, Decimal("1000.00"), icms=Decimal("120.00"), iss=Decimal("50.00"))) == Decimal("830.00")
    with pytest.raises(CampoInvalido, match="a partir de 2033: ICMS"):
        calcular_cibs(EntradaCibs(2033, Decimal("1000.00"), icms=Decimal("100.00")))
    assert calcular_cibs(EntradaCibs(2033, Decimal("1000.00"), icms=Decimal(0))) == Decimal("1000.00")
    with pytest.raises(CampoInvalido, match="ICMS") as erro:
        calcular_cibs(EntradaCibs(2034, Decimal("1000.00"), icms=Decimal("50.00")))
    assert "ICMS" in str(erro.value)


def test_cibs_mensagem_lista_os_campos_em_ordem() -> None:
    with pytest.raises(CampoInvalido) as pis:
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
    texto = str(pis.value)
    assert texto.startswith("Os seguintes campos não podem ser informados a partir de 2027:")
    assert texto.index("COFINS,") < texto.index("COFINS Importação") < texto.index("PIS,") < texto.index("PIS Importação")
    with pytest.raises(CampoInvalido) as icms:
        calcular_cibs(EntradaCibs(2033, Decimal("1000.00"), icms=Decimal("100.00"), iss=Decimal("50.00")))
    assert str(icms.value).index("ICMS") < str(icms.value).index("ISS")


def test_cibs_deduz_todos_os_campos_de_2026() -> None:
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


def test_cibs_valida_o_pis_antes_da_soma_e_antes_do_icms() -> None:
    with pytest.raises(CampoInvalido, match="2027"):
        calcular_cibs(EntradaCibs(2033, Decimal("1000.00"), pis=Decimal("10.00")))


def test_is_mercadorias_soma_e_deduz() -> None:
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


def test_is_mercadorias_negativa_e_ano() -> None:
    with pytest.raises(CampoInvalido, match=MENSAGEM_BASE_NEGATIVA):
        calcular_is_mercadorias(EntradaIsMercadorias(2027, Decimal("100.00"), bonificacao=Decimal("50.00"), devolucao_vendas=Decimal("60.00")))
    assert calcular_is_mercadorias(EntradaIsMercadorias(2027)) == Decimal(0)
    with pytest.raises(CampoInvalido, match="Para IS, o ano do fato gerador deve ser 2027 ou superior"):
        calcular_is_mercadorias(EntradaIsMercadorias(2026, Decimal("1000.00")))
