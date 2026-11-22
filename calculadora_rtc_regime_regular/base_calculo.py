"""Unified tax base of the official calculator.

Pin ``f1eebd7ce3157423b1a6aaca7dc1d6c3395452c4``,
``ElementoBaseCalculo`` and ``BaseCalculoUnificadaService``.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from decimal import Decimal
from enum import Enum

from calculadora_rtc_regime_regular.arredondamento import arredondar_valor_fiscal, subtrair
from calculadora_rtc_regime_regular.base_calculo_service import CampoInvalido


class Natureza(Enum):
    BEM = "BEM"
    SERVICO = "SERVICO"


class Operacao(Enum):
    SOMA = "SOMA"
    SUBTRAI = "SUBTRAI"


class Base(Enum):
    RG = "RG"
    IS = "IS"
    SN = "SN"


class ElementoBaseCalculo(Enum):
    """``br.gov.serpro.rtc.api.model.input.basecalculo.enumeration.ElementoBaseCalculo``."""

    V_PROD = "vProd"
    V_FRETE = "vFrete"
    V_SEG = "vSeg"
    V_OUTRO = "vOutro"
    V_II = "vII"
    V_IS = "vIS"
    V_DESC = "vDesc"
    V_PIS = "vPIS"
    V_COFINS = "vCOFINS"
    V_ICMS = "vICMS"
    V_ICMS_UF_DEST = "vICMSUFDest"
    V_FCP = "vFCP"
    V_FCP_UF_DEST = "vFCPUFDest"
    V_ICMS_MONO = "vICMSMono"
    V_ISSQN = "vISSQN"

    @property
    def tag(self) -> str:
        return self.value


@dataclass(frozen=True)
class Elemento:
    tag: str
    operacao: Operacao
    bases: frozenset[Base]
    natureza: Natureza | None
    ano_inicio: int
    ano_fim: int
    tipos_documento: frozenset[int]

    def compoe(self, ano: int, natureza: Natureza | None, tipo_documento: int) -> bool:
        ano_valido = self.ano_inicio <= ano <= self.ano_fim
        natureza_valida = self.natureza is None or (natureza is not None and self.natureza is natureza)
        return ano_valido and natureza_valida and tipo_documento in self.tipos_documento

    def motivo(self, ano: int, natureza: Natureza | None, tipo_documento: int) -> str | None:
        if not self.ano_inicio <= ano <= self.ano_fim:
            return (
                f"Campo {self.tag} não compõe as bases para o ano {ano} "
                f"(vigência {self.ano_inicio}–{self.ano_fim}) e foi ignorado no cálculo"
            )
        natureza_valida = self.natureza is None or (natureza is not None and self.natureza is natureza)
        if not natureza_valida:
            return (
                f"Campo {self.tag} não compõe as bases para a natureza {getattr(natureza, 'value', natureza)} "
                f"(aplicável apenas a {self.natureza.value}) e foi ignorado no cálculo"
            )
        if tipo_documento not in self.tipos_documento:
            return f"Campo {self.tag} não compõe as bases para o documento modelo {tipo_documento} e foi ignorado no cálculo"
        return None

    def aplica(self, base: Base) -> bool:
        return base in self.bases


def _el(
    tag: str,
    operacao: Operacao,
    bases: set[Base],
    natureza: Natureza | None,
    inicio: int,
    fim: int,
    tipos: set[int],
) -> Elemento:
    return Elemento(tag, operacao, frozenset(bases), natureza, inicio, fim, frozenset(tipos))


_RG_IS_SN = {Base.RG, Base.IS, Base.SN}
_RG_IS = {Base.RG, Base.IS}
_RG_SN = {Base.RG, Base.SN}
_NFE_NFCE = {55, 65}

ELEMENTOS: tuple[Elemento, ...] = (
    _el("vProd", Operacao.SOMA, _RG_IS_SN, None, 2026, 2033, _NFE_NFCE),
    _el("vFrete", Operacao.SOMA, _RG_IS_SN, None, 2026, 2033, _NFE_NFCE),
    _el("vSeg", Operacao.SOMA, _RG_IS_SN, None, 2026, 2033, _NFE_NFCE),
    _el("vOutro", Operacao.SOMA, _RG_IS_SN, None, 2026, 2033, _NFE_NFCE),
    _el("vII", Operacao.SOMA, _RG_IS, Natureza.BEM, 2026, 2033, {55}),
    _el("vIS", Operacao.SOMA, _RG_SN, None, 2027, 2033, _NFE_NFCE),
    _el("vDesc", Operacao.SUBTRAI, _RG_IS_SN, None, 2026, 2033, _NFE_NFCE),
    _el("vPIS", Operacao.SUBTRAI, _RG_IS, None, 2026, 2026, _NFE_NFCE),
    _el("vCOFINS", Operacao.SUBTRAI, _RG_IS, None, 2026, 2026, _NFE_NFCE),
    _el("vICMS", Operacao.SUBTRAI, _RG_IS, Natureza.BEM, 2026, 2032, _NFE_NFCE),
    _el("vICMSUFDest", Operacao.SUBTRAI, _RG_IS, Natureza.BEM, 2026, 2032, {55}),
    _el("vFCP", Operacao.SUBTRAI, _RG_IS, Natureza.BEM, 2026, 2032, _NFE_NFCE),
    _el("vFCPUFDest", Operacao.SUBTRAI, _RG_IS, Natureza.BEM, 2026, 2032, {55}),
    _el("vICMSMono", Operacao.SUBTRAI, _RG_IS, Natureza.BEM, 2026, 2032, _NFE_NFCE),
    _el("vISSQN", Operacao.SUBTRAI, _RG_IS, Natureza.SERVICO, 2026, 2032, _NFE_NFCE),
)


class DocumentoInvalido(ValueError):
    def __init__(self) -> None:
        super().__init__("Tipo de documento deve ser 55 (NF-e) ou 65 (NFC-e)")


@dataclass
class Componentes:
    vProd: Decimal | None = None
    vFrete: Decimal | None = None
    vSeg: Decimal | None = None
    vOutro: Decimal | None = None
    vII: Decimal | None = None
    vIS: Decimal | None = None
    vDesc: Decimal | None = None
    vPIS: Decimal | None = None
    vCOFINS: Decimal | None = None
    vICMS: Decimal | None = None
    vICMSUFDest: Decimal | None = None
    vFCP: Decimal | None = None
    vFCPUFDest: Decimal | None = None
    vICMSMono: Decimal | None = None
    vISSQN: Decimal | None = None

    def valor(self, elemento: Elemento) -> Decimal | None:
        return getattr(self, elemento.tag)

    def get_valor(self, elemento: ElementoBaseCalculo) -> Decimal | None:
        return getattr(self, elemento.tag)


@dataclass
class Bases:
    base_rg: Decimal | None
    base_is: Decimal | None
    base_sn: Decimal | None
    avisos: list[str] = field(default_factory=list)


def calcular(componentes: Componentes, ano: int, natureza: Natureza | None, tipo_documento: int | None) -> Bases:
    if tipo_documento not in {55, 65}:
        raise DocumentoInvalido
    assert tipo_documento is not None
    somas = {Base.RG: Decimal(0), Base.IS: Decimal(0), Base.SN: Decimal(0)}
    subtrai = {Base.RG: Decimal(0), Base.IS: Decimal(0), Base.SN: Decimal(0)}
    avisos: list[str] = []
    for elemento in ELEMENTOS:
        if not elemento.compoe(ano, natureza, tipo_documento):
            valor = componentes.valor(elemento)
            if valor is not None and valor != 0:
                motivo = elemento.motivo(ano, natureza, tipo_documento)
                if motivo:
                    avisos.append(motivo)
            continue
        valor = componentes.valor(elemento)
        if valor is None or valor == 0:
            continue
        destino = somas if elemento.operacao is Operacao.SOMA else subtrai
        for base in Base:
            if elemento.aplica(base):
                destino[base] = destino[base] + valor
    return Bases(
        subtrair(somas[Base.RG], subtrai[Base.RG]),
        subtrair(somas[Base.IS], subtrai[Base.IS]),
        subtrair(somas[Base.SN], subtrai[Base.SN]),
        avisos,
    )


def calcular_publicado(componentes: Componentes, ano: int, natureza: Natureza | None, tipo_documento: int | None) -> Bases:
    exato = calcular(componentes, ano, natureza, tipo_documento)
    return Bases(
        arredondar_valor_fiscal(exato.base_rg),
        arredondar_valor_fiscal(exato.base_is),
        arredondar_valor_fiscal(exato.base_sn),
        exato.avisos,
    )


@dataclass
class BaseCalculoUnificadaOutput:
    """``br.gov.serpro.rtc.api.model.output.basecalculo.BaseCalculoUnificadaOutput``."""

    base_rg: Decimal | None
    base_is: Decimal | None
    base_sn: Decimal | None
    avisos: list[str] = field(default_factory=list)

    def getBaseRG(self) -> Decimal | None:
        return self.base_rg

    def getBaseIS(self) -> Decimal | None:
        return self.base_is

    def getBaseSN(self) -> Decimal | None:
        return self.base_sn

    def getAvisos(self) -> list[str]:
        return self.avisos


@dataclass
class BaseCalculoUnificadaInput:
    """``br.gov.serpro.rtc.api.model.input.basecalculo.BaseCalculoUnificadaInput``."""

    anoFatoGerador: int | None = None
    tipoDocumento: int | None = None
    natureza: Natureza | None = None
    componentes: Componentes = field(default_factory=Componentes)

    def getComponentes(self) -> Componentes:
        return self.componentes

    def getAnoFatoGerador(self) -> int | None:
        return self.anoFatoGerador

    def getNatureza(self) -> Natureza | None:
        return self.natureza

    def getTipoDocumento(self) -> int | None:
        return self.tipoDocumento

    def setAnoFatoGerador(self, ano: int) -> None:
        self.anoFatoGerador = ano

    def setTipoDocumento(self, tipo: int) -> None:
        self.tipoDocumento = tipo

    def setNatureza(self, natureza: Natureza) -> None:
        self.natureza = natureza


def _validar_tipo_documento(tp_doc: int | None) -> None:
    if tp_doc is None or tp_doc not in {55, 65}:
        raise CampoInvalido("Tipo de documento deve ser 55 (NF-e) ou 65 (NFC-e)")


def _saida_exata(bases: Bases) -> BaseCalculoUnificadaOutput:
    return BaseCalculoUnificadaOutput(bases.base_rg, bases.base_is, bases.base_sn, list(bases.avisos))


def _saida_publicada(bases: Bases) -> BaseCalculoUnificadaOutput:
    return BaseCalculoUnificadaOutput(
        bases.base_rg,
        bases.base_is,
        bases.base_sn,
        list(bases.avisos),
    )


class BaseCalculoUnificadaService:
    """``br.gov.serpro.rtc.domain.service.basecalculo.BaseCalculoUnificadaService``."""

    def calcular(
        self,
        entrada: BaseCalculoUnificadaInput | Componentes,
        ano: int | None = None,
        natureza: Natureza | None = None,
        tp_doc: int | None = None,
    ) -> BaseCalculoUnificadaOutput:
        if isinstance(entrada, BaseCalculoUnificadaInput):
            _validar_tipo_documento(entrada.tipoDocumento)
            publicado = calcular_publicado(
                entrada.componentes,
                entrada.anoFatoGerador or 0,
                entrada.natureza,
                entrada.tipoDocumento,
            )
            return _saida_publicada(publicado)
        _validar_tipo_documento(tp_doc)
        exato = calcular(entrada, ano or 0, natureza, tp_doc)
        return _saida_exata(exato)
