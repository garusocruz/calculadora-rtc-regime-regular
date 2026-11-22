"""Paridade com testes Java em ``br.gov.serpro.rtc.config.serializer``."""

from __future__ import annotations

import json
from datetime import date, datetime
from decimal import Decimal

import pytest

from calculadora_rtc_regime_regular.deserializadores import (
    ErroFormatoInvalido,
    build_regime_geral_payload,
    deserializar_local_date,
    deserializar_offset_date_time,
    deserializar_offset_date_time_json_string,
    operacao_regime_geral_from_dh,
    serializar_quantidade_tdec,
)

_VALID_OFFSET = (
    "2026-01-15T13:45:00-03:00",
    "2026-05-22T10:57:23Z",
)

_INVALID_OFFSET = (
    "2026-01-15T13:45:00+0300",
    "2026-01-15T13:45:00+03",
    "2026-01-15T13:45:00.000-03:00",
    "2026-01-15T13:45:00.123456-03:00",
    "2026-01-15T13:45:00+03:00[Europe/Moscow]",
    "2026-01-15T13:45:00",
    "2026-01-15 13:45:00",
    "2026-02-28T25:45:00.000-03:00",
    "2026-02-28T25:45:00.000Z",
    "2026-02-28T25:45-03:00",
    "2026-02-30T13:45:00-03:00",
    "2026-02-28T25:45:00-03:00",
    "QUALQUERCOISAQUENAOSEJAUMADATAHORA",
)

_INVALID_LOCAL_DATE = (
    "15/01/2026",
    "2026-02-30",
    "2026-13-01",
    "2026-01-32",
    "2026-00-15",
    "2026-01-00",
    "2026-01-1",
    "2026-1-15",
    "2026/01/15",
    "abcd-ef-gh",
)

_TDCE_CENARIOS = (
    ("1000", "1000"),
    ("1", "1"),
    ("55.55", "55.5500"),
    ("55.5555", "55.5555"),
    ("55.550", "55.5500"),
    ("55.5500", "55.5500"),
    ("0.0001", "0.0001"),
    ("0.1", "0.1000"),
    ("0", "0"),
)


def _esperado_offset(valid: str) -> datetime:
    texto = valid[:-1] + "+00:00" if valid.endswith("Z") else valid
    return datetime.fromisoformat(texto)


@pytest.mark.parametrize("valid", _VALID_OFFSET, ids=[str(i) for i in range(1, 3)])
def test_shouldDeserializeValidOffsetDateTime(valid: str) -> None:
    resultado = deserializar_offset_date_time(valid, "nomeCampoData")
    assert resultado == _esperado_offset(valid)


@pytest.mark.parametrize("invalid", _INVALID_OFFSET, ids=[str(i) for i in range(1, 14)])
def test_shouldThrowExceptionForInvalidOffsetDateTime(invalid: str) -> None:
    with pytest.raises(ErroFormatoInvalido) as exc:
        deserializar_offset_date_time(invalid, "nomeCampoData")
    msg = str(exc.value)
    assert "nomeCampoData" in msg
    assert "Formato esperado" in msg


@pytest.mark.parametrize("valid", _VALID_OFFSET, ids=[str(i) for i in range(1, 3)])
def test_shouldUseApplicationJacksonDeserializerForValidDateTime(valid: str) -> None:
    operacao = operacao_regime_geral_from_dh(valid)
    assert operacao.dh_fato_gerador == _esperado_offset(valid)


@pytest.mark.parametrize("invalid", _INVALID_OFFSET, ids=[str(i) for i in range(1, 14)])
def test_shouldRejectInvalidDateTimeByCustomRule(invalid: str) -> None:
    with pytest.raises(ErroFormatoInvalido) as exc:
        operacao_regime_geral_from_dh(invalid)
    msg = str(exc.value)
    assert "dhFatoGerador" in msg
    assert "Formato esperado" in msg
    assert "yyyy-MM-dd'T'HH:mm:ssXXX" in msg


@pytest.mark.parametrize("valid", _VALID_OFFSET, ids=[str(i) for i in range(1, 3)])
def test_shouldDeserializeValidOffsetDateTimeJackson(valid: str) -> None:
    resultado = deserializar_offset_date_time_json_string(f'"{valid}"')
    assert resultado == _esperado_offset(valid)


@pytest.mark.parametrize("invalid", _INVALID_OFFSET, ids=[str(i) for i in range(1, 14)])
def test_shouldRejectInvalidOffsetDateTimeWithCustomMessage(invalid: str) -> None:
    with pytest.raises(ErroFormatoInvalido) as exc:
        deserializar_offset_date_time_json_string(f'"{invalid}"')
    msg = str(exc.value)
    assert "Formato esperado" in msg
    assert "yyyy-MM-dd'T'HH:mm:ssXXX" in msg


def test_shouldDeserializeValidDate() -> None:
    resultado = deserializar_local_date("2026-01-15", "nomeCampoData")
    assert resultado == date(2026, 1, 15)


@pytest.mark.parametrize("invalid", _INVALID_LOCAL_DATE, ids=[str(i) for i in range(1, 11)])
def test_shouldThrowExceptionForInvalidDate(invalid: str) -> None:
    with pytest.raises(ErroFormatoInvalido) as exc:
        deserializar_local_date(invalid, "nomeCampoData")
    msg = str(exc.value)
    assert "nomeCampoData" in msg
    assert "Formato esperado" in msg


@pytest.mark.parametrize(
    ("entrada", "esperado"),
    _TDCE_CENARIOS,
    ids=[str(i) for i in range(1, 10)],
)
def test_deveSerializarQuantidadeConformePadrao(entrada: str, esperado: str) -> None:
    serializado = serializar_quantidade_tdec(Decimal(entrada))
    json_obtido = json.dumps({"value": serializado})
    assert json_obtido == f'{{"value": "{esperado}"}}'