"""O pin oficial fica no pacote, e o JSON não perde dígito no float."""

from decimal import Decimal

from calculadora_rtc_regime_regular import (
    PIN_OFICIAL_COMMIT,
    PIN_OFICIAL_DATA,
    PIN_OFICIAL_VERSAO,
)
from calculadora_rtc_regime_regular.processamento_item import operacao_input_from_json_text
from calculadora_rtc_regime_regular.versao_offline import VersaoOutput


def test_pin_oficial_e_o_calculador_1_7_2() -> None:
    assert PIN_OFICIAL_VERSAO == "1.7.2"
    assert PIN_OFICIAL_COMMIT == "f1eebd7ce3157423b1a6aaca7dc1d6c3395452c4"
    assert PIN_OFICIAL_DATA == "2026-11-19"


def test_json_de_texto_preserva_decimal_que_o_float_perde() -> None:
    operacao = operacao_input_from_json_text(
        '{"itens":[{"baseCalculo": 1234567890123456789.25}]}'
    )
    assert operacao.itens[0].base_calculo == Decimal("1234567890123456789.25")


def test_versao_remota_nao_guarda_float() -> None:
    versao = VersaoOutput.from_json({"versaoDb": Decimal("1.25")})
    assert versao.versao_db == "1.25"
    assert not isinstance(versao.versao_db, float)
