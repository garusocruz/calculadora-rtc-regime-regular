"""Implementação independente, em Python, do cálculo de CBS, IBS e Imposto Seletivo.

Não é produto oficial, homologado ou certificado da Receita Federal.
O pin é o CalculadorTributo 1.7.2, commit f1eebd7ce3157423b1a6aaca7dc1d6c3395452c4.
"""

from calculadora_rtc_regime_regular.base_calculo import calcular, calcular_publicado
from calculadora_rtc_regime_regular.cbs_ibs import calcular_cbs_ibs
from calculadora_rtc_regime_regular.imposto_seletivo import calcular_imposto_seletivo

PIN_OFICIAL_VERSAO = "1.7.2"
PIN_OFICIAL_COMMIT = "f1eebd7ce3157423b1a6aaca7dc1d6c3395452c4"
PIN_OFICIAL_DATA = "2026-11-19"

__all__ = [
    "PIN_OFICIAL_COMMIT",
    "PIN_OFICIAL_DATA",
    "PIN_OFICIAL_VERSAO",
    "calcular",
    "calcular_cbs_ibs",
    "calcular_imposto_seletivo",
    "calcular_publicado",
]
