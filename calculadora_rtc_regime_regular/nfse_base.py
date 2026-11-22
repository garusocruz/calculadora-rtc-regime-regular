"""Base de cálculo da NFS-e.

Pin ``f1eebd7ce3157423b1a6aaca7dc1d6c3395452c4``, ``NfseService.calcularBaseCalculo``.
"""

from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal

from calculadora_rtc_regime_regular.base_calculo_service import CampoInvalido

ZERO = Decimal(0)


@dataclass
class EntradaNfse:
    ano: int
    valor_servico: Decimal = ZERO
    desconto_incondicional: Decimal = ZERO
    reembolso: Decimal = ZERO
    deducao: Decimal = ZERO
    iss: Decimal = ZERO
    pis: Decimal = ZERO
    cofins: Decimal = ZERO


def calcular_base_nfse(entrada: EntradaNfse) -> Decimal:
    if entrada.ano < 2026:
        raise CampoInvalido("O ano do fato gerador deve ser 2026 ou superior")
    _vigencia({"PIS": entrada.pis, "COFINS": entrada.cofins}, entrada.ano, 2027)
    _vigencia({"ISS": entrada.iss}, entrada.ano, 2033)
    base = (
        entrada.valor_servico
        - entrada.desconto_incondicional
        - entrada.reembolso
        - entrada.deducao
        - entrada.pis
        - entrada.cofins
        - entrada.iss
    )
    if base < 0:
        raise CampoInvalido(
            "Base de cálculo não pode ser negativa. Valores que não integram a base são maiores que o valor do serviço."
        )
    return base


def _vigencia(campos: dict[str, Decimal], ano: int, extincao: int) -> None:
    if ano < extincao:
        return
    informados = ", ".join(sorted(nome for nome, valor in campos.items() if valor != 0))
    if informados:
        raise CampoInvalido(f"Os seguintes campos não podem ser informados a partir de {extincao}: {informados}")
