"""Validações de processamento de item da calculadora RTC.

Pin ``f1eebd7ce3157423b1a6aaca7dc1d6c3395452c4``, ``ProcessamentoItemService``.
Sem Spring, controller, log, CompletableFuture nem orquestração de cálculo tributário.
"""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass, field
from datetime import date, datetime
from decimal import Decimal
from typing import Any

from calculadora_rtc_regime_regular.arredondamento import (
    ESCALA_VALOR_FISCAL,
    formatar_moeda,
)
from calculadora_rtc_regime_regular.base_calculo import (
    Componentes,
    DocumentoInvalido,
    Natureza,
    calcular as calcular_bases_unificadas,
)
from calculadora_rtc_regime_regular.base_calculo_service import CampoInvalido
from calculadora_rtc_regime_regular.nomenclatura import (
    ModoValidacaoNomenclatura,
    SiglaDFe,
    ValidacaoException,
    normalizar_sigla,
    sigla_dfe_por_normalizada,
)

ZERO = Decimal(0)
UNIDADE_PADRAO_ITEM = "UN"
ANO_LIMITE_SUPERIOR_ALIQUOTAS_NOMINAIS = 2027
ID_TRIBUTO_IS = 1
ID_TRIBUTO_CBS_IBS = 2
_IMPOSTO_SELETIVO_APLICAVEL = frozenset({"NFE", "NFCE"})


class ErroGenericoValidacaoException(ValidacaoException):
    pass


class BaseCalculoComponentesInconsistenteException(ValidacaoException):
    def __init__(self, declarada: Decimal, calculada: Decimal) -> None:
        super().__init__(
            "A base de cálculo declarada (%s) diverge da base calculada a partir dos componentes informados (%s)"
            % (_texto_valor(declarada), _texto_valor(calculada))
        )


class BaseCalculoNaoInformadaException(ValidacaoException):
    def __init__(self) -> None:
        super().__init__(
            "A base de cálculo de CBS e IBS deve ser informada quando o grupo do Imposto Seletivo não é informado"
        )


class BaseCalculoInconsistenteException(ValidacaoException):
    def __init__(
        self,
        base_calculo: Decimal,
        base_calculo_imposto_seletivo: Decimal,
        imposto_seletivo_informado: Decimal,
    ) -> None:
        super().__init__(
            "A base de cálculo de CBS e IBS informada %s difere da soma da base de cálculo do Imposto Seletivo %s "
            "com o Imposto Seletivo informado %s"
            % (base_calculo, base_calculo_imposto_seletivo, imposto_seletivo_informado)
        )


class BaseCalculoMenorBaseCalculoImpostoSeletivoException(ValidacaoException):
    def __init__(self, base_calculo: Decimal, base_calculo_imposto_seletivo: Decimal) -> None:
        super().__init__(
            "A base de cálculo de CBS e IBS informada %s é menor que a base de cálculo do Imposto Seletivo %s"
            % (base_calculo, base_calculo_imposto_seletivo)
        )


class NcmNbsSimultaneasException(ValidacaoException):
    def __init__(self) -> None:
        super().__init__("Não é permitido informar NCM e NBS simultaneamente para um item")


class NcmNaoEncontradaException(ValidacaoException):
    def __init__(self, ncm: str, data: date) -> None:
        super().__init__("NCM de código %s não encontrada para a data %s" % (ncm, data))


class NbsNaoEncontradaException(ValidacaoException):
    def __init__(self, nbs: str, data: date) -> None:
        super().__init__("NBS de código %s não encontrada para a data %s" % (nbs, data))


class AliquotasNominaisInformadasIndevidamenteException(ValidacaoException):
    def __init__(self) -> None:
        super().__init__(
            "As alíquotas nominais não podem ser informadas para operações com fato "
            "gerador anterior a 01/01/2027, pois a calculadora resolve as alíquotas vigentes"
        )


class AliquotasNominaisNaoInformadasException(ValidacaoException):
    def __init__(self) -> None:
        super().__init__(
            "As alíquotas nominais (os três campos cbs, ibsEstadual e ibsMunicipal) "
            "devem ser informadas para operações com fato gerador a partir de 01/01/2027"
        )


class ClassificacaoTributariaNaoVinculadaSituacaoTributariaException(ValidacaoException):
    def __init__(self, c_class_trib: str, cst: str, tributo: str) -> None:
        super().__init__(
            "Classificação tributária (cClassTrib) de código %s não está vinculada à situação tributária "
            "(CST) de código %s (%s)" % (c_class_trib, cst, tributo)
        )


class TributacaoRegularNaoInformadaException(ValidacaoException):
    def __init__(self, c_class_trib: str, cst: str) -> None:
        super().__init__(
            "Dados da tributação regular devem ser informados para cClassTrib %s e CST %s"
            % (c_class_trib, cst)
        )


class TributacaoRegularInformadaIndevidamenteException(ValidacaoException):
    def __init__(self, c_class_trib: str, cst: str) -> None:
        super().__init__(
            "Dados da tributação regular informados indevidamente para cClassTrib %s e CST %s"
            % (c_class_trib, cst)
        )


class ImpostoSeletivoInformadoIndevidamenteException(ValidacaoException):
    def __init__(self, ncm: str, data: date) -> None:
        super().__init__(
            "Dados do Imposto Seletivo informados indevidamente para NCM %s e data %s" % (ncm, data)
        )


class IncompatibilidadeSuspensaoException(ValidacaoException):
    def __init__(self, c_class_trib: str, cst: str) -> None:
        super().__init__(
            "Classificação tributária (cClassTrib) %s e situação tributária (CST) %s incompatíveis com suspensão"
            % (c_class_trib, cst)
        )


class ImpostoSeletivoNaoAdmitidoTipoDfeException(ValidacaoException):
    def __init__(self, tp_doc: int, tipo_nomenclatura: str, codigo: str) -> None:
        super().__init__(
            "O tipo de documento fiscal (tpDoc) %d não admite Imposto Seletivo, exigido para %s de código %s"
            % (tp_doc, tipo_nomenclatura, codigo)
        )


class ImpostoSeletivoNaoInformadoException(ValidacaoException):
    def __init__(self, tipo_nomenclatura: str, codigo: str, data: date) -> None:
        super().__init__(
            "Dados do Imposto Seletivo devem ser informados para %s %s e data %s"
            % (tipo_nomenclatura, codigo, data)
        )


class AliquotaImpostoSeletivoNaoInformadaException(ValidacaoException):
    def __init__(self, tipo_nomenclatura: str, codigo: str, data: date) -> None:
        super().__init__(
            "A alíquota do Imposto Seletivo deve ser informada em "
            "aliquotasNominais.impostoSeletivo para %s %s e data %s, pois ainda não foi definida em lei"
            % (tipo_nomenclatura, codigo, data)
        )


class DataFatoGeradorNaoInformadaException(ValidacaoException):
    pass


class SituacaoTributariaNaoEncontradaException(ValidacaoException):
    def __init__(self, codigo: str, tributo: str, data: date) -> None:
        super().__init__(
            "Situação tributária (CST) não encontrada para código %s e data %s (%s)"
            % (codigo, data, tributo)
        )


def _texto_valor(valor: Decimal) -> str:
    if valor.normalize().as_tuple().exponent * -1 <= ESCALA_VALOR_FISCAL:
        return formatar_moeda(valor)
    return format(valor, "f")


def _vazio(texto: str | None) -> bool:
    return texto is None or not texto.strip()


def _preenchido(texto: str | None) -> bool:
    return not _vazio(texto)


def imposto_seletivo_aplicavel(sigla_dfe: str) -> bool:
    return normalizar_sigla(sigla_dfe) in _IMPOSTO_SELETIVO_APLICAVEL


def possui_componentes(componentes: Componentes) -> bool:
    return any(
        getattr(componentes, nome) is not None
        for nome in (
            "vProd",
            "vFrete",
            "vSeg",
            "vOutro",
            "vII",
            "vIS",
            "vDesc",
            "vPIS",
            "vCOFINS",
            "vICMS",
            "vICMSUFDest",
            "vFCP",
            "vFCPUFDest",
            "vICMSMono",
            "vISSQN",
        )
    )


def aplicar_defaults_quantidade_unidade(item: ItemOperacaoInput) -> None:
    if item.quantidade is None:
        item.quantidade = Decimal(1)
    if item.unidade is None:
        item.unidade = UNIDADE_PADRAO_ITEM


ExisteCst = Callable[[str, int, date], bool]


@dataclass
class SituacaoTributariaService:
    existe_cst: ExisteCst
    consultar_por_codigo: Callable[[str, int, date], SituacaoTributaria | None] | None = None

    def validar_cst(self, cst: str, id_tributo: int, data: date) -> None:
        if not self.existe_cst(cst, id_tributo, data):
            tributo = "Imposto Seletivo" if id_tributo == ID_TRIBUTO_IS else "CBS e IBS"
            raise SituacaoTributariaNaoEncontradaException(cst, tributo, data)

    def consultar_situacao_tributaria_por_codigo(
        self, cst: str, id_tributo: int, data: date
    ) -> SituacaoTributaria | None:
        if self.consultar_por_codigo is None:
            return None
        return self.consultar_por_codigo(cst, id_tributo, data)


@dataclass
class AliquotasNominaisImpostoSeletivo:
    ad_valorem: Decimal | None = None
    ad_rem: Decimal | None = None


@dataclass
class AliquotasNominaisInput:
    cbs: Decimal | None = None
    ibs_estadual: Decimal | None = None
    ibs_municipal: Decimal | None = None
    imposto_seletivo: AliquotasNominaisImpostoSeletivo | None = None


@dataclass
class ImpostoSeletivoInput:
    cst: str | None = None
    c_class_trib: str | None = None
    base_calculo: Decimal | None = None
    quantidade: Decimal | None = None
    unidade: str | None = None
    imposto_informado: Decimal | None = None

    def valor_imposto_seletivo_informado(self) -> Decimal:
        return self.imposto_informado if self.imposto_informado is not None else ZERO


@dataclass
class TributacaoRegularInput:
    cst: str
    c_class_trib: str


@dataclass
class ItemOperacaoInput:
    numero: int | None = None
    ncm: str | None = None
    nbs: str | None = None
    cst: str | None = None
    c_class_trib: str | None = None
    base_calculo: Decimal | None = None
    quantidade: Decimal | None = None
    unidade: str | None = None
    imposto_seletivo: ImpostoSeletivoInput | None = None
    tributacao_regular: TributacaoRegularInput | None = None
    g_componentes_bc: Componentes | None = None
    aliquotas_nominais: AliquotasNominaisInput | None = None

    def possui_ncm_zero(self) -> bool:
        return self.ncm == "00" or self.ncm == "00000000"

    def ajustar_ncm(self, tipo_dfe: TipoDfe | None) -> None:
        if tipo_dfe is None or not tipo_dfe.permite_ncm_zero or not self.possui_ncm_zero():
            return
        self.ncm = None


def ajustar_ncm_item(item: ItemOperacaoInput, tipo_dfe: TipoDfe | None) -> None:
    if tipo_dfe is None or not tipo_dfe.permite_ncm_zero:
        return
    if item.possui_ncm_zero():
        item.ncm = None


@dataclass(frozen=True)
class TipoDfe:
    tipo: int
    sigla: str
    permite_ncm_zero: bool = False


@dataclass
class OperacaoInput:
    id: str | None = None
    versao: str | None = None
    tp_doc: int | None = None
    municipio: int | None = None
    uf: str | None = None
    dh_fato_gerador: datetime | None = None
    data_hora_emissao: datetime | None = None
    data_fato_gerador: date | None = None
    itens: list[ItemOperacaoInput] = field(default_factory=list)

    def fato_gerador_aplicavel(self) -> date:
        if self.dh_fato_gerador is not None:
            return self.dh_fato_gerador.date()
        if self.data_hora_emissao is not None:
            return self.data_hora_emissao.date()
        if self.data_fato_gerador is not None:
            return self.data_fato_gerador
        raise DataFatoGeradorNaoInformadaException("Data do fato gerador não informada")


def _parse_offset_datetime(text: str) -> datetime:
    if text.endswith("Z"):
        text = text[:-1] + "+00:00"
    return datetime.fromisoformat(text)


def _decimal_json(val: object) -> Decimal | None:
    if val is None:
        return None
    return Decimal(str(val))


def _componentes_from_json(raw: dict[str, Any] | None) -> Componentes | None:
    if raw is None:
        return None
    return Componentes(
        vProd=_decimal_json(raw.get("vProd")),
        vFrete=_decimal_json(raw.get("vFrete")),
        vSeg=_decimal_json(raw.get("vSeg")),
        vOutro=_decimal_json(raw.get("vOutro")),
        vII=_decimal_json(raw.get("vII")),
        vIS=_decimal_json(raw.get("vIS")),
        vDesc=_decimal_json(raw.get("vDesc")),
        vPIS=_decimal_json(raw.get("vPIS")),
        vCOFINS=_decimal_json(raw.get("vCOFINS")),
        vICMS=_decimal_json(raw.get("vICMS")),
        vICMSUFDest=_decimal_json(raw.get("vICMSUFDest")),
        vFCP=_decimal_json(raw.get("vFCP")),
        vFCPUFDest=_decimal_json(raw.get("vFCPUFDest")),
        vICMSMono=_decimal_json(raw.get("vICMSMono")),
        vISSQN=_decimal_json(raw.get("vISSQN")),
    )


def operacao_input_from_json(payload: dict[str, Any]) -> OperacaoInput:
    """Espelha desserialização Jackson de ``OperacaoInput`` (nomes de campo da API)."""

    dh_fato_gerador: datetime | None = None
    if payload.get("dhFatoGerador"):
        dh_fato_gerador = _parse_offset_datetime(str(payload["dhFatoGerador"]))

    data_hora_emissao: datetime | None = None
    if payload.get("dataHoraEmissao"):
        data_hora_emissao = _parse_offset_datetime(str(payload["dataHoraEmissao"]))

    itens: list[ItemOperacaoInput] = []
    for raw_item in payload.get("itens") or []:
        g_bc = raw_item.get("gComponentesBC")
        g_componentes = _componentes_from_json(g_bc) if "gComponentesBC" in raw_item else None
        itens.append(
            ItemOperacaoInput(
                numero=raw_item.get("numero"),
                ncm=raw_item.get("ncm"),
                nbs=raw_item.get("nbs"),
                cst=raw_item.get("cst"),
                c_class_trib=raw_item.get("cClassTrib"),
                base_calculo=_decimal_json(raw_item.get("baseCalculo")),
                quantidade=_decimal_json(raw_item.get("quantidade")),
                unidade=raw_item.get("unidade"),
                g_componentes_bc=g_componentes,
            )
        )

    return OperacaoInput(
        id=payload.get("id"),
        versao=payload.get("versao"),
        tp_doc=payload.get("tpDoc"),
        municipio=payload.get("municipio"),
        uf=payload.get("uf"),
        dh_fato_gerador=dh_fato_gerador,
        data_hora_emissao=data_hora_emissao,
        itens=itens,
    )


def operacao_input_from_json_text(json_text: str) -> OperacaoInput:
    import json

    return operacao_input_from_json(json.loads(json_text, parse_float=Decimal))


def item_operacao_input_to_json_dict(item: ItemOperacaoInput) -> dict[str, Any]:
    """Serializa item com nomes Jackson (roundtrip parcial como nos testes de integração)."""
    out: dict[str, Any] = {}
    if item.numero is not None:
        out["numero"] = item.numero
    if item.cst is not None:
        out["cst"] = item.cst
    if item.c_class_trib is not None:
        out["cClassTrib"] = item.c_class_trib
    if item.base_calculo is not None:
        out["baseCalculo"] = format(item.base_calculo, "f")
    comp = item.g_componentes_bc
    if comp is not None:
        grupo: dict[str, str] = {}
        for nome in (
            "vProd",
            "vFrete",
            "vSeg",
            "vOutro",
            "vII",
            "vIS",
            "vDesc",
            "vPIS",
            "vCOFINS",
            "vICMS",
            "vICMSUFDest",
            "vFCP",
            "vFCPUFDest",
            "vICMSMono",
            "vISSQN",
        ):
            valor = getattr(comp, nome)
            if valor is not None:
                grupo[nome] = format(valor, "f")
        if grupo:
            out["gComponentesBC"] = grupo
    return out


@dataclass(frozen=True)
class ClassificacaoTributariaDTO:
    id: int
    codigo: str
    cst: str


@dataclass(frozen=True)
class TratamentoClassificacaoDTO:
    id_tratamento_tributario: int | None = None
    id_classificacao_tributaria: int | None = None
    in_incompativel_com_suspensao: bool = False
    in_exige_grupo_desoneracao: bool = False


@dataclass(frozen=True)
class SituacaoTributaria:
    in_grupo_ibs_cbs: bool | None = None


@dataclass(frozen=True)
class AliquotaAdValoremDTO:
    valor: Decimal


@dataclass(frozen=True)
class AliquotaAdRemDTO:
    valor: Decimal
    unidade_medida: str | None = None


@dataclass(frozen=True)
class AliquotaImpostoSeletivoModel:
    aliquota_ad_valorem: Decimal | None = None
    aliquota_ad_rem: Decimal | None = None
    unidade_medida: str | None = None


@dataclass
class TratamentoClassificacaoModel:
    tratamento_classificacao_cbs_ibs: TratamentoClassificacaoDTO | None = None
    tratamento_classificacao_imposto_seletivo: TratamentoClassificacaoDTO | None = None
    tratamento_classificacao_cbs_ibs_desoneracao: TratamentoClassificacaoDTO | None = None
    aliquota_imposto_seletivo: AliquotaImpostoSeletivoModel | None = None
    tem_desoneracao: bool = False


ValidarVinculoTipoDfe = Callable[[TipoDfe, int, str, date, str], None]
ValidarNomenclatura = Callable[
    [SiglaDFe, int, str, str | None, str | None, date, str, ModoValidacaoNomenclatura], None
]
ValidarNcmAplicavel = Callable[[str | None, int, str, date, str], None]
ValidarNbsAplicavel = Callable[[str | None, int, str, date, str], None]
ValidarCst = Callable[[str, int, date], None]
ExisteNcm = Callable[[str, date], bool]
ExisteNbs = Callable[[str, date], bool]


@dataclass
class ProcessamentoItemService:
    """Validações compartilhadas de item (espelho do serviço Java neste pin)."""

    situacao_tributaria: SituacaoTributariaService | None = None
    buscar_classificacao_cbs_ibs: Callable[[str, date], ClassificacaoTributariaDTO] | None = None
    buscar_classificacao_imposto_seletivo: Callable[[str, date], ClassificacaoTributariaDTO] | None = None
    buscar_tratamento_classificacao: Callable[[int, date], TratamentoClassificacaoDTO] | None = None
    validar_vinculo_tipo_dfe: ValidarVinculoTipoDfe | None = None
    validar_nomenclatura: ValidarNomenclatura | None = None
    validar_ncm_aplicavel: ValidarNcmAplicavel | None = None
    validar_nbs_aplicavel: ValidarNbsAplicavel | None = None
    validar_cst: ValidarCst | None = None
    existe_ncm: ExisteNcm | None = None
    existe_nbs: ExisteNbs | None = None
    consultar_situacao_tributaria: Callable[[str, int, date], SituacaoTributaria | None] | None = None
    existe_ncm_ad_valorem: Callable[[str, date], bool] | None = None
    buscar_aliquota_ad_rem_produto: Callable[[str, int, date], AliquotaAdRemDTO | None] | None = None
    existe_nbs_ad_valorem: Callable[[str, date], bool] | None = None
    buscar_aliquota_ad_valorem_produto: Callable[[str, int, date], AliquotaAdValoremDTO | None] | None = None
    buscar_aliquota_ad_valorem_servico: Callable[[str, int, date], Decimal | None] | None = None

    def _validar_cst(self, cst: str, id_tributo: int, data: date) -> None:
        if self.situacao_tributaria is not None:
            self.situacao_tributaria.validar_cst(cst, id_tributo, data)
        elif self.validar_cst is not None:
            self.validar_cst(cst, id_tributo, data)

    def processar_item(
        self,
        operacao: OperacaoInput,
        item: ItemOperacaoInput,
        data: date,
        tipo_dfe: TipoDfe | None = None,
    ) -> TratamentoClassificacaoModel:
        """Validações de ``processarItem`` sem cálculo de tributos (``CalculoTributoService``)."""
        aplicar_defaults_quantidade_unidade(item)
        item.ajustar_ncm(tipo_dfe)
        componentes = item.g_componentes_bc
        if componentes is not None and possui_componentes(componentes):
            self.validar_base_calculo_com_componentes(operacao, item, componentes)
        if componentes is None or not possui_componentes(componentes):
            self.validar_base_calculo_legado(item)
        self.validar_ncm_nbs(item.ncm, item.nbs, data)
        self._validar_cst(item.cst or "", ID_TRIBUTO_CBS_IBS, data)
        self.validar_aliquotas_nominais(item, data)
        return self.obter_tratamento_classificacao(item, data, tipo_dfe)

    def validar_quantidade_e_unidade(
        self, item: ItemOperacaoInput, aliquota: AliquotaImpostoSeletivoModel
    ) -> None:
        if aliquota.aliquota_ad_rem is not None and item.imposto_seletivo is not None:
            is_item = item.imposto_seletivo
            if is_item.quantidade is None:
                raise ErroGenericoValidacaoException(
                    "A quantidade do Imposto Seletivo deve ser informada para alíquota ad rem"
                )
            if is_item.quantidade <= ZERO:
                raise ErroGenericoValidacaoException(
                    "A quantidade do Imposto Seletivo deve ser maior do que zero para alíquota ad rem"
                )
            if is_item.unidade is None:
                raise ErroGenericoValidacaoException(
                    "A unidade de medida do Imposto Seletivo deve ser informada para alíquota ad rem"
                )
        if item.quantidade is not None and item.quantidade <= ZERO:
            raise ErroGenericoValidacaoException("A quantidade do item deve ser maior do que zero")

    def validar_base_calculo_com_componentes(
        self,
        operacao: OperacaoInput,
        item: ItemOperacaoInput,
        componentes: Componentes,
    ) -> None:
        tp_doc = operacao.tp_doc
        natureza = self._inferir_natureza(item)
        ano = operacao.fato_gerador_aplicavel().year
        try:
            resultado = calcular_bases_unificadas(componentes, ano, natureza, tp_doc)
        except DocumentoInvalido as exc:
            raise CampoInvalido(str(exc)) from exc
        imposto_seletivo = item.imposto_seletivo
        if imposto_seletivo is not None:
            bc_calculada = resultado.base_is
            if bc_calculada is None or bc_calculada < ZERO:
                raise ErroGenericoValidacaoException(
                    "A base de cálculo do Imposto Seletivo calculada a partir dos componentes é negativa"
                )
            base_declarada = imposto_seletivo.base_calculo
            if base_declarada is not None and base_declarada != bc_calculada:
                raise BaseCalculoComponentesInconsistenteException(base_declarada, bc_calculada)
            if base_declarada is None:
                imposto_seletivo.base_calculo = bc_calculada
            return
        bc_calculada = resultado.base_rg
        if bc_calculada is None or bc_calculada < ZERO:
            raise ErroGenericoValidacaoException("A base de cálculo calculada a partir dos componentes é negativa")
        base_declarada = item.base_calculo
        if base_declarada is not None and base_declarada != bc_calculada:
            raise BaseCalculoComponentesInconsistenteException(base_declarada, bc_calculada)
        if base_declarada is None:
            item.base_calculo = bc_calculada

    def validar_base_calculo_legado(self, item: ItemOperacaoInput) -> None:
        imposto_seletivo = item.imposto_seletivo
        base_calculo = item.base_calculo
        if imposto_seletivo is None:
            if base_calculo is None:
                raise BaseCalculoNaoInformadaException()
            return
        base_calculo_imposto_seletivo = imposto_seletivo.base_calculo
        if base_calculo_imposto_seletivo is None:
            raise ErroGenericoValidacaoException(
                "A base de cálculo do Imposto Seletivo deve ser informada quando o grupo de Imposto Seletivo é informado"
            )
        imposto_informado = imposto_seletivo.imposto_informado
        if base_calculo is None:
            item.base_calculo = base_calculo_imposto_seletivo + imposto_seletivo.valor_imposto_seletivo_informado()
            return
        if imposto_informado is not None:
            esperada = base_calculo_imposto_seletivo + imposto_informado
            if base_calculo != esperada:
                raise BaseCalculoInconsistenteException(base_calculo, base_calculo_imposto_seletivo, imposto_informado)
        elif base_calculo < base_calculo_imposto_seletivo:
            raise BaseCalculoMenorBaseCalculoImpostoSeletivoException(base_calculo, base_calculo_imposto_seletivo)

    def validar_ncm_nbs(self, ncm: str | None, nbs: str | None, data: date) -> None:
        if _preenchido(ncm) and _preenchido(nbs):
            raise NcmNbsSimultaneasException()
        if _preenchido(ncm) and self.existe_ncm is not None and not self.existe_ncm(ncm, data):
            raise NcmNaoEncontradaException(ncm, data)
        if _preenchido(nbs) and self.existe_nbs is not None and not self.existe_nbs(nbs, data):
            raise NbsNaoEncontradaException(nbs, data)

    def validar_aliquotas_nominais(self, item: ItemOperacaoInput, data: date) -> None:
        if data.year < ANO_LIMITE_SUPERIOR_ALIQUOTAS_NOMINAIS:
            if self._informou_aliquotas_nominais(item.aliquotas_nominais):
                raise AliquotasNominaisInformadasIndevidamenteException()
            return
        situacao: SituacaoTributaria | None = None
        if self.situacao_tributaria is not None:
            situacao = self.situacao_tributaria.consultar_situacao_tributaria_por_codigo(
                item.cst or "", ID_TRIBUTO_CBS_IBS, data
            )
        elif self.consultar_situacao_tributaria is not None:
            situacao = self.consultar_situacao_tributaria(item.cst or "", ID_TRIBUTO_CBS_IBS, data)
        else:
            return
        cst_exige_grupo = situacao is not None and situacao.in_grupo_ibs_cbs is True
        if not cst_exige_grupo:
            return
        aliquotas = item.aliquotas_nominais
        if (
            aliquotas is None
            or aliquotas.cbs is None
            or aliquotas.ibs_estadual is None
            or aliquotas.ibs_municipal is None
        ):
            raise AliquotasNominaisNaoInformadasException()

    def validar_classificacao_tributaria_cbs_ibs(
        self,
        classificacao: ClassificacaoTributariaDTO,
        cst: str,
        ncm: str | None,
        nbs: str | None,
    ) -> None:
        if _vazio(ncm) and _vazio(nbs):
            return
        if classificacao.cst != cst:
            raise ClassificacaoTributariaNaoVinculadaSituacaoTributariaException(
                classificacao.codigo, cst, "CBS e IBS"
            )

    def validar_classificacao_tributaria_imposto_seletivo(
        self, classificacao: ClassificacaoTributariaDTO, cst: str
    ) -> None:
        if classificacao.cst != cst:
            raise ClassificacaoTributariaNaoVinculadaSituacaoTributariaException(
                classificacao.codigo, cst, "Imposto Seletivo"
            )

    def validar_nomenclatura_aplicavel_imposto_seletivo(
        self,
        ncm: str | None,
        nbs: str | None,
        classificacao: ClassificacaoTributariaDTO,
        data: date,
    ) -> None:
        """Desativada no pin Java (corpo comentado); mantida como no-op."""

    def _validar_vinculo_tipo_dfe(
        self, tipo_dfe: TipoDfe | None, classificacao: ClassificacaoTributariaDTO, data: date
    ) -> None:
        if tipo_dfe is None or self.validar_vinculo_tipo_dfe is None:
            return
        self.validar_vinculo_tipo_dfe(
            tipo_dfe, classificacao.id, classificacao.codigo, data, "CBS e IBS"
        )

    def obter_tratamento_classificacao(
        self, item: ItemOperacaoInput, data: date, tipo_dfe: TipoDfe | None
    ) -> TratamentoClassificacaoModel:
        if self.buscar_classificacao_cbs_ibs is None or self.buscar_tratamento_classificacao is None:
            raise RuntimeError("Dependências de classificação tributária não configuradas")
        ncm = item.ncm
        nbs = item.nbs
        classificacao_cbs_ibs = self.buscar_classificacao_cbs_ibs(item.c_class_trib or "", data)
        self.validar_classificacao_tributaria_cbs_ibs(classificacao_cbs_ibs, item.cst or "", ncm, nbs)
        self._validar_vinculo_tipo_dfe(tipo_dfe, classificacao_cbs_ibs, data)
        tratamento_cbs_ibs = self.buscar_tratamento_classificacao(classificacao_cbs_ibs.id, data)
        cst = item.cst
        c_class_trib = item.c_class_trib
        tem_desoneracao = False
        tratamento_desoneracao: TratamentoClassificacaoDTO | None = None
        classificacao_imposto_seletivo: ClassificacaoTributariaDTO | None = None
        tratamento_imposto_seletivo: TratamentoClassificacaoDTO | None = None

        if tratamento_cbs_ibs.in_exige_grupo_desoneracao:
            if item.tributacao_regular is None:
                raise TributacaoRegularNaoInformadaException(c_class_trib or "", cst or "")
            tr = item.tributacao_regular
            cst = tr.cst
            c_class_trib = tr.c_class_trib
            tratamento_desoneracao = tratamento_cbs_ibs
            classificacao_cbs_ibs = self.buscar_classificacao_cbs_ibs(c_class_trib, data)
            self.validar_classificacao_tributaria_cbs_ibs(classificacao_cbs_ibs, cst, ncm, nbs)
            self._validar_vinculo_tipo_dfe(tipo_dfe, classificacao_cbs_ibs, data)
            tratamento_cbs_ibs = self.buscar_tratamento_classificacao(classificacao_cbs_ibs.id, data)
            if tratamento_cbs_ibs.in_incompativel_com_suspensao:
                raise IncompatibilidadeSuspensaoException(c_class_trib, cst)
            tem_desoneracao = True
        elif item.tributacao_regular is not None and tipo_dfe is not None and self.buscar_classificacao_cbs_ibs:
            tr = item.tributacao_regular
            classificacao_tr = self.buscar_classificacao_cbs_ibs(tr.c_class_trib, data)
            self._validar_vinculo_tipo_dfe(tipo_dfe, classificacao_tr, data)

        if tipo_dfe is not None and self.validar_nomenclatura is not None:
            sigla = sigla_dfe_por_normalizada(tipo_dfe.sigla)
            self.validar_nomenclatura(
                sigla,
                classificacao_cbs_ibs.id,
                classificacao_cbs_ibs.codigo,
                ncm,
                nbs,
                data,
                "CBS e IBS",
                ModoValidacaoNomenclatura.PERMISSIVO,
            )
        elif tipo_dfe is None and self.validar_ncm_aplicavel is not None and self.validar_nbs_aplicavel is not None:
            if _vazio(ncm) and _vazio(nbs):
                self.validar_ncm_aplicavel(
                    ncm, classificacao_cbs_ibs.id, classificacao_cbs_ibs.codigo, data, "CBS e IBS"
                )
                self.validar_nbs_aplicavel(
                    nbs, classificacao_cbs_ibs.id, classificacao_cbs_ibs.codigo, data, "CBS e IBS"
                )
            elif _preenchido(ncm) and _vazio(nbs):
                self.validar_ncm_aplicavel(
                    ncm, classificacao_cbs_ibs.id, classificacao_cbs_ibs.codigo, data, "CBS e IBS"
                )
            elif _preenchido(nbs) and _vazio(ncm):
                self.validar_nbs_aplicavel(
                    nbs, classificacao_cbs_ibs.id, classificacao_cbs_ibs.codigo, data, "CBS e IBS"
                )

        if item.imposto_seletivo is not None:
            self._validar_cst(item.imposto_seletivo.cst or "", ID_TRIBUTO_IS, data)
            if self.buscar_classificacao_imposto_seletivo is not None:
                classificacao_imposto_seletivo = self.buscar_classificacao_imposto_seletivo(
                    item.imposto_seletivo.c_class_trib or "", data
                )
                self.validar_classificacao_tributaria_imposto_seletivo(
                    classificacao_imposto_seletivo, item.imposto_seletivo.cst or ""
                )

        aliquota_imposto_seletivo = self._analisar_aliquota_imposto_seletivo(item, data)

        if (
            tipo_dfe is not None
            and not imposto_seletivo_aplicavel(tipo_dfe.sigla)
            and aliquota_imposto_seletivo is not None
        ):
            tipo_nom = "NCM" if _preenchido(ncm) else "NBS"
            codigo = ncm if _preenchido(ncm) else (nbs or "")
            raise ImpostoSeletivoNaoAdmitidoTipoDfeException(int(tipo_dfe.tipo), tipo_nom, codigo)

        if (
            aliquota_imposto_seletivo is None
            and data.year >= ANO_LIMITE_SUPERIOR_ALIQUOTAS_NOMINAIS
            and self._existe_incidencia_imposto_seletivo(ncm, nbs, data)
        ):
            tipo_nom = "NCM" if _preenchido(ncm) else "NBS"
            codigo = ncm if _preenchido(ncm) else (nbs or "")
            if item.imposto_seletivo is None:
                raise ImpostoSeletivoNaoInformadoException(tipo_nom, codigo, data)
            raise AliquotaImpostoSeletivoNaoInformadaException(tipo_nom, codigo, data)

        if aliquota_imposto_seletivo is not None:
            if item.imposto_seletivo is None:
                tipo_nom = "NCM" if _preenchido(ncm) else "NBS"
                codigo = ncm if _preenchido(ncm) else (nbs or "")
                raise ImpostoSeletivoNaoInformadoException(tipo_nom, codigo, data)
            self.validar_quantidade_e_unidade(item, aliquota_imposto_seletivo)
            if classificacao_imposto_seletivo is not None and self.buscar_tratamento_classificacao is not None:
                tratamento_imposto_seletivo = self.buscar_tratamento_classificacao(
                    classificacao_imposto_seletivo.id, data
                )

        if aliquota_imposto_seletivo is not None:
            self.validar_nomenclatura_aplicavel_imposto_seletivo(
                ncm, nbs, classificacao_imposto_seletivo or classificacao_cbs_ibs, data
            )

        return TratamentoClassificacaoModel(
            tratamento_classificacao_cbs_ibs=tratamento_cbs_ibs,
            tratamento_classificacao_imposto_seletivo=tratamento_imposto_seletivo,
            tratamento_classificacao_cbs_ibs_desoneracao=tratamento_desoneracao,
            aliquota_imposto_seletivo=aliquota_imposto_seletivo,
            tem_desoneracao=tem_desoneracao,
        )

    @staticmethod
    def _inferir_natureza(item: ItemOperacaoInput) -> Natureza | None:
        possui_ncm = _preenchido(item.ncm)
        possui_nbs = _preenchido(item.nbs)
        if possui_ncm and possui_nbs:
            return None
        if possui_ncm:
            return Natureza.BEM
        if possui_nbs:
            return Natureza.SERVICO
        return None

    @staticmethod
    def _informou_aliquotas_nominais(aliquotas: AliquotasNominaisInput | None) -> bool:
        if aliquotas is None:
            return False
        is_nom = aliquotas.imposto_seletivo
        return (
            aliquotas.cbs is not None
            or aliquotas.ibs_estadual is not None
            or aliquotas.ibs_municipal is not None
            or (
                is_nom is not None
                and (is_nom.ad_valorem is not None or is_nom.ad_rem is not None)
            )
        )

    def _existe_incidencia_imposto_seletivo(self, ncm: str | None, nbs: str | None, data: date) -> bool:
        if _preenchido(ncm) and len(ncm) == 8 and self.existe_ncm_ad_valorem and self.buscar_aliquota_ad_rem_produto:
            return self.existe_ncm_ad_valorem(ncm, data) or (
                self.buscar_aliquota_ad_rem_produto(ncm, 1, data) is not None
            )
        if _preenchido(nbs) and len(nbs) == 9 and self.existe_nbs_ad_valorem:
            return self.existe_nbs_ad_valorem(nbs, data)
        return False

    def _analisar_aliquota_imposto_seletivo(
        self, item: ItemOperacaoInput, data: date
    ) -> AliquotaImpostoSeletivoModel | None:
        ncm = item.ncm
        nbs = item.nbs
        aliquotas_informadas = self._obter_aliquotas_nominais_imposto_seletivo(item)
        possui_ad_rem_informada = aliquotas_informadas is not None and aliquotas_informadas.ad_rem is not None
        if (
            possui_ad_rem_informada
            and item.imposto_seletivo is not None
            and _vazio(item.imposto_seletivo.unidade)
        ):
            raise ErroGenericoValidacaoException(
                "A unidade de medida do Imposto Seletivo deve ser informada quando a alíquota ad rem é informada pelo usuário"
            )
        aliquota_ad_valorem = aliquotas_informadas.ad_valorem if aliquotas_informadas else None
        aliquota_ad_rem = aliquotas_informadas.ad_rem if aliquotas_informadas else None
        unidade_medida = item.imposto_seletivo.unidade if aliquota_ad_rem is not None and item.imposto_seletivo else None

        if _preenchido(ncm) and len(ncm) == 8:
            if aliquota_ad_valorem is None and self.buscar_aliquota_ad_valorem_produto:
                dto = self.buscar_aliquota_ad_valorem_produto(ncm, 1, data)
                if dto is not None:
                    aliquota_ad_valorem = dto.valor
            if aliquota_ad_rem is None and self.buscar_aliquota_ad_rem_produto:
                dto = self.buscar_aliquota_ad_rem_produto(ncm, 1, data)
                if dto is not None:
                    aliquota_ad_rem = dto.valor
                    unidade_medida = dto.unidade_medida
        elif _preenchido(nbs) and len(nbs) == 9:
            if aliquota_ad_valorem is None and self.buscar_aliquota_ad_valorem_servico:
                aliquota_ad_valorem = self.buscar_aliquota_ad_valorem_servico(nbs, 1, data)

        if aliquota_ad_valorem is not None or aliquota_ad_rem is not None:
            return AliquotaImpostoSeletivoModel(
                aliquota_ad_valorem=aliquota_ad_valorem,
                aliquota_ad_rem=aliquota_ad_rem,
                unidade_medida=unidade_medida,
            )
        return None

    @staticmethod
    def _obter_aliquotas_nominais_imposto_seletivo(
        item: ItemOperacaoInput,
    ) -> AliquotasNominaisImpostoSeletivo | None:
        if item.imposto_seletivo is None:
            return None
        if item.aliquotas_nominais is None:
            return None
        return item.aliquotas_nominais.imposto_seletivo


def criar_processamento_item_servico_minimo() -> ProcessamentoItemService:
    """Instância mínima como ``ProcessamentoItemServiceTest`` (@BeforeAll, só BC unificada)."""
    return ProcessamentoItemService()