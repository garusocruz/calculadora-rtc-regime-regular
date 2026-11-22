from decimal import Decimal

import pytest

from calculadora_rtc_regime_regular.base_calculo_service import CampoInvalido
from calculadora_rtc_regime_regular.nfse_base import EntradaNfse, calcular_base_nfse


def test_nfse_em_2026_deduz_pis_cofins_e_iss() -> None:
    base = calcular_base_nfse(
        EntradaNfse(
            2026,
            Decimal("1000.00"),
            Decimal("50.00"),
            Decimal("20.00"),
            Decimal("10.00"),
            Decimal("80.00"),
            Decimal("16.50"),
            Decimal("76.00"),
        )
    )
    assert base == Decimal("747.50")


def test_nfse_em_2027_deduz_iss_sem_pis() -> None:
    base = calcular_base_nfse(
        EntradaNfse(2027, Decimal("1000.00"), Decimal("50.00"), Decimal("20.00"), Decimal("10.00"), Decimal("80.00"))
    )
    assert base == Decimal("840.00")


def test_nfse_em_2033_sem_iss() -> None:
    assert calcular_base_nfse(EntradaNfse(2033, Decimal("1000.00"), Decimal("50.00"), Decimal("20.00"), Decimal("10.00"))) == Decimal("920.00")


def test_nfse_negativa_e_ano_minimo() -> None:
    with pytest.raises(CampoInvalido, match="maiores que o valor do serviço"):
        calcular_base_nfse(EntradaNfse(2026, Decimal("100.00"), Decimal("200.00")))
    with pytest.raises(CampoInvalido, match="O ano do fato gerador deve ser 2026 ou superior"):
        calcular_base_nfse(EntradaNfse(2025, Decimal("1000.00")))
    with pytest.raises(CampoInvalido, match="ano do fato gerador"):
        calcular_base_nfse(EntradaNfse(2020, Decimal("1000.00"), Decimal("50.00")))


def test_nfse_cada_deducao_e_transicao() -> None:
    assert calcular_base_nfse(EntradaNfse(2026, Decimal("1000.00"), Decimal("100.00"))) == Decimal("900.00")
    assert calcular_base_nfse(EntradaNfse(2026, Decimal("1000.00"), reembolso=Decimal("50.00"))) == Decimal("950.00")
    assert calcular_base_nfse(EntradaNfse(2026, Decimal("1000.00"), deducao=Decimal("75.00"))) == Decimal("925.00")
    assert calcular_base_nfse(EntradaNfse(2026, Decimal("1000.00"), iss=Decimal("80.00"))) == Decimal("920.00")
    assert calcular_base_nfse(EntradaNfse(2026, Decimal("1000.00"), pis=Decimal("16.50"), cofins=Decimal("76.00"))) == Decimal("907.50")
    with pytest.raises(CampoInvalido):
        calcular_base_nfse(EntradaNfse(2027, Decimal("1000.00"), pis=Decimal("16.50"), cofins=Decimal("76.00")))


def test_nfse_extincao_de_pis_e_de_iss() -> None:
    with pytest.raises(CampoInvalido, match="2027"):
        calcular_base_nfse(EntradaNfse(2027, Decimal("500.00"), pis=Decimal("10.00")))
    with pytest.raises(CampoInvalido, match="2027"):
        calcular_base_nfse(EntradaNfse(2030, Decimal("500.00"), pis=Decimal("10.00"), cofins=Decimal("20.00")))
    with pytest.raises(CampoInvalido, match="2033"):
        calcular_base_nfse(EntradaNfse(2033, Decimal("1000.00"), iss=Decimal("80.00")))
    with pytest.raises(CampoInvalido, match="2033"):
        calcular_base_nfse(EntradaNfse(2034, Decimal("1000.00"), Decimal("50.00"), iss=Decimal("80.00")))
    assert calcular_base_nfse(EntradaNfse(2033, Decimal("1000.00"), iss=Decimal(0))) == Decimal("1000.00")
    assert calcular_base_nfse(EntradaNfse(2027, Decimal("1000.00"), pis=Decimal(0), cofins=Decimal(0))) == Decimal("1000.00")
    assert calcular_base_nfse(EntradaNfse(2032, Decimal("1000.00"), iss=Decimal("50.00"))) == Decimal("950.00")


def test_nfse_mensagem_ordena_cofins_antes_de_pis() -> None:
    with pytest.raises(CampoInvalido) as erro:
        calcular_base_nfse(EntradaNfse(2027, Decimal("1000.00"), pis=Decimal("10.00"), cofins=Decimal("20.00")))
    texto = str(erro.value)
    assert "a partir de 2027" in texto
    assert texto.index("COFINS") < texto.index("PIS")
    with pytest.raises(CampoInvalido) as so_pis:
        calcular_base_nfse(EntradaNfse(2033, Decimal("1000.00"), pis=Decimal("10.00")))
    assert "PIS" in str(so_pis.value) and "2027" in str(so_pis.value)
    assert "ISS" not in str(so_pis.value) and "2033" not in str(so_pis.value)


def test_nfse_todos_os_campos_em_2026_e_2032() -> None:
    assert calcular_base_nfse(
        EntradaNfse(2026, Decimal("2000.00"), Decimal("100.00"), Decimal("50.00"), Decimal("30.00"), Decimal("80.00"), Decimal("16.50"), Decimal("76.00"))
    ) == Decimal("1647.50")
    assert calcular_base_nfse(
        EntradaNfse(2026, Decimal("1000.00"), pis=Decimal("10.00"), cofins=Decimal("20.00"), iss=Decimal("50.00"))
    ) == Decimal("920.00")
    assert calcular_base_nfse(
        EntradaNfse(2026, Decimal("2000.00"), Decimal("100.00"), Decimal("50.00"), Decimal("30.00"), Decimal("60.00"), Decimal("20.00"), Decimal("80.00"))
    ) == Decimal("1660.00")
    assert calcular_base_nfse(
        EntradaNfse(2032, Decimal("1500.00"), Decimal("100.00"), Decimal("50.00"), Decimal("30.00"), Decimal("60.00"))
    ) == Decimal("1260.00")
    assert calcular_base_nfse(EntradaNfse(2026, Decimal(0))) == Decimal(0)
