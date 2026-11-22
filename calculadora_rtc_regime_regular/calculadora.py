"""Orquestração do cálculo de tributos da operação (pin f1eebd7ce3157423b1a6aaca7dc1d6c3395452c4).

Espelha ``CalculadoraService.calcularTributos`` sem Spring, ModelMapper, parallelStream ou log.
"""

from __future__ import annotations

import sqlite3
from dataclasses import dataclass, field
from datetime import date
from decimal import Decimal

from calculadora_rtc_regime_regular.aliquota_resultado import AliquotaResultado
from calculadora_rtc_regime_regular.banco import conectar
from calculadora_rtc_regime_regular.calculo_item import (
    AliquotasNominais,
    ImpostoSeletivoItem,
    ItemOperacao,
    OperacaoCalculo,
    TratamentoClassificacaoItem,
    TributacaoRegularItem,
    TributosItem,
    calcular_tributos,
)
from calculadora_rtc_regime_regular.imposto_seletivo import AliquotaSeletivo
from calculadora_rtc_regime_regular.cbs_ibs import AjusteNaoImplementado, Classificacao, Tratamento
from calculadora_rtc_regime_regular.consultas import (
    AliquotaAdRemProdutoService,
    AliquotaAdValoremProdutoService,
    AliquotaAdValoremServicoService,
    AliquotaReferenciaService,
    FundamentacaoClassificacaoService,
    MunicipioService,
    TratamentoClassificacaoDTO as TratamentoConsulta,
    PercentualReducaoService,
    RedutorCompraGovernamentalService,
    SituacaoTributariaService,
    TipoDfeService,
    TipoEnteGovernamental,
    TransferenciaCBSService,
    TratamentoClassificacaoService,
    TratamentoTributarioService,
    TributoEnum,
    UfService,
)
from calculadora_rtc_regime_regular.memoria import MemoriaCalculoService
from calculadora_rtc_regime_regular.nomenclatura import (
    NbsAplicavelRepositorioSqlite,
    NbsAplicavelService,
    NbsRepositorioSqlite,
    NbsService,
    NcmAplicavelRepositorioSqlite,
    NcmAplicavelService,
    NcmRepositorioSqlite,
    NcmService,
    montar_nomenclatura_sqlite,
)
from calculadora_rtc_regime_regular.pedagio import buscar_aliquota_sqlite
from calculadora_rtc_regime_regular.processamento_item import (
    ClassificacaoTributariaDTO,
    ItemOperacaoInput,
    OperacaoInput,
    ProcessamentoItemService,
    SituacaoTributaria as SituacaoTributariaItem,
    TipoDfe as TipoDfeItem,
    ValidacaoException,
)
from calculadora_rtc_regime_regular.roc import (
    CBSDomain,
    DiferimentoDomain,
    GrupoIBSCBSDomain,
    IBSCBSDomain,
    IBSMunDomain,
    IBSUFDomain,
    ImpostoSeletivoDomain,
    MonofasiaDiferimentoDomain,
    MonofasiaDomain,
    MonofasiaPadraoDomain,
    MonofasiaRetencaoDomain,
    MonofasiaRetidoAnteriormenteDomain,
    ObjetoDomain,
    ReducaoAliquotaDomain,
    TributacaoCompraGovernamentalDomain,
    TributacaoRegularDomain,
    TributosDomain,
    ValoresTotaisDomain,
)
from calculadora_rtc_regime_regular.calculo_item import (
    CompraGovernamentalGrupo,
    GrupoCbs,
    GrupoDiferimento,
    GrupoReducao,
    GrupoIbsCbs,
    TributacaoRegularGrupo,
    GrupoIbsMun,
    GrupoIbsUf,
    MonofasiaDiferimento,
    MonofasiaItem,
    MonofasiaPadrao,
    MonofasiaRetencao,
    MonofasiaRetido,
)

ZERO = Decimal(0)
ID_TRIBUTO_IS = 1


class ClassificacaoTributariaNaoVinculadaTipoDfeException(ValidacaoException):
    def __init__(self, c_class_trib: str, tp_doc: int, tributos: str) -> None:
        super().__init__(
            f"Classificação Tributária de código {c_class_trib} não vinculada ao tipo de "
            f"documento fiscal (tpDoc) {tp_doc} ({tributos})"
        )


@dataclass
class CompraGovernamentalInput:
    tp_ente_gov: TipoEnteGovernamental
    tp_oper_gov: int | None = None


@dataclass
class CompraGovernamentalDomain:
    tp_ente_gov: TipoEnteGovernamental | None = None
    p_redutor: Decimal = ZERO
    tp_oper_gov: int | None = None


@dataclass
class OperacaoConsumoDomain:
    g_compra_gov: CompraGovernamentalDomain | None = None


@dataclass
class ROCDomain:
    oper: OperacaoConsumoDomain | None = None
    objetos: list[ObjetoDomain] = field(default_factory=list)
    total: ValoresTotaisDomain | None = None


@dataclass
class OperacaoCalculadoraInput:
    id: str | None = None
    versao: str | None = None
    municipio: int | None = None
    uf: str | None = None
    tp_doc: int | None = None
    data_fato_gerador: date | None = None
    g_compra_gov: CompraGovernamentalInput | None = None
    itens: list[ItemOperacaoInput] = field(default_factory=list)

    def fato_gerador_aplicavel(self) -> date:
        if self.data_fato_gerador is None:
            from calculadora_rtc_regime_regular.processamento_item import DataFatoGeradorNaoInformadaException

            raise DataFatoGeradorNaoInformadaException("Data do fato gerador não informada")
        return self.data_fato_gerador

    def tp_ente_gov(self) -> TipoEnteGovernamental | None:
        if self.g_compra_gov is None:
            return None
        return self.g_compra_gov.tp_ente_gov


def _tratamento_consulta(origem) -> TratamentoConsulta | None:
    if origem is None:
        return None
    if origem.id_tratamento_tributario is None or origem.id_classificacao_tributaria is None:
        return None
    return TratamentoConsulta(
        id_tratamento_tributario=origem.id_tratamento_tributario,
        id_classificacao_tributaria=origem.id_classificacao_tributaria,
        in_incompativel_com_suspensao=origem.in_incompativel_com_suspensao,
        in_exige_grupo_desoneracao=origem.in_exige_grupo_desoneracao,
    )


def _tratamento_de_entidade(ent) -> Tratamento:  # noqa: ANN001
    return Tratamento(
        expressao_aliquota=ent.expressao_aliquota or "",
        expressao_base_calculo=ent.expressao_base_calculo,
        expressao_aliquota_efetiva=ent.expressao_aliquota_efetiva or "",
        expressao_tributo_calculado=ent.expressao_tributo_calculado,
        expressao_tributo_devido=ent.expressao_tributo_devido,
        expressao_percentual_diferimento=ent.expressao_percentual_diferimento or "",
        expressao_valor_diferimento=ent.expressao_valor_diferimento or "",
        possui_ajuste=ent.in_possui_ajuste,
        possui_percentual_reducao=ent.in_possui_percentual_reducao,
        possui_monofasia=ent.in_possui_monofasia,
    )


def _classificacao_calculo(
    conexao: sqlite3.Connection,
    id_cltr: int,
    codigo: str,
    cst: str,
    data: date,
    sit: SituacaoTributariaService,
) -> Classificacao:
    row = conexao.execute(
        "SELECT CLTR_TIPO_ALIQUOTA FROM CLASSIFICACAO_TRIBUTARIA WHERE CLTR_ID = ?",
        (id_cltr,),
    ).fetchone()
    tipo_aliq = str(row[0]) if row is not None else "Padrão"
    st = sit.consultar_situacao_tributaria_por_codigo(cst, 2, data)
    grupo_red = st.in_grupo_reducao if st is not None else False
    grupo_ibscbs = st.in_grupo_ibs_cbs if st is not None else True
    mono_padrao = st.in_grupo_ibs_cbs_mono if st is not None else False
    return Classificacao(
        id_cltr,
        codigo,
        tipo_aliq,
        grupo_reducao=grupo_red,
        grupo_ibs_cbs=grupo_ibscbs,
        grupo_monofasia_padrao=mono_padrao,
        grupo_monofasia_reten=mono_padrao,
        grupo_monofasia_ret=mono_padrao,
        grupo_monofasia_diferimento=mono_padrao,
    )


def _buscar_aliquota_fixa(
    conexao: sqlite3.Connection, id_tributo: int, id_classificacao: int, data: date
) -> Decimal | None:
    d = data.isoformat()
    row = conexao.execute(
        """
        SELECT ALFX_VALOR FROM ALIQUOTA_FIXA
        WHERE ALFX_CLTR_ID = ? AND ALFX_TBTO_ID = ?
          AND ALFX_INICIO_VIGENCIA <= ? AND (ALFX_FIM_VIGENCIA IS NULL OR ALFX_FIM_VIGENCIA >= ?)
        LIMIT 1
        """,
        (id_classificacao, id_tributo, d, d),
    ).fetchone()
    return Decimal(str(row[0])) if row else None


def _buscar_aliquota_setorial(
    conexao: sqlite3.Connection, nbs: str | None, id_tributo: int, id_classificacao: int, data: date
) -> Decimal | None:
    if not nbs:
        return None
    d = data.isoformat()
    row = conexao.execute(
        """
        SELECT ALST_VALOR FROM ALIQUOTA_SETORIAL a
        JOIN NBS n ON a.ALST_NBS_CD = n.NBS_CD
        WHERE n.NBS_CD = ? AND a.ALST_TBTO_ID = ? AND a.ALST_CLTR_ID = ?
          AND ? BETWEEN a.ALST_INICIO_VIGENCIA AND COALESCE(a.ALST_FIM_VIGENCIA, ?)
        LIMIT 1
        """,
        (nbs, id_tributo, id_classificacao, d, d),
    ).fetchone()
    return Decimal(str(row[0])) if row else None


def _diferimento_domain(grupo: GrupoDiferimento | None) -> DiferimentoDomain | None:
    if grupo is None:
        return None
    return DiferimentoDomain(p_dif=grupo.percentual, v_dif=grupo.valor)


def _mapear_cbs(grupo: GrupoCbs | None) -> CBSDomain | None:
    if grupo is None:
        return None
    return CBSDomain(
        p_cbs=grupo.aliquota or ZERO,
        v_cbs=grupo.valor or ZERO,
        g_dif=_diferimento_domain(grupo.diferimento),
        g_red=_reducao_domain(grupo.reducao),
    )


def _mapear_ibs_uf(grupo: GrupoIbsUf | None) -> IBSUFDomain | None:
    if grupo is None:
        return None
    return IBSUFDomain(
        p_ibs_uf=grupo.aliquota or ZERO,
        v_ibs_uf=grupo.valor or ZERO,
        g_dif=_diferimento_domain(grupo.diferimento),
        g_red=_reducao_domain(grupo.reducao),
    )


def _mapear_ibs_mun(grupo: GrupoIbsMun | None) -> IBSMunDomain | None:
    if grupo is None:
        return None
    return IBSMunDomain(
        p_ibs_mun=grupo.aliquota or ZERO,
        v_ibs_mun=grupo.valor or ZERO,
        g_dif=_diferimento_domain(grupo.diferimento),
        g_red=_reducao_domain(grupo.reducao),
    )


def _mapear_compra_gov(grupo: CompraGovernamentalGrupo | None) -> TributacaoCompraGovernamentalDomain | None:
    if grupo is None:
        return None
    return TributacaoCompraGovernamentalDomain(
        p_aliq_cbs=grupo.aliquota_cbs,
        v_trib_cbs=grupo.tributo_cbs,
        p_aliq_ibs_uf=grupo.aliquota_ibs_uf,
        v_trib_ibs_uf=grupo.tributo_ibs_uf,
        p_aliq_ibs_mun=grupo.aliquota_ibs_mun,
        v_trib_ibs_mun=grupo.tributo_ibs_mun,
    )


def _reducao_domain(grupo: GrupoReducao | None) -> ReducaoAliquotaDomain | None:
    if grupo is None:
        return None
    return ReducaoAliquotaDomain(
        p_red_aliq=grupo.percentual_reducao,
        p_aliq_efet=grupo.aliquota_efetiva,
    )


def _regular_domain(grupo: TributacaoRegularGrupo | None) -> TributacaoRegularDomain | None:
    if grupo is None:
        return None
    return TributacaoRegularDomain(
        cst_reg=grupo.cst,
        c_class_trib_reg=grupo.c_class_trib,
        p_aliq_efet_reg_cbs=grupo.aliquota_efetiva_cbs or ZERO,
        v_trib_reg_cbs=grupo.tributo_cbs or ZERO,
        p_aliq_efet_reg_ibs_uf=grupo.aliquota_efetiva_ibs_uf or ZERO,
        v_trib_reg_ibs_uf=grupo.tributo_ibs_uf or ZERO,
        p_aliq_efet_reg_ibs_mun=grupo.aliquota_efetiva_ibs_mun or ZERO,
        v_trib_reg_ibs_mun=grupo.tributo_ibs_mun or ZERO,
    )


def _mapear_grupo_ibscbs(grupo: GrupoIbsCbs | None) -> GrupoIBSCBSDomain | None:
    if grupo is None:
        return None
    trib_reg = _regular_domain(grupo.tributacao_regular)
    return GrupoIBSCBSDomain(
        v_bc=grupo.base_calculo,
        g_ibs_uf=_mapear_ibs_uf(grupo.ibs_uf),
        g_ibs_mun=_mapear_ibs_mun(grupo.ibs_mun),
        v_ibs=grupo.valor_ibs,
        g_cbs=_mapear_cbs(grupo.cbs),
        g_trib_regular=trib_reg,
        g_trib_compra_gov=_mapear_compra_gov(grupo.compra_governamental),
    )


def _mapear_monofasia(mono: MonofasiaItem | None) -> MonofasiaDomain | None:
    if mono is None:
        return None
    padrao = None
    if mono.padrao is not None:
        p = mono.padrao
        padrao = MonofasiaPadraoDomain(
            q_bc_mono=p.quantidade,
            ad_rem_ibs=p.ad_rem_ibs,
            ad_rem_cbs=p.ad_rem_cbs,
            v_ibs_mono=p.valor_ibs,
            v_cbs_mono=p.valor_cbs,
        )
    reten = None
    if mono.retencao is not None:
        r = mono.retencao
        reten = MonofasiaRetencaoDomain(
            q_bc_mono_reten=r.quantidade,
            ad_rem_ibs_reten=r.ad_rem_ibs,
            v_ibs_mono_reten=r.valor_ibs,
            ad_rem_cbs_reten=r.ad_rem_cbs,
            v_cbs_mono_reten=r.valor_cbs,
        )
    retido = None
    if mono.retido is not None:
        r = mono.retido
        retido = MonofasiaRetidoAnteriormenteDomain(
            q_bc_mono_ret=r.quantidade,
            ad_rem_ibs_ret=r.ad_rem_ibs,
            v_ibs_mono_ret=r.valor_ibs,
            ad_rem_cbs_ret=r.ad_rem_cbs,
            v_cbs_mono_ret=r.valor_cbs,
        )
    difer = None
    if mono.diferimento is not None:
        d = mono.diferimento
        difer = MonofasiaDiferimentoDomain(
            p_dif_ibs=d.percentual_ibs,
            v_ibs_mono_dif=d.valor_ibs,
            p_dif_cbs=d.percentual_cbs,
            v_cbs_mono_dif=d.valor_cbs,
        )
    return MonofasiaDomain(
        g_mono_padrao=padrao,
        g_mono_reten=reten,
        g_mono_ret=retido,
        g_mono_dif=difer,
        v_tot_ibs_mono_item=mono.total_ibs,
        v_tot_cbs_mono_item=mono.total_cbs,
    )


def _tributos_item_para_domain(tributos: TributosItem) -> TributosDomain:
    is_dom = None
    if tributos.imposto_seletivo is not None:
        s = tributos.imposto_seletivo
        is_dom = ImpostoSeletivoDomain(
            CSTIS=s.cst,
            c_class_trib_is=s.c_class_trib,
            v_bcis=s.base_calculo,
            p_is=s.aliquota_ad_valorem,
            p_is_espec=s.aliquota_ad_rem,
            ad_rem_is=s.aliquota_ad_rem,
            u_trib=s.unidade,
            q_trib=s.quantidade,
            v_is=s.valor,
        )
    ibscbs_dom = None
    if tributos.ibs_cbs is not None:
        ib = tributos.ibs_cbs
        mono = _mapear_monofasia(ib.monofasia)
        grupo = None if mono is not None else _mapear_grupo_ibscbs(ib.grupo_ibs_cbs)
        ibscbs_dom = IBSCBSDomain(
            CST=ib.cst,
            c_class_trib=ib.c_class_trib,
            g_ibscbs=grupo,
            g_ibscbs_mono=mono,
        )
    return TributosDomain(IS=is_dom, IBSCBS=ibscbs_dom)


def _item_para_calculo(item: ItemOperacaoInput) -> ItemOperacao:
    nominais = None
    if item.aliquotas_nominais is not None:
        an = item.aliquotas_nominais
        nominais = AliquotasNominais(
            cbs=an.cbs,
            ibs_estadual=an.ibs_estadual,
            ibs_municipal=an.ibs_municipal,
        )
    is_item = None
    if item.imposto_seletivo is not None:
        ii = item.imposto_seletivo
        is_item = ImpostoSeletivoItem(
            cst=ii.cst or "",
            c_class_trib=ii.c_class_trib or "",
            base_calculo=ii.base_calculo,
            quantidade=ii.quantidade,
            unidade=ii.unidade,
            valor_informado=ii.imposto_informado,
        )
    trib_reg = None
    if item.tributacao_regular is not None:
        tr = item.tributacao_regular
        trib_reg = TributacaoRegularItem(tr.cst, tr.c_class_trib)
    return ItemOperacao(
        numero=item.numero or 1,
        cst=item.cst or "",
        c_class_trib=item.c_class_trib or "",
        base_calculo=item.base_calculo or ZERO,
        quantidade=item.quantidade,
        unidade=item.unidade,
        ncm=item.ncm,
        nbs=item.nbs,
        aliquotas_nominais=nominais,
        imposto_seletivo=is_item,
        tributacao_regular=trib_reg,
    )


def _montar_processamento(conexao: sqlite3.Connection, tipo_dfe_db_holder: list) -> ProcessamentoItemService:
    trat_classif = TratamentoClassificacaoService(conexao)
    sit = SituacaoTributariaService(conexao)
    ad_rem = AliquotaAdRemProdutoService(conexao)
    ad_val_prod = AliquotaAdValoremProdutoService(conexao)
    ad_val_serv = AliquotaAdValoremServicoService(conexao)
    ncm_repo = NcmRepositorioSqlite(conexao)
    nbs_repo = NbsRepositorioSqlite(conexao)
    validacao = montar_nomenclatura_sqlite(conexao)

    def buscar_cbs_ibs(codigo: str, data: date) -> ClassificacaoTributariaDTO:
        d = data.isoformat()
        row = conexao.execute(
            """
            SELECT ct.CLTR_ID, ct.CLTR_CD, st.SITR_CD
            FROM CLASSIFICACAO_TRIBUTARIA ct
            JOIN SITUACAO_TRIBUTARIA st ON ct.CLTR_SITR_ID = st.SITR_ID
            JOIN TRIBUTO_SITUACAO_TRIBUTARIA tst ON tst.TRST_SITR_ID = st.SITR_ID
            WHERE ct.CLTR_CD = ? AND tst.TRST_TBTO_ID = 2
              AND ? BETWEEN ct.CLTR_INICIO_VIGENCIA AND COALESCE(ct.CLTR_FIM_VIGENCIA, ?)
            LIMIT 1
            """,
            (codigo, d, d),
        ).fetchone()
        if row is None:
            from calculadora_rtc_regime_regular.nomenclatura import ClassificacaoTributariaNaoEncontradaException

            raise ClassificacaoTributariaNaoEncontradaException(codigo, "CBS e IBS", data)
        return ClassificacaoTributariaDTO(int(row[0]), str(row[1]), str(row[2]))

    def buscar_is(codigo: str, data: date) -> ClassificacaoTributariaDTO:
        row = conexao.execute(
            """
            SELECT ct.CLTR_ID, ct.CLTR_CD, st.SITR_CD
            FROM CLASSIFICACAO_TRIBUTARIA ct
            JOIN SITUACAO_TRIBUTARIA st ON ct.CLTR_SITR_ID = st.SITR_ID
            JOIN TRIBUTO_SITUACAO_TRIBUTARIA tst ON tst.TRST_SITR_ID = st.SITR_ID
            WHERE ct.CLTR_CD = ? AND tst.TRST_TBTO_ID = 1
              AND ? BETWEEN ct.CLTR_INICIO_VIGENCIA AND COALESCE(ct.CLTR_FIM_VIGENCIA, ?)
            LIMIT 1
            """,
            (codigo, data.isoformat(), data.isoformat()),
        ).fetchone()
        if row is None:
            from calculadora_rtc_regime_regular.nomenclatura import ClassificacaoTributariaNaoEncontradaException

            raise ClassificacaoTributariaNaoEncontradaException(codigo, "Imposto Seletivo", data)
        return ClassificacaoTributariaDTO(int(row[0]), str(row[1]), str(row[2]))

    def buscar_tratamento(id_cltr: int, data: date) -> TratamentoClassificacaoDTO:
        return trat_classif.buscar_tratamento_classificacao(id_cltr, data)

    def validar_vinculo(
        tipo_dfe: TipoDfeItem, id_cltr: int, codigo: str, data: date, tributos: str
    ) -> None:
        tipo_db = tipo_dfe_db_holder[0] if tipo_dfe_db_holder else None
        if tipo_db is None:
            return
        d = data.isoformat()
        vinculado = conexao.execute(
            """
            SELECT EXISTS (
                SELECT 1 FROM TIPO_DFE_CLASSIFICACAO tdcl
                WHERE tdcl.TDCL_CLTR_ID = ? AND tdcl.TDCL_TPDF_ID = ?
                  AND tdcl.TDCL_INICIO_VIGENCIA <= ?
                  AND (tdcl.TDCL_FIM_VIGENCIA IS NULL OR tdcl.TDCL_FIM_VIGENCIA >= ?)
            )
            """,
            (id_cltr, tipo_db.id, d, d),
        ).fetchone()
        if not vinculado or not vinculado[0]:
            raise ClassificacaoTributariaNaoVinculadaTipoDfeException(codigo, tipo_dfe.tipo, tributos)

    def validar_nomenclatura(
        sigla, id_cltr, codigo, ncm, nbs, data, tributos, modo  # noqa: ANN001
    ) -> None:
        validacao.validar(sigla, id_cltr, codigo, ncm, nbs, data, tributos, modo)

    def validar_ncm(ncm, id_cltr, codigo, data, tributos) -> None:  # noqa: ANN001
        NcmAplicavelService(NcmAplicavelRepositorioSqlite(conexao)).validar_ncm_aplicavel(
            ncm, id_cltr, codigo, data, tributos
        )

    def validar_nbs(nbs, id_cltr, codigo, data, tributos) -> None:  # noqa: ANN001
        NbsAplicavelService(NbsAplicavelRepositorioSqlite(conexao)).validar_nbs_aplicavel(
            nbs, id_cltr, codigo, data, tributos
        )

    def consultar_situacao(cst: str, id_tributo: int, data: date) -> SituacaoTributariaItem | None:
        st = sit.consultar_situacao_tributaria_por_codigo(cst, id_tributo, data)
        if st is None:
            return None
        return SituacaoTributariaItem(in_grupo_ibs_cbs=st.in_grupo_ibs_cbs)

    return ProcessamentoItemService(
        situacao_tributaria=sit,
        buscar_classificacao_cbs_ibs=buscar_cbs_ibs,
        buscar_classificacao_imposto_seletivo=buscar_is,
        buscar_tratamento_classificacao=buscar_tratamento,
        validar_vinculo_tipo_dfe=validar_vinculo,
        validar_nomenclatura=validar_nomenclatura,
        validar_ncm_aplicavel=validar_ncm,
        validar_nbs_aplicavel=validar_nbs,
        validar_cst=sit.validar_cst,
        existe_ncm=NcmService(ncm_repo).existe_ncm,
        existe_nbs=NbsService(nbs_repo).existe_nbs,
        consultar_situacao_tributaria=consultar_situacao,
        existe_ncm_ad_valorem=lambda ncm, data: ad_val_prod.existe_ncm_ad_valorem(
            ncm, TributoEnum.IS, data
        ),
        buscar_aliquota_ad_rem_produto=ad_rem.buscar_aliquota_ad_rem,
        existe_nbs_ad_valorem=lambda nbs, data: ad_val_serv.existe_nbs_ad_valorem(
            nbs, TributoEnum.IS, data
        ),
        buscar_aliquota_ad_valorem_produto=ad_val_prod.buscar_aliquota_ad_valorem,
        buscar_aliquota_ad_valorem_servico=lambda nbs, trib, data: ad_val_serv.buscar_aliquota_ad_valorem(
            nbs, trib, None, data
        ),
    )


class CalculadoraService:
    """Orquestra validação de operação, processamento de itens e montagem do ROC."""

    def __init__(
        self,
        conexao: sqlite3.Connection | None = None,
        *,
        calculo_ibs_habilitado: bool = False,
    ) -> None:
        self._conexao = conexao
        self._calculo_ibs_habilitado = calculo_ibs_habilitado
        self._uf = UfService(conexao)
        self._municipio = MunicipioService(conexao)
        self._tipo_dfe = TipoDfeService(conexao)
        self._redutor = RedutorCompraGovernamentalService(conexao)
        self._transferencia = TransferenciaCBSService(conexao)
        self._referencia = AliquotaReferenciaService(conexao)
        self._percentual_reducao = PercentualReducaoService(conexao)
        self._tratamento_tributario = TratamentoTributarioService(conexao)

    def _abrir(self) -> sqlite3.Connection:
        return self._conexao or conectar()

    def calcular_tributos(self, operacao: OperacaoCalculadoraInput) -> ROCDomain:
        data = operacao.fato_gerador_aplicavel()

        if not operacao.uf:
            operacao.uf = self._municipio.buscar_uf_por_municipio(operacao.municipio or 0)
        self._uf.validar_uf(operacao.uf or "")
        self._municipio.validar_municipio(operacao.municipio or 0, operacao.uf or "")

        tipo_dfe_db = self._tipo_dfe.buscar_por_tipo(operacao.tp_doc, data)
        tipo_dfe_item = None
        if tipo_dfe_db is not None:
            tipo_dfe_item = TipoDfeItem(tipo_dfe_db.tipo, tipo_dfe_db.sigla, tipo_dfe_db.permite_ncm_zero)

        op_proc = OperacaoInput(
            id=operacao.id,
            versao=operacao.versao,
            tp_doc=operacao.tp_doc,
            municipio=operacao.municipio,
            uf=operacao.uf,
            data_fato_gerador=data,
        )

        codigo_uf = self._uf.buscar(operacao.uf or "")
        p_redutor = self._redutor.buscar_valor_redutor(operacao.tp_ente_gov(), data)
        tp_ente = operacao.tp_ente_gov().name if operacao.tp_ente_gov() is not None else None

        detalhes: list[ObjetoDomain] = []
        with self._abrir() as conexao:
            tipo_holder: list = [tipo_dfe_db]
            processamento = _montar_processamento(conexao, tipo_holder)

            def buscar_padrao(id_tributo: int, uf: int | None, municipio: int | None, d: date) -> AliquotaResultado:
                resultado = buscar_aliquota_sqlite(id_tributo, uf, municipio, d, conexao)
                if resultado is None:
                    from calculadora_rtc_regime_regular.aliquota_resultado import AliquotaReferenciaNaoEncontrada

                    raise AliquotaReferenciaNaoEncontrada()
                return resultado

            def buscar_referencia(id_tributo: int, d: date) -> Decimal:
                return self._referencia.buscar(id_tributo, d)

            def buscar_setorial(
                nbs: str | None, id_tributo: int, id_classificacao: int, d: date
            ) -> Decimal | None:
                return _buscar_aliquota_setorial(conexao, nbs, id_tributo, id_classificacao, d)

            def buscar_fixa(id_tributo: int, id_classificacao: int, d: date) -> Decimal | None:
                return _buscar_aliquota_fixa(conexao, id_tributo, id_classificacao, d)

            def buscar_pct_transferencia(d: date) -> Decimal:
                return self._transferencia.get_percentual_transferencia(d)

            itens_ordenados = sorted(operacao.itens, key=lambda i: (i.numero is None, i.numero or 0))

            for item_in in itens_ordenados:
                item_proc = ItemOperacaoInput(
                    numero=item_in.numero,
                    ncm=item_in.ncm,
                    nbs=item_in.nbs,
                    cst=item_in.cst,
                    c_class_trib=item_in.c_class_trib,
                    base_calculo=item_in.base_calculo,
                    quantidade=item_in.quantidade,
                    unidade=item_in.unidade,
                    imposto_seletivo=item_in.imposto_seletivo,
                    tributacao_regular=item_in.tributacao_regular,
                    g_componentes_bc=item_in.g_componentes_bc,
                    aliquotas_nominais=item_in.aliquotas_nominais,
                )
                modelo = processamento.processar_item(op_proc, item_proc, data, tipo_dfe_item)
                try:
                    tributos_item = self._calcular_item(
                        conexao,
                        op_proc,
                        item_proc,
                        data,
                        modelo,
                        codigo_uf,
                        tp_ente,
                        p_redutor,
                        sit=SituacaoTributariaService(conexao),
                        buscar_padrao=buscar_padrao,
                        buscar_referencia=buscar_referencia,
                        buscar_setorial=buscar_setorial,
                        buscar_fixa=buscar_fixa,
                        buscar_percentual_transferencia=buscar_pct_transferencia,
                    )
                except AjusteNaoImplementado as ex:
                    from calculadora_rtc_regime_regular.observabilidade import ErroFaltaImplementacaoException

                    codigo = str(ex.args[0]) if ex.args else ""
                    raise ErroFaltaImplementacaoException(codigo) from ex
                trib_domain = _tributos_item_para_domain(tributos_item)
                self._anexar_memorias(conexao, modelo, item_proc, data, trib_domain)
                simulado = item_proc.aliquotas_nominais is not None
                detalhes.append(
                    ObjetoDomain(n_obj=item_proc.numero, trib_calc=trib_domain, calculo_simulado=simulado)
                )

        return ROCDomain(
            oper=self._operacao_output(operacao, data),
            objetos=detalhes,
            total=ValoresTotaisDomain.create(detalhes),
        )

    def _anexar_memorias(
        self,
        conexao: sqlite3.Connection,
        modelo,
        item: ItemOperacaoInput,
        data: date,
        tributos: TributosDomain,
    ) -> None:
        memoria = MemoriaCalculoService(
            fundamentacao_classificacao_service=FundamentacaoClassificacaoService(conexao),
            tratamento_service=TratamentoTributarioService(conexao),
        )
        if tributos.IS is not None and modelo.tratamento_classificacao_imposto_seletivo is not None:
            seletivo = _tratamento_consulta(modelo.tratamento_classificacao_imposto_seletivo)
            if seletivo is not None and item.imposto_seletivo is not None:
                memoria.gerar_memoria_calculo_imposto_seletivo(
                    seletivo,
                    tributos.IS,
                    item.imposto_seletivo.quantidade,
                    item.imposto_seletivo.unidade,
                    data,
                )
        if tributos.IBSCBS is None:
            return
        origem = (
            modelo.tratamento_classificacao_cbs_ibs_desoneracao
            if modelo.tem_desoneracao
            else modelo.tratamento_classificacao_cbs_ibs
        )
        tratamento = _tratamento_consulta(origem)
        if tratamento is None:
            return
        nominais = item.aliquotas_nominais
        nbs = bool(item.nbs and item.nbs.strip())
        memoria.anexar_memoria_ibscbs(
            tratamento,
            tributos.IBSCBS,
            item.base_calculo,
            item.quantidade,
            item.unidade,
            data,
            calcular_ibs_estadual=self._calculo_ibs_habilitado
            or nbs
            or (nominais is not None and nominais.ibs_estadual is not None),
            calcular_ibs_municipal=self._calculo_ibs_habilitado
            or nbs
            or (nominais is not None and nominais.ibs_municipal is not None),
        )

    def _operacao_output(
        self, operacao: OperacaoCalculadoraInput, data: date
    ) -> OperacaoConsumoDomain | None:
        entrada = operacao.g_compra_gov
        if entrada is None:
            return None
        compra = CompraGovernamentalDomain(
            tp_ente_gov=entrada.tp_ente_gov,
            p_redutor=self._redutor.buscar_valor_redutor(entrada.tp_ente_gov, data),
            tp_oper_gov=entrada.tp_oper_gov,
        )
        return OperacaoConsumoDomain(g_compra_gov=compra)

    def _calcular_item(
        self,
        conexao: sqlite3.Connection,
        operacao: OperacaoInput,
        item: ItemOperacaoInput,
        data: date,
        modelo,
        codigo_uf: int,
        tp_ente: str | None,
        p_redutor: Decimal,
        *,
        sit: SituacaoTributariaService,
        **kwargs: object,
    ) -> TributosItem:
        dto = modelo.tratamento_classificacao_cbs_ibs
        assert dto is not None
        classificacao = _classificacao_calculo(
            conexao,
            dto.id_classificacao_tributaria,
            item.c_class_trib or "",
            item.cst or "",
            data,
            sit,
        )
        ent = self._tratamento_tributario.buscar(dto.id_tratamento_tributario)
        tratamento = _tratamento_de_entidade(ent)
        def buscar_percentual_reducao(id_tributo: int):
            if not ent.in_possui_percentual_reducao:
                return None
            try:
                return self._percentual_reducao.buscar(
                    dto.id_classificacao_tributaria, id_tributo, data
                )
            except Exception:
                return None

        tratamento_imposto_seletivo = None
        aliquota_imposto_seletivo = None
        if (
            modelo.tratamento_classificacao_imposto_seletivo is not None
            and modelo.aliquota_imposto_seletivo is not None
        ):
            ent_is = self._tratamento_tributario.buscar(
                modelo.tratamento_classificacao_imposto_seletivo.id_tratamento_tributario
            )
            tratamento_imposto_seletivo = _tratamento_de_entidade(ent_is)
            ali_is = modelo.aliquota_imposto_seletivo
            aliquota_imposto_seletivo = AliquotaSeletivo(
                ali_is.aliquota_ad_valorem,
                ali_is.aliquota_ad_rem,
            )

        tratamento_item = TratamentoClassificacaoItem(
            tratamento_cbs_ibs=tratamento,
            classificacao_cbs_ibs=classificacao,
            tratamento_imposto_seletivo=tratamento_imposto_seletivo,
            aliquota_imposto_seletivo=aliquota_imposto_seletivo,
            tem_desoneracao=modelo.tem_desoneracao,
        )

        op_calculo = OperacaoCalculo(
            data=data,
            codigo_uf=codigo_uf,
            codigo_municipio=operacao.municipio,
            tp_ente_gov=tp_ente,
            p_redutor=p_redutor,
            item=_item_para_calculo(item),
            tratamento=tratamento_item,
        )
        kwargs_extra = dict(kwargs)
        kwargs_extra["buscar_percentual_reducao"] = buscar_percentual_reducao
        return calcular_tributos(
            op_calculo,
            calculo_ibs_habilitado=self._calculo_ibs_habilitado,
            **kwargs_extra,  # type: ignore[arg-type]
        )