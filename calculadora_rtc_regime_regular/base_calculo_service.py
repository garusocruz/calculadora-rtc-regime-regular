"""Bases de CBS, IBS e Imposto Seletivo sobre mercadorias.

Pin ``f1eebd7ce3157423b1a6aaca7dc1d6c3395452c4``, ``BaseCalculoService``.
"""

from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal

ZERO = Decimal(0)
ANO_INICIO_CBS_IBS = 2026
ANO_INICIO_IS = 2027
ANO_EXTINCAO_PIS_COFINS = 2027
ANO_EXTINCAO_ICMS_ISS = 2033
MENSAGEM_BASE_NEGATIVA = (
    "Base de cálculo não pode ser negativa. A soma dos valores que não integram "
    "a base é maior que a soma dos valores que integram a base."
)


class CampoInvalido(Exception):
    pass


@dataclass
class EntradaCibs:
    ano: int
    valor_bem: Decimal = ZERO
    ajuste_acrescimos: Decimal = ZERO
    juros: Decimal = ZERO
    multas: Decimal = ZERO
    encargos: Decimal = ZERO
    frete: Decimal = ZERO
    imposto_seletivo: Decimal = ZERO
    outros_tributos: Decimal = ZERO
    demais_importancias: Decimal = ZERO
    icms: Decimal = ZERO
    iss: Decimal = ZERO
    pis: Decimal = ZERO
    pis_importacao: Decimal = ZERO
    cofins: Decimal = ZERO
    cofins_importacao: Decimal = ZERO
    cosip: Decimal = ZERO
    ipi: Decimal = ZERO
    desconto_incondicional: Decimal = ZERO


@dataclass
class EntradaIsMercadorias:
    ano: int
    valor_bem: Decimal = ZERO
    ajuste_acrescimos: Decimal = ZERO
    juros: Decimal = ZERO
    multas: Decimal = ZERO
    encargos: Decimal = ZERO
    frete_cobrado: Decimal = ZERO
    outros_tributos: Decimal = ZERO
    demais_importancias: Decimal = ZERO
    cosip: Decimal = ZERO
    ipi: Decimal = ZERO
    desconto_incondicional: Decimal = ZERO
    bonificacao: Decimal = ZERO
    devolucao_vendas: Decimal = ZERO
    icms: Decimal = ZERO
    iss: Decimal = ZERO


def calcular_cibs(entrada: EntradaCibs) -> Decimal:
    _ano_inicio(entrada.ano, ANO_INICIO_CBS_IBS, "Para CBS/IBS, o ano do fato gerador deve ser 2026 ou superior")
    _vigencia(
        {
            "PIS": entrada.pis,
            "PIS Importação": entrada.pis_importacao,
            "COFINS": entrada.cofins,
            "COFINS Importação": entrada.cofins_importacao,
        },
        entrada.ano,
        ANO_EXTINCAO_PIS_COFINS,
    )
    _vigencia({"ICMS": entrada.icms, "ISS": entrada.iss}, entrada.ano, ANO_EXTINCAO_ICMS_ISS)
    integra = (
        entrada.valor_bem
        + entrada.ajuste_acrescimos
        + entrada.juros
        + entrada.multas
        + entrada.encargos
        + entrada.frete
        + entrada.imposto_seletivo
        + entrada.outros_tributos
        + entrada.demais_importancias
    )
    nao_integra = (
        entrada.cosip
        + entrada.ipi
        + entrada.desconto_incondicional
        + entrada.pis
        + entrada.pis_importacao
        + entrada.cofins
        + entrada.cofins_importacao
        + entrada.icms
        + entrada.iss
    )
    base = integra - nao_integra
    _base_nao_negativa(base)
    return base


def calcular_is_mercadorias(entrada: EntradaIsMercadorias) -> Decimal:
    _ano_inicio(entrada.ano, ANO_INICIO_IS, "Para IS, o ano do fato gerador deve ser 2027 ou superior")
    _vigencia({"ICMS": entrada.icms, "ISS": entrada.iss}, entrada.ano, ANO_EXTINCAO_ICMS_ISS)
    integra = (
        entrada.valor_bem
        + entrada.ajuste_acrescimos
        + entrada.juros
        + entrada.multas
        + entrada.encargos
        + entrada.frete_cobrado
        + entrada.outros_tributos
        + entrada.demais_importancias
    )
    nao_integra = (
        entrada.cosip
        + entrada.ipi
        + entrada.desconto_incondicional
        + entrada.bonificacao
        + entrada.devolucao_vendas
        + entrada.icms
        + entrada.iss
    )
    base = integra - nao_integra
    _base_nao_negativa(base)
    return base


def _ano_inicio(ano: int, inicio: int, mensagem: str) -> None:
    if ano < inicio:
        raise CampoInvalido(mensagem)


def _vigencia(campos: dict[str, Decimal], ano: int, extincao: int) -> None:
    if ano < extincao:
        return
    informados = ", ".join(sorted(nome for nome, valor in campos.items() if valor != 0))
    if informados:
        raise CampoInvalido(f"Os seguintes campos não podem ser informados a partir de {extincao}: {informados}")


def _base_nao_negativa(base: Decimal) -> None:
    if base < 0:
        raise CampoInvalido(MENSAGEM_BASE_NEGATIVA)
