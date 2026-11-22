"""Regras de desserialização/serialização espelhando os custom serializers Java (sem Jackson/Spring)."""

from __future__ import annotations

import re
from datetime import date, datetime
from decimal import Decimal
from typing import Any

from calculadora_rtc_regime_regular.arredondamento import formatar_quantidade

_OFFSET_PATTERN = re.compile(
    r"\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}([+-]\d{2}:\d{2}|Z)$"
)
_OFFSET_FORMAT = "yyyy-MM-dd'T'HH:mm:ssXXX"
_OFFSET_EXAMPLE = "2026-01-05T13:45:00-03:00 ou 2026-05-22T10:57:23Z"

_LOCAL_DATE_PATTERN = re.compile(r"\d{4}-\d{2}-\d{2}$")
_LOCAL_DATE_FORMAT = "yyyy-MM-dd"
_LOCAL_DATE_EXAMPLE = "2026-01-05"


class ErroFormatoInvalido(ValueError):
    """Equivalente funcional a ``InvalidFormatException`` do Jackson."""


def _mensagem_formato(nome_campo: str | None, valor: str, formato: str, exemplo: str) -> str:
    rotulo = "null" if nome_campo is None else nome_campo
    return (
        f"Campo '{rotulo}' [{valor}] inválido. "
        f"Formato esperado: '{formato}'. Exemplo de valor: '{exemplo}'"
    )


def _parse_offset_datetime_iso(valor: str) -> datetime:
    texto = valor[:-1] + "+00:00" if valor.endswith("Z") else valor
    return datetime.fromisoformat(texto)


def deserializar_offset_date_time(valor: str, nome_campo: str | None = None) -> datetime:
    if not _OFFSET_PATTERN.fullmatch(valor):
        raise ErroFormatoInvalido(
            _mensagem_formato(nome_campo, valor, _OFFSET_FORMAT, _OFFSET_EXAMPLE)
        )
    try:
        return _parse_offset_datetime_iso(valor)
    except ValueError:
        raise ErroFormatoInvalido(
            _mensagem_formato(nome_campo, valor, _OFFSET_FORMAT, _OFFSET_EXAMPLE)
        ) from None


def deserializar_local_date(valor: str, nome_campo: str | None = None) -> date:
    if not _LOCAL_DATE_PATTERN.fullmatch(valor):
        raise ErroFormatoInvalido(
            _mensagem_formato(nome_campo, valor, _LOCAL_DATE_FORMAT, _LOCAL_DATE_EXAMPLE)
        )
    try:
        return date.fromisoformat(valor)
    except ValueError:
        raise ErroFormatoInvalido(
            _mensagem_formato(nome_campo, valor, _LOCAL_DATE_FORMAT, _LOCAL_DATE_EXAMPLE)
        ) from None


def deserializar_offset_date_time_json_string(valor_json: str) -> datetime:
    """Espelha ``objectMapper.readValue("\"…\"", OffsetDateTime.class)`` (sem nome de campo)."""
    if len(valor_json) < 2 or valor_json[0] != '"' or valor_json[-1] != '"':
        raise ErroFormatoInvalido(
            _mensagem_formato(None, valor_json, _OFFSET_FORMAT, _OFFSET_EXAMPLE)
        )
    return deserializar_offset_date_time(valor_json[1:-1], None)


def serializar_quantidade_tdec(valor: Decimal) -> str:
    if valor < 0:
        raise ValueError("Números negativos não são permitidos para TDec_1104OpRTC")
    return formatar_quantidade(valor)


def build_regime_geral_payload(dh_fato_gerador: str) -> dict[str, Any]:
    return {
        "id": "6194602ea71cbf9431c236de4409d920",
        "versao": "0.0.1",
        "dhFatoGerador": dh_fato_gerador,
        "municipio": 4314902,
        "uf": "RS",
        "itens": [
            {
                "numero": 1,
                "ncm": "99999999",
                "cst": "000",
                "cClassTrib": "000001",
                "baseCalculo": 200,
                "quantidade": 1,
                "unidade": "LT",
            }
        ],
    }


def operacao_regime_geral_from_dh(dh_fato_gerador: str):
    """Valida ``dhFatoGerador`` com a regra RTC e devolve ``OperacaoInput``."""
    from calculadora_rtc_regime_regular.processamento_item import operacao_input_from_json

    deserializar_offset_date_time(dh_fato_gerador, "dhFatoGerador")
    return operacao_input_from_json(build_regime_geral_payload(dh_fato_gerador))