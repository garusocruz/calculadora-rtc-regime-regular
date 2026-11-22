"""Aviso de dados simulados (pin f1eebd7ce3157423b1a6aaca7dc1d6c3395452c4).

Transcrição de ``AvisoDadosSimuladosService``. A detecção de compra
governamental permanece desligada, como o TODO do Java.
"""

from __future__ import annotations

from datetime import date
from enum import Enum
from typing import Protocol


class TipoWarningDadosSimulados(Enum):
    CASO_GERAL = 1
    CASO_COMPRAS_GOVERNAMENTAIS = 2
    CASO_IMPOSTO_SELETIVO = 3
    CASO_COMPRAS_GOVERNAMENTAIS_IS = 4
    CASO_ALIQUOTAS_FICTICIAS = 5
    CASO_CALCULOS_SIMULADOS = 6


class _Item(Protocol):
    cst: str | None
    imposto_seletivo: object | None


_CST_ALIQUOTA_FICTICIA = frozenset({"010", "220", "221"})


def aviso_dados_simulados(data_fato_gerador: date, itens: list[_Item]) -> TipoWarningDadosSimulados | None:
    if data_fato_gerador > date(2026, 12, 31):
        return TipoWarningDadosSimulados.CASO_CALCULOS_SIMULADOS

    tem_compras_governamentais = False
    tem_imposto_seletivo = False
    tem_aliquotas_ficticias = False

    for item in itens:
        if item.cst in _CST_ALIQUOTA_FICTICIA:
            tem_aliquotas_ficticias = True
        if item.imposto_seletivo is not None:
            tem_imposto_seletivo = True

    if tem_aliquotas_ficticias and data_fato_gerador > date(2025, 12, 31):
        return TipoWarningDadosSimulados.CASO_ALIQUOTAS_FICTICIAS

    if data_fato_gerador < date(2027, 1, 1):
        return None

    if tem_compras_governamentais and tem_imposto_seletivo:
        return TipoWarningDadosSimulados.CASO_COMPRAS_GOVERNAMENTAIS_IS
    if tem_imposto_seletivo:
        return TipoWarningDadosSimulados.CASO_IMPOSTO_SELETIVO
    if tem_compras_governamentais:
        return TipoWarningDadosSimulados.CASO_COMPRAS_GOVERNAMENTAIS
    return TipoWarningDadosSimulados.CASO_GERAL
