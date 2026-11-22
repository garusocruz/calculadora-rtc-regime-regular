"""Orquestração do cálculo de tributos de um item.

Pin ``f1eebd7ce3157423b1a6aaca7dc1d6c3395452c4``, ``CalculoTributoService``.
Reutiliza ``calcular_cbs_ibs`` e ``calcular_imposto_seletivo``; não inclui memória
de cálculo, Spring, CompletableFuture nem validações de ``ProcessamentoItemService``.
"""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass, replace
from datetime import date
from decimal import Decimal

from calculadora_rtc_regime_regular.arredondamento import (
    arredondar_aliquota_publicada,
    arredondar_valor_fiscal,
    multiplicar,
    percentual_para_fracao,
)
from calculadora_rtc_regime_regular.cbs_ibs import (
    BuscaFixa,
    BuscaPadrao,
    BuscaReferencia,
    BuscaSetorial,
    Classificacao,
    CompraGovernamental,
    Diferimento,
    EtapaMonofasia,
    Monofasia,
    Reducao,
    ResultadoCbsIbs,
    TributacaoRegular,
    Tributo,
    Tratamento,
    calcular_cbs_ibs,
)
from calculadora_rtc_regime_regular.imposto_seletivo import (
    AliquotaSeletivo,
    ResultadoSeletivo,
    TratamentoSeletivo,
    calcular_imposto_seletivo,
)

ZERO = Decimal(0)
ID_CBS = 2
ID_IBS_UF = 3
ID_IBS_MUN = 4

BuscaPercentualTransferencia = Callable[[date], Decimal | None]
BuscaPercentualReducao = Callable[[int], Decimal | None]


class CompraGovernamentalInconsistente(RuntimeError):
    pass


@dataclass(frozen=True)
class AliquotasNominais:
    cbs: Decimal | None = None
    ibs_estadual: Decimal | None = None
    ibs_municipal: Decimal | None = None


@dataclass(frozen=True)
class ImpostoSeletivoItem:
    cst: str
    c_class_trib: str
    base_calculo: Decimal | None = None
    quantidade: Decimal | None = None
    unidade: str | None = None
    valor_informado: Decimal | None = None


@dataclass(frozen=True)
class TributacaoRegularItem:
    cst: str
    c_class_trib: str


@dataclass(frozen=True)
class ItemOperacao:
    numero: int = 1
    cst: str = ""
    c_class_trib: str = ""
    base_calculo: Decimal = ZERO
    quantidade: Decimal | None = None
    unidade: str | None = None
    ncm: str | None = None
    nbs: str | None = None
    aliquotas_nominais: AliquotasNominais | None = None
    imposto_seletivo: ImpostoSeletivoItem | None = None
    tributacao_regular: TributacaoRegularItem | None = None


@dataclass(frozen=True)
class TratamentoClassificacaoItem:
    tratamento_cbs_ibs: Tratamento
    classificacao_cbs_ibs: Classificacao
    tratamento_imposto_seletivo: TratamentoSeletivo | None = None
    aliquota_imposto_seletivo: AliquotaSeletivo | None = None
    tem_desoneracao: bool = False


@dataclass(frozen=True)
class OperacaoCalculo:
    data: date
    codigo_uf: int | None
    codigo_municipio: int | None
    tp_ente_gov: str | None
    p_redutor: Decimal
    item: ItemOperacao
    tratamento: TratamentoClassificacaoItem


@dataclass
class SaidaCbsIbs:
    """Cópia mutável de ``ResultadoCbsIbs`` para impacto de compra governamental."""

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

    @classmethod
    def de(cls, resultado: ResultadoCbsIbs) -> SaidaCbsIbs:
        return cls(
            resultado.base_calculo,
            resultado.aliquota,
            resultado.tributo_calculado,
            resultado.tributo_devido,
            resultado.diferimento,
            resultado.quantidade,
            resultado.reducao,
            resultado.compra_governamental,
            resultado.tributacao_regular,
            resultado.monofasia,
        )

    def possui_compra_gov(self) -> bool:
        return self.compra_governamental is not None


@dataclass(frozen=True)
class GrupoDiferimento:
    percentual: Decimal
    valor: Decimal


@dataclass(frozen=True)
class GrupoReducao:
    percentual_reducao: Decimal
    aliquota_efetiva: Decimal


@dataclass(frozen=True)
class GrupoCbs:
    aliquota: Decimal | None
    valor: Decimal | None
    diferimento: GrupoDiferimento | None = None
    reducao: GrupoReducao | None = None


@dataclass(frozen=True)
class GrupoIbsUf:
    aliquota: Decimal | None
    valor: Decimal | None
    diferimento: GrupoDiferimento | None = None
    reducao: GrupoReducao | None = None


@dataclass(frozen=True)
class GrupoIbsMun:
    aliquota: Decimal | None
    valor: Decimal | None
    diferimento: GrupoDiferimento | None = None
    reducao: GrupoReducao | None = None


@dataclass(frozen=True)
class TributacaoRegularGrupo:
    cst: str
    c_class_trib: str
    aliquota_efetiva_cbs: Decimal | None = None
    tributo_cbs: Decimal | None = None
    aliquota_efetiva_ibs_uf: Decimal | None = None
    tributo_ibs_uf: Decimal | None = None
    aliquota_efetiva_ibs_mun: Decimal | None = None
    tributo_ibs_mun: Decimal | None = None


@dataclass(frozen=True)
class CompraGovernamentalGrupo:
    aliquota_cbs: Decimal
    tributo_cbs: Decimal
    aliquota_ibs_uf: Decimal
    tributo_ibs_uf: Decimal
    aliquota_ibs_mun: Decimal
    tributo_ibs_mun: Decimal

    def zerar_valores(self) -> CompraGovernamentalGrupo:
        return CompraGovernamentalGrupo(ZERO, ZERO, ZERO, ZERO, ZERO, ZERO)


@dataclass(frozen=True)
class MonofasiaPadrao:
    quantidade: Decimal
    ad_rem_ibs: Decimal
    ad_rem_cbs: Decimal
    valor_ibs: Decimal
    valor_cbs: Decimal


@dataclass(frozen=True)
class MonofasiaRetencao:
    quantidade: Decimal
    ad_rem_ibs: Decimal
    ad_rem_cbs: Decimal
    valor_ibs: Decimal
    valor_cbs: Decimal


@dataclass(frozen=True)
class MonofasiaRetido:
    quantidade: Decimal
    ad_rem_ibs: Decimal
    ad_rem_cbs: Decimal
    valor_ibs: Decimal
    valor_cbs: Decimal


@dataclass(frozen=True)
class MonofasiaDiferimento:
    percentual_ibs: Decimal
    valor_ibs: Decimal
    percentual_cbs: Decimal
    valor_cbs: Decimal


@dataclass(frozen=True)
class MonofasiaItem:
    padrao: MonofasiaPadrao | None = None
    retencao: MonofasiaRetencao | None = None
    retido: MonofasiaRetido | None = None
    diferimento: MonofasiaDiferimento | None = None
    total_ibs: Decimal = ZERO
    total_cbs: Decimal = ZERO


@dataclass(frozen=True)
class GrupoIbsCbs:
    base_calculo: Decimal | None
    ibs_uf: GrupoIbsUf | None
    ibs_mun: GrupoIbsMun | None
    valor_ibs: Decimal
    cbs: GrupoCbs | None
    tributacao_regular: TributacaoRegularGrupo | None
    compra_governamental: CompraGovernamentalGrupo | None


@dataclass(frozen=True)
class IbsCbsItem:
    cst: str
    c_class_trib: str
    grupo_ibs_cbs: GrupoIbsCbs | None
    monofasia: MonofasiaItem | None
    transferencia_credito: None = None
    ajuste_competencia: None = None
    estorno_credito: None = None
    credito_presumido_operacao: None = None
    credito_presumido_ibs_zfm: None = None


@dataclass(frozen=True)
class TributosItem:
    imposto_seletivo: ResultadoSeletivo | None
    ibs_cbs: IbsCbsItem | None


def calcular_tributos(
    operacao: OperacaoCalculo,
    *,
    calculo_ibs_habilitado: bool = False,
    percentual_transferencia_cbs: Decimal | None = None,
    buscar_percentual_transferencia: BuscaPercentualTransferencia | None = None,
    buscar_percentual_reducao: BuscaPercentualReducao | None = None,
    buscar_padrao: BuscaPadrao | None = None,
    buscar_referencia: BuscaReferencia | None = None,
    buscar_setorial: BuscaSetorial | None = None,
    buscar_fixa: BuscaFixa | None = None,
) -> TributosItem:
    item = operacao.item
    tc = operacao.tratamento
    memoria_tratamento = tc.tratamento_cbs_ibs
    if tc.tem_desoneracao:
        memoria_tratamento = tc.tratamento_cbs_ibs

    imposto_seletivo: ResultadoSeletivo | None = None
    valor_is = ZERO
    if tc.tratamento_imposto_seletivo is not None and tc.aliquota_imposto_seletivo is not None:
        assert item.imposto_seletivo is not None
        is_item = item.imposto_seletivo
        imposto_seletivo = calcular_imposto_seletivo(
            cst=is_item.cst,
            c_class_trib=is_item.c_class_trib,
            unidade=is_item.unidade,
            base_informada=is_item.base_calculo,
            quantidade=is_item.quantidade,
            imposto_seletivo_informado=is_item.valor_informado,
            aliquota=tc.aliquota_imposto_seletivo,
            tratamento=tc.tratamento_imposto_seletivo,
        )
        if imposto_seletivo.valor is not None:
            valor_is = imposto_seletivo.valor

    cbs: SaidaCbsIbs | None = None
    ibs_uf: SaidaCbsIbs | None = None
    ibs_mun: SaidaCbsIbs | None = None

    if tc.classificacao_cbs_ibs is not None:
        nominais = item.aliquotas_nominais
        calcular_ibs_uf = calculo_ibs_habilitado or _texto(item.nbs) or _aliquota_nominal(nominais, Tributo.IBS_ESTADUAL)
        calcular_ibs_mun = calculo_ibs_habilitado or _texto(item.nbs) or _aliquota_nominal(nominais, Tributo.IBS_MUNICIPAL)
        comum = _parametros_cbs_ibs(operacao, valor_is, buscar_padrao, buscar_referencia, buscar_setorial, buscar_fixa)
        comum["buscar_percentual_reducao"] = buscar_percentual_reducao
        cbs = _calcular_tributo(
            Tributo.CBS,
            None,
            None,
            True,
            comum,
        )
        ibs_uf = _calcular_tributo(
            Tributo.IBS_ESTADUAL,
            operacao.codigo_uf,
            None,
            calcular_ibs_uf,
            comum,
        )
        ibs_mun = _calcular_tributo(
            Tributo.IBS_MUNICIPAL,
            None,
            operacao.codigo_municipio,
            calcular_ibs_mun,
            comum,
        )

    ibs_cbs = _montar_ibscbs(
        item,
        cbs,
        ibs_uf,
        ibs_mun,
        operacao.tp_ente_gov,
        operacao.data,
        percentual_transferencia_cbs,
        buscar_percentual_transferencia,
    )
    return TributosItem(imposto_seletivo, ibs_cbs)


def _parametros_cbs_ibs(
    operacao: OperacaoCalculo,
    imposto_seletivo_calculado: Decimal,
    buscar_padrao: BuscaPadrao | None,
    buscar_referencia: BuscaReferencia | None,
    buscar_setorial: BuscaSetorial | None,
    buscar_fixa: BuscaFixa | None,
) -> dict[str, object]:
    item = operacao.item
    is_item = item.imposto_seletivo
    imposto_informado = is_item.valor_informado if is_item is not None else None
    regular = item.tributacao_regular
    return {
        "operacao": operacao,
        "base_informada": item.base_calculo,
        "imposto_seletivo_calculado": imposto_seletivo_calculado,
        "imposto_seletivo_informado": imposto_informado,
        "quantidade": item.quantidade,
        "nbs": item.nbs,
        "tem_tributacao_regular": operacao.tratamento.tem_desoneracao,
        "cst_regular": regular.cst if regular else None,
        "c_class_trib_regular": regular.c_class_trib if regular else None,
        "buscar_padrao": buscar_padrao,
        "buscar_referencia": buscar_referencia,
        "buscar_setorial": buscar_setorial,
        "buscar_fixa": buscar_fixa,
    }


def _calcular_tributo(
    tributo: Tributo,
    codigo_uf: int | None,
    codigo_municipio: int | None,
    calcular: bool,
    comum: dict[str, object],
) -> SaidaCbsIbs | None:
    if not calcular:
        return None
    operacao = comum["operacao"]
    assert isinstance(operacao, OperacaoCalculo)
    item = operacao.item
    tc = operacao.tratamento
    nominais = item.aliquotas_nominais
    aliquota_informada = _aliquota_nominal_por_tributo(nominais, tributo)
    id_tributo = {Tributo.CBS: ID_CBS, Tributo.IBS_ESTADUAL: ID_IBS_UF, Tributo.IBS_MUNICIPAL: ID_IBS_MUN}[tributo]
    buscar_red = comum.get("buscar_percentual_reducao")
    percentual_reducao = None
    if buscar_red is not None:
        percentual_reducao = buscar_red(id_tributo)
    resultado = calcular_cbs_ibs(
        aliquota_informada=aliquota_informada,
        base_informada=comum["base_informada"],  # type: ignore[arg-type]
        imposto_seletivo_calculado=comum["imposto_seletivo_calculado"],  # type: ignore[arg-type]
        imposto_seletivo_informado=comum["imposto_seletivo_informado"],  # type: ignore[arg-type]
        redutor_compra_gov=operacao.p_redutor,
        tratamento=tc.tratamento_cbs_ibs,
        classificacao=tc.classificacao_cbs_ibs,
        quantidade=comum["quantidade"],  # type: ignore[arg-type]
        percentual_reducao=percentual_reducao,
        id_tributo=id_tributo,
        codigo_uf=codigo_uf,
        codigo_municipio=codigo_municipio,
        data=operacao.data,
        nbs=comum["nbs"],  # type: ignore[arg-type]
        tributo=tributo,
        ente_governamental=operacao.tp_ente_gov,
        tem_tributacao_regular=comum["tem_tributacao_regular"],  # type: ignore[arg-type]
        cst_regular=comum["cst_regular"],  # type: ignore[arg-type]
        c_class_trib_regular=comum["c_class_trib_regular"],  # type: ignore[arg-type]
        buscar_padrao=comum["buscar_padrao"],  # type: ignore[arg-type]
        buscar_referencia=comum["buscar_referencia"],  # type: ignore[arg-type]
        buscar_setorial=comum["buscar_setorial"],  # type: ignore[arg-type]
        buscar_fixa=comum["buscar_fixa"],  # type: ignore[arg-type]
    )
    if resultado is None:
        return None
    return SaidaCbsIbs.de(resultado)


def _montar_ibscbs(
    item: ItemOperacao,
    cbs: SaidaCbsIbs | None,
    ibs_uf: SaidaCbsIbs | None,
    ibs_mun: SaidaCbsIbs | None,
    tp_ente_gov: str | None,
    data_fato_gerador: date,
    percentual_transferencia: Decimal | None,
    buscar_percentual_transferencia: BuscaPercentualTransferencia | None,
) -> IbsCbsItem:
    monofasia = _montar_monofasia(cbs, ibs_uf, ibs_mun)
    grupo = None if monofasia is not None else _montar_grupo_ibscbs(
        cbs,
        ibs_uf,
        ibs_mun,
        tp_ente_gov,
        data_fato_gerador,
        percentual_transferencia,
        buscar_percentual_transferencia,
    )
    return IbsCbsItem(
        item.cst,
        item.c_class_trib,
        grupo,
        monofasia,
    )


def _montar_grupo_ibscbs(
    cbs: SaidaCbsIbs | None,
    ibs_uf: SaidaCbsIbs | None,
    ibs_mun: SaidaCbsIbs | None,
    tp_ente_gov: str | None,
    data_fato_gerador: date,
    percentual_transferencia: Decimal | None,
    buscar_percentual_transferencia: BuscaPercentualTransferencia | None,
) -> GrupoIbsCbs | None:
    if cbs is None and ibs_uf is None and ibs_mun is None:
        return None

    v_bc = _v_bc(ibs_mun, _v_bc(ibs_uf, _v_bc(cbs, None)))
    assert v_bc is not None

    p_transferencia = percentual_transferencia
    if p_transferencia is None and buscar_percentual_transferencia is not None:
        p_transferencia = buscar_percentual_transferencia(data_fato_gerador)

    compra = _compra_governamental(cbs, ibs_uf, ibs_mun)
    compra_efetiva = None
    if compra is not None and tp_ente_gov is not None:
        assert p_transferencia is not None
        compra_efetiva = _valores_efetivos_compra_governamental(compra, tp_ente_gov, p_transferencia, data_fato_gerador, v_bc)

    if compra_efetiva is not None:
        _trata_impacto_compra_gov(cbs, compra_efetiva.aliquota_cbs, compra_efetiva.tributo_cbs, v_bc)
        _trata_impacto_compra_gov(ibs_uf, compra_efetiva.aliquota_ibs_uf, compra_efetiva.tributo_ibs_uf, v_bc)
        _trata_impacto_compra_gov(ibs_mun, compra_efetiva.aliquota_ibs_mun, compra_efetiva.tributo_ibs_mun, v_bc)

    grupo_ibs_uf = _ibs_uf(ibs_uf)
    grupo_ibs_mun = _ibs_mun(ibs_mun)
    v_ibs = _v_ibs(grupo_ibs_uf, grupo_ibs_mun)
    grupo_cbs = _cbs(cbs)
    tributacao_regular = _tributacao_regular(cbs, ibs_uf, ibs_mun)

    if tributacao_regular is not None and compra is not None:
        compra = compra.zerar_valores()

    return GrupoIbsCbs(v_bc, grupo_ibs_uf, grupo_ibs_mun, v_ibs, grupo_cbs, tributacao_regular, compra)


def _trata_impacto_compra_gov(
    tributo: SaidaCbsIbs | None,
    aliquota_efetiva: Decimal,
    valor: Decimal,
    v_bc: Decimal,
) -> None:
    if tributo is None:
        return
    reducao = tributo.reducao
    if reducao is None:
        reducao = Reducao(ZERO, ZERO)
        tributo.reducao = reducao

    regular = tributo.tributacao_regular
    if regular is not None:
        tributo.reducao = Reducao(ZERO, ZERO)
        tributo.tributo_devido = ZERO
        tributo.tributacao_regular = replace(regular, aliquota_efetiva=aliquota_efetiva, tributo_devido=valor)
        return

    tributo.reducao = replace(reducao, aliquota_efetiva=aliquota_efetiva)
    if tributo.diferimento is None:
        tributo.tributo_devido = valor
        return

    bruto = arredondar_valor_fiscal(multiplicar(v_bc, percentual_para_fracao(aliquota_efetiva)))
    assert bruto is not None
    v_dif = arredondar_valor_fiscal(
        multiplicar(
            multiplicar(v_bc, percentual_para_fracao(aliquota_efetiva)),
            percentual_para_fracao(tributo.diferimento.percentual),
        )
    )
    assert v_dif is not None
    tributo.diferimento = replace(tributo.diferimento, valor=v_dif)
    devido = bruto - v_dif
    tributo.tributo_devido = ZERO if devido < 0 else devido


def _v_ibs(ibs_uf: GrupoIbsUf | None, ibs_mun: GrupoIbsMun | None) -> Decimal:
    v_uf = ibs_uf.valor if ibs_uf is not None and ibs_uf.valor is not None else ZERO
    v_mun = ibs_mun.valor if ibs_mun is not None and ibs_mun.valor is not None else ZERO
    return v_uf + v_mun


def _v_bc(saida: SaidaCbsIbs | None, valor: Decimal | None) -> Decimal | None:
    if valor is not None:
        return valor
    if saida is not None:
        return saida.base_calculo
    return None


def _ibs_uf(saida: SaidaCbsIbs | None) -> GrupoIbsUf | None:
    if saida is None:
        return None
    return GrupoIbsUf(
        saida.aliquota,
        saida.tributo_devido,
        _diferimento_grupo(saida.diferimento),
        _reducao_grupo(saida.reducao),
    )


def _ibs_mun(saida: SaidaCbsIbs | None) -> GrupoIbsMun | None:
    if saida is None:
        return None
    return GrupoIbsMun(
        saida.aliquota,
        saida.tributo_devido,
        _diferimento_grupo(saida.diferimento),
        _reducao_grupo(saida.reducao),
    )


def _cbs(saida: SaidaCbsIbs | None) -> GrupoCbs | None:
    if saida is None:
        return None
    return GrupoCbs(
        saida.aliquota,
        saida.tributo_devido,
        _diferimento_grupo(saida.diferimento),
        _reducao_grupo(saida.reducao),
    )


def _diferimento_grupo(dif: Diferimento | None) -> GrupoDiferimento | None:
    if dif is None:
        return None
    return GrupoDiferimento(dif.percentual, dif.valor)


def _reducao_grupo(red: Reducao | None) -> GrupoReducao | None:
    if red is None:
        return None
    return GrupoReducao(red.percentual, red.aliquota_efetiva)


def _tributacao_regular(
    cbs: SaidaCbsIbs | None,
    ibs_uf: SaidaCbsIbs | None,
    ibs_mun: SaidaCbsIbs | None,
) -> TributacaoRegularGrupo | None:
    cst: str | None = None
    c_class: str | None = None
    aliq_cbs: Decimal | None = None
    trib_cbs: Decimal | None = None
    aliq_uf: Decimal | None = None
    trib_uf: Decimal | None = None
    aliq_mun: Decimal | None = None
    trib_mun: Decimal | None = None

    if cbs is not None and cbs.tributacao_regular is not None:
        tr = cbs.tributacao_regular
        cst, c_class = tr.cst, tr.c_class_trib
        aliq_cbs, trib_cbs = tr.aliquota_efetiva, tr.tributo_devido
    if ibs_uf is not None and ibs_uf.tributacao_regular is not None:
        tr = ibs_uf.tributacao_regular
        if cst is None:
            cst, c_class = tr.cst, tr.c_class_trib
        aliq_uf, trib_uf = tr.aliquota_efetiva, tr.tributo_devido
    if ibs_mun is not None and ibs_mun.tributacao_regular is not None:
        tr = ibs_mun.tributacao_regular
        if cst is None:
            cst, c_class = tr.cst, tr.c_class_trib
        aliq_mun, trib_mun = tr.aliquota_efetiva, tr.tributo_devido

    if cst is None or c_class is None:
        return None
    return TributacaoRegularGrupo(cst, c_class, aliq_cbs, trib_cbs, aliq_uf, trib_uf, aliq_mun, trib_mun)


def _compra_governamental(
    cbs: SaidaCbsIbs | None,
    ibs_uf: SaidaCbsIbs | None,
    ibs_mun: SaidaCbsIbs | None,
) -> CompraGovernamentalGrupo | None:
    tem_cbs = cbs is not None and cbs.possui_compra_gov()
    tem_uf = ibs_uf is not None and ibs_uf.possui_compra_gov()
    tem_mun = ibs_mun is not None and ibs_mun.possui_compra_gov()
    if tem_cbs and tem_uf and tem_mun:
        assert cbs is not None and ibs_uf is not None and ibs_mun is not None
        cg_cbs = cbs.compra_governamental
        cg_uf = ibs_uf.compra_governamental
        cg_mun = ibs_mun.compra_governamental
        assert cg_cbs is not None and cg_uf is not None and cg_mun is not None
        return CompraGovernamentalGrupo(
            _req(cg_cbs.aliquota_cbs),
            _req(cg_cbs.tributo_cbs),
            _req(cg_uf.aliquota_ibs_estadual),
            _req(cg_uf.tributo_ibs_estadual),
            _req(cg_mun.aliquota_ibs_municipal),
            _req(cg_mun.tributo_ibs_municipal),
        )
    if tem_cbs or tem_uf or tem_mun:
        raise CompraGovernamentalInconsistente(
            "Erro ao consolidar valores de compras governamentais. Algum dos tributos não calculou compra governamental."
        )
    return None


def _valores_efetivos_compra_governamental(
    compra: CompraGovernamentalGrupo,
    tp_ente_gov: str,
    p_transferencia_cbs: Decimal,
    data_fato_gerador: date,
    v_bc: Decimal,
) -> CompraGovernamentalGrupo | None:
    if tp_ente_gov is None:
        return None
    if data_fato_gerador < date(2027, 1, 1):
        return compra

    soma = compra.aliquota_cbs + compra.aliquota_ibs_uf + compra.aliquota_ibs_mun
    if _ente_uniao(tp_ente_gov):
        return _com_aliquotas(soma, ZERO, ZERO, v_bc)

    p_cbs_final = arredondar_aliquota_publicada(
        compra.aliquota_cbs - compra.aliquota_cbs * percentual_para_fracao(p_transferencia_cbs)
    )
    assert p_cbs_final is not None
    p_recebedor = soma - p_cbs_final

    if _ente_estado(tp_ente_gov):
        return _com_aliquotas(p_cbs_final, p_recebedor, ZERO, v_bc)
    if _ente_municipio(tp_ente_gov):
        return _com_aliquotas(p_cbs_final, ZERO, p_recebedor, v_bc)
    return _com_aliquotas(p_cbs_final, ZERO, ZERO, v_bc)


def _com_aliquotas(
    p_cbs: Decimal,
    p_ibs_uf: Decimal,
    p_ibs_mun: Decimal,
    v_bc: Decimal,
) -> CompraGovernamentalGrupo:
    return CompraGovernamentalGrupo(
        p_cbs,
        _valor_pela_aliquota(v_bc, p_cbs),
        p_ibs_uf,
        _valor_pela_aliquota(v_bc, p_ibs_uf),
        p_ibs_mun,
        _valor_pela_aliquota(v_bc, p_ibs_mun),
    )


def _valor_pela_aliquota(v_bc: Decimal, aliquota: Decimal) -> Decimal:
    return arredondar_valor_fiscal(multiplicar(v_bc, percentual_para_fracao(aliquota)))


def _montar_monofasia(
    cbs: SaidaCbsIbs | None,
    ibs_uf: SaidaCbsIbs | None,
    ibs_mun: SaidaCbsIbs | None,
) -> MonofasiaItem | None:
    padrao = _mono_padrao(cbs, ibs_uf, ibs_mun)
    retencao = _mono_retencao(cbs, ibs_uf, ibs_mun)
    retido = _mono_retido(cbs, ibs_uf, ibs_mun)
    diferido = _mono_diferimento(cbs, ibs_uf, ibs_mun)
    if padrao is None and retencao is None and retido is None and diferido is None:
        return None

    v_ibs_mono = padrao.valor_ibs if padrao is not None else ZERO
    v_cbs_mono = padrao.valor_cbs if padrao is not None else ZERO
    v_ibs_reten = retencao.valor_ibs if retencao is not None else ZERO
    v_cbs_reten = retencao.valor_cbs if retencao is not None else ZERO
    v_ibs_dif = diferido.valor_ibs if diferido is not None else ZERO
    v_cbs_dif = diferido.valor_cbs if diferido is not None else ZERO

  # NT NFe 1.30
    total_ibs = v_ibs_mono + v_ibs_reten - v_ibs_dif
    total_cbs = v_cbs_mono + v_cbs_reten - v_cbs_dif
    return MonofasiaItem(padrao, retencao, retido, diferido, total_ibs, total_cbs)


def _mono_padrao(
    cbs: SaidaCbsIbs | None,
    ibs_uf: SaidaCbsIbs | None,
    ibs_mun: SaidaCbsIbs | None,
) -> MonofasiaPadrao | None:
    parte_cbs = _etapa_cbs(cbs, "padrao")
    parte_ibs = _etapa_ibs(ibs_uf, ibs_mun, "padrao")
    if parte_cbs is None and parte_ibs is None:
        return None
    qtd = ZERO
    ad_rem_ibs = ZERO
    ad_rem_cbs = ZERO
    v_ibs = ZERO
    v_cbs = ZERO
    if parte_cbs is not None:
        qtd = parte_cbs.quantidade
        ad_rem_cbs = parte_cbs.aliquota_ad_rem
        v_cbs = parte_cbs.valor
    if parte_ibs is not None:
        qtd = parte_ibs.quantidade if qtd == ZERO else qtd
        ad_rem_ibs = parte_ibs.aliquota_ad_rem
        v_ibs = parte_ibs.valor
    return MonofasiaPadrao(qtd, ad_rem_ibs, ad_rem_cbs, v_ibs, v_cbs)


def _mono_retencao(
    cbs: SaidaCbsIbs | None,
    ibs_uf: SaidaCbsIbs | None,
    ibs_mun: SaidaCbsIbs | None,
) -> MonofasiaRetencao | None:
    return _mono_etapa_generica(cbs, ibs_uf, ibs_mun, "retencao", MonofasiaRetencao)


def _mono_retido(
    cbs: SaidaCbsIbs | None,
    ibs_uf: SaidaCbsIbs | None,
    ibs_mun: SaidaCbsIbs | None,
) -> MonofasiaRetido | None:
    return _mono_etapa_generica(cbs, ibs_uf, ibs_mun, "retido", MonofasiaRetido)


def _mono_etapa_generica(
    cbs: SaidaCbsIbs | None,
    ibs_uf: SaidaCbsIbs | None,
    ibs_mun: SaidaCbsIbs | None,
    atributo: str,
    fabrica: type,
):
    parte_cbs = _etapa_cbs(cbs, atributo)
    parte_ibs = _etapa_ibs(ibs_uf, ibs_mun, atributo)
    if parte_cbs is None and parte_ibs is None:
        return None
    qtd = ZERO
    ad_rem_ibs = ZERO
    ad_rem_cbs = ZERO
    v_ibs = ZERO
    v_cbs = ZERO
    if parte_cbs is not None:
        qtd = parte_cbs.quantidade
        ad_rem_cbs = parte_cbs.aliquota_ad_rem
        v_cbs = parte_cbs.valor
    if parte_ibs is not None:
        qtd = parte_ibs.quantidade if qtd == ZERO else qtd
        ad_rem_ibs = parte_ibs.aliquota_ad_rem
        v_ibs = parte_ibs.valor
    return fabrica(qtd, ad_rem_ibs, ad_rem_cbs, v_ibs, v_cbs)


def _mono_diferimento(
    cbs: SaidaCbsIbs | None,
    ibs_uf: SaidaCbsIbs | None,
    ibs_mun: SaidaCbsIbs | None,
) -> MonofasiaDiferimento | None:
    from calculadora_rtc_regime_regular.cbs_ibs import DiferimentoMonofasia

    p_ibs = ZERO
    v_ibs = ZERO
    p_cbs = ZERO
    v_cbs = ZERO
    dif_cbs = _diferido_cbs(cbs)
    dif_ibs = _diferido_ibs(ibs_uf)
    if dif_cbs is None and dif_ibs is None:
        return None
    if dif_cbs is not None:
        assert isinstance(dif_cbs, DiferimentoMonofasia)
        p_cbs = dif_cbs.percentual if dif_cbs.percentual is not None else ZERO
        v_cbs = dif_cbs.valor
    if dif_ibs is not None:
        assert isinstance(dif_ibs, DiferimentoMonofasia)
        p_ibs = dif_ibs.percentual if dif_ibs.percentual is not None else ZERO
        v_ibs = dif_ibs.valor
    return MonofasiaDiferimento(p_ibs, v_ibs, p_cbs, v_cbs)


def _etapa_cbs(saida: SaidaCbsIbs | None, atributo: str) -> EtapaMonofasia | None:
    if saida is None or saida.monofasia is None:
        return None
    return getattr(saida.monofasia, atributo)


def _etapa_ibs(
    ibs_uf: SaidaCbsIbs | None,
    ibs_mun: SaidaCbsIbs | None,
    atributo: str,
) -> EtapaMonofasia | None:
    etapa_uf = _etapa_cbs(ibs_uf, atributo)
    return _merge_etapa(etapa_uf, None)


def _merge_etapa(g1: EtapaMonofasia | None, g2: EtapaMonofasia | None) -> EtapaMonofasia | None:
    if g1 is None:
        return g2
    if g2 is None:
        return g1
    quantidade = g1.quantidade if g1.quantidade is not None else g2.quantidade
    aliquota = g1.aliquota_ad_rem if g1.aliquota_ad_rem is not None else g2.aliquota_ad_rem
    valor = (g1.valor if g1.valor is not None else ZERO) + (g2.valor if g2.valor is not None else ZERO)
    assert quantidade is not None and aliquota is not None
    return EtapaMonofasia(quantidade, aliquota, valor)


def _diferido_cbs(saida: SaidaCbsIbs | None):
    if saida is None or saida.monofasia is None:
        return None
    return saida.monofasia.diferido


def _diferido_ibs(ibs_uf: SaidaCbsIbs | None):
    return _diferido_cbs(ibs_uf)


def _aliquota_nominal(nominais: AliquotasNominais | None, tributo: Tributo) -> bool:
    if nominais is None:
        return False
    if tributo is Tributo.IBS_ESTADUAL:
        return nominais.ibs_estadual is not None
    if tributo is Tributo.IBS_MUNICIPAL:
        return nominais.ibs_municipal is not None
    return False


def _aliquota_nominal_por_tributo(nominais: AliquotasNominais | None, tributo: Tributo) -> Decimal | None:
    if nominais is None:
        return None
    if tributo is Tributo.CBS:
        return nominais.cbs
    if tributo is Tributo.IBS_ESTADUAL:
        return nominais.ibs_estadual
    if tributo is Tributo.IBS_MUNICIPAL:
        return nominais.ibs_municipal
    return None


def _texto(valor: str | None) -> bool:
    return valor is not None and valor.strip() != ""


def _req(valor: Decimal | None) -> Decimal:
    assert valor is not None
    return valor


def _ente_uniao(tp: str) -> bool:
    return tp.upper() in {"UNIAO", "UNIÃO", "1"}


def _ente_estado(tp: str) -> bool:
    return tp.upper() in {"ESTADO", "DISTRITO_FEDERAL", "2", "3"}


def _ente_municipio(tp: str) -> bool:
    return tp.upper() in {"MUNICIPIO", "MUNICÍPIO", "CONSORCIO_PUBLICO", "COMITE_GESTOR_IBS", "4", "5", "6"}