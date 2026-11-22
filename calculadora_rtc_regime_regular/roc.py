"""Numeric output domain (ROC) of the official Receita calculator.

Pin ``f1eebd7ce3157423b1a6aaca7dc1d6c3395452c4``, package
``br.gov.serpro.rtc.api.model.roc`` (+ ``reduce`` accumulators).
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date
from decimal import Decimal
from enum import Enum
from functools import total_ordering
from typing import Any

from calculadora_rtc_regime_regular.arredondamento import (
    arredondar_aliquota_publicada,
    arredondar_valor_fiscal,
    multiplicar,
    percentual_para_fracao,
)

ZERO = Decimal(0)


def _nn(value: Decimal | None) -> Decimal:
    return value if value is not None else ZERO


# --- Minimal calculation output stubs (monofasia ``create`` only) ---


@dataclass
class GrupoEtapaMonofasiaOutput:
    quantidade: Decimal | None = None
    aliquota_ad_rem: Decimal | None = None
    valor: Decimal | None = None

    @staticmethod
    def merge(
        g1: GrupoEtapaMonofasiaOutput | None,
        g2: GrupoEtapaMonofasiaOutput | None,
    ) -> GrupoEtapaMonofasiaOutput | None:
        if g1 is None:
            return g2
        if g2 is None:
            return g1
        quantidade = g1.quantidade if g1.quantidade is not None else g2.quantidade
        if quantidade is None:
            raise ValueError("quantidade obrigatória no merge de monofasia")
        aliquota_ad_rem = g1.aliquota_ad_rem if g1.aliquota_ad_rem is not None else g2.aliquota_ad_rem
        if aliquota_ad_rem is None:
            raise ValueError("aliquota_ad_rem obrigatória no merge de monofasia")
        valor = _nn(g1.valor) + _nn(g2.valor)
        return GrupoEtapaMonofasiaOutput(
            quantidade=quantidade,
            aliquota_ad_rem=aliquota_ad_rem,
            valor=valor,
        )


@dataclass
class GrupoDiferimentoMonofasiaOutput:
    valor_diferimento: Decimal | None = None
    percentual_diferimento: Decimal | None = None

    @staticmethod
    def merge(
        g1: GrupoDiferimentoMonofasiaOutput | None,
        g2: GrupoDiferimentoMonofasiaOutput | None,
    ) -> GrupoDiferimentoMonofasiaOutput | None:
        if g1 is None:
            return g2
        if g2 is None:
            return g1
        valor_diferimento = _nn(g1.valor_diferimento) + _nn(g2.valor_diferimento)
        percentual_diferimento = (
            g1.percentual_diferimento
            if g1.percentual_diferimento is not None
            else g2.percentual_diferimento
        )
        if percentual_diferimento is None:
            raise ValueError("percentual_diferimento obrigatório no merge de diferimento")
        return GrupoDiferimentoMonofasiaOutput(
            percentual_diferimento=percentual_diferimento,
            valor_diferimento=valor_diferimento,
        )


@dataclass
class GrupoMonofasiaOutput:
    tributo_monofasico: GrupoEtapaMonofasiaOutput | None = None
    tributo_sujeito_retencao: GrupoEtapaMonofasiaOutput | None = None
    tributo_retido: GrupoEtapaMonofasiaOutput | None = None
    tributo_diferido: GrupoDiferimentoMonofasiaOutput | None = None


@dataclass
class CbsIbsOutput:
    grupo_monofasia: GrupoMonofasiaOutput | None = None


class TipoEnteGovernamental(Enum):
    UNIAO = 1
    ESTADO = 2
    DISTRITO_FEDERAL = 3
    MUNICIPIO = 4
    CONSORCIO_PUBLICO = 5
    COMITE_GESTOR_IBS = 6

    def tipo_ente_equivalente(self) -> TipoEnteGovernamental:
        if self in (TipoEnteGovernamental.DISTRITO_FEDERAL,):
            return TipoEnteGovernamental.ESTADO
        if self in (
            TipoEnteGovernamental.CONSORCIO_PUBLICO,
            TipoEnteGovernamental.COMITE_GESTOR_IBS,
        ):
            return TipoEnteGovernamental.MUNICIPIO
        return self

    def is_uniao(self) -> bool:
        return self.tipo_ente_equivalente() is TipoEnteGovernamental.UNIAO

    def is_estado(self) -> bool:
        return self.tipo_ente_equivalente() is TipoEnteGovernamental.ESTADO

    def is_municipio(self) -> bool:
        return self.tipo_ente_equivalente() is TipoEnteGovernamental.MUNICIPIO


@dataclass
class DevolucaoTributosDomain:
    p_dev_trib: Decimal = ZERO
    v_dev_trib: Decimal = ZERO


@dataclass
class DiferimentoDomain:
    p_dif: Decimal = ZERO
    v_dif: Decimal = ZERO


@dataclass
class ReducaoAliquotaDomain:
    p_red_aliq: Decimal | None = None
    p_aliq_efet: Decimal | None = None


@dataclass
class TributacaoRegularDomain:
    cst_reg: str | None = None
    c_class_trib_reg: str | None = None
    p_aliq_efet_reg_ibs_uf: Decimal = ZERO
    v_trib_reg_ibs_uf: Decimal = ZERO
    p_aliq_efet_reg_ibs_mun: Decimal = ZERO
    v_trib_reg_ibs_mun: Decimal = ZERO
    p_aliq_efet_reg_cbs: Decimal = ZERO
    v_trib_reg_cbs: Decimal = ZERO


@dataclass
class TransferenciaCreditoDomain:
    v_ibs: Decimal = ZERO
    v_cbs: Decimal = ZERO


@dataclass
class AjusteCompetenciaDomain:
    compet_apur: str | None = None
    v_ibs: Decimal | None = None
    v_cbs: Decimal | None = None


@dataclass
class EstornoCreditoDomain:
    v_ibs_est_cred: Decimal | None = None
    v_cbs_est_cred: Decimal | None = None


@dataclass
class IBSCBSCreditoPresumidoDomain:
    p_cred_pres: Decimal | None = None
    v_cred_pres: Decimal | None = None
    v_cred_pres_cond_sus: Decimal | None = None


@dataclass
class CreditoPresumidoOperacaoDomain:
    v_bc_cred_pres: Decimal | None = None
    c_cred_pres: int | None = None
    g_ibs_cred_pres: IBSCBSCreditoPresumidoDomain | None = None
    g_cbs_cred_pres: IBSCBSCreditoPresumidoDomain | None = None

    def possui_cred_pres_cbs(self) -> bool:
        return self.g_cbs_cred_pres is not None

    def possui_cred_pres_ibs(self) -> bool:
        return self.g_ibs_cred_pres is not None and self.g_ibs_cred_pres.v_cred_pres is not None

    def get_v_cred_pres_ibs(self) -> Decimal:
        return self.g_ibs_cred_pres.v_cred_pres if self.possui_cred_pres_ibs() else ZERO

    def possui_cred_pres_cond_sus_ibs(self) -> bool:
        return (
            self.g_ibs_cred_pres is not None
            and self.g_ibs_cred_pres.v_cred_pres_cond_sus is not None
        )

    def get_v_cred_pres_cond_sus_ibs(self) -> Decimal:
        return (
            self.g_ibs_cred_pres.v_cred_pres_cond_sus
            if self.possui_cred_pres_cond_sus_ibs()
            else ZERO
        )


@dataclass
class CreditoPresumidoIBSZFMDomain:
    pass


@dataclass
class MemoriaCalculoDomain:
    cbs: str | None = None
    ibs_uf: str | None = None
    ibs_mun: str | None = None


@dataclass
class CBSDomain:
    p_cbs: Decimal = ZERO
    g_dif: DiferimentoDomain | None = None
    g_dev_trib: DevolucaoTributosDomain | None = None
    g_red: ReducaoAliquotaDomain | None = None
    v_cbs: Decimal = ZERO

    def get_v_dif(self) -> Decimal:
        return self.g_dif.v_dif if self.g_dif is not None else ZERO

    def get_v_dev_trib(self) -> Decimal:
        return self.g_dev_trib.v_dev_trib if self.g_dev_trib is not None else ZERO


@dataclass
class IBSUFDomain:
    p_ibs_uf: Decimal = ZERO
    g_dif: DiferimentoDomain | None = None
    g_dev_trib: DevolucaoTributosDomain | None = None
    g_red: ReducaoAliquotaDomain | None = None
    v_ibs_uf: Decimal = ZERO

    def get_v_dif(self) -> Decimal:
        return self.g_dif.v_dif if self.g_dif is not None else ZERO

    def get_v_dev_trib(self) -> Decimal:
        return self.g_dev_trib.v_dev_trib if self.g_dev_trib is not None else ZERO


@dataclass
class IBSMunDomain:
    p_ibs_mun: Decimal = ZERO
    g_dif: DiferimentoDomain | None = None
    g_dev_trib: DevolucaoTributosDomain | None = None
    g_red: ReducaoAliquotaDomain | None = None
    v_ibs_mun: Decimal = ZERO

    def get_v_dif(self) -> Decimal:
        return self.g_dif.v_dif if self.g_dif is not None else ZERO

    def get_v_dev_trib(self) -> Decimal:
        return self.g_dev_trib.v_dev_trib if self.g_dev_trib is not None else ZERO


@dataclass
class TributacaoCompraGovernamentalDomain:
    p_aliq_ibs_uf: Decimal = ZERO
    v_trib_ibs_uf: Decimal = ZERO
    p_aliq_ibs_mun: Decimal = ZERO
    v_trib_ibs_mun: Decimal = ZERO
    p_aliq_cbs: Decimal = ZERO
    v_trib_cbs: Decimal = ZERO

    def zerar_valores(self) -> None:
        self.p_aliq_ibs_uf = ZERO
        self.v_trib_ibs_uf = ZERO
        self.p_aliq_ibs_mun = ZERO
        self.v_trib_ibs_mun = ZERO
        self.p_aliq_cbs = ZERO
        self.v_trib_cbs = ZERO

    def get_valores_efetivos(
        self,
        tp_ente_gov: TipoEnteGovernamental | None,
        p_transferencia_cbs: Decimal | None,
        data_fato_gerador: date | None,
        v_bc: Decimal,
    ) -> TributacaoCompraGovernamentalDomain | None:
        if tp_ente_gov is None:
            return None
        if data_fato_gerador is None:
            raise TypeError("Data do fato gerador obrigatória")
        if p_transferencia_cbs is None:
            raise TypeError("Percentual de transferência da CBS obrigatória")
        if data_fato_gerador < date(2027, 1, 1):
            return self
        soma_aliquotas = self.p_aliq_cbs + self.p_aliq_ibs_uf + self.p_aliq_ibs_mun
        if tp_ente_gov.is_uniao():
            return _com_aliquotas(soma_aliquotas, ZERO, ZERO, v_bc)
        p_aliq_cbs_final = arredondar_aliquota_publicada(
            self.p_aliq_cbs
            - multiplicar(self.p_aliq_cbs, percentual_para_fracao(p_transferencia_cbs))
        )
        assert p_aliq_cbs_final is not None
        p_aliq_recebedor = soma_aliquotas - p_aliq_cbs_final
        if tp_ente_gov.is_estado():
            return _com_aliquotas(p_aliq_cbs_final, p_aliq_recebedor, ZERO, v_bc)
        if tp_ente_gov.is_municipio():
            return _com_aliquotas(p_aliq_cbs_final, ZERO, p_aliq_recebedor, v_bc)
        return _com_aliquotas(p_aliq_cbs_final, ZERO, ZERO, v_bc)


def _valor_pela_aliquota_publicada(v_bc: Decimal, aliquota: Decimal) -> Decimal:
    produto = multiplicar(v_bc, percentual_para_fracao(aliquota))
    assert produto is not None
    return arredondar_valor_fiscal(produto) or ZERO


def _com_aliquotas(
    p_aliq_cbs: Decimal,
    p_aliq_ibs_uf: Decimal,
    p_aliq_ibs_mun: Decimal,
    v_bc: Decimal,
) -> TributacaoCompraGovernamentalDomain:
    return TributacaoCompraGovernamentalDomain(
        p_aliq_cbs=p_aliq_cbs,
        v_trib_cbs=_valor_pela_aliquota_publicada(v_bc, p_aliq_cbs),
        p_aliq_ibs_uf=p_aliq_ibs_uf,
        v_trib_ibs_uf=_valor_pela_aliquota_publicada(v_bc, p_aliq_ibs_uf),
        p_aliq_ibs_mun=p_aliq_ibs_mun,
        v_trib_ibs_mun=_valor_pela_aliquota_publicada(v_bc, p_aliq_ibs_mun),
    )


@dataclass
class GrupoIBSCBSDomain:
    v_bc: Decimal | None = None
    g_ibs_uf: IBSUFDomain | None = None
    g_ibs_mun: IBSMunDomain | None = None
    v_ibs: Decimal | None = None
    g_cbs: CBSDomain | None = None
    g_trib_regular: TributacaoRegularDomain | None = None
    g_trib_compra_gov: TributacaoCompraGovernamentalDomain | None = None

    def possui_base_calculo_ibscbs(self) -> bool:
        return self.v_bc is not None

    def get_valor_base_calculo_ibscbs(self) -> Decimal:
        return self.v_bc if self.possui_base_calculo_ibscbs() else ZERO

    def possui_cbs(self) -> bool:
        return self.g_cbs is not None

    def possui_ibs_uf(self) -> bool:
        return self.g_ibs_uf is not None

    def possui_ibs_mun(self) -> bool:
        return self.g_ibs_mun is not None

    def possui_tributacao_regular(self) -> bool:
        return self.g_trib_regular is not None

    def get_tributacao_regular(self) -> TributacaoRegularDomain | None:
        return self.g_trib_regular


@dataclass
class MonofasiaPadraoDomain:
    q_bc_mono: Decimal = ZERO
    ad_rem_ibs: Decimal = ZERO
    ad_rem_cbs: Decimal = ZERO
    v_ibs_mono: Decimal = ZERO
    v_cbs_mono: Decimal = ZERO

    @staticmethod
    def create(
        cbs: CbsIbsOutput | None,
        ibs_estadual: CbsIbsOutput | None,
        ibs_municipal: CbsIbsOutput | None,
    ) -> MonofasiaPadraoDomain | None:
        partial = _padrao_cbs(cbs)
        merged = _padrao_ibs(ibs_estadual, ibs_municipal, partial)
        return merged.build() if merged is not None else None


@dataclass
class MonofasiaRetencaoDomain:
    q_bc_mono_reten: Decimal = ZERO
    ad_rem_ibs_reten: Decimal = ZERO
    v_ibs_mono_reten: Decimal = ZERO
    ad_rem_cbs_reten: Decimal = ZERO
    v_cbs_mono_reten: Decimal = ZERO

    @staticmethod
    def create(
        cbs: CbsIbsOutput | None,
        ibs_estadual: CbsIbsOutput | None,
        ibs_municipal: CbsIbsOutput | None,
    ) -> MonofasiaRetencaoDomain | None:
        partial = _retencao_cbs(cbs)
        merged = _retencao_ibs(ibs_estadual, ibs_municipal, partial)
        return merged.build() if merged is not None else None


@dataclass
class MonofasiaRetidoAnteriormenteDomain:
    q_bc_mono_ret: Decimal = ZERO
    ad_rem_ibs_ret: Decimal = ZERO
    v_ibs_mono_ret: Decimal = ZERO
    ad_rem_cbs_ret: Decimal = ZERO
    v_cbs_mono_ret: Decimal = ZERO

    @staticmethod
    def create(
        cbs: CbsIbsOutput | None,
        ibs_estadual: CbsIbsOutput | None,
        ibs_municipal: CbsIbsOutput | None,
    ) -> MonofasiaRetidoAnteriormenteDomain | None:
        partial = _retido_cbs(cbs)
        merged = _retido_ibs(ibs_estadual, ibs_municipal, partial)
        return merged.build() if merged is not None else None


@dataclass
class MonofasiaDiferimentoDomain:
    p_dif_ibs: Decimal = ZERO
    v_ibs_mono_dif: Decimal = ZERO
    p_dif_cbs: Decimal = ZERO
    v_cbs_mono_dif: Decimal = ZERO

    @staticmethod
    def create(
        cbs: CbsIbsOutput | None,
        ibs_estadual: CbsIbsOutput | None,
        ibs_municipal: CbsIbsOutput | None,
    ) -> MonofasiaDiferimentoDomain | None:
        partial = _diferimento_cbs(cbs)
        merged = _diferimento_ibs(ibs_estadual, ibs_municipal, partial)
        return merged.build() if merged is not None else None


@dataclass
class MonofasiaDomain:
    g_mono_padrao: MonofasiaPadraoDomain | None = None
    g_mono_reten: MonofasiaRetencaoDomain | None = None
    g_mono_ret: MonofasiaRetidoAnteriormenteDomain | None = None
    g_mono_dif: MonofasiaDiferimentoDomain | None = None
    v_tot_ibs_mono_item: Decimal = ZERO
    v_tot_cbs_mono_item: Decimal = ZERO

    def get_v_ibs_mono(self) -> Decimal:
        return self.g_mono_padrao.v_ibs_mono if self.g_mono_padrao is not None else ZERO

    def get_v_cbs_mono(self) -> Decimal:
        return self.g_mono_padrao.v_cbs_mono if self.g_mono_padrao is not None else ZERO

    def get_v_ibs_mono_reten(self) -> Decimal:
        return self.g_mono_reten.v_ibs_mono_reten if self.g_mono_reten is not None else ZERO

    def get_v_cbs_mono_reten(self) -> Decimal:
        return self.g_mono_reten.v_cbs_mono_reten if self.g_mono_reten is not None else ZERO

    def get_v_ibs_mono_ret(self) -> Decimal:
        return self.g_mono_ret.v_ibs_mono_ret if self.g_mono_ret is not None else ZERO

    def get_v_cbs_mono_ret(self) -> Decimal:
        return self.g_mono_ret.v_cbs_mono_ret if self.g_mono_ret is not None else ZERO

    def get_v_ibs_mono_dif(self) -> Decimal:
        return self.g_mono_dif.v_ibs_mono_dif if self.g_mono_dif is not None else ZERO

    def get_v_cbs_mono_dif(self) -> Decimal:
        return self.g_mono_dif.v_cbs_mono_dif if self.g_mono_dif is not None else ZERO

    def get_v_tot_ibs_mono_item(self) -> Decimal:
        return _nn(self.v_tot_ibs_mono_item)

    def get_v_tot_cbs_mono_item(self) -> Decimal:
        return _nn(self.v_tot_cbs_mono_item)


class _MonoBuilder:
    def __init__(self, cls: type[Any]) -> None:
        self._cls = cls
        self._kwargs: dict[str, Any] = {}

    def __getattr__(self, name: str) -> _MonoBuilder:
        return self

    def build(self) -> Any:
        return self._cls(**self._kwargs)

    def set(self, **kwargs: Any) -> _MonoBuilder:
        self._kwargs.update(kwargs)
        return self


def _etapa_monofasico(o: CbsIbsOutput | None) -> GrupoEtapaMonofasiaOutput | None:
    if o is None or o.grupo_monofasia is None:
        return None
    return o.grupo_monofasia.tributo_monofasico


def _etapa_retencao(o: CbsIbsOutput | None) -> GrupoEtapaMonofasiaOutput | None:
    if o is None or o.grupo_monofasia is None:
        return None
    return o.grupo_monofasia.tributo_sujeito_retencao


def _etapa_retido(o: CbsIbsOutput | None) -> GrupoEtapaMonofasiaOutput | None:
    if o is None or o.grupo_monofasia is None:
        return None
    return o.grupo_monofasia.tributo_retido


def _etapa_diferido(o: CbsIbsOutput | None) -> GrupoDiferimentoMonofasiaOutput | None:
    if o is None or o.grupo_monofasia is None:
        return None
    return o.grupo_monofasia.tributo_diferido


def _padrao_cbs(cbs: CbsIbsOutput | None) -> _MonoBuilder | None:
    t = _etapa_monofasico(cbs)
    if t is None:
        return None
    b = _MonoBuilder(MonofasiaPadraoDomain)
    return b.set(
        q_bc_mono=t.quantidade,
        ad_rem_cbs=t.aliquota_ad_rem,
        v_cbs_mono=t.valor,
    )


def _padrao_ibs(
    ibs_uf: CbsIbsOutput | None,
    _ibs_mun: CbsIbsOutput | None,
    b: _MonoBuilder | None,
) -> _MonoBuilder | None:
    mono_uf = _etapa_monofasico(ibs_uf)
    if mono_uf is None:
        return b
    merged = GrupoEtapaMonofasiaOutput.merge(mono_uf, None)
    if merged is None:
        return b
    if b is None:
        b = _MonoBuilder(MonofasiaPadraoDomain)
    return b.set(
        q_bc_mono=merged.quantidade,
        ad_rem_ibs=merged.aliquota_ad_rem,
        v_ibs_mono=merged.valor,
    )


def _retencao_cbs(cbs: CbsIbsOutput | None) -> _MonoBuilder | None:
    t = _etapa_retencao(cbs)
    if t is None:
        return None
    b = _MonoBuilder(MonofasiaRetencaoDomain)
    return b.set(
        q_bc_mono_reten=t.quantidade,
        ad_rem_cbs_reten=t.aliquota_ad_rem,
        v_cbs_mono_reten=t.valor,
    )


def _retencao_ibs(
    ibs_uf: CbsIbsOutput | None,
    _ibs_mun: CbsIbsOutput | None,
    b: _MonoBuilder | None,
) -> _MonoBuilder | None:
    mono_uf = _etapa_retencao(ibs_uf)
    if mono_uf is None:
        return b
    merged = GrupoEtapaMonofasiaOutput.merge(mono_uf, None)
    if merged is None:
        return b
    if b is None:
        b = _MonoBuilder(MonofasiaRetencaoDomain)
    return b.set(
        q_bc_mono_reten=merged.quantidade,
        ad_rem_ibs_reten=merged.aliquota_ad_rem,
        v_ibs_mono_reten=merged.valor,
    )


def _retido_cbs(cbs: CbsIbsOutput | None) -> _MonoBuilder | None:
    t = _etapa_retido(cbs)
    if t is None:
        return None
    b = _MonoBuilder(MonofasiaRetidoAnteriormenteDomain)
    return b.set(
        q_bc_mono_ret=t.quantidade,
        ad_rem_cbs_ret=t.aliquota_ad_rem,
        v_cbs_mono_ret=t.valor,
    )


def _retido_ibs(
    ibs_uf: CbsIbsOutput | None,
    _ibs_mun: CbsIbsOutput | None,
    b: _MonoBuilder | None,
) -> _MonoBuilder | None:
    mono_uf = _etapa_retido(ibs_uf)
    if mono_uf is None:
        return b
    merged = GrupoEtapaMonofasiaOutput.merge(mono_uf, None)
    if merged is None:
        return b
    if b is None:
        b = _MonoBuilder(MonofasiaRetidoAnteriormenteDomain)
    return b.set(
        q_bc_mono_ret=merged.quantidade,
        ad_rem_ibs_ret=merged.aliquota_ad_rem,
        v_ibs_mono_ret=merged.valor,
    )


def _diferimento_cbs(cbs: CbsIbsOutput | None) -> _MonoBuilder | None:
    t = _etapa_diferido(cbs)
    if t is None:
        return None
    b = _MonoBuilder(MonofasiaDiferimentoDomain)
    return b.set(p_dif_cbs=t.percentual_diferimento, v_cbs_mono_dif=t.valor_diferimento)


def _diferimento_ibs(
    ibs_uf: CbsIbsOutput | None,
    _ibs_mun: CbsIbsOutput | None,
    b: _MonoBuilder | None,
) -> _MonoBuilder | None:
    mono_uf = _etapa_diferido(ibs_uf)
    if mono_uf is None:
        return b
    merged = GrupoDiferimentoMonofasiaOutput.merge(mono_uf, None)
    if merged is None:
        return b
    if b is None:
        b = _MonoBuilder(MonofasiaDiferimentoDomain)
    return b.set(p_dif_ibs=merged.percentual_diferimento, v_ibs_mono_dif=merged.valor_diferimento)


@dataclass
class IBSCBSDomain:
    CST: str | None = None
    c_class_trib: str | None = None
    ind_doacao: int | None = None
    g_ibscbs: GrupoIBSCBSDomain | None = None
    g_ibscbs_mono: MonofasiaDomain | None = None
    g_transf_cred: TransferenciaCreditoDomain | None = None
    g_ajuste_compet: AjusteCompetenciaDomain | None = None
    g_estorno_cred: EstornoCreditoDomain | None = None
    g_cred_pres_oper: CreditoPresumidoOperacaoDomain | None = None
    g_cred_pres_ibs_zfm: CreditoPresumidoIBSZFMDomain | None = None
    memoria_calculo: MemoriaCalculoDomain | None = None

    def possui_base_calculo_ibscbs(self) -> bool:
        return self.g_ibscbs is not None and self.g_ibscbs.possui_base_calculo_ibscbs()

    def get_valor_base_calculo_ibscbs(self) -> Decimal:
        return self.g_ibscbs.get_valor_base_calculo_ibscbs() if self.possui_base_calculo_ibscbs() else ZERO

    def possui_cbs(self) -> bool:
        return self.g_ibscbs is not None and self.g_ibscbs.possui_cbs()

    def get_g_cbs(self) -> CBSDomain | None:
        return self.g_ibscbs.g_cbs if self.g_ibscbs is not None else None

    def possui_cred_pres_cbs(self) -> bool:
        return self.g_cred_pres_oper is not None and self.g_cred_pres_oper.possui_cred_pres_cbs()

    def get_cred_pres_cbs(self) -> IBSCBSCreditoPresumidoDomain | None:
        if self.possui_cred_pres_cbs() and self.g_cred_pres_oper is not None:
            return self.g_cred_pres_oper.g_cbs_cred_pres
        return None

    def possui_cred_pres_ibs(self) -> bool:
        return self.g_cred_pres_oper is not None and self.g_cred_pres_oper.possui_cred_pres_ibs()

    def get_v_cred_pres_ibs(self) -> Decimal:
        if self.g_cred_pres_oper is not None:
            return self.g_cred_pres_oper.get_v_cred_pres_ibs()
        return ZERO

    def possui_cred_pres_cond_sus_ibs(self) -> bool:
        return (
            self.g_cred_pres_oper is not None and self.g_cred_pres_oper.possui_cred_pres_cond_sus_ibs()
        )

    def get_v_cred_pres_cond_sus_ibs(self) -> Decimal:
        if self.g_cred_pres_oper is not None:
            return self.g_cred_pres_oper.get_v_cred_pres_cond_sus_ibs()
        return ZERO

    def get_grupo_ibscbs(self) -> GrupoIBSCBSDomain | None:
        return self.g_ibscbs

    def possui_ibs_uf(self) -> bool:
        return self.g_ibscbs is not None and self.g_ibscbs.possui_ibs_uf()

    def possui_ibs_mun(self) -> bool:
        return self.g_ibscbs is not None and self.g_ibscbs.possui_ibs_mun()

    def get_g_ibs_uf(self) -> IBSUFDomain | None:
        return self.g_ibscbs.g_ibs_uf if self.g_ibscbs is not None else None

    def get_g_ibs_mun(self) -> IBSMunDomain | None:
        return self.g_ibscbs.g_ibs_mun if self.g_ibscbs is not None else None

    def possui_monofasia(self) -> bool:
        return self.g_ibscbs_mono is not None

    def possui_tributacao_regular(self) -> bool:
        return self.g_ibscbs is not None and self.g_ibscbs.possui_tributacao_regular()

    def get_tributacao_regular(self) -> TributacaoRegularDomain | None:
        return self.g_ibscbs.get_tributacao_regular() if self.g_ibscbs is not None else None

    def possui_estorno_credito(self) -> bool:
        return self.g_estorno_cred is not None


@dataclass
class ImpostoSeletivoDomain:
    CSTIS: str | None = None
    c_class_trib_is: str | None = None
    v_bcis: Decimal | None = None
    p_is: Decimal | None = None
    p_is_espec: Decimal | None = None
    ad_rem_is: Decimal | None = None
    u_trib: str | None = None
    q_trib: Decimal | None = None
    v_is: Decimal | None = None
    memoria_calculo: str | None = None

    def get_valor_imposto_seletivo(self) -> Decimal:
        return self.v_is if self.v_is is not None else ZERO


@dataclass
class TributosDomain:
    IS: ImpostoSeletivoDomain | None = None
    IBSCBS: IBSCBSDomain | None = None

    def possui_imposto_seletivo(self) -> bool:
        return self.IS is not None

    def get_valor_imposto_seletivo(self) -> Decimal:
        return self.IS.get_valor_imposto_seletivo() if self.possui_imposto_seletivo() else ZERO

    def possui_base_calculo_ibscbs(self) -> bool:
        return self.IBSCBS is not None and self.IBSCBS.possui_base_calculo_ibscbs()

    def get_valor_base_calculo_ibscbs(self) -> Decimal:
        return self.IBSCBS.get_valor_base_calculo_ibscbs() if self.possui_base_calculo_ibscbs() else ZERO

    def possui_cbs(self) -> bool:
        return self.IBSCBS is not None and self.IBSCBS.possui_cbs()

    def get_g_cbs(self) -> CBSDomain | None:
        return self.IBSCBS.get_g_cbs() if self.IBSCBS is not None else None

    def possui_cred_pres_cbs(self) -> bool:
        return self.IBSCBS is not None and self.IBSCBS.possui_cred_pres_cbs()

    def get_cred_pres_cbs(self) -> IBSCBSCreditoPresumidoDomain | None:
        return self.IBSCBS.get_cred_pres_cbs() if self.possui_cred_pres_cbs() and self.IBSCBS else None

    def possui_cred_pres_ibs(self) -> bool:
        return self.IBSCBS is not None and self.IBSCBS.possui_cred_pres_ibs()

    def get_v_cred_pres_ibs(self) -> Decimal:
        return self.IBSCBS.get_v_cred_pres_ibs() if self.possui_cred_pres_ibs() and self.IBSCBS else ZERO

    def possui_cred_pres_cond_sus_ibs(self) -> bool:
        return self.IBSCBS is not None and self.IBSCBS.possui_cred_pres_cond_sus_ibs()

    def get_v_cred_pres_cond_sus_ibs(self) -> Decimal:
        return (
            self.IBSCBS.get_v_cred_pres_cond_sus_ibs()
            if self.possui_cred_pres_cond_sus_ibs() and self.IBSCBS
            else ZERO
        )

    def get_grupo_ibscbs(self) -> GrupoIBSCBSDomain | None:
        return self.IBSCBS.get_grupo_ibscbs() if self.IBSCBS is not None else None

    def possui_ibs_uf(self) -> bool:
        return self.IBSCBS is not None and self.IBSCBS.possui_ibs_uf()

    def possui_ibs_mun(self) -> bool:
        return self.IBSCBS is not None and self.IBSCBS.possui_ibs_mun()

    def get_g_ibs_uf(self) -> IBSUFDomain | None:
        return self.IBSCBS.get_g_ibs_uf() if self.IBSCBS is not None else None

    def get_g_ibs_mun(self) -> IBSMunDomain | None:
        return self.IBSCBS.get_g_ibs_mun() if self.IBSCBS is not None else None

    def possui_monofasia(self) -> bool:
        return self.IBSCBS is not None and self.IBSCBS.possui_monofasia()

    def get_g_ibscbs_mono(self) -> MonofasiaDomain | None:
        if self.possui_monofasia() and self.IBSCBS is not None:
            return self.IBSCBS.g_ibscbs_mono
        return None

    def possui_tributacao_regular(self) -> bool:
        return self.IBSCBS is not None and self.IBSCBS.possui_tributacao_regular()

    def get_tributacao_regular(self) -> TributacaoRegularDomain | None:
        return self.IBSCBS.get_tributacao_regular() if self.IBSCBS is not None else None

    def possui_estorno_credito(self) -> bool:
        return self.IBSCBS is not None and self.IBSCBS.possui_estorno_credito()

    def get_g_estorno_cred(self) -> EstornoCreditoDomain | None:
        return self.IBSCBS.g_estorno_cred if self.IBSCBS is not None else None


def _cmp_n_obj(a: int | None, b: int | None) -> int:
    if a is None and b is None:
        return 0
    if a is None:
        return -1
    if b is None:
        return 1
    return (a > b) - (a < b)


@total_ordering
@dataclass
class ObjetoDomain:
    n_obj: int | None = None
    trib_calc: TributosDomain | None = None
    calculo_simulado: bool = False

    def possui_imposto_seletivo(self) -> bool:
        return self.trib_calc is not None and self.trib_calc.possui_imposto_seletivo()

    def get_imposto_seletivo(self) -> ImpostoSeletivoDomain | None:
        return self.trib_calc.IS if self.trib_calc is not None else None

    def get_valor_imposto_seletivo(self) -> Decimal:
        return self.trib_calc.get_valor_imposto_seletivo() if self.possui_imposto_seletivo() else ZERO

    def possui_base_calculo_ibscbs(self) -> bool:
        return self.trib_calc is not None and self.trib_calc.possui_base_calculo_ibscbs()

    def get_valor_base_calculo_ibscbs(self) -> Decimal:
        return (
            self.trib_calc.get_valor_base_calculo_ibscbs()
            if self.possui_base_calculo_ibscbs()
            else ZERO
        )

    def possui_cbs(self) -> bool:
        return self.trib_calc is not None and self.trib_calc.possui_cbs()

    def get_g_cbs(self) -> CBSDomain | None:
        return self.trib_calc.get_g_cbs() if self.trib_calc is not None else None

    def possui_cred_pres_cbs(self) -> bool:
        return self.trib_calc is not None and self.trib_calc.possui_cred_pres_cbs()

    def get_cred_pres_cbs(self) -> IBSCBSCreditoPresumidoDomain | None:
        return self.trib_calc.get_cred_pres_cbs() if self.possui_cred_pres_cbs() and self.trib_calc else None

    def possui_cred_pres_ibs(self) -> bool:
        return self.trib_calc is not None and self.trib_calc.possui_cred_pres_ibs()

    def possui_cred_pres_cond_sus_ibs(self) -> bool:
        return self.trib_calc is not None and self.trib_calc.possui_cred_pres_cond_sus_ibs()

    def get_v_cred_pres_ibs(self) -> Decimal:
        return self.trib_calc.get_v_cred_pres_ibs() if self.possui_cred_pres_ibs() and self.trib_calc else ZERO

    def get_v_cred_pres_cond_sus_ibs(self) -> Decimal:
        return (
            self.trib_calc.get_v_cred_pres_cond_sus_ibs()
            if self.possui_cred_pres_cond_sus_ibs() and self.trib_calc
            else ZERO
        )

    def get_grupo_ibscbs(self) -> GrupoIBSCBSDomain | None:
        return self.trib_calc.get_grupo_ibscbs() if self.trib_calc is not None else None

    def possui_ibs_uf(self) -> bool:
        return self.trib_calc is not None and self.trib_calc.possui_ibs_uf()

    def get_g_ibs_uf(self) -> IBSUFDomain | None:
        return self.trib_calc.get_g_ibs_uf() if self.trib_calc is not None else None

    def possui_ibs_mun(self) -> bool:
        return self.trib_calc is not None and self.trib_calc.possui_ibs_mun()

    def get_g_ibs_mun(self) -> IBSMunDomain | None:
        return self.trib_calc.get_g_ibs_mun() if self.trib_calc is not None else None

    def possui_monofasia(self) -> bool:
        return self.trib_calc is not None and self.trib_calc.possui_monofasia()

    def get_g_ibscbs_mono(self) -> MonofasiaDomain | None:
        return self.trib_calc.get_g_ibscbs_mono() if self.possui_monofasia() and self.trib_calc else None

    def possui_tributacao_regular(self) -> bool:
        return self.trib_calc is not None and self.trib_calc.possui_tributacao_regular()

    def get_tributacao_regular(self) -> TributacaoRegularDomain | None:
        return self.trib_calc.get_tributacao_regular() if self.trib_calc is not None else None

    def possui_estorno_credito(self) -> bool:
        return self.trib_calc is not None and self.trib_calc.possui_estorno_credito()

    def get_g_estorno_cred(self) -> EstornoCreditoDomain | None:
        return self.trib_calc.get_g_estorno_cred() if self.trib_calc is not None else None

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, ObjetoDomain):
            return NotImplemented
        return self.n_obj == other.n_obj

    def __hash__(self) -> int:
        return hash(self.n_obj)

    def __lt__(self, other: ObjetoDomain) -> bool:
        if not isinstance(other, ObjetoDomain):
            return NotImplemented
        return _cmp_n_obj(self.n_obj, other.n_obj) < 0


# --- reduce accumulators ---


@dataclass(frozen=True)
class CBSTotalAccumulator:
    v_dif: Decimal = ZERO
    v_dev_trib: Decimal = ZERO
    v_cbs: Decimal = ZERO
    v_cred_pres: Decimal = ZERO
    v_cred_pres_cond_sus: Decimal = ZERO

    @staticmethod
    def from_fields(
        cbs: CBSDomain | None,
        cbs_cred_pres: IBSCBSCreditoPresumidoDomain | None,
    ) -> CBSTotalAccumulator:
        return CBSTotalAccumulator(
            v_dif=cbs.get_v_dif() if cbs is not None else ZERO,
            v_dev_trib=cbs.get_v_dev_trib() if cbs is not None else ZERO,
            v_cbs=_nn(cbs.v_cbs) if cbs is not None else ZERO,
            v_cred_pres=_nn(cbs_cred_pres.v_cred_pres) if cbs_cred_pres is not None else ZERO,
            v_cred_pres_cond_sus=_nn(cbs_cred_pres.v_cred_pres_cond_sus)
            if cbs_cred_pres is not None
            else ZERO,
        )

    from_ = from_fields

    def add(self, other: CBSTotalAccumulator | None) -> CBSTotalAccumulator:
        if other is None:
            return self
        return CBSTotalAccumulator(
            v_dif=self.v_dif + other.v_dif,
            v_dev_trib=self.v_dev_trib + other.v_dev_trib,
            v_cbs=self.v_cbs + other.v_cbs,
            v_cred_pres=self.v_cred_pres + other.v_cred_pres,
            v_cred_pres_cond_sus=self.v_cred_pres_cond_sus + other.v_cred_pres_cond_sus,
        )

    def to_cbs_total(self) -> CBSTotalDomain:
        return CBSTotalDomain(
            v_dif=self.v_dif,
            v_dev_trib=self.v_dev_trib,
            v_cbs=self.v_cbs,
            v_cred_pres=self.v_cred_pres,
            v_cred_pres_cond_sus=self.v_cred_pres_cond_sus,
        )


@dataclass(frozen=True)
class IBSUFTotalAccumulator:
    v_dif: Decimal = ZERO
    v_dev_trib: Decimal = ZERO
    v_ibs_uf: Decimal = ZERO

    @staticmethod
    def from_fields(ibs_uf: IBSUFDomain | None) -> IBSUFTotalAccumulator:
        if ibs_uf is None:
            return IBSUFTotalAccumulator()
        return IBSUFTotalAccumulator(
            v_dif=ibs_uf.get_v_dif(),
            v_dev_trib=ibs_uf.get_v_dev_trib(),
            v_ibs_uf=_nn(ibs_uf.v_ibs_uf),
        )

    from_ = from_fields

    def add(self, other: IBSUFTotalAccumulator | None) -> IBSUFTotalAccumulator:
        if other is None:
            return self
        return IBSUFTotalAccumulator(
            v_dif=self.v_dif + other.v_dif,
            v_dev_trib=self.v_dev_trib + other.v_dev_trib,
            v_ibs_uf=self.v_ibs_uf + other.v_ibs_uf,
        )

    def to_ibs_uf_total(self) -> IBSUFTotalDomain:
        return IBSUFTotalDomain(
            v_dif=self.v_dif,
            v_dev_trib=self.v_dev_trib,
            v_ibs_uf=self.v_ibs_uf,
        )


@dataclass(frozen=True)
class IBSMunTotalAccumulator:
    v_dif: Decimal = ZERO
    v_dev_trib: Decimal = ZERO
    v_ibs_mun: Decimal = ZERO

    @staticmethod
    def from_fields(ibs_mun: IBSMunDomain | None) -> IBSMunTotalAccumulator:
        if ibs_mun is None:
            return IBSMunTotalAccumulator()
        return IBSMunTotalAccumulator(
            v_dif=ibs_mun.get_v_dif(),
            v_dev_trib=ibs_mun.get_v_dev_trib(),
            v_ibs_mun=_nn(ibs_mun.v_ibs_mun),
        )

    from_ = from_fields

    def add(self, other: IBSMunTotalAccumulator | None) -> IBSMunTotalAccumulator:
        if other is None:
            return self
        return IBSMunTotalAccumulator(
            v_dif=self.v_dif + other.v_dif,
            v_dev_trib=self.v_dev_trib + other.v_dev_trib,
            v_ibs_mun=self.v_ibs_mun + other.v_ibs_mun,
        )

    def to_ibs_mun_total(self) -> IBSMunTotalDomain:
        return IBSMunTotalDomain(
            v_dif=self.v_dif,
            v_dev_trib=self.v_dev_trib,
            v_ibs_mun=self.v_ibs_mun,
        )


@dataclass(frozen=True)
class MonofasiaTotalAccumulator:
    v_ibs_mono: Decimal = ZERO
    v_cbs_mono: Decimal = ZERO
    v_ibs_mono_reten: Decimal = ZERO
    v_cbs_mono_reten: Decimal = ZERO
    v_ibs_mono_ret: Decimal = ZERO
    v_cbs_mono_ret: Decimal = ZERO

    @staticmethod
    def from_fields(m: MonofasiaDomain | None) -> MonofasiaTotalAccumulator:
        if m is None:
            return MonofasiaTotalAccumulator()
        return MonofasiaTotalAccumulator(
            v_ibs_mono=m.get_v_ibs_mono(),
            v_cbs_mono=m.get_v_cbs_mono(),
            v_ibs_mono_reten=m.get_v_ibs_mono_reten(),
            v_cbs_mono_reten=m.get_v_cbs_mono_reten(),
            v_ibs_mono_ret=m.get_v_ibs_mono_ret(),
            v_cbs_mono_ret=m.get_v_cbs_mono_ret(),
        )

    from_ = from_fields

    def add(self, other: MonofasiaTotalAccumulator | None) -> MonofasiaTotalAccumulator:
        if other is None:
            return self
        return MonofasiaTotalAccumulator(
            v_ibs_mono=self.v_ibs_mono + other.v_ibs_mono,
            v_cbs_mono=self.v_cbs_mono + other.v_cbs_mono,
            v_ibs_mono_reten=self.v_ibs_mono_reten + other.v_ibs_mono_reten,
            v_cbs_mono_reten=self.v_cbs_mono_reten + other.v_cbs_mono_reten,
            v_ibs_mono_ret=self.v_ibs_mono_ret + other.v_ibs_mono_ret,
            v_cbs_mono_ret=self.v_cbs_mono_ret + other.v_cbs_mono_ret,
        )

    def to_monofasia_total(self) -> MonofasiaTotalDomain:
        return MonofasiaTotalDomain(
            v_ibs_mono=self.v_ibs_mono,
            v_cbs_mono=self.v_cbs_mono,
            v_ibs_mono_reten=self.v_ibs_mono_reten,
            v_cbs_mono_reten=self.v_cbs_mono_reten,
            v_ibs_mono_ret=self.v_ibs_mono_ret,
            v_cbs_mono_ret=self.v_cbs_mono_ret,
        )


@dataclass(frozen=True)
class EstornoCreditoAccumulator:
    v_ibs_est_cred: Decimal = ZERO
    v_cbs_est_cred: Decimal = ZERO

    def __init__(
        self,
        v_ibs_est_cred: Decimal | None = None,
        v_cbs_est_cred: Decimal | None = None,
    ) -> None:
        object.__setattr__(self, "v_ibs_est_cred", _nn(v_ibs_est_cred))
        object.__setattr__(self, "v_cbs_est_cred", _nn(v_cbs_est_cred))

    @staticmethod
    def from_fields(e: EstornoCreditoDomain | None) -> EstornoCreditoAccumulator:
        if e is None:
            return EstornoCreditoAccumulator()
        return EstornoCreditoAccumulator(e.v_ibs_est_cred, e.v_cbs_est_cred)

    from_ = from_fields

    def add(self, other: EstornoCreditoAccumulator | None) -> EstornoCreditoAccumulator:
        if other is None:
            return self
        return EstornoCreditoAccumulator(
            v_ibs_est_cred=self.v_ibs_est_cred + other.v_ibs_est_cred,
            v_cbs_est_cred=self.v_cbs_est_cred + other.v_cbs_est_cred,
        )

    def to_estorno_credito_domain_total(self) -> EstornoCreditoDomain:
        return EstornoCreditoDomain(
            v_ibs_est_cred=self.v_ibs_est_cred,
            v_cbs_est_cred=self.v_cbs_est_cred,
        )


# --- totals ---


@dataclass
class CBSTotalDomain:
    v_dif: Decimal = ZERO
    v_dev_trib: Decimal = ZERO
    v_cbs: Decimal = ZERO
    v_cred_pres: Decimal = ZERO
    v_cred_pres_cond_sus: Decimal = ZERO

    @staticmethod
    def create(detalhes: list[ObjetoDomain] | None) -> CBSTotalDomain | None:
        if not detalhes:
            return None

        def condicao(d: ObjetoDomain) -> bool:
            return d.possui_cbs() or d.possui_cred_pres_cbs()

        if not any(condicao(d) for d in detalhes):
            return None
        acc = CBSTotalAccumulator()
        for d in detalhes:
            if condicao(d):
                acc = acc.add(
                    CBSTotalAccumulator.from_fields(d.get_g_cbs(), d.get_cred_pres_cbs())
                )
        return acc.to_cbs_total()


@dataclass
class IBSUFTotalDomain:
    v_dif: Decimal = ZERO
    v_dev_trib: Decimal = ZERO
    v_ibs_uf: Decimal = ZERO

    @staticmethod
    def create(detalhes: list[ObjetoDomain] | None) -> IBSUFTotalDomain | None:
        if not detalhes or not any(d.possui_ibs_uf() for d in detalhes):
            return None
        acc = IBSUFTotalAccumulator()
        for d in detalhes:
            if d.possui_ibs_uf():
                acc = acc.add(IBSUFTotalAccumulator.from_fields(d.get_g_ibs_uf()))
        return acc.to_ibs_uf_total()


@dataclass
class IBSMunTotalDomain:
    v_dif: Decimal = ZERO
    v_dev_trib: Decimal = ZERO
    v_ibs_mun: Decimal = ZERO

    @staticmethod
    def create(detalhes: list[ObjetoDomain] | None) -> IBSMunTotalDomain | None:
        if not detalhes or not any(d.possui_ibs_mun() for d in detalhes):
            return None
        acc = IBSMunTotalAccumulator()
        for d in detalhes:
            if d.possui_ibs_mun():
                acc = acc.add(IBSMunTotalAccumulator.from_fields(d.get_g_ibs_mun()))
        return acc.to_ibs_mun_total()


@dataclass
class IBSTotalDomain:
    g_ibs_uf: IBSUFTotalDomain | None = None
    g_ibs_mun: IBSMunTotalDomain | None = None
    v_ibs: Decimal | None = None
    v_cred_pres: Decimal | None = None
    v_cred_pres_cond_sus: Decimal | None = None

    @staticmethod
    def create(detalhes: list[ObjetoDomain] | None) -> IBSTotalDomain | None:
        if not detalhes:
            return None
        g_ibs_uf = IBSUFTotalDomain.create(detalhes) or IBSUFTotalDomain()
        g_ibs_mun = IBSMunTotalDomain.create(detalhes) or IBSMunTotalDomain()
        v_ibs = sum(
            (g.v_ibs for g in (d.get_grupo_ibscbs() for d in detalhes) if g is not None and g.v_ibs is not None),
            ZERO,
        )
        v_cred_pres = sum(
            (d.get_v_cred_pres_ibs() for d in detalhes if d.possui_cred_pres_ibs()),
            ZERO,
        )
        v_cred_pres_cond_sus = sum(
            (d.get_v_cred_pres_cond_sus_ibs() for d in detalhes if d.possui_cred_pres_cond_sus_ibs()),
            ZERO,
        )
        return IBSTotalDomain(
            g_ibs_uf=g_ibs_uf,
            g_ibs_mun=g_ibs_mun,
            v_ibs=v_ibs,
            v_cred_pres=v_cred_pres,
            v_cred_pres_cond_sus=v_cred_pres_cond_sus,
        )


@dataclass
class MonofasiaTotalDomain:
    v_ibs_mono: Decimal = ZERO
    v_cbs_mono: Decimal = ZERO
    v_ibs_mono_reten: Decimal = ZERO
    v_cbs_mono_reten: Decimal = ZERO
    v_ibs_mono_ret: Decimal = ZERO
    v_cbs_mono_ret: Decimal = ZERO

    @staticmethod
    def create(detalhes: list[ObjetoDomain] | None) -> MonofasiaTotalDomain | None:
        if not detalhes or not any(d.possui_monofasia() for d in detalhes):
            return None
        acc = MonofasiaTotalAccumulator()
        for d in detalhes:
            if d.possui_monofasia():
                acc = acc.add(MonofasiaTotalAccumulator.from_fields(d.get_g_ibscbs_mono()))
        return acc.to_monofasia_total()


@dataclass
class ImpostoSeletivoTotalDomain:
    v_is: Decimal = ZERO

    @staticmethod
    def create(detalhes: list[ObjetoDomain] | None) -> ImpostoSeletivoTotalDomain | None:
        if not detalhes or not any(d.possui_imposto_seletivo() for d in detalhes):
            return None
        total = sum(
            (d.get_valor_imposto_seletivo() for d in detalhes if d.possui_imposto_seletivo()),
            ZERO,
        )
        return ImpostoSeletivoTotalDomain(v_is=total)


@dataclass
class IBSCBSTotalDomain:
    v_bc_ibscbs: Decimal | None = None
    g_ibs: IBSTotalDomain | None = None
    g_cbs: CBSTotalDomain | None = None
    g_mono: MonofasiaTotalDomain | None = None
    g_estorno_cred: EstornoCreditoDomain | None = None

    @staticmethod
    def create(detalhes: list[ObjetoDomain] | None) -> IBSCBSTotalDomain | None:
        if not detalhes:
            return None
        v_bc = sum(
            (d.get_valor_base_calculo_ibscbs() for d in detalhes if d.possui_base_calculo_ibscbs()),
            ZERO,
        )
        g_cbs = CBSTotalDomain.create(detalhes) or CBSTotalDomain()
        g_mono = MonofasiaTotalDomain.create(detalhes) or MonofasiaTotalDomain()
        return IBSCBSTotalDomain(
            v_bc_ibscbs=v_bc,
            g_ibs=IBSTotalDomain.create(detalhes),
            g_cbs=g_cbs,
            g_mono=g_mono,
            g_estorno_cred=EstornoCreditoDomain.create(detalhes),
        )


@dataclass
class TributosTotaisDomain:
    is_tot: ImpostoSeletivoTotalDomain | None = None
    ibscbs_tot: IBSCBSTotalDomain | None = None

    @staticmethod
    def create(detalhes: list[ObjetoDomain]) -> TributosTotaisDomain:
        return TributosTotaisDomain(
            is_tot=ImpostoSeletivoTotalDomain.create(detalhes),
            ibscbs_tot=IBSCBSTotalDomain.create(detalhes),
        )


@dataclass
class ValoresTotaisDomain:
    trib_calc: TributosTotaisDomain | None = None

    @staticmethod
    def create(detalhes: list[ObjetoDomain]) -> ValoresTotaisDomain:
        return ValoresTotaisDomain(trib_calc=TributosTotaisDomain.create(detalhes))


# EstornoCreditoDomain.create placed after ObjetoDomain
def _estorno_create(detalhes: list[ObjetoDomain] | None) -> EstornoCreditoDomain | None:
    if not detalhes or not any(d.possui_estorno_credito() for d in detalhes):
        return None
    acc = EstornoCreditoAccumulator()
    for d in detalhes:
        if d.possui_estorno_credito():
            acc = acc.add(EstornoCreditoAccumulator.from_fields(d.get_g_estorno_cred()))
    return acc.to_estorno_credito_domain_total()


EstornoCreditoDomain.create = staticmethod(_estorno_create)  # type: ignore[method-assign]

# Alias accumulators ``from`` like Java (tests)
CBSTotalAccumulator.from_ = CBSTotalAccumulator.from_fields
IBSUFTotalAccumulator.from_ = IBSUFTotalAccumulator.from_fields
IBSMunTotalAccumulator.from_ = IBSMunTotalAccumulator.from_fields
MonofasiaTotalAccumulator.from_ = MonofasiaTotalAccumulator.from_fields
EstornoCreditoAccumulator.from_ = EstornoCreditoAccumulator.from_fields