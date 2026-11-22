from datetime import date
from decimal import Decimal

import pytest

from calculadora_rtc_regime_regular.aliquota_resultado import (
    AliquotaNegativa,
    AliquotaPadraoNaoEncontrada,
    AliquotaReferenciaNaoEncontrada,
    AliquotaResultado,
    FormaAplicacao,
    FormaAplicacaoNaoDefinida,
)
from calculadora_rtc_regime_regular.cbs_ibs import buscar_aliquota_padrao


def test_referencia_sozinha_permanece() -> None:
    resultado = AliquotaResultado(Decimal("10.50"))
    assert resultado.valor_referencia == Decimal("10.50")
    assert resultado.valor_padrao is None
    assert resultado.forma_aplicacao is None
    assert resultado.valor_aplicavel() == Decimal("10.50")


def test_valor_aplicavel_sem_padrao_e_a_referencia() -> None:
    resultado = AliquotaResultado(Decimal("15.75"))
    assert resultado.valor_aplicavel() == Decimal("15.75")


def test_acrescimo_soma_e_guarda_o_aplicavel() -> None:
    resultado = AliquotaResultado(Decimal("100.00"), Decimal("5.00"), FormaAplicacao.ACRESCIMO)
    assert resultado.valor_padrao == Decimal("105.00")
    assert resultado.valor_referencia == Decimal("100.00")
    assert AliquotaResultado(Decimal("50.00"), Decimal("10.00"), FormaAplicacao.ACRESCIMO).valor_aplicavel() == Decimal("60.00")


def test_decrescimo_subtrai_e_guarda_o_aplicavel() -> None:
    resultado = AliquotaResultado(Decimal("100.00"), Decimal("15.00"), FormaAplicacao.DECRESCIMO)
    assert resultado.valor_padrao == Decimal("85.00")
    assert resultado.valor_referencia == Decimal("100.00")
    assert AliquotaResultado(Decimal("80.00"), Decimal("20.00"), FormaAplicacao.DECRESCIMO).valor_aplicavel() == Decimal("60.00")


def test_referencia_ausente() -> None:
    with pytest.raises(AliquotaReferenciaNaoEncontrada):
        AliquotaResultado(None, Decimal("10.00"), FormaAplicacao.ACRESCIMO)  # type: ignore[arg-type]


def test_padrao_sem_forma() -> None:
    with pytest.raises(FormaAplicacaoNaoDefinida):
        AliquotaResultado(Decimal("100.00"), Decimal("10.00"), None)


def test_forma_sem_padrao() -> None:
    with pytest.raises(AliquotaPadraoNaoEncontrada):
        AliquotaResultado(Decimal("100.00"), None, FormaAplicacao.ACRESCIMO)


def test_decimais_de_acrescimo_e_decrescimo() -> None:
    assert AliquotaResultado(Decimal("12.345"), Decimal("2.655"), FormaAplicacao.ACRESCIMO).valor_padrao == Decimal("15.000")
    assert AliquotaResultado(Decimal("25.750"), Decimal("5.250"), FormaAplicacao.DECRESCIMO).valor_padrao == Decimal("20.500")


def test_acrescimo_e_decrescimo_de_zero() -> None:
    acrescimo = AliquotaResultado(Decimal("50.00"), Decimal(0), FormaAplicacao.ACRESCIMO)
    decrescimo = AliquotaResultado(Decimal("50.00"), Decimal(0), FormaAplicacao.DECRESCIMO)
    assert acrescimo.valor_padrao == Decimal("50.00")
    assert acrescimo.valor_aplicavel() == Decimal("50.00")
    assert decrescimo.valor_padrao == Decimal("50.00")
    assert decrescimo.valor_aplicavel() == Decimal("50.00")


def test_valores_negativos() -> None:
    with pytest.raises(AliquotaNegativa):
        AliquotaResultado(Decimal("-10.00"))
    with pytest.raises(AliquotaNegativa):
        AliquotaResultado(Decimal("100.00"), Decimal("-10.00"), FormaAplicacao.ACRESCIMO)
    with pytest.raises(AliquotaNegativa):
        AliquotaResultado(Decimal("10.00"), Decimal("15.00"), FormaAplicacao.DECRESCIMO)


def test_muitas_casas_e_igualdade() -> None:
    preciso = AliquotaResultado(Decimal("123.456789"), Decimal("0.000001"), FormaAplicacao.ACRESCIMO)
    assert preciso.valor_padrao == Decimal("123.456790")
    um = AliquotaResultado(Decimal("100.00"), Decimal("10.00"), FormaAplicacao.ACRESCIMO)
    outro = AliquotaResultado(Decimal("100.00"), Decimal("10.00"), FormaAplicacao.ACRESCIMO)
    assert um == outro
    assert hash(um) == hash(outro)
    assert "50.00" in str(AliquotaResultado(Decimal("50.00")))


def test_substituicao_guarda_o_padrao() -> None:
    resultado = AliquotaResultado(Decimal("100.00"), Decimal("25.00"), FormaAplicacao.SUBSTITUICAO)
    assert resultado.valor_padrao == Decimal("25.00")
    assert resultado.valor_referencia == Decimal("100.00")
    assert AliquotaResultado(Decimal("50.00"), Decimal("30.00"), FormaAplicacao.SUBSTITUICAO).valor_aplicavel() == Decimal("30.00")
    maior = AliquotaResultado(Decimal("10.00"), Decimal("50.00"), FormaAplicacao.SUBSTITUICAO)
    assert maior.valor_padrao == Decimal("50.00")
    assert maior.valor_aplicavel() == Decimal("50.00")
    menor = AliquotaResultado(Decimal("80.00"), Decimal("15.00"), FormaAplicacao.SUBSTITUICAO)
    assert menor.valor_aplicavel() == Decimal("15.00")
    fracao = AliquotaResultado(Decimal("45.678"), Decimal("12.345"), FormaAplicacao.SUBSTITUICAO)
    assert fracao.valor_aplicavel() == Decimal("12.345")
    zero = AliquotaResultado(Decimal("50.00"), Decimal(0), FormaAplicacao.SUBSTITUICAO)
    assert zero.valor_aplicavel() == Decimal(0)


def test_extremos_das_formas() -> None:
    grande = AliquotaResultado(Decimal("9999999.99"), Decimal("0.01"), FormaAplicacao.ACRESCIMO)
    assert grande.valor_aplicavel() == Decimal("10000000.00")
    assert AliquotaResultado(Decimal("100.00"), Decimal("100.00"), FormaAplicacao.DECRESCIMO).valor_aplicavel() == Decimal("0.00")
    assert AliquotaResultado(Decimal(0), Decimal("25.00"), FormaAplicacao.ACRESCIMO).valor_aplicavel() == Decimal("25.00")
    with pytest.raises(AliquotaNegativa):
        AliquotaResultado(Decimal(0), Decimal("10.00"), FormaAplicacao.DECRESCIMO)
    igual = AliquotaResultado(Decimal("75.50"), Decimal("75.50"), FormaAplicacao.SUBSTITUICAO)
    assert igual.valor_aplicavel() == Decimal("75.50")
    assert AliquotaResultado(Decimal("1.123456789"), Decimal("2.876543211"), FormaAplicacao.ACRESCIMO).valor_padrao == Decimal("4.000000000")
    pequeno = AliquotaResultado(Decimal("10.000001"), Decimal("10.000000"), FormaAplicacao.DECRESCIMO)
    assert pequeno.valor_aplicavel() == Decimal("0.000001")
    assert AliquotaResultado(Decimal(0)).valor_aplicavel() == Decimal(0)
    assert AliquotaResultado(Decimal("0.5"), Decimal("0.3"), FormaAplicacao.ACRESCIMO).valor_aplicavel() == Decimal("0.8")
    assert AliquotaResultado(Decimal("0.9"), Decimal("0.4"), FormaAplicacao.DECRESCIMO).valor_aplicavel() == Decimal("0.5")
    assert AliquotaResultado(Decimal("10.0"), Decimal("0.25"), FormaAplicacao.SUBSTITUICAO).valor_aplicavel() == Decimal("0.25")
    assert AliquotaResultado(Decimal("0.01"), Decimal("0.01"), FormaAplicacao.ACRESCIMO).valor_padrao == Decimal("0.02")
    referencia = Decimal("100.00")
    padrao = Decimal("10.00")
    assert AliquotaResultado(referencia, padrao, FormaAplicacao.ACRESCIMO).valor_padrao == Decimal("110.00")
    assert AliquotaResultado(referencia, padrao, FormaAplicacao.DECRESCIMO).valor_padrao == Decimal("90.00")
    assert AliquotaResultado(referencia, padrao, FormaAplicacao.SUBSTITUICAO).valor_padrao == Decimal("10.00")


def test_busca_da_aliquota_padrao_converte_o_aplicavel() -> None:
    dia = date(2026, 1, 1)
    chamadas: list[tuple[int, int | None, int | None, date]] = []

    def buscar(id_tributo: int, uf: int | None, municipio: int | None, data: date) -> AliquotaResultado:
        chamadas.append((id_tributo, uf, municipio, data))
        tabela = {
            (1, 35, 3550308, dia): AliquotaResultado(Decimal("26.50")),
            (1, 33, 3550308, dia): AliquotaResultado(Decimal("24.00")),
            (2, 35, 3550308, dia): AliquotaResultado(Decimal("25.00")),
            (1, 35, 3550308, date(2027, 6, 15)): AliquotaResultado(Decimal("28.00")),
        }
        return tabela[(id_tributo, uf, municipio, data)]

    assert buscar_aliquota_padrao(1, 35, 3550308, dia, buscar) == Decimal("0.265")
    assert buscar_aliquota_padrao(2, 35, 3550308, dia, buscar) == Decimal("0.25")
    assert buscar_aliquota_padrao(1, 33, 3550308, dia, buscar) == Decimal("0.24")
    assert buscar_aliquota_padrao(1, 35, 3550308, date(2027, 6, 15), buscar) == Decimal("0.28")
    assert chamadas[0] == (1, 35, 3550308, dia)


def test_busca_aplica_a_forma_antes_de_dividir_por_cem() -> None:
    dia = date(2026, 1, 1)

    def buscar(id_tributo: int, uf: int | None, municipio: int | None, data: date) -> AliquotaResultado:
        casos = {
            "acrescimo": AliquotaResultado(Decimal("26.50"), Decimal("1.50"), FormaAplicacao.ACRESCIMO),
            "decrescimo": AliquotaResultado(Decimal("26.50"), Decimal("1.50"), FormaAplicacao.DECRESCIMO),
            "substituicao": AliquotaResultado(Decimal("26.50"), Decimal("12.75"), FormaAplicacao.SUBSTITUICAO),
            "zero": AliquotaResultado(Decimal("0.00")),
            "preciso": AliquotaResultado(Decimal("17.345")),
            "substituicao_zero": AliquotaResultado(Decimal("26.50"), Decimal("0.00"), FormaAplicacao.SUBSTITUICAO),
            "acrescimo_preciso": AliquotaResultado(Decimal("15.123"), Decimal("2.877"), FormaAplicacao.ACRESCIMO),
            "decrescimo_preciso": AliquotaResultado(Decimal("20.500"), Decimal("5.250"), FormaAplicacao.DECRESCIMO),
            "cem": AliquotaResultado(Decimal("100.00")),
        }
        return casos[str(id_tributo)]

    assert buscar_aliquota_padrao("acrescimo", 35, 3550308, dia, buscar) == Decimal("0.28")  # type: ignore[arg-type]
    assert buscar_aliquota_padrao("decrescimo", 35, 3550308, dia, buscar) == Decimal("0.25")  # type: ignore[arg-type]
    assert buscar_aliquota_padrao("substituicao", 35, 3550308, dia, buscar) == Decimal("0.1275")  # type: ignore[arg-type]
    assert buscar_aliquota_padrao("zero", 35, 3550308, dia, buscar) == Decimal(0)  # type: ignore[arg-type]
    assert buscar_aliquota_padrao("preciso", 35, 3550308, dia, buscar) == Decimal("0.17345")  # type: ignore[arg-type]
    assert buscar_aliquota_padrao("substituicao_zero", 35, 3550308, dia, buscar) == Decimal(0)  # type: ignore[arg-type]
    assert buscar_aliquota_padrao("acrescimo_preciso", 35, 3550308, dia, buscar) == Decimal("0.18")  # type: ignore[arg-type]
    assert buscar_aliquota_padrao("decrescimo_preciso", 35, 3550308, dia, buscar) == Decimal("0.1525")  # type: ignore[arg-type]
    assert buscar_aliquota_padrao("cem", 35, 3550308, dia, buscar) == Decimal("1.0000")  # type: ignore[arg-type]
