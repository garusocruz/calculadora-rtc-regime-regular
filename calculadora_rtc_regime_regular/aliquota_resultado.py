"""Composição da alíquota aplicável.

Pin ``f1eebd7ce3157423b1a6aaca7dc1d6c3395452c4``,
``AliquotaResultadoDTO``. O valor padrão, quando existe, já entra armazenado
como o resultado da forma de aplicação.
"""

from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal
from enum import Enum


class FormaAplicacao(Enum):
    SUBSTITUICAO = "Substitui a alíquota de referência pelo percentual informado"
    ACRESCIMO = "Acrescenta os pontos percentuais informados à alíquota de referência"
    DECRESCIMO = "Diminui os pontos percentuais informados à alíquota de referência"


class AliquotaReferenciaNaoEncontrada(Exception):
    pass


class AliquotaPadraoNaoEncontrada(Exception):
    pass


class AliquotaNegativa(Exception):
    def __init__(self, origem: str) -> None:
        self.origem = origem
        super().__init__(origem)


class FormaAplicacaoNaoDefinida(Exception):
    def __init__(self) -> None:
        super().__init__("Forma de aplicação da alíquota própria não definida")


class FormaAplicacaoNaoTratada(Exception):
    pass


@dataclass(frozen=True)
class AliquotaResultado:
    valor_referencia: Decimal
    valor_padrao: Decimal | None = None
    forma_aplicacao: FormaAplicacao | None = None

    def __post_init__(self) -> None:
        if self.valor_referencia is None:
            raise AliquotaReferenciaNaoEncontrada()
        if self.valor_referencia < 0:
            raise AliquotaNegativa("referencia")
        if self.valor_padrao is not None:
            if self.valor_padrao < 0:
                raise AliquotaNegativa("padrao")
            if self.forma_aplicacao is None:
                raise FormaAplicacaoNaoDefinida()
            aplicado = _aplicar(self.valor_referencia, self.valor_padrao, self.forma_aplicacao)
            if aplicado < 0:
                raise AliquotaNegativa("aplicavel")
            object.__setattr__(self, "valor_padrao", aplicado)
            return
        if self.forma_aplicacao is not None:
            raise AliquotaPadraoNaoEncontrada()

    def valor_aplicavel(self) -> Decimal:
        if self.valor_padrao is not None:
            return self.valor_padrao
        return self.valor_referencia

    def __str__(self) -> str:
        return (
            "AliquotaResultado["
            f"valorReferencia={self.valor_referencia}, "
            f"valorPadrao={self.valor_padrao}, "
            f"formaAplicacao={self.forma_aplicacao}"
            "]"
        )


def _aplicar(referencia: Decimal, padrao: Decimal, forma: FormaAplicacao) -> Decimal:
    if forma is FormaAplicacao.ACRESCIMO:
        return referencia + padrao
    if forma is FormaAplicacao.DECRESCIMO:
        return referencia - padrao
    if forma is FormaAplicacao.SUBSTITUICAO:
        return padrao
    raise FormaAplicacaoNaoTratada()
