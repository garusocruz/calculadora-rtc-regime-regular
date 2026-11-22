"""CBS and IBS calculation of the official calculator.

Pin ``f1eebd7ce3157423b1a6aaca7dc1d6c3395452c4``, ``CalculoCbsIbsService``.
Table lookups stay behind callables. The numeric steps are the ones in that class.
"""

from __future__ import annotations

import re
from collections.abc import Callable
from dataclasses import dataclass
from datetime import date
from decimal import Decimal
from enum import Enum

from calculadora_rtc_regime_regular.aliquota_resultado import AliquotaResultado
from calculadora_rtc_regime_regular.arredondamento import (
    arredondar_aliquota_publicada,
    arredondar_valor_fiscal,
    dividir,
    fracao_para_percentual,
    multiplicar,
    percentual_para_fracao,
)
from calculadora_rtc_regime_regular.expressao import avaliar

ZERO = Decimal(0)
CEM = Decimal(100)
PBIO = Decimal(30)
PDIF = Decimal(100)
VARIACAO_EAC = Decimal(5)
ALIQUOTA_EAC = Decimal("0.1922")
ALIQUOTA_GASOLINA_TIPO_A = Decimal("0.7925")
_ALIQUOTA = re.compile(r"\baliquota\b")

BuscaPadrao = Callable[[int, int | None, int | None, date], AliquotaResultado]
BuscaReferencia = Callable[[int, date], Decimal]
BuscaSetorial = Callable[[str | None, int, int, date], Decimal | None]
BuscaFixa = Callable[[int, int, date], Decimal | None]


class Tributo(Enum):
    CBS = "CBS"
    IBS_ESTADUAL = "IBS_ESTADUAL"
    IBS_MUNICIPAL = "IBS_MUNICIPAL"


class AjusteNaoImplementado(Exception):
    pass


class TipoAliquotaDesconhecido(Exception):
    def __init__(self, tipo: str, c_class_trib: str | None, cst: str | None) -> None:
        self.tipo = tipo
        self.c_class_trib = c_class_trib
        self.cst = cst
        super().__init__(
            f"Tipo de alíquota ({tipo}) desconhecido para cClassTrib {c_class_trib} e CST {cst}"
        )


class AliquotaUniformeSetorialNaoEncontrada(Exception):
    pass


class AliquotaFixaNaoEncontrada(Exception):
    pass


class CompraGovernamentalIndisponivel(Exception):
    pass


@dataclass(frozen=True)
class Tratamento:
    expressao_aliquota: str = ""
    expressao_base_calculo: str = ""
    expressao_aliquota_efetiva: str = ""
    expressao_tributo_calculado: str = ""
    expressao_tributo_devido: str = ""
    expressao_percentual_diferimento: str = ""
    expressao_valor_diferimento: str = ""
    possui_ajuste: bool = False
    possui_percentual_reducao: bool = False
    possui_monofasia: bool = False


@dataclass(frozen=True)
class Classificacao:
    id: int
    codigo: str
    tipo_aliquota: str
    grupo_reducao: bool = False
    grupo_ibs_cbs: bool = True
    grupo_monofasia_padrao: bool = False
    grupo_monofasia_reten: bool = False
    grupo_monofasia_ret: bool = False
    grupo_monofasia_diferimento: bool = False


@dataclass(frozen=True)
class Diferimento:
    percentual: Decimal
    valor: Decimal


@dataclass(frozen=True)
class Reducao:
    percentual: Decimal
    aliquota_efetiva: Decimal


@dataclass(frozen=True)
class CompraGovernamental:
    aliquota_cbs: Decimal | None = None
    tributo_cbs: Decimal | None = None
    aliquota_ibs_estadual: Decimal | None = None
    tributo_ibs_estadual: Decimal | None = None
    aliquota_ibs_municipal: Decimal | None = None
    tributo_ibs_municipal: Decimal | None = None


@dataclass(frozen=True)
class TributacaoRegular:
    cst: str
    c_class_trib: str
    base_calculo: Decimal
    aliquota_efetiva: Decimal
    tributo_devido: Decimal


@dataclass(frozen=True)
class EtapaMonofasia:
    quantidade: Decimal
    aliquota_ad_rem: Decimal
    valor: Decimal


@dataclass(frozen=True)
class DiferimentoMonofasia:
    percentual: Decimal | None
    valor: Decimal


@dataclass(frozen=True)
class Monofasia:
    padrao: EtapaMonofasia | None
    retencao: EtapaMonofasia | None
    retido: EtapaMonofasia | None
    diferido: DiferimentoMonofasia | None


@dataclass(frozen=True)
class ResultadoCbsIbs:
    base_calculo: Decimal
    aliquota: Decimal | None
    tributo_calculado: Decimal | None
    tributo_devido: Decimal | None
    diferimento: Diferimento | None
    quantidade: Decimal | None = None
    reducao: Reducao | None = None
    compra_governamental: CompraGovernamental | None = None
    tributacao_regular: TributacaoRegular | None = None
    monofasia: Monofasia | None = None


def buscar_aliquota_padrao(
    id_tributo: int,
    codigo_uf: int | None,
    codigo_municipio: int | None,
    data: date,
    buscar: BuscaPadrao,
) -> Decimal | None:
    aliquota = buscar(id_tributo, codigo_uf, codigo_municipio, data)
    return percentual_para_fracao(aliquota.valor_aplicavel())


def calcular_cbs_ibs(
    *,
    aliquota_informada: Decimal | None,
    base_informada: Decimal,
    imposto_seletivo_calculado: Decimal,
    imposto_seletivo_informado: Decimal | None,
    redutor_compra_gov: Decimal,
    tratamento: Tratamento,
    classificacao: Classificacao,
    quantidade: Decimal | None = None,
    percentual_reducao: Decimal | None = None,
    id_tributo: int | None = None,
    codigo_uf: int | None = None,
    codigo_municipio: int | None = None,
    data: date | None = None,
    nbs: str | None = None,
    tributo: Tributo | None = None,
    ente_governamental: str | None = None,
    tem_tributacao_regular: bool = False,
    cst_regular: str | None = None,
    c_class_trib_regular: str | None = None,
    buscar_padrao: BuscaPadrao | None = None,
    buscar_referencia: BuscaReferencia | None = None,
    buscar_setorial: BuscaSetorial | None = None,
    buscar_fixa: BuscaFixa | None = None,
) -> ResultadoCbsIbs | None:
    if tratamento.possui_ajuste:
        raise AjusteNaoImplementado(classificacao.codigo)
    reducao = percentual_para_fracao(percentual_reducao) if tratamento.possui_percentual_reducao else None
    tipo = "Padrão" if classificacao.codigo == "510001" else classificacao.tipo_aliquota
    valor_aliquota, aliquota_informada_aplicada, aliquota_dividida = _resolver_aliquota(
        tipo,
        aliquota_informada,
        tratamento.possui_monofasia,
        id_tributo,
        codigo_uf,
        codigo_municipio,
        data,
        nbs,
        classificacao.id,
        cst_regular,
        c_class_trib_regular,
        buscar_padrao,
        buscar_referencia,
        buscar_setorial,
        buscar_fixa,
    )
    ad_rem_principal = ALIQUOTA_GASOLINA_TIPO_A if _monofasia_setorial(tipo, tratamento) else None
    ad_rem_secundaria = ALIQUOTA_EAC if _monofasia_setorial(tipo, tratamento) else None
    p_bio = percentual_para_fracao(PBIO) if _monofasia_setorial(tipo, tratamento) else None
    p_dif = percentual_para_fracao(PDIF) if _monofasia_setorial(tipo, tratamento) else None
    variacao = VARIACAO_EAC if _monofasia_setorial(tipo, tratamento) else None
    if aliquota_informada_aplicada and not _usa_aliquota(tratamento.expressao_aliquota):
        resultado_aliquota = valor_aliquota
    elif tratamento.expressao_aliquota.strip():
        resultado_aliquota = avaliar(
            tratamento.expressao_aliquota,
            _vars(
                aliquota=valor_aliquota,
                quantidade=quantidade,
                percentualReducao=reducao,
                aliquotaAdRemPrincipal=ad_rem_principal,
                aliquotaAdRemSecundaria=ad_rem_secundaria,
                variacaoPontoPercentual=variacao,
                pBio=p_bio,
                percentualDiferimento=p_dif,
            ),
        )
    else:
        resultado_aliquota = None
    if aliquota_dividida:
        resultado_aliquota = _publicar_aliquota(resultado_aliquota)
    resultado_efetiva = None
    if tratamento.expressao_aliquota_efetiva.strip():
        resultado_efetiva = avaliar(
            tratamento.expressao_aliquota_efetiva,
            _vars(
                aliquota=resultado_aliquota,
                quantidade=quantidade,
                percentualReducao=reducao,
                pRedutorCompraGov=redutor_compra_gov,
                aliquotaAdRemPrincipal=ad_rem_principal,
                aliquotaAdRemSecundaria=ad_rem_secundaria,
                variacaoPontoPercentual=variacao,
                pBio=p_bio,
                percentualDiferimento=p_dif,
            ),
        )
        if aliquota_dividida:
            resultado_efetiva = _publicar_aliquota(resultado_efetiva)
    base = avaliar(
        tratamento.expressao_base_calculo,
        _vars(
            aliquota=resultado_aliquota,
            aliquotaEfetiva=resultado_efetiva,
            baseCalculoInformada=base_informada,
            impostoSeletivoInformado=imposto_seletivo_informado,
            impostoSeletivoCalculado=imposto_seletivo_calculado,
            percentualReducao=reducao,
            quantidade=quantidade,
            aliquotaAdRemPrincipal=ad_rem_principal,
            aliquotaAdRemSecundaria=ad_rem_secundaria,
            variacaoPontoPercentual=variacao,
            pBio=p_bio,
            percentualDiferimento=p_dif,
        ),
    )
    if not tratamento.possui_monofasia:
        base = arredondar_valor_fiscal(base)
    assert base is not None
    if base < 0:
        base = ZERO
    tributo_exato = avaliar(
        tratamento.expressao_tributo_calculado,
        _vars(
            baseCalculo=base,
            aliquota=resultado_aliquota,
            aliquotaEfetiva=resultado_efetiva,
            quantidade=quantidade,
            aliquotaAdRemPrincipal=ad_rem_principal,
            aliquotaAdRemSecundaria=ad_rem_secundaria,
            variacaoPontoPercentual=variacao,
            pBio=p_bio,
            percentualDiferimento=p_dif,
        ),
    )
    tributo_calculado = arredondar_valor_fiscal(tributo_exato)
    assert tributo_calculado is not None
    devido = None
    if tratamento.expressao_tributo_devido.strip():
        devido = arredondar_valor_fiscal(
            avaliar(
                tratamento.expressao_tributo_devido,
                _vars(
                    tributoCalculado=tributo_calculado,
                    baseCalculo=base,
                    aliquotaEfetiva=resultado_efetiva,
                    aliquota=resultado_aliquota,
                    quantidade=quantidade,
                ),
            )
        )
    diferimento = None
    percentual_diferimento = None
    if tratamento.expressao_percentual_diferimento.strip() and tratamento.expressao_valor_diferimento.strip():
        percentual_diferimento = _publicar_aliquota(avaliar(tratamento.expressao_percentual_diferimento, _vars()))
        valor = arredondar_valor_fiscal(
            avaliar(
                tratamento.expressao_valor_diferimento,
                _vars(percentualDiferimento=percentual_diferimento, tributoCalculado=tributo_exato),
            )
        )
        assert tributo_calculado is not None and valor is not None and percentual_diferimento is not None
        devido = tributo_calculado - valor
        if devido < 0:
            devido = ZERO
        diferimento = Diferimento(fracao_para_percentual(percentual_diferimento), valor)
    if not classificacao.grupo_ibs_cbs:
        return None
    aliquota_publicada = resultado_aliquota
    if aliquota_dividida and resultado_aliquota is not None:
        aliquota_publicada = fracao_para_percentual(resultado_aliquota)
    if tem_tributacao_regular:
        aliquota_publicada = ZERO
        tributo_calculado_publicado = ZERO
        devido_publicado = ZERO
    else:
        tributo_calculado_publicado = tributo_calculado
        devido_publicado = devido
    return ResultadoCbsIbs(
        base,
        aliquota_publicada,
        tributo_calculado_publicado,
        devido_publicado,
        diferimento,
        quantidade,
        _reducao(classificacao, resultado_efetiva, reducao, aliquota_dividida, tem_tributacao_regular, ente_governamental),
        _compra_gov(ente_governamental, tributo, resultado_efetiva, devido),
        _regular(
            tem_tributacao_regular,
            cst_regular,
            c_class_trib_regular,
            base,
            resultado_aliquota,
            reducao,
            aliquota_dividida,
            tratamento.possui_percentual_reducao,
        ),
        _monofasia(classificacao, quantidade, resultado_aliquota, resultado_efetiva, tributo_calculado, devido, variacao),
    )


def _resolver_aliquota(
    tipo: str,
    informada: Decimal | None,
    monofasia: bool,
    id_tributo: int | None,
    codigo_uf: int | None,
    codigo_municipio: int | None,
    data: date | None,
    nbs: str | None,
    id_classificacao: int,
    cst: str | None,
    c_class_trib: str | None,
    buscar_padrao: BuscaPadrao | None,
    buscar_referencia: BuscaReferencia | None,
    buscar_setorial: BuscaSetorial | None,
    buscar_fixa: BuscaFixa | None,
) -> tuple[Decimal | None, bool, bool]:
    if tipo in {"Padrão", "Uniforme nacional (referência)", "Fixa"} or (tipo == "Uniforme setorial" and not monofasia):
        if informada is not None:
            return percentual_para_fracao(informada), True, True
        return _buscar_tipo(tipo, id_tributo, codigo_uf, codigo_municipio, data, nbs, id_classificacao, buscar_padrao, buscar_referencia, buscar_setorial, buscar_fixa), False, True
    if tipo == "Uniforme setorial" and monofasia:
        return None, False, False
    if tipo == "Sem alíquota":
        if informada is not None:
            return percentual_para_fracao(informada), True, True
        return ZERO, False, False
    if tipo == "Alíquotas Combinadas (Ad Valorem e Ad Rem)":
        return None, False, False
    raise TipoAliquotaDesconhecido(tipo, c_class_trib, cst)


def _buscar_tipo(
    tipo: str,
    id_tributo: int | None,
    codigo_uf: int | None,
    codigo_municipio: int | None,
    data: date | None,
    nbs: str | None,
    id_classificacao: int,
    buscar_padrao: BuscaPadrao | None,
    buscar_referencia: BuscaReferencia | None,
    buscar_setorial: BuscaSetorial | None,
    buscar_fixa: BuscaFixa | None,
) -> Decimal | None:
    if id_tributo is None or data is None:
        raise AliquotaUniformeSetorialNaoEncontrada(data)
    if tipo == "Padrão":
        if buscar_padrao is None:
            raise AliquotaUniformeSetorialNaoEncontrada(data)
        return buscar_aliquota_padrao(id_tributo, codigo_uf, codigo_municipio, data, buscar_padrao)
    if tipo == "Uniforme nacional (referência)":
        if buscar_referencia is None:
            raise AliquotaUniformeSetorialNaoEncontrada(data)
        return percentual_para_fracao(buscar_referencia(id_tributo, data))
    if tipo == "Uniforme setorial":
        if buscar_setorial is None:
            raise AliquotaUniformeSetorialNaoEncontrada(data)
        encontrada = buscar_setorial(nbs, id_tributo, id_classificacao, data)
        if encontrada is None:
            raise AliquotaUniformeSetorialNaoEncontrada(data)
        return percentual_para_fracao(encontrada)
    if buscar_fixa is None:
        raise AliquotaFixaNaoEncontrada(data)
    encontrada = buscar_fixa(id_tributo, id_classificacao, data)
    if encontrada is None:
        raise AliquotaFixaNaoEncontrada(data)
    return percentual_para_fracao(encontrada)


def _monofasia_setorial(tipo: str, tratamento: Tratamento) -> bool:
    return tipo == "Uniforme setorial" and tratamento.possui_monofasia


def _reducao(
    classificacao: Classificacao,
    aliquota_efetiva: Decimal | None,
    reducao: Decimal | None,
    aliquota_dividida: bool,
    tem_regular: bool,
    ente: str | None,
) -> Reducao | None:
    if not classificacao.grupo_reducao or (tem_regular and ente is None):
        return None
    if reducao is None or aliquota_efetiva is None:
        return None
    percentual = fracao_para_percentual(reducao)
    efetiva = fracao_para_percentual(aliquota_efetiva) if aliquota_dividida else aliquota_efetiva
    assert percentual is not None and efetiva is not None
    return Reducao(percentual, efetiva)


def _compra_gov(
    ente: str | None,
    tributo: Tributo | None,
    aliquota: Decimal | None,
    valor: Decimal | None,
) -> CompraGovernamental | None:
    if ente is None:
        return None
    if tributo is None or aliquota is None or valor is None:
        raise CompraGovernamentalIndisponivel(tributo)
    publicada = fracao_para_percentual(aliquota)
    assert publicada is not None
    if tributo is Tributo.CBS:
        return CompraGovernamental(aliquota_cbs=publicada, tributo_cbs=valor)
    if tributo is Tributo.IBS_ESTADUAL:
        return CompraGovernamental(aliquota_ibs_estadual=publicada, tributo_ibs_estadual=valor)
    if tributo is Tributo.IBS_MUNICIPAL:
        return CompraGovernamental(aliquota_ibs_municipal=publicada, tributo_ibs_municipal=valor)
    raise CompraGovernamentalIndisponivel(tributo)


def _regular(
    tem_regular: bool,
    cst: str | None,
    c_class_trib: str | None,
    base: Decimal,
    aliquota: Decimal | None,
    reducao: Decimal | None,
    aliquota_dividida: bool,
    possui_reducao: bool,
) -> TributacaoRegular | None:
    if not tem_regular:
        return None
    assert cst is not None and c_class_trib is not None and aliquota is not None
    efetiva = aliquota
    if possui_reducao and reducao is not None:
        efetiva = multiplicar(aliquota, Decimal(1) - reducao)
    if aliquota_dividida:
        efetiva = _publicar_aliquota(efetiva)
    assert efetiva is not None
    devido = arredondar_valor_fiscal(multiplicar(base, efetiva))
    assert devido is not None
    publicada = fracao_para_percentual(efetiva) if aliquota_dividida else efetiva
    assert publicada is not None
    return TributacaoRegular(cst, c_class_trib, base, publicada, devido)


def _monofasia(
    classificacao: Classificacao,
    quantidade: Decimal | None,
    principal: Decimal | None,
    secundaria: Decimal | None,
    tributo_calculado: Decimal,
    tributo_devido: Decimal | None,
    variacao: Decimal | None,
) -> Monofasia:
    padrao = None
    retencao = None
    retido = None
    diferido = None
    if classificacao.grupo_monofasia_padrao:
        assert quantidade is not None and principal is not None and secundaria is not None
        quantidade_padrao = quantidade
        aliquota = principal
        if classificacao.grupo_monofasia_ret:
            assert variacao is not None
            quantidade_padrao = percentual_para_fracao(quantidade * variacao)
            aliquota = secundaria
        padrao = EtapaMonofasia(quantidade_padrao, arredondar_aliquota_publicada(aliquota), tributo_calculado)
    if classificacao.grupo_monofasia_reten:
        assert quantidade is not None and secundaria is not None and tributo_devido is not None
        retencao = EtapaMonofasia(
            multiplicar(quantidade, _fator_biocombustivel()),
            arredondar_aliquota_publicada(secundaria),
            tributo_devido,
        )
    if classificacao.grupo_monofasia_ret:
        assert quantidade is not None and principal is not None and tributo_devido is not None
        retido = EtapaMonofasia(quantidade, arredondar_aliquota_publicada(principal), tributo_devido)
    if classificacao.grupo_monofasia_diferimento:
        assert tributo_devido is not None
        diferido = DiferimentoMonofasia(
            arredondar_aliquota_publicada(
                fracao_para_percentual(dividir(tributo_calculado - tributo_devido, tributo_calculado))
            ),
            tributo_calculado - tributo_devido,
        )
    return Monofasia(padrao, retencao, retido, diferido)


def _fator_biocombustivel() -> Decimal | None:
    return dividir(PBIO, CEM - PBIO)


def _publicar_aliquota(fracao: Decimal | None) -> Decimal | None:
    if fracao is None:
        return None
    return percentual_para_fracao(arredondar_aliquota_publicada(fracao_para_percentual(fracao)))


def _usa_aliquota(expressao: str) -> bool:
    return bool(expressao.strip()) and _ALIQUOTA.search(expressao) is not None


def _vars(**valores: Decimal | None) -> dict[str, Decimal]:
    nomes = (
        "baseCalculo",
        "impostoSeletivoCalculado",
        "baseCalculoInformada",
        "impostoSeletivoInformado",
        "aliquotaEfetiva",
        "redutor",
        "ajuste",
        "aliquotaAdRem",
        "aliquotaAdValorem",
        "aliquotaReferencia",
        "aliquotaPadraoOuReferencia",
        "percentualReducao",
        "pRedutorCompraGov",
        "aliquota",
        "quantidade",
        "tributoCalculado",
        "percentualDiferimento",
        "aliquotaAdRemPrincipal",
        "aliquotaAdRemSecundaria",
        "variacaoPontoPercentual",
        "pBio",
    )
    mapa = {nome: ZERO for nome in nomes}
    for nome, valor in valores.items():
        mapa[nome] = valor if valor is not None else ZERO
    return mapa
