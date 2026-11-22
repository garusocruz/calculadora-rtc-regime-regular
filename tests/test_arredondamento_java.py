"""Paridade com Teste_ArredondamentoUtils (identidade JUnit via teste_*)."""

import random
from decimal import ROUND_HALF_EVEN, Decimal

from calculadora_rtc_regime_regular.arredondamento import (
    MODO,
    CONTEXTO_DIVISAO,
    arredondar_aliquota,
    arredondar_aliquota_publicada,
    arredondar_valor_fiscal,
    dividir,
    formatar_aliquota,
    formatar_moeda,
    formatar_quantidade,
    fracao_para_percentual,
    multiplicar,
    percentual_para_fracao,
    ratear_valor_fiscal,
    subtrair,
    totalizar,
)

CBS_INTEGRAL = Decimal("1.6839379378389463610262954")


def teste_modoUnico_eHalfEven() -> None:
    assert MODO == ROUND_HALF_EVEN
    assert CONTEXTO_DIVISAO.rounding == ROUND_HALF_EVEN


def teste_multiplicarESubtrair_saoExatos_semEscalaFixa() -> None:
    assert multiplicar(Decimal("0.9"), CBS_INTEGRAL) == Decimal("1.51554414405505172492366586")
    assert subtrair(Decimal(1), Decimal("0.10")) == Decimal("0.90")
    assert multiplicar(None, Decimal(1)) is None
    assert subtrair(Decimal(1), None) is None


def teste_conversaoPercentualFracao_eExataNosDoisSentidos() -> None:
    fracao = percentual_para_fracao(CBS_INTEGRAL)
    assert fracao == Decimal("0.016839379378389463610262954")
    assert fracao_para_percentual(fracao) == CBS_INTEGRAL
    assert percentual_para_fracao(None) is None
    assert fracao_para_percentual(None) is None


def teste_valorFiscal_arredondaUmaVezA2Casas_halfEven() -> None:
    assert arredondar_valor_fiscal(Decimal("2.005")) == Decimal("2.00")
    assert arredondar_valor_fiscal(Decimal("2.015")) == Decimal("2.02")
    assert arredondar_valor_fiscal(
        multiplicar(Decimal("987654.32"), percentual_para_fracao(CBS_INTEGRAL))
    ) == Decimal("16631.49")
    assert arredondar_valor_fiscal(None) is None


def teste_valorFiscal_contaExataNaoSobeQuaseEmpate() -> None:
    exato = multiplicar(
        multiplicar(Decimal("32902.73"), Decimal("0.5")),
        percentual_para_fracao(Decimal("1.3663")),
    )
    assert exato == Decimal("224.774999995")
    assert arredondar_valor_fiscal(exato) == Decimal("224.77")


def teste_aliquotaPublicada_arredondaUmaVezA4Casas_halfEven() -> None:
    assert arredondar_aliquota_publicada(multiplicar(Decimal("8.8123"), Decimal("0.4"))) == Decimal("3.5249")
    assert arredondar_aliquota_publicada(Decimal("0.12345")) == Decimal("0.1234")
    assert arredondar_aliquota_publicada(Decimal("0.12355")) == Decimal("0.1236")
    assert arredondar_aliquota_publicada(Decimal("8.8")) == Decimal("8.8000")
    assert arredondar_aliquota_publicada(None) is None


def teste_aliquotaDoLeiaute_arredondaNasCasasDoDocumento() -> None:
    assert arredondar_aliquota(CBS_INTEGRAL, 2) == Decimal("1.68")
    assert arredondar_aliquota(CBS_INTEGRAL, None) == CBS_INTEGRAL
    assert arredondar_aliquota(None, 2) is None


def teste_totalizar_somaExata() -> None:
    assert totalizar([Decimal("2.00"), Decimal("4.41")]) == Decimal("6.41")
    assert totalizar([]) == Decimal(0)


def teste_dividir_usa34DigitosSignificativos() -> None:
    terco = dividir(Decimal(1), Decimal(3))
    assert terco is not None
    assert len(terco.as_tuple().digits) == 34
    pequeno = dividir(Decimal("0.0001"), Decimal(3))
    assert pequeno is not None
    assert len(pequeno.as_tuple().digits) == 34
    assert dividir(None, Decimal(1)) is None


def teste_ratear_parcelasSomamOTotal_centavosAoMaiorResto() -> None:
    total = Decimal("1.80")
    extensao = Decimal(33)
    exatas = [dividir(total * Decimal(trecho), extensao) for trecho in ("10", "13", "10")]
    assert ratear_valor_fiscal(exatas) == [Decimal("0.55"), Decimal("0.71"), Decimal("0.54")]
    total_ibs = Decimal("0.20")
    exatas_ibs = [dividir(total_ibs * Decimal(trecho), extensao) for trecho in ("10", "13", "10")]
    assert ratear_valor_fiscal(exatas_ibs) == [Decimal("0.06"), Decimal("0.08"), Decimal("0.06")]


def teste_ratear_casosDeBorda() -> None:
    assert ratear_valor_fiscal([]) == []
    assert ratear_valor_fiscal([Decimal(0), Decimal(0)]) == [Decimal("0.00"), Decimal("0.00")]
    assert ratear_valor_fiscal([Decimal("2.005")]) == [Decimal("2.00")]
    terco = Decimal("0.0033333333")
    assert ratear_valor_fiscal([terco, terco, terco]) == [
        Decimal("0.01"),
        Decimal("0.00"),
        Decimal("0.00"),
    ]


def teste_ratear_propriedade_somaIgualAoTotalEParcelaAMenosDeUmCentavoDaExata() -> None:
    rng = random.Random(20261117)
    centavo = Decimal("0.01")
    for _ in range(2000):
        quantidade = 1 + rng.randint(0, 11)
        exatas = [Decimal(rng.randint(0, 4_999_999)) / Decimal(1_000_000) for _ in range(quantidade)]
        parcelas = ratear_valor_fiscal(exatas)
        assert totalizar(parcelas) == arredondar_valor_fiscal(totalizar(exatas))
        for i in range(quantidade):
            assert parcelas[i].as_tuple().exponent == -2
            assert abs(parcelas[i] - exatas[i]) <= centavo


def teste_formatarMoeda_naoAlteraValorFiscalJaArredondado() -> None:
    rng = random.Random(20261117)
    for _ in range(2000):
        valor = arredondar_valor_fiscal(Decimal(rng.randint(0, 999_999_999_999)) / Decimal(100_000))
        assert Decimal(formatar_moeda(valor)) == valor
    assert formatar_moeda(Decimal("804.37")) == "804.37"
    assert formatar_moeda(Decimal(0)) == "0.00"
    assert formatar_moeda(Decimal("0E-8")) == "0.00"


def teste_formatarAliquota_apresentaDe2a4Casas() -> None:
    assert formatar_aliquota(CBS_INTEGRAL) == "1.6839"
    assert formatar_aliquota(Decimal("0.01867380622521988789135487")) == "0.0187"
    assert formatar_aliquota(Decimal("2.8780")) == "2.878"
    assert formatar_aliquota(Decimal(0)) == "0.00"
    assert formatar_aliquota(Decimal("60.0000")) == "60.00"


def teste_formatarAliquota_naoAlteraAliquotaPublicada() -> None:
    rng = random.Random(20261117)
    for _ in range(2000):
        aliquota = arredondar_aliquota_publicada(Decimal(rng.randint(0, 99_999_999)) / Decimal(1_000_000))
        assert Decimal(formatar_aliquota(aliquota)) == aliquota


def teste_formatarQuantidade_inteiroOu4Casas() -> None:
    assert formatar_quantidade(Decimal("1000.000")) == "1000"
    assert formatar_quantidade(Decimal("55.55")) == "55.5500"
    assert formatar_quantidade(Decimal("0.0001")) == "0.0001"