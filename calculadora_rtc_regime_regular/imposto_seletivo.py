"""Imposto Seletivo of the official calculator.

Pin ``f1eebd7ce3157423b1a6aaca7dc1d6c3395452c4``, ``CalculoImpostoSeletivoService``.
The aliquot expressions stay unused, as in that class at this pin. The base is
rounded to 2 places and the ad valorem and ad rem rates to 4 places before the
product. The published value is that product rounded once.
"""

from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal

from calculadora_rtc_regime_regular.arredondamento import (
    arredondar_aliquota_publicada,
    arredondar_valor_fiscal,
    fracao_para_percentual,
    percentual_para_fracao,
)
from calculadora_rtc_regime_regular.expressao import avaliar

ZERO = Decimal(0)


@dataclass(frozen=True)
class TratamentoSeletivo:
    expressao_base_calculo: str
    expressao_tributo_calculado: str
    expressao_tributo_devido: str = ""


@dataclass(frozen=True)
class AliquotaSeletivo:
    ad_valorem: Decimal | None
    ad_rem: Decimal | None


@dataclass(frozen=True)
class ResultadoSeletivo:
    cst: str
    c_class_trib: str
    quantidade: Decimal | None
    unidade: str | None
    valor: Decimal | None
    aliquota_ad_valorem: Decimal | None
    aliquota_ad_rem: Decimal | None
    base_calculo: Decimal | None


def calcular_imposto_seletivo(
    *,
    cst: str,
    c_class_trib: str,
    unidade: str | None,
    base_informada: Decimal | None,
    quantidade: Decimal | None,
    imposto_seletivo_informado: Decimal | None,
    aliquota: AliquotaSeletivo,
    tratamento: TratamentoSeletivo,
) -> ResultadoSeletivo:
    ad_valorem = arredondar_aliquota_publicada(aliquota.ad_valorem)
    if ad_valorem is not None:
        ad_valorem = percentual_para_fracao(ad_valorem)
    ad_rem = arredondar_aliquota_publicada(aliquota.ad_rem)
    variaveis = _vars(
        quantidade=quantidade,
        baseCalculoInformada=base_informada,
        impostoSeletivoInformado=imposto_seletivo_informado,
        impostoSeletivoCalculado=ZERO,
        aliquotaAdValorem=ad_valorem,
        aliquotaAdRem=ad_rem,
    )
    base = arredondar_valor_fiscal(avaliar(tratamento.expressao_base_calculo, variaveis))
    tributo = arredondar_valor_fiscal(
        avaliar(
            tratamento.expressao_tributo_calculado,
            _vars(
                quantidade=quantidade,
                baseCalculo=base,
                baseCalculoInformada=base_informada,
                impostoSeletivoInformado=imposto_seletivo_informado,
                impostoSeletivoCalculado=ZERO,
                aliquotaAdValorem=ad_valorem,
                aliquotaAdRem=ad_rem,
            ),
        )
    )
    devido = None
    if tratamento.expressao_tributo_devido.strip():
        devido = arredondar_valor_fiscal(
            avaliar(
                tratamento.expressao_tributo_devido,
                _vars(
                    tributoCalculado=tributo,
                    quantidade=quantidade,
                    baseCalculo=base,
                    baseCalculoInformada=base_informada,
                    impostoSeletivoInformado=imposto_seletivo_informado,
                    aliquotaAdValorem=ad_valorem,
                    aliquotaAdRem=ad_rem,
                ),
            )
        )
    return ResultadoSeletivo(
        cst,
        c_class_trib,
        quantidade,
        unidade,
        devido,
        fracao_para_percentual(ad_valorem),
        ad_rem,
        base,
    )


def _vars(**valores: Decimal | None) -> dict[str, Decimal]:
    nomes = (
        "quantidade",
        "aliquota",
        "aliquotaEfetiva",
        "baseCalculoInformada",
        "impostoSeletivoInformado",
        "impostoSeletivoCalculado",
        "percentualReducao",
        "aliquotaPadraoOuReferencia",
        "aliquotaReferencia",
        "aliquotaAdValorem",
        "aliquotaAdRem",
        "ajuste",
        "redutor",
        "baseCalculo",
        "tributoCalculado",
    )
    mapa = {nome: ZERO for nome in nomes}
    for nome, valor in valores.items():
        mapa[nome] = valor if valor is not None else ZERO
    return mapa
