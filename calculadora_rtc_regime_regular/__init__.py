"""Cálculo de CBS, IBS e Imposto Seletivo do regime regular.

Transcrição em Python da calculadora pública da Receita Federal,
commit f1eebd7ce3157423b1a6aaca7dc1d6c3395452c4.
"""

from calculadora_rtc_regime_regular.base_calculo import calcular, calcular_publicado
from calculadora_rtc_regime_regular.cbs_ibs import calcular_cbs_ibs
from calculadora_rtc_regime_regular.imposto_seletivo import calcular_imposto_seletivo

__all__ = [
    "calcular",
    "calcular_cbs_ibs",
    "calcular_imposto_seletivo",
    "calcular_publicado",
]
