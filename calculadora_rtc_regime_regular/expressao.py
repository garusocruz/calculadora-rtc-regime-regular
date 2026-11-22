"""Safe arithmetic of the official formula evaluator.

Pin ``f1eebd7ce3157423b1a6aaca7dc1d6c3395452c4``, class
``AvaliadorExpressaoAritmetica``. Addition, subtraction and multiplication stay
exact. Division uses ``dividir``. A expression that is only a variable name
returns that value unchanged.
"""

from __future__ import annotations

from decimal import Decimal

from calculadora_rtc_regime_regular.arredondamento import dividir


class ExpressaoInvalida(ValueError):
    pass


class ErroAvaliadorExpressaoAritmeticaException(Exception):
    def __init__(self, erro: str) -> None:
        super().__init__(f"Erro na avaliação de expressão aritmética ({erro})")


def avaliar(expressao: str, variaveis: dict[str, Decimal]) -> Decimal:
    nome = expressao.strip()
    if nome in variaveis:
        valor = variaveis[nome]
        if valor is None:
            raise ExpressaoInvalida(f"valor nao mapeado: {nome}")
        return valor
    parser = _Parser(expressao, variaveis)
    return parser.parse()


class _Parser:
    def __init__(self, texto: str, variaveis: dict[str, Decimal]) -> None:
        self._texto = texto
        self._n = len(texto)
        self._i = 0
        self._variaveis = variaveis

    def parse(self) -> Decimal:
        valor = self._soma()
        self._pular()
        if self._i != self._n:
            raise ExpressaoInvalida(self._texto)
        return valor

    def _soma(self) -> Decimal:
        valor = self._termo()
        while True:
            self._pular()
            if self._come("+-"):
                op = self._texto[self._i]
                self._i += 1
                direito = self._termo()
                valor = valor + direito if op == "+" else valor - direito
                continue
            return valor

    def _termo(self) -> Decimal:
        valor = self._unario()
        while True:
            self._pular()
            if self._come("*/"):
                op = self._texto[self._i]
                self._i += 1
                direito = self._unario()
                if op == "*":
                    valor = valor * direito
                    continue
                quociente = dividir(valor, direito)
                if quociente is None:
                    raise ExpressaoInvalida(self._texto)
                valor = quociente
                continue
            return valor

    def _unario(self) -> Decimal:
        self._pular()
        if self._come("-"):
            self._i += 1
            return -self._unario()
        if self._come("+"):
            self._i += 1
            return self._unario()
        return self._primario()

    def _primario(self) -> Decimal:
        self._pular()
        if self._come("("):
            self._i += 1
            valor = self._soma()
            self._pular()
            if not self._come(")"):
                raise ExpressaoInvalida(self._texto)
            self._i += 1
            return valor
        if self._i < self._n and (self._texto[self._i].isdigit() or self._texto[self._i] == "."):
            return self._numero()
        if self._i < self._n and (self._texto[self._i].isalpha() or self._texto[self._i] == "_"):
            return self._nome()
        raise ExpressaoInvalida(self._texto)

    def _numero(self) -> Decimal:
        inicio = self._i
        while self._i < self._n and (self._texto[self._i].isdigit() or self._texto[self._i] == "."):
            self._i += 1
        try:
            return Decimal(self._texto[inicio : self._i])
        except Exception as exc:
            raise ExpressaoInvalida(self._texto) from exc

    def _nome(self) -> Decimal:
        inicio = self._i
        while self._i < self._n and (self._texto[self._i].isalnum() or self._texto[self._i] == "_"):
            self._i += 1
        nome = self._texto[inicio : self._i]
        if nome not in self._variaveis:
            raise ExpressaoInvalida(nome)
        return self._variaveis[nome]

    def _pular(self) -> None:
        while self._i < self._n and self._texto[self._i].isspace():
            self._i += 1

    def _come(self, simbolos: str) -> bool:
        return self._i < self._n and self._texto[self._i] in simbolos
