"""Base unificada da NFS-e, regime geral e Simples.

Pin ``f1eebd7ce3157423b1a6aaca7dc1d6c3395452c4``,
``BaseCalculoUnificadaNfseService``.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from decimal import Decimal
from enum import Enum

from calculadora_rtc_regime_regular.arredondamento import (
    arredondar_valor_fiscal,
    formatar_moeda,
    multiplicar,
    percentual_para_fracao,
    subtrair,
)
from calculadora_rtc_regime_regular.base_calculo_service import CampoInvalido

ZERO = Decimal(0)


class Situacao(Enum):
    COMUM = "comum"
    SALAO_PARCEIRO = "salaoParceiro"
    LOCACAO = "locacao9903"

    def locacao(self) -> bool:
        return self is Situacao.LOCACAO

    def salao(self) -> bool:
        return self is Situacao.SALAO_PARCEIRO


class OpcaoSimples(Enum):
    NAO_OPTANTE = 1
    MEI = 2
    OPTANTE = 3
    PENDENTE = 4

    def mei(self) -> bool:
        return self is OpcaoSimples.MEI

    def exige_regime(self) -> bool:
        return self in {OpcaoSimples.OPTANTE, OpcaoSimples.PENDENTE}

    def proibe_regime(self) -> bool:
        return self is OpcaoSimples.NAO_OPTANTE

    def veda_locacao(self) -> bool:
        return self in {OpcaoSimples.MEI, OpcaoSimples.OPTANTE}

    def base_sn_inaplicavel(self) -> bool:
        return self in {OpcaoSimples.NAO_OPTANTE, OpcaoSimples.MEI}


class RegimeSimples(Enum):
    PELO_SN = 1
    CBS_PELO_SN = 2
    AMBOS_REGULARES = 3

    def calcula_base_sn(self) -> bool:
        return self is not RegimeSimples.AMBOS_REGULARES


_AJUSTES = {
    "101": (True, False, False),
    "102": (True, False, False),
    "103": (True, False, False),
    "104": (True, False, False),
    "105": (True, False, False),
    "199": (True, False, True),
    "9": (False, True, False),
}


@dataclass(frozen=True)
class Ajuste:
    tipo: str
    valor: Decimal
    descricao: str | None = None


@dataclass(frozen=True)
class Locacao:
    copropriedade: Decimal
    total: Decimal
    desconto: Decimal
    ajustes: Decimal


@dataclass
class EntradaUnificada:
    ano: int
    opcao: OpcaoSimples
    situacao: Situacao
    valor_servico: Decimal | None = None
    desconto: Decimal | None = None
    iss: Decimal | None = None
    pis: Decimal | None = None
    cofins: Decimal | None = None
    regime: RegimeSimples | None = None
    documentos: list[Ajuste] | None = None
    locacao: Locacao | None = None


@dataclass(frozen=True)
class Erro:
    codigo: str
    mensagem: str


@dataclass
class ResultadoUnificado:
    base_rg: Decimal | None
    base_sn: Decimal | None
    avisos: list[str] = field(default_factory=list)
    erros: list[Erro] = field(default_factory=list)


def calcular_unificada(entrada: EntradaUnificada) -> ResultadoUnificado:
    avisos: list[str] = []
    erros: list[Erro] = []
    documentos = list(entrada.documentos or [])
    if entrada.situacao.locacao() and entrada.locacao is None:
        raise CampoInvalido("Campo locacao obrigatório quando situacao é locacao9903")
    _negocio(entrada, erros)
    validos = _documentos(documentos, avisos, erros)
    if entrada.opcao.mei():
        avisos.append("E1302: Operação MEI: bases de cálculo não aplicáveis")
        if documentos:
            erros.append(Erro("E0436", "Documentos de ajuste não são permitidos para MEI"))
        return ResultadoUnificado(None, None, avisos, erros)
    ajuste_ibs = _soma(validos, entrada.situacao, ibs=True)
    ajuste_parceiro = _soma(validos, entrada.situacao, ibs=False)
    servico = _zero(entrada.valor_servico)
    if ajuste_ibs > 0 and ajuste_ibs >= servico:
        erros.append(
            Erro(
                "E1534",
                "Soma dos ajustes (%s) excede ou iguala o valor do serviço (%s)"
                % (formatar_moeda(ajuste_ibs), formatar_moeda(servico)),
            )
        )
    if entrada.situacao.locacao() and documentos:
        avisos.append("Documentos de ajuste ignorados em contexto de locação de imóveis")
    if not entrada.situacao.locacao() and entrada.locacao is not None:
        avisos.append("Grupo locacao ignorado fora de contexto de locação de imóveis")
    base_rg = arredondar_valor_fiscal(_base_rg(entrada, ajuste_ibs))
    base_sn = _base_sn(entrada, ajuste_ibs, ajuste_parceiro)
    if base_sn is not None:
        base_sn = arredondar_valor_fiscal(base_sn)
    if entrada.opcao is OpcaoSimples.PENDENTE:
        avisos.append("Optante pendente: cálculo realizado com ressalva")
    if base_rg is not None and base_rg < 0:
        erros.append(Erro("BASE-NEGATIVA", "Base de cálculo RG negativa: %s" % formatar_moeda(base_rg)))
    if base_sn is not None and base_sn < 0:
        erros.append(Erro("BASE-NEGATIVA", "Base de cálculo SN negativa: %s" % formatar_moeda(base_sn)))
    return ResultadoUnificado(base_rg, base_sn, avisos, erros)


def _negocio(entrada: EntradaUnificada, erros: list[Erro]) -> None:
    if entrada.opcao.exige_regime() and entrada.regime is None:
        erros.append(Erro("EXXX-REGAP", "Campo regApIBSCBSSN obrigatório para optante do Simples Nacional"))
    if entrada.opcao.proibe_regime() and entrada.regime is not None:
        erros.append(Erro("EXXX-REGAP", "Campo regApIBSCBSSN proibido para não optante do Simples Nacional"))
    if entrada.opcao.veda_locacao() and entrada.situacao.locacao():
        erros.append(Erro("EXXX-LOC-SN", "Locação de imóveis incompatível com optante do Simples Nacional"))


def _documentos(documentos: list[Ajuste], avisos: list[str], erros: list[Erro]) -> list[Ajuste]:
    validos: list[Ajuste] = []
    for documento in documentos:
        flags = _AJUSTES.get(documento.tipo)
        if flags is None:
            avisos.append("Tipo de ajuste '%s' desconhecido: documento ignorado" % documento.tipo)
            continue
        if flags[2] and not (documento.descricao or "").strip():
            erros.append(Erro("LEIAUTE-XTP", "Campo xTpAjusteBC obrigatório para tipo de ajuste 199"))
            continue
        validos.append(documento)
    return validos


def _soma(documentos: list[Ajuste], situacao: Situacao, *, ibs: bool) -> Decimal:
    if situacao.locacao():
        return ZERO
    indice = 0 if ibs else 1
    total = ZERO
    for documento in documentos:
        flags = _AJUSTES[documento.tipo]
        if flags[indice]:
            total += documento.valor
    return total


def _base_rg(entrada: EntradaUnificada, ajuste: Decimal) -> Decimal | None:
    if entrada.situacao.locacao():
        assert entrada.locacao is not None
        fator = percentual_para_fracao(entrada.locacao.copropriedade)
        servico = multiplicar(fator, entrada.locacao.total)
        desconto = multiplicar(fator, entrada.locacao.desconto)
        ajustes = multiplicar(fator, entrada.locacao.ajustes)
        pis = _zero(entrada.pis) if entrada.ano < 2027 else ZERO
        cofins = _zero(entrada.cofins) if entrada.ano < 2027 else ZERO
        return subtrair(subtrair(subtrair(subtrair(servico, desconto), ajustes), pis), cofins)
    iss = _zero(entrada.iss) if entrada.ano < 2033 else ZERO
    pis = _zero(entrada.pis) if entrada.ano < 2027 else ZERO
    cofins = _zero(entrada.cofins) if entrada.ano < 2027 else ZERO
    base = _zero(entrada.valor_servico) - _zero(entrada.desconto) - ajuste - iss - pis - cofins
    return base


def _base_sn(entrada: EntradaUnificada, ajuste_ibs: Decimal, ajuste_parceiro: Decimal) -> Decimal | None:
    if entrada.opcao.base_sn_inaplicavel() or entrada.regime is None:
        return None
    if entrada.situacao.locacao():
        assert entrada.locacao is not None
        fator = percentual_para_fracao(entrada.locacao.copropriedade)
        base = subtrair(multiplicar(fator, entrada.locacao.total), multiplicar(fator, entrada.locacao.desconto))
    else:
        base = subtrair(_zero(entrada.valor_servico), _zero(entrada.desconto))
    base = subtrair(base, ajuste_ibs)
    if entrada.situacao.salao() and entrada.regime.calcula_base_sn():
        base = subtrair(base, ajuste_parceiro)
    return base


def _zero(valor: Decimal | None) -> Decimal:
    return valor if valor is not None else ZERO
