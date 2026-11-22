"""Consultas públicas de dados abertos (pin f1eebd7ce3157423b1a6aaca7dc1d6c3395452c4).

Transcrição de ``br.gov.serpro.rtc.domain.service.dadosabertos.DadosAbertosService``.
"""

from __future__ import annotations

import re
import sqlite3
from dataclasses import dataclass, field
from datetime import date
from decimal import Decimal
from enum import Enum
from typing import Any, Protocol

from calculadora_rtc_regime_regular.aliquota_resultado import (
    AliquotaResultado,
    FormaAplicacao,
)
from calculadora_rtc_regime_regular.banco import conectar


# --- exceções (espelho Java) ---


class ValidacaoException(Exception):
    pass


class AliquotaNaoEncontradaException(Exception):
    pass


class ClassificacaoTributariaNaoEncontradaException(Exception):
    def __init__(self, codigo: str, contexto: str, data: date) -> None:
        super().__init__(f"{codigo} / {contexto} / {data}")


class NcmNaoEncontradaException(Exception):
    def __init__(self, ncm: str, data: date) -> None:
        super().__init__(f"NCM {ncm} em {data}")


class NbsNaoEncontradaException(Exception):
    def __init__(self, nbs: str, data: date) -> None:
        super().__init__(f"NBS {nbs} em {data}")


class NbsNaoVinculadaException(Exception):
    pass


class NcmNaoVinculadaException(Exception):
    pass


class SiglaDfeNaoEncontradaException(Exception):
    pass


class ErroGenericoValidacaoException(Exception):
    pass


class TributoSituacaoTributariaNaoEncontradoException(Exception):
    pass


# --- enums ---


class PapelAtor(Enum):
    FORNECEDOR = "Fornecedor"
    ADQUIRENTE = "Adquirente"


class TipoWarningDadosSimulados(Enum):
    CASO_GERAL = 1


class NomenclaturaResultado(Enum):
    SEM = "SEM"
    NCM = "NCM"
    NBS = "NBS"
    MISTO = "MISTO"
    EXCECAO_NCM = "EXCECAO_NCM"
    EXCECAO_NBS = "EXCECAO_NBS"


_SIGLAS_DFE = (
    "NFEABI",
    "NFE",
    "NFCE",
    "CTE",
    "CTEOS",
    "CTESIMPLIFICADO",
    "BPE",
    "BPETA",
    "BPETM",
    "NF3E",
    "NFSE",
    "NFSEVIA",
    "NFCOM",
    "DERE",
    "DIR",
    "DUIMP",
    "NFAG",
    "NFGAS",
)
_NCM_APLICAVEL_SIGLAS = frozenset({"NFSE", "NFE", "NFCE"})
_NBS_APLICAVEL_SIGLAS = frozenset({"NFSE"})
_IS_APLICAVEL_SIGLAS = frozenset({"NFE", "NFCE"})
_EXCECAO_CLASSIFICACOES = frozenset({"200038", "515001"})


def normalizar_sigla(sigla: str | None) -> str:
    if sigla is None:
        return ""
    return re.sub(r"[\s\-_]", "", sigla).upper()


def _sigla_enum(sigla: str) -> str:
    chave = normalizar_sigla(sigla)
    if chave not in _SIGLAS_DFE:
        raise SiglaDfeNaoEncontradaException(sigla)
    return chave


def _corresponde_sigla(chave: str, sigla: str) -> bool:
    return chave == normalizar_sigla(sigla)


# --- DTOs ---


@dataclass(frozen=True)
class AliquotaDadosAbertos:
    aliquota_referencia: Decimal
    aliquota_propria: Decimal | None
    forma_aplicacao: FormaAplicacao | None


@dataclass(frozen=True)
class UfDadosAbertos:
    sigla: str
    nome: str
    codigo: int


@dataclass(frozen=True)
class MunicipioDadosAbertos:
    codigo: int
    nome: str


@dataclass(frozen=True)
class SituacaoTributariaDadosAbertos:
    id: int
    codigo: str
    descricao: str


@dataclass(frozen=True)
class TipoDfeClassificacaoDadosAbertos:
    tipo: int
    sigla: str
    descricao: str


@dataclass
class ClassificacaoTributariaDadosAbertos:
    codigo: str
    descricao: str
    tipo_aliquota: str
    nomenclatura: str
    descricao_tratamento_tributario: str
    incompativel_com_suspensao: bool
    exige_grupo_desoneracao: bool
    possui_percentual_reducao: bool
    tipos_dfe_classificacao: list[TipoDfeClassificacaoDadosAbertos] = field(
        default_factory=list
    )
    data_atualizacao: date | None = None
    indica_apropriacao_credito_adquirente_cbs: bool | None = None
    indica_apropriacao_credito_adquirente_ibs: bool | None = None
    indica_credito_presumido_fornecedor: bool | None = None
    indica_credito_presumido_adquirente: bool | None = None
    credito_operacao_antecedente: str | None = None
    percentual_reducao_cbs: Decimal | None = None
    percentual_reducao_ibs_uf: Decimal | None = None
    percentual_reducao_ibs_mun: Decimal | None = None
    tipo_receita_bruta_simples_nacional: int | None = None


@dataclass(frozen=True)
class NcmDadosAbertos:
    tributado_pelo_imposto_seletivo: bool
    tem_aliquota_ad_valorem: bool
    tem_aliquota_ad_rem: bool
    aliquota_ad_valorem: Decimal | None
    aliquota_ad_rem: Decimal | None
    capitulo: str | None
    posicao: str | None
    subposicao: str | None
    item: str | None
    subitem: str | None
    unidade: str | None


@dataclass(frozen=True)
class NbsDadosAbertos:
    tributado_pelo_imposto_seletivo: bool
    tem_aliquota_ad_valorem: bool
    aliquota_ad_valorem: Decimal | None
    capitulo: str | None
    posicao: str | None
    subposicao1: str | None
    subposicao2: str | None
    item: str | None


@dataclass(frozen=True)
class NbsListaDadosAbertos:
    codigo: str
    descricao: str


@dataclass(frozen=True)
class FundamentacaoClassificacaoDadosAbertos:
    codigo_classificacao_tributaria: str
    descricao_classificacao_tributaria: str
    codigo_situacao_tributaria: str
    descricao_situacao_tributaria: str
    conjunto_tributo: str
    texto: str
    texto_curto: str
    referencia_normativa: str


@dataclass(frozen=True)
class NcmAplicavelSaida:
    c_class_trib: str
    ncm: str
    data_ocorrencia_fato_gerador: str
    valido: bool


@dataclass(frozen=True)
class NbsAplicavelSaida:
    c_class_trib: str
    nbs: str
    data_ocorrencia_fato_gerador: str
    valido: bool


@dataclass(frozen=True)
class ClassificacaoTributariaResumo:
    codigo: str
    descricao: str


@dataclass
class SituacaoClassificacaoAninhado:
    id: int | None
    codigo: str
    descricao: str
    classificacoes_tributarias: list[ClassificacaoTributariaResumo] = field(
        default_factory=list
    )


@dataclass(frozen=True)
class RedutorCompraGovernamentalDadosAbertos:
    valor: Decimal
    inicio_vigencia: date
    fim_vigencia: date | None


@dataclass(frozen=True)
class TransferenciaCBSDadosAbertos:
    valor: Decimal
    inicio_vigencia: date
    fim_vigencia: date | None


@dataclass(frozen=True)
class TransferenciaIBSDadosAbertos:
    valor: Decimal
    inicio_vigencia: date
    fim_vigencia: date | None


@dataclass(frozen=True)
class NcmVigencia:
    codigo: str
    descricao: str


@dataclass(frozen=True)
class ValidadeDfeClassificacaoTributariaDadosAbertos:
    sigla_dfe_informado: str
    valido_para_sigla_dfe_informado: bool
    nomenclatura: str
    exige_grupo_tributacao_regular: bool
    permite_diferimento: bool
    possibilidade_credito_presumido: bool
    exige_grupo_ibs_cbs: bool


@dataclass(frozen=True)
class TipoDfeDadosAbertos:
    codigo: str
    titulo: str
    modelo: str | None
    ordem: int
    suportado: bool
    permite_ncm_zero: bool


@dataclass
class GrupoDfeDadosAbertos:
    id: str
    titulo: str
    ordem: int = 0
    tipos: list[TipoDfeDadosAbertos] = field(default_factory=list)


@dataclass
class AtorDadosAbertos:
    id: int
    descricao: str
    ordem: int


@dataclass
class GrupoAtorDadosAbertos:
    id: int
    descricao: str
    ordem: int
    atores: list[AtorDadosAbertos] = field(default_factory=list)


@dataclass(frozen=True)
class NomenclaturaDadosAbertos:
    sigla_dfe: str
    c_class_trib: str
    data: date
    nomenclatura: str
    obrigatorio: bool
    ncm_opcional: bool
    nbs_opcional: bool


class BuscarAliquota(Protocol):
    def buscar_aliquota(
        self,
        id_tributo: int,
        codigo_uf: int | None,
        codigo_municipio: int | None,
        data: date,
    ) -> AliquotaResultado: ...


def convert_to_big_decimal(value: object) -> Decimal | None:
    """Espelha ``DadosAbertosService.convertToBigDecimal``."""
    if value is None:
        return None
    if isinstance(value, Decimal):
        return value
    if isinstance(value, float):
        return Decimal(str(value))
    if isinstance(value, int) and not isinstance(value, bool):
        return Decimal(value)
    if isinstance(value, str):
        try:
            return Decimal(value)
        except Exception:
            return None
    try:
        return Decimal(str(value))
    except Exception:
        return None


def _data_str(data: date) -> str:
    return data.isoformat()


def _flag(val: Any) -> bool:
    if isinstance(val, bool):
        return val
    if isinstance(val, (int, float, Decimal)):
        return int(val) != 0
    return bool(val)


def _parse_data(val: Any) -> date | None:
    if val is None:
        return None
    if isinstance(val, date):
        return val
    s = str(val).strip()
    if not s:
        return None
    try:
        return date.fromisoformat(s[:10])
    except Exception:
        return None


def _parse_data_linha(row: tuple[Any, ...], index: int) -> date | None:
    if row is None or index < 0 or index >= len(row):
        return None
    return _parse_data(row[index])


def _trim_descricao(texto: str | None) -> str | None:
    if texto is None:
        return None
    return texto.strip().strip(" -").strip()


def _forma_aplicacao(nome: str | None) -> FormaAplicacao | None:
    if not nome:
        return None
    return FormaAplicacao[nome]


class _SqliteDadosAbertos:
    def _exec(self, sql: str, params: tuple[Any, ...] = ()) -> list[tuple[Any, ...]]:
        with conectar() as conn:
            return list(conn.execute(sql, params).fetchall())

    def _one(self, sql: str, params: tuple[Any, ...] = ()) -> tuple[Any, ...] | None:
        linhas = self._exec(sql, params)
        return linhas[0] if linhas else None

    def _scalar(self, sql: str, params: tuple[Any, ...] = ()) -> Any:
        row = self._one(sql, params)
        return row[0] if row else None

    def consultar_ufs(self) -> list[tuple[Any, ...]]:
        return self._exec(
            "SELECT UF_SIGLA, UF_NOME, UF_CD FROM UF ORDER BY UF_SIGLA"
        )

    def municipios_por_uf(self, sigla: str) -> list[tuple[Any, ...]]:
        return self._exec(
            """
            SELECT m.MUNI_CD, m.MUNI_NOME
            FROM MUNICIPIO m
            JOIN UF u ON m.MUNI_UF_CD = u.UF_CD
            WHERE LOWER(u.UF_SIGLA) = LOWER(?)
            ORDER BY m.MUNI_NOME
            """,
            (sigla,),
        )

    def situacoes_por_tributo(self, id_tributo: int, data: date) -> list[tuple[Any, ...]]:
        d = _data_str(data)
        return self._exec(
            """
            SELECT s.SITR_ID, s.SITR_CD, s.SITR_DESCRICAO
            FROM TRIBUTO_SITUACAO_TRIBUTARIA t
            JOIN SITUACAO_TRIBUTARIA s ON t.TRST_SITR_ID = s.SITR_ID
            WHERE t.TRST_TBTO_ID = ?
              AND t.TRST_INICIO_VIGENCIA <= ?
              AND (t.TRST_FIM_VIGENCIA IS NULL OR t.TRST_FIM_VIGENCIA >= ?)
            ORDER BY s.SITR_CD
            """,
            (id_tributo, d, d),
        )

    def tratamento_por_id_situacao(
        self, id_situacao: int, data: date
    ) -> list[tuple[Any, ...]]:
        d = _data_str(data)
        return self._exec(
            """
            SELECT ct.CLTR_CD, ct.CLTR_DESCRICAO, ct.CLTR_TIPO_ALIQUOTA, ct.CLTR_NOMENCLATURA,
                   tt.TRTR_DESCRICAO, tt.TRTR_IN_INCOMPATIVEL_COM_SUSPENSAO,
                   tt.TRTR_IN_EXIGE_GRUPO_DESONERACAO, st.SITR_IND_GRED, ct.CLTR_ID,
                   ct.CLTR_DATA_ATUALIZACAO
            FROM TRATAMENTO_CLASSIFICACAO tc
            JOIN CLASSIFICACAO_TRIBUTARIA ct ON tc.TRCL_CLTR_ID = ct.CLTR_ID
            JOIN SITUACAO_TRIBUTARIA st ON st.SITR_ID = ct.CLTR_SITR_ID
            JOIN TRATAMENTO_TRIBUTARIO tt ON tt.TRTR_ID = tc.TRCL_TRTR_ID
            WHERE ct.CLTR_SITR_ID = ?
              AND ? BETWEEN tc.TRCL_INICIO_VIGENCIA AND COALESCE(tc.TRCL_FIM_VIGENCIA, ?)
              AND ? BETWEEN ct.CLTR_INICIO_VIGENCIA AND COALESCE(ct.CLTR_FIM_VIGENCIA, ?)
              AND ? BETWEEN tt.TRTR_INICIO_VIGENCIA AND COALESCE(tt.TRTR_FIM_VIGENCIA, ?)
              AND ? BETWEEN st.SITR_INICIO_VIGENCIA AND COALESCE(st.SITR_FIM_VIGENCIA, ?)
            ORDER BY ct.CLTR_CD
            """,
            (id_situacao, d, d, d, d, d, d, d, d),
        )

    def tratamento_por_cst_e_tributo_tipo(
        self, cst: str, siglas: list[str], data: date
    ) -> list[tuple[Any, ...]]:
        if not siglas:
            return []
        d = _data_str(data)
        marks = ",".join("?" * len(siglas))
        return self._exec(
            f"""
            SELECT ct.CLTR_CD, ct.CLTR_DESCRICAO, ct.CLTR_TIPO_ALIQUOTA, ct.CLTR_NOMENCLATURA,
                   tt.TRTR_DESCRICAO, tt.TRTR_IN_INCOMPATIVEL_COM_SUSPENSAO,
                   tt.TRTR_IN_EXIGE_GRUPO_DESONERACAO, st.SITR_IND_GRED, ct.CLTR_ID,
                   ct.CLTR_DATA_ATUALIZACAO
            FROM TRATAMENTO_CLASSIFICACAO tc
            JOIN CLASSIFICACAO_TRIBUTARIA ct ON tc.TRCL_CLTR_ID = ct.CLTR_ID
            JOIN SITUACAO_TRIBUTARIA st ON st.SITR_ID = ct.CLTR_SITR_ID
            JOIN TRATAMENTO_TRIBUTARIO tt ON tt.TRTR_ID = tc.TRCL_TRTR_ID
            WHERE st.SITR_CD = ?
              AND EXISTS (
                  SELECT 1 FROM TRIBUTO_SITUACAO_TRIBUTARIA tst2
                  JOIN TRIBUTO tb2 ON tst2.TRST_TBTO_ID = tb2.TBTO_ID
                  WHERE tst2.TRST_SITR_ID = st.SITR_ID
                    AND tb2.TBTO_SIGLA IN ({marks})
                    AND ? BETWEEN tst2.TRST_INICIO_VIGENCIA AND COALESCE(tst2.TRST_FIM_VIGENCIA, ?)
                    AND ? BETWEEN tb2.TBTO_INICIO_VIGENCIA AND COALESCE(tb2.TBTO_FIM_VIGENCIA, ?)
              )
              AND ? BETWEEN tc.TRCL_INICIO_VIGENCIA AND COALESCE(tc.TRCL_FIM_VIGENCIA, ?)
              AND ? BETWEEN ct.CLTR_INICIO_VIGENCIA AND COALESCE(ct.CLTR_FIM_VIGENCIA, ?)
              AND ? BETWEEN tt.TRTR_INICIO_VIGENCIA AND COALESCE(tt.TRTR_FIM_VIGENCIA, ?)
              AND ? BETWEEN st.SITR_INICIO_VIGENCIA AND COALESCE(st.SITR_FIM_VIGENCIA, ?)
            ORDER BY ct.CLTR_CD
            """,
            (cst, *siglas, d, d, d, d, d, d, d, d, d, d, d, d),
        )

    def tratamento_cbs_ibs(
        self, codigo: str | None, data: date
    ) -> list[tuple[Any, ...]]:
        d = _data_str(data)
        return self._exec(
            """
            SELECT ct.CLTR_ID, ct.CLTR_CD, ct.CLTR_DESCRICAO, ct.CLTR_TIPO_ALIQUOTA,
                   ct.CLTR_NOMENCLATURA, tt.TRTR_DESCRICAO,
                   tt.TRTR_IN_INCOMPATIVEL_COM_SUSPENSAO, tt.TRTR_IN_EXIGE_GRUPO_DESONERACAO,
                   st.SITR_IND_GRED,
                   ct.CLTR_IN_APROPRIACAO_CREDITOS_ADQUIRENTES_CBS,
                   ct.CLTR_IN_APROPRIACAO_CREDITOS_ADQUIRENTES_IBS,
                   ct.CLTR_IN_CREDITO_PRESUMIDO_FORNECEDOR,
                   ct.CLTR_IN_CREDITO_PRESUMIDO_ADQUIRENTE,
                   ct.CLTR_CREDITO_OPERACAO_ANTECEDENTE,
                   pr_cbs.PERE_VALOR, pr_ibsuf.PERE_VALOR, pr_ibsmun.PERE_VALOR,
                   st.SITR_IND_GDIF, ct.CLTR_DATA_ATUALIZACAO, ct.CLTR_TPRBSN
            FROM TRATAMENTO_CLASSIFICACAO tc
            JOIN CLASSIFICACAO_TRIBUTARIA ct ON tc.TRCL_CLTR_ID = ct.CLTR_ID
            JOIN SITUACAO_TRIBUTARIA st ON st.SITR_ID = ct.CLTR_SITR_ID
            JOIN TRATAMENTO_TRIBUTARIO tt ON tt.TRTR_ID = tc.TRCL_TRTR_ID
            JOIN TRIBUTO_SITUACAO_TRIBUTARIA tst ON tst.TRST_SITR_ID = ct.CLTR_SITR_ID
            LEFT JOIN PERCENTUAL_REDUCAO pr_cbs ON pr_cbs.PERE_CLTR_ID = ct.CLTR_ID
              AND pr_cbs.PERE_TBTO_ID = 2
              AND ? BETWEEN pr_cbs.PERE_INICIO_VIGENCIA AND COALESCE(pr_cbs.PERE_FIM_VIGENCIA, ?)
            LEFT JOIN PERCENTUAL_REDUCAO pr_ibsuf ON pr_ibsuf.PERE_CLTR_ID = ct.CLTR_ID
              AND pr_ibsuf.PERE_TBTO_ID = 3
              AND ? BETWEEN pr_ibsuf.PERE_INICIO_VIGENCIA AND COALESCE(pr_ibsuf.PERE_FIM_VIGENCIA, ?)
            LEFT JOIN PERCENTUAL_REDUCAO pr_ibsmun ON pr_ibsmun.PERE_CLTR_ID = ct.CLTR_ID
              AND pr_ibsmun.PERE_TBTO_ID = 4
              AND ? BETWEEN pr_ibsmun.PERE_INICIO_VIGENCIA AND COALESCE(pr_ibsmun.PERE_FIM_VIGENCIA, ?)
            WHERE ? BETWEEN tc.TRCL_INICIO_VIGENCIA AND COALESCE(tc.TRCL_FIM_VIGENCIA, ?)
              AND ? BETWEEN ct.CLTR_INICIO_VIGENCIA AND COALESCE(ct.CLTR_FIM_VIGENCIA, ?)
              AND ? BETWEEN tt.TRTR_INICIO_VIGENCIA AND COALESCE(tt.TRTR_FIM_VIGENCIA, ?)
              AND ? BETWEEN tst.TRST_INICIO_VIGENCIA AND COALESCE(tst.TRST_FIM_VIGENCIA, ?)
              AND tst.TRST_TBTO_ID = 2
              AND (? IS NULL OR ct.CLTR_CD = ?)
            ORDER BY ct.CLTR_CD
            """,
            (d, d, d, d, d, d, d, d, d, d, d, d, d, d, codigo, codigo),
        )

    def tratamento_is(
        self, codigo: str | None, data: date
    ) -> list[tuple[Any, ...]]:
        d = _data_str(data)
        return self._exec(
            """
            SELECT ct.CLTR_ID, ct.CLTR_CD, ct.CLTR_DESCRICAO, ct.CLTR_TIPO_ALIQUOTA,
                   ct.CLTR_NOMENCLATURA, tt.TRTR_DESCRICAO,
                   tt.TRTR_IN_INCOMPATIVEL_COM_SUSPENSAO, tt.TRTR_IN_EXIGE_GRUPO_DESONERACAO,
                   st.SITR_IND_GRED, tt.TRTR_IN_POSSUI_PERCENTUAL_REDUCAO,
                   st.SITR_IND_GDIF, ct.CLTR_DATA_ATUALIZACAO
            FROM TRATAMENTO_CLASSIFICACAO tc
            JOIN CLASSIFICACAO_TRIBUTARIA ct ON tc.TRCL_CLTR_ID = ct.CLTR_ID
            JOIN SITUACAO_TRIBUTARIA st ON st.SITR_ID = ct.CLTR_SITR_ID
            JOIN TRATAMENTO_TRIBUTARIO tt ON tt.TRTR_ID = tc.TRCL_TRTR_ID
            JOIN TRIBUTO_SITUACAO_TRIBUTARIA tst ON tst.TRST_SITR_ID = ct.CLTR_SITR_ID
            WHERE ? BETWEEN tc.TRCL_INICIO_VIGENCIA AND COALESCE(tc.TRCL_FIM_VIGENCIA, ?)
              AND ? BETWEEN ct.CLTR_INICIO_VIGENCIA AND COALESCE(ct.CLTR_FIM_VIGENCIA, ?)
              AND ? BETWEEN tt.TRTR_INICIO_VIGENCIA AND COALESCE(tt.TRTR_FIM_VIGENCIA, ?)
              AND ? BETWEEN tst.TRST_INICIO_VIGENCIA AND COALESCE(tst.TRST_FIM_VIGENCIA, ?)
              AND ? BETWEEN st.SITR_INICIO_VIGENCIA AND COALESCE(st.SITR_FIM_VIGENCIA, ?)
              AND tst.TRST_TBTO_ID = 1
              AND (? IS NULL OR ct.CLTR_CD = ?)
            ORDER BY ct.CLTR_CD
            """,
            (d, d, d, d, d, d, d, d, d, d, codigo, codigo),
        )

    def tipos_dfe_classificacao(
        self, id_classificacao: int, data: date
    ) -> list[tuple[Any, ...]]:
        d = _data_str(data)
        return self._exec(
            """
            SELECT td.TPDF_TIPO, td.TPDF_SIGLA, td.TPDF_DESCRICAO
            FROM TIPO_DFE_CLASSIFICACAO tdc
            JOIN TIPO_DFE td ON tdc.TDCL_TPDF_ID = td.TPDF_ID
            WHERE tdc.TDCL_CLTR_ID = ?
              AND tdc.TDCL_INICIO_VIGENCIA <= ?
              AND (tdc.TDCL_FIM_VIGENCIA IS NULL OR tdc.TDCL_FIM_VIGENCIA >= ?)
            """,
            (id_classificacao, d, d),
        )

    def existe_ncm(self, ncm: str, data: date) -> bool:
        d = _data_str(data)
        return bool(
            self._scalar(
                """
                SELECT EXISTS (
                    SELECT 1 FROM NCM n
                    WHERE n.NCM_CD = ?
                      AND ? BETWEEN n.NCM_INICIO_VIGENCIA AND COALESCE(n.NCM_FIM_VIGENCIA, ?)
                )
                """,
                (ncm, d, d),
            )
        )

    def descricao_ncm(self, ncm: str, limite: int, data: date) -> str | None:
        d = _data_str(data)
        row = self._one(
            """
            SELECT TRIM(TRIM(n.NCM_DESCRICAO, ' -'), ' ')
            FROM NCM n
            WHERE n.NCM_CD = SUBSTR(?, 1, ?)
              AND ? BETWEEN n.NCM_INICIO_VIGENCIA AND COALESCE(n.NCM_FIM_VIGENCIA, ?)
            """,
            (ncm, limite, d, d),
        )
        return row[0] if row else None

    def aliquota_ad_valorem_produto(
        self, ncm: str, id_tributo: int, data: date
    ) -> tuple[bool, Decimal | None]:
        d = _data_str(data)
        row = self._one(
            """
            SELECT av.AADV_VALOR
            FROM ALIQUOTA_AD_VALOREM_PRODUTO a
            JOIN ALIQUOTA_AD_VALOREM av ON a.AAVP_AADV_ID = av.AADV_ID
            WHERE EXISTS (SELECT 1 FROM NCM n WHERE n.NCM_CD = ?)
              AND a.AAVP_NCM_CD = SUBSTR(?, 1, LENGTH(a.AAVP_NCM_CD))
              AND av.AADV_TBTO_ID = ?
              AND ? BETWEEN a.AAVP_INICIO_VIGENCIA AND COALESCE(a.AAVP_FIM_VIGENCIA, ?)
              AND NOT EXISTS (
                SELECT 1 FROM EXCECAO_AD_VALOREM_PRODUTO e
                WHERE e.EAVP_NCM_CD = SUBSTR(?, 1, LENGTH(e.EAVP_NCM_CD))
                  AND e.EAVP_AAVP_ID = a.AAVP_ID
                  AND ? BETWEEN e.EAVP_INICIO_VIGENCIA AND COALESCE(e.EAVP_FIM_VIGENCIA, ?)
              )
              AND NOT EXISTS (
                SELECT 1 FROM EXCECAO_AD_VALOREM_PRODUTO e
                WHERE e.EAVP_NCM_CD = SUBSTR(a.AAVP_NCM_CD, 1, LENGTH(e.EAVP_NCM_CD))
                  AND e.EAVP_AAVP_ID = a.AAVP_ID
                  AND ? BETWEEN e.EAVP_INICIO_VIGENCIA AND COALESCE(e.EAVP_FIM_VIGENCIA, ?)
              )
            ORDER BY LENGTH(a.AAVP_NCM_CD) DESC
            LIMIT 1
            """,
            (ncm, ncm, id_tributo, d, d, ncm, d, d, d, d),
        )
        if not row:
            return False, None
        return True, convert_to_big_decimal(row[0])

    def aliquota_ad_rem_produto(
        self, ncm: str, id_tributo: int, data: date
    ) -> tuple[bool, Decimal | None, str | None]:
        d = _data_str(data)
        row = self._one(
            """
            SELECT ar.AARE_VALOR, um.UNMD_SIGLA
            FROM ALIQUOTA_AD_REM_PRODUTO a
            JOIN ALIQUOTA_AD_REM ar ON a.AARP_AARE_ID = ar.AARE_ID
            JOIN UNIDADE_MEDIDA um ON ar.AARE_UNMD_ID = um.UNMD_ID
            WHERE EXISTS (SELECT 1 FROM NCM n WHERE n.NCM_CD = ?)
              AND ar.AARE_TBTO_ID = ?
              AND a.AARP_NCM_CD = SUBSTR(?, 1, LENGTH(a.AARP_NCM_CD))
              AND ? BETWEEN a.AARP_INICIO_VIGENCIA AND COALESCE(a.AARP_FIM_VIGENCIA, ?)
              AND NOT EXISTS (
                SELECT 1 FROM EXCECAO_AD_REM_PRODUTO e
                WHERE e.EARP_NCM_CD = SUBSTR(?, 1, LENGTH(e.EARP_NCM_CD))
                  AND e.EARP_AARP_ID = a.AARP_ID
                  AND ? BETWEEN e.EARP_INICIO_VIGENCIA AND COALESCE(e.EARP_FIM_VIGENCIA, ?)
              )
              AND NOT EXISTS (
                SELECT 1 FROM EXCECAO_AD_REM_PRODUTO e
                WHERE e.EARP_NCM_CD = SUBSTR(a.AARP_NCM_CD, 1, LENGTH(e.EARP_NCM_CD))
                  AND e.EARP_AARP_ID = a.AARP_ID
                  AND ? BETWEEN e.EARP_INICIO_VIGENCIA AND COALESCE(e.EARP_FIM_VIGENCIA, ?)
              )
            ORDER BY LENGTH(a.AARP_NCM_CD) DESC
            LIMIT 1
            """,
            (ncm, id_tributo, ncm, d, d, ncm, d, d, d, d),
        )
        if not row:
            return False, None, None
        return True, convert_to_big_decimal(row[0]), row[1]

    def existe_nbs(self, nbs: str, data: date) -> bool:
        d = _data_str(data)
        return bool(
            self._scalar(
                """
                SELECT EXISTS (
                    SELECT 1 FROM NBS n
                    WHERE n.NBS_CD = ?
                      AND ? BETWEEN n.NBS_INICIO_VIGENCIA AND COALESCE(n.NBS_FIM_VIGENCIA, ?)
                )
                """,
                (nbs, d, d),
            )
        )

    def descricao_nbs(self, nbs: str, limite: int, data: date) -> str | None:
        d = _data_str(data)
        row = self._one(
            """
            SELECT TRIM(TRIM(n.NBS_DESCRICAO, ' -'), ' ')
            FROM NBS n
            WHERE n.NBS_CD = SUBSTR(?, 1, ?)
              AND ? BETWEEN n.NBS_INICIO_VIGENCIA AND COALESCE(n.NBS_FIM_VIGENCIA, ?)
            """,
            (nbs, limite, d, d),
        )
        return row[0] if row else None

    def listar_nbs(self, data: date) -> list[tuple[str, str]]:
        d = _data_str(data)
        return self._exec(
            """
            SELECT n.NBS_CD, n.NBS_DESCRICAO
            FROM NBS n
            WHERE ? BETWEEN n.NBS_INICIO_VIGENCIA AND COALESCE(n.NBS_FIM_VIGENCIA, ?)
              AND LENGTH(n.NBS_CD) = 9
            ORDER BY n.NBS_CD
            """,
            (d, d),
        )

    def aliquota_ad_valorem_servico(
        self, nbs: str, id_tributo: int, data: date
    ) -> tuple[bool, Decimal | None]:
        d = _data_str(data)
        row = self._one(
            """
            SELECT av.AADV_VALOR
            FROM ALIQUOTA_AD_VALOREM_SERVICO a
            JOIN ALIQUOTA_AD_VALOREM av ON a.AAVS_AADV_ID = av.AADV_ID
            WHERE EXISTS (SELECT 1 FROM NBS n WHERE n.NBS_CD = ?)
              AND a.AAVS_NBS_CD = SUBSTR(?, 1, LENGTH(a.AAVS_NBS_CD))
              AND av.AADV_TBTO_ID = ?
              AND ? BETWEEN a.AAVS_INICIO_VIGENCIA AND COALESCE(a.AAVS_FIM_VIGENCIA, ?)
              AND NOT EXISTS (
                SELECT 1 FROM EXCECAO_AD_VALOREM_SERVICO e
                WHERE e.EAVS_NBS_CD = SUBSTR(?, 1, LENGTH(e.EAVS_NBS_CD))
                  AND e.EAVS_AAVS_ID = a.AAVS_ID
                  AND ? BETWEEN e.EAVS_INICIO_VIGENCIA AND COALESCE(e.EAVS_FIM_VIGENCIA, ?)
              )
              AND NOT EXISTS (
                SELECT 1 FROM EXCECAO_AD_VALOREM_SERVICO e
                WHERE e.EAVS_NBS_CD = SUBSTR(a.AAVS_NBS_CD, 1, LENGTH(e.EAVS_NBS_CD))
                  AND e.EAVS_AAVS_ID = a.AAVS_ID
                  AND ? BETWEEN e.EAVS_INICIO_VIGENCIA AND COALESCE(e.EAVS_FIM_VIGENCIA, ?)
              )
            ORDER BY LENGTH(a.AAVS_NBS_CD) DESC
            LIMIT 1
            """,
            (nbs, nbs, id_tributo, d, d, nbs, d, d, d, d),
        )
        if not row:
            return False, None
        return True, convert_to_big_decimal(row[0])

    def fundamentacoes(self, data: date) -> list[tuple[Any, ...]]:
        d = _data_str(data)
        return self._exec(
            """
            SELECT ct.CLTR_CD, ct.CLTR_DESCRICAO, st.SITR_CD, st.SITR_DESCRICAO,
                   st.SITR_ID, fl.FDLG_TEXTO, fl.FDLG_TEXTO_CURTO, fl.FDLG_REFERENCIA_NORMATIVA
            FROM FUNDAMENTACAO_CLASSIFICACAO fc
            JOIN CLASSIFICACAO_TRIBUTARIA ct ON fc.FDCL_CLTR_ID = ct.CLTR_ID
            JOIN SITUACAO_TRIBUTARIA st ON ct.CLTR_SITR_ID = st.SITR_ID
            JOIN FUNDAMENTACAO_LEGAL fl ON fc.FDCL_FDLG_ID = fl.FDLG_ID
            WHERE ? BETWEEN fc.FDCL_INICIO_VIGENCIA AND COALESCE(fc.FDCL_FIM_VIGENCIA, ?)
            ORDER BY ct.CLTR_CD
            """,
            (d, d),
        )

    def tributo_por_situacao(self, id_situacao: int, data: date) -> int | None:
        d = _data_str(data)
        val = self._scalar(
            """
            SELECT t.TRST_TBTO_ID
            FROM TRIBUTO_SITUACAO_TRIBUTARIA t
            WHERE t.TRST_SITR_ID = ?
              AND ? BETWEEN t.TRST_INICIO_VIGENCIA AND COALESCE(t.TRST_FIM_VIGENCIA, ?)
            LIMIT 1
            """,
            (id_situacao, d, d),
        )
        return int(val) if val is not None else None

    def classificacao_cbs_ibs(self, codigo: str, data: date) -> tuple[int, str, str] | None:
        d = _data_str(data)
        row = self._one(
            """
            SELECT ct.CLTR_ID, ct.CLTR_CD, ct.CLTR_NOMENCLATURA
            FROM CLASSIFICACAO_TRIBUTARIA ct
            JOIN SITUACAO_TRIBUTARIA st ON ct.CLTR_SITR_ID = st.SITR_ID
            JOIN TRIBUTO_SITUACAO_TRIBUTARIA tst ON tst.TRST_SITR_ID = st.SITR_ID
            JOIN TRIBUTO tb ON tst.TRST_TBTO_ID = tb.TBTO_ID
            WHERE ct.CLTR_CD = ?
              AND tb.TBTO_ID = 2
              AND ? BETWEEN ct.CLTR_INICIO_VIGENCIA AND COALESCE(ct.CLTR_FIM_VIGENCIA, ?)
              AND ? BETWEEN st.SITR_INICIO_VIGENCIA AND COALESCE(st.SITR_FIM_VIGENCIA, ?)
              AND ? BETWEEN tst.TRST_INICIO_VIGENCIA AND COALESCE(tst.TRST_FIM_VIGENCIA, ?)
              AND ? BETWEEN tb.TBTO_INICIO_VIGENCIA AND COALESCE(tb.TBTO_FIM_VIGENCIA, ?)
            """,
            (codigo, d, d, d, d, d, d, d, d),
        )
        if not row:
            return None
        return int(row[0]), str(row[1]), str(row[2])

    def tem_ncm_aplicavel(self, id_cltr: int, data: date) -> bool:
        d = _data_str(data)
        return bool(
            self._scalar(
                """
                SELECT EXISTS (
                    SELECT 1 FROM NCM_APLICAVEL n
                    WHERE n.NCMA_CLTR_ID = ?
                      AND ? BETWEEN n.NCMA_INICIO_VIGENCIA AND COALESCE(n.NCMA_FIM_VIGENCIA, ?)
                )
                """,
                (id_cltr, d, d),
            )
        )

    def tem_nbs_aplicavel(self, id_cltr: int, data: date) -> bool:
        d = _data_str(data)
        return bool(
            self._scalar(
                """
                SELECT EXISTS (
                    SELECT 1 FROM NBS_APLICAVEL n
                    WHERE n.NBSA_CLTR_ID = ?
                      AND ? BETWEEN n.NBSA_INICIO_VIGENCIA AND COALESCE(n.NBSA_FIM_VIGENCIA, ?)
                )
                """,
                (id_cltr, d, d),
            )
        )

    def tem_ncm_aplicavel_vinculo(self, ncm: str, id_cltr: int, data: date) -> bool:
        d = _data_str(data)
        return bool(
            self._scalar(
                """
                SELECT EXISTS (
                    SELECT 1 FROM NCM_APLICAVEL n
                    WHERE n.NCMA_NCM_CD = SUBSTR(?, 1, LENGTH(n.NCMA_NCM_CD))
                      AND n.NCMA_CLTR_ID = ?
                      AND ? BETWEEN n.NCMA_INICIO_VIGENCIA AND COALESCE(n.NCMA_FIM_VIGENCIA, ?)
                )
                """,
                (ncm, id_cltr, d, d),
            )
        )

    def tem_excecao_ncm(self, ncm: str, id_cltr: int, data: date) -> bool:
        d = _data_str(data)
        return bool(
            self._scalar(
                """
                SELECT EXISTS (
                    SELECT 1 FROM EXCECAO_NCM_APLICAVEL e
                    JOIN NCM_APLICAVEL n ON e.ENCM_NCMA_ID = n.NCMA_ID
                    WHERE n.NCMA_NCM_CD = SUBSTR(?, 1, LENGTH(n.NCMA_NCM_CD))
                      AND e.ENCM_NCM_CD = SUBSTR(?, 1, LENGTH(e.ENCM_NCM_CD))
                      AND n.NCMA_CLTR_ID = ?
                      AND ? BETWEEN e.ENCM_INICIO_VIGENCIA AND COALESCE(e.ENCM_FIM_VIGENCIA, ?)
                )
                """,
                (ncm, ncm, id_cltr, d, d),
            )
        )

    def tem_ncm_sem_excecao(self, ncm: str, id_cltr: int, data: date) -> bool:
        d = _data_str(data)
        return bool(
            self._scalar(
                """
                SELECT EXISTS (
                    SELECT 1 FROM NCM_APLICAVEL n
                    LEFT JOIN EXCECAO_NCM_APLICAVEL e ON e.ENCM_NCMA_ID = n.NCMA_ID
                    WHERE n.NCMA_NCM_CD = SUBSTR(?, 1, LENGTH(n.NCMA_NCM_CD))
                      AND n.NCMA_CLTR_ID = ?
                      AND ? BETWEEN n.NCMA_INICIO_VIGENCIA AND COALESCE(n.NCMA_FIM_VIGENCIA, ?)
                      AND (e.ENCM_ID IS NULL OR ? NOT BETWEEN e.ENCM_INICIO_VIGENCIA AND COALESCE(e.ENCM_FIM_VIGENCIA, ?))
                )
                """,
                (ncm, id_cltr, d, d, d, d),
            )
        )

    def tem_nbs_vinculo(self, nbs: str, id_cltr: int, data: date) -> bool:
        d = _data_str(data)
        return bool(
            self._scalar(
                """
                SELECT EXISTS (
                    SELECT 1 FROM NBS_APLICAVEL n
                    WHERE n.NBSA_NBS_CD = SUBSTR(?, 1, LENGTH(n.NBSA_NBS_CD))
                      AND n.NBSA_CLTR_ID = ?
                      AND ? BETWEEN n.NBSA_INICIO_VIGENCIA AND COALESCE(n.NBSA_FIM_VIGENCIA, ?)
                )
                """,
                (nbs, id_cltr, d, d),
            )
        )

    def tem_excecao_nbs(self, nbs: str, id_cltr: int, data: date) -> bool:
        d = _data_str(data)
        return bool(
            self._scalar(
                """
                SELECT EXISTS (
                    SELECT 1 FROM EXCECAO_NBS_APLICAVEL e
                    JOIN NBS_APLICAVEL n ON e.ENBS_NBSA_ID = n.NBSA_ID
                    WHERE n.NBSA_NBS_CD = SUBSTR(?, 1, LENGTH(n.NBSA_NBS_CD))
                      AND e.ENBS_NBS_CD = SUBSTR(?, 1, LENGTH(e.ENBS_NBS_CD))
                      AND n.NBSA_CLTR_ID = ?
                      AND ? BETWEEN e.ENBS_INICIO_VIGENCIA AND COALESCE(e.ENBS_FIM_VIGENCIA, ?)
                )
                """,
                (nbs, nbs, id_cltr, d, d),
            )
        )

    def tem_nbs_sem_excecao(self, nbs: str, id_cltr: int, data: date) -> bool:
        d = _data_str(data)
        return bool(
            self._scalar(
                """
                SELECT EXISTS (
                    SELECT 1 FROM NBS_APLICAVEL n
                    LEFT JOIN EXCECAO_NBS_APLICAVEL e ON e.ENBS_NBSA_ID = n.NBSA_ID
                    WHERE n.NBSA_NBS_CD = SUBSTR(?, 1, LENGTH(n.NBSA_NBS_CD))
                      AND n.NBSA_CLTR_ID = ?
                      AND ? BETWEEN n.NBSA_INICIO_VIGENCIA AND COALESCE(n.NBSA_FIM_VIGENCIA, ?)
                      AND (e.ENBS_ID IS NULL OR ? NOT BETWEEN e.ENBS_INICIO_VIGENCIA AND COALESCE(e.ENBS_FIM_VIGENCIA, ?))
                )
                """,
                (nbs, id_cltr, d, d, d, d),
            )
        )

    def buscar_aliquota_padrao(
        self,
        id_tributo: int,
        codigo_uf: int | None,
        codigo_municipio: int | None,
        data: date,
    ) -> tuple[Decimal, Decimal | None, str | None] | None:
        d = _data_str(data)
        row = self._one(
            """
            SELECT r.ALRE_VALOR, p.ALPA_VALOR, p.ALPA_FORMA_APLICACAO
            FROM ALIQUOTA_REFERENCIA r
            LEFT JOIN ALIQUOTA_PADRAO p ON p.ALPA_ALRE_ID = r.ALRE_ID
              AND (
                (? IS NULL AND p.ALPA_MUNI_CD IS NULL) OR
                (? IS NOT NULL AND p.ALPA_MUNI_CD = ?)
              )
              AND (
                (? IS NULL AND p.ALPA_UF_CD IS NULL) OR
                (? IS NOT NULL AND p.ALPA_UF_CD = ?)
              )
              AND p.ALPA_INICIO_VIGENCIA <= ?
              AND (p.ALPA_FIM_VIGENCIA IS NULL OR p.ALPA_FIM_VIGENCIA >= ?)
            WHERE r.ALRE_TBTO_ID = ?
              AND r.ALRE_INICIO_VIGENCIA <= ?
              AND (r.ALRE_FIM_VIGENCIA IS NULL OR r.ALRE_FIM_VIGENCIA >= ?)
            LIMIT 1
            """,
            (
                codigo_municipio,
                codigo_municipio,
                codigo_municipio,
                codigo_uf,
                codigo_uf,
                codigo_uf,
                d,
                d,
                id_tributo,
                d,
                d,
            ),
        )
        if not row:
            return None
        ref = convert_to_big_decimal(row[0])
        pad = convert_to_big_decimal(row[1]) if row[1] is not None else None
        forma = row[2]
        if ref is None:
            return None
        return ref, pad, forma

    def ncms_vigentes(self, data: date) -> list[tuple[str, str]]:
        d = _data_str(data)
        return self._exec(
            """
            SELECT DISTINCT n.NCM_CD, n.NCM_DESCRICAO
            FROM NCM n
            WHERE ? BETWEEN n.NCM_INICIO_VIGENCIA AND COALESCE(n.NCM_FIM_VIGENCIA, ?)
              AND LENGTH(n.NCM_CD) = 8
            ORDER BY n.NCM_CD
            """,
            (d, d),
        )

    def redutores(self) -> list[tuple[Any, ...]]:
        return self._exec(
            """
            SELECT RCGO_VALOR, RCGO_INICIO_VIGENCIA, RCGO_FIM_VIGENCIA
            FROM REDUTOR_COMPRA_GOVERNAMENTAL
            ORDER BY RCGO_INICIO_VIGENCIA
            """
        )

    def transferencias_cbs(self) -> list[tuple[Any, ...]]:
        return self._exec(
            """
            SELECT TCEG_VALOR, TCEG_INICIO_VIGENCIA, TCEG_FIM_VIGENCIA
            FROM TRANSFERENCIA_CBS_ENTE_GOV
            ORDER BY TCEG_INICIO_VIGENCIA
            """
        )

    def codigos_por_atores(
        self,
        data: date,
        fornecedor: int | None,
        adquirente: int | None,
        sigla_dfe: str | None,
    ) -> list[str]:
        d = _data_str(data)
        return [
            str(r[0])
            for r in self._exec(
                """
                SELECT ct.CLTR_CD
                FROM CLASSIFICACAO_TRIBUTARIA ct
                WHERE ? BETWEEN ct.CLTR_INICIO_VIGENCIA AND COALESCE(ct.CLTR_FIM_VIGENCIA, ?)
                  AND ( ? IS NULL
                        OR NOT EXISTS (SELECT 1 FROM ATOR_CLASSIFICACAO ac
                                        WHERE ac.ATCL_CLTR_ID = ct.CLTR_ID
                                          AND ac.ATCL_IN_PAPEL = 'Fornecedor'
                                          AND ? BETWEEN ac.ATCL_INICIO_VIGENCIA
                                                        AND COALESCE(ac.ATCL_FIM_VIGENCIA, ?))
                        OR EXISTS (SELECT 1 FROM ATOR_CLASSIFICACAO ac
                                    WHERE ac.ATCL_CLTR_ID = ct.CLTR_ID
                                      AND ac.ATCL_IN_PAPEL = 'Fornecedor'
                                      AND ac.ATCL_ATOR_ID = ?
                                      AND ? BETWEEN ac.ATCL_INICIO_VIGENCIA
                                                    AND COALESCE(ac.ATCL_FIM_VIGENCIA, ?)) )
                  AND ( ? IS NULL
                        OR NOT EXISTS (SELECT 1 FROM ATOR_CLASSIFICACAO ac
                                        WHERE ac.ATCL_CLTR_ID = ct.CLTR_ID
                                          AND ac.ATCL_IN_PAPEL = 'Adquirente'
                                          AND ? BETWEEN ac.ATCL_INICIO_VIGENCIA
                                                        AND COALESCE(ac.ATCL_FIM_VIGENCIA, ?))
                        OR EXISTS (SELECT 1 FROM ATOR_CLASSIFICACAO ac
                                    WHERE ac.ATCL_CLTR_ID = ct.CLTR_ID
                                      AND ac.ATCL_IN_PAPEL = 'Adquirente'
                                      AND ac.ATCL_ATOR_ID = ?
                                      AND ? BETWEEN ac.ATCL_INICIO_VIGENCIA
                                                    AND COALESCE(ac.ATCL_FIM_VIGENCIA, ?)) )
                  AND ( ? IS NULL
                        OR EXISTS (SELECT 1 FROM TIPO_DFE_CLASSIFICACAO tdcl
                                    JOIN TIPO_DFE td ON tdcl.TDCL_TPDF_ID = td.TPDF_ID
                                    WHERE tdcl.TDCL_CLTR_ID = ct.CLTR_ID
                                      AND UPPER(REPLACE(REPLACE(REPLACE(td.TPDF_SIGLA, ' ', ''), '-', ''), '_', '')) = ?
                                      AND ? BETWEEN tdcl.TDCL_INICIO_VIGENCIA
                                                AND COALESCE(tdcl.TDCL_FIM_VIGENCIA, ?)) )
                """,
                (
                    d,
                    d,
                    fornecedor,
                    d,
                    d,
                    fornecedor,
                    d,
                    d,
                    adquirente,
                    d,
                    d,
                    adquirente,
                    d,
                    d,
                    sigla_dfe,
                    sigla_dfe,
                    d,
                    d,
                ),
            )
        ]

    def validade_dfe_classificacao(
        self, codigo: str, data: date
    ) -> tuple[Any, ...] | None:
        d = _data_str(data)
        return self._one(
            """
            SELECT ct.CLTR_ID, ct.CLTR_NOMENCLATURA,
                   tt.TRTR_IN_EXIGE_GRUPO_DESONERACAO, st.SITR_IND_GDIF,
                   ct.CLTR_IND_GCREDPRESOPER, st.SITR_IND_GIBSCBS
            FROM TRATAMENTO_CLASSIFICACAO tc
            INNER JOIN CLASSIFICACAO_TRIBUTARIA ct ON tc.TRCL_CLTR_ID = ct.CLTR_ID
              AND ? BETWEEN ct.CLTR_INICIO_VIGENCIA AND COALESCE(ct.CLTR_FIM_VIGENCIA, ?)
            INNER JOIN SITUACAO_TRIBUTARIA st ON st.SITR_ID = ct.CLTR_SITR_ID
              AND ? BETWEEN st.SITR_INICIO_VIGENCIA AND COALESCE(st.SITR_FIM_VIGENCIA, ?)
            INNER JOIN TRATAMENTO_TRIBUTARIO tt ON tt.TRTR_ID = tc.TRCL_TRTR_ID
              AND ? BETWEEN tt.TRTR_INICIO_VIGENCIA AND COALESCE(tt.TRTR_FIM_VIGENCIA, ?)
            INNER JOIN TRIBUTO_SITUACAO_TRIBUTARIA tst ON tst.TRST_SITR_ID = st.SITR_ID
              AND tst.TRST_TBTO_ID = 2
              AND ? BETWEEN tst.TRST_INICIO_VIGENCIA AND COALESCE(tst.TRST_FIM_VIGENCIA, ?)
            WHERE ct.CLTR_CD = ?
              AND ? BETWEEN tc.TRCL_INICIO_VIGENCIA AND COALESCE(tc.TRCL_FIM_VIGENCIA, ?)
            LIMIT 1
            """,
            (d, d, d, d, d, d, d, d, codigo, d, d),
        )

    def csts_cbs_ibs(
        self, sigla_normalizada: str | None, data: date
    ) -> list[tuple[Any, ...]]:
        d = _data_str(data)
        if sigla_normalizada is None:
            return self._exec(
                """
                SELECT DISTINCT st.SITR_ID, st.SITR_CD, st.SITR_DESCRICAO,
                       ct.CLTR_CD, ct.CLTR_DESCRICAO
                FROM CLASSIFICACAO_TRIBUTARIA ct
                JOIN SITUACAO_TRIBUTARIA st ON ct.CLTR_SITR_ID = st.SITR_ID
                JOIN TRIBUTO_SITUACAO_TRIBUTARIA tst ON tst.TRST_SITR_ID = st.SITR_ID
                  AND tst.TRST_TBTO_ID != 1
                  AND ? BETWEEN tst.TRST_INICIO_VIGENCIA AND COALESCE(tst.TRST_FIM_VIGENCIA, ?)
                ORDER BY st.SITR_CD ASC, ct.CLTR_CD ASC
                """,
                (d, d),
            )
        return self._exec(
            """
            SELECT DISTINCT st.SITR_ID, st.SITR_CD, st.SITR_DESCRICAO,
                   ct.CLTR_CD, ct.CLTR_DESCRICAO
            FROM TIPO_DFE_CLASSIFICACAO tdcl
            JOIN TIPO_DFE td ON tdcl.TDCL_TPDF_ID = td.TPDF_ID
            JOIN CLASSIFICACAO_TRIBUTARIA ct ON tdcl.TDCL_CLTR_ID = ct.CLTR_ID
            JOIN SITUACAO_TRIBUTARIA st ON ct.CLTR_SITR_ID = st.SITR_ID
            JOIN TRIBUTO_SITUACAO_TRIBUTARIA tst ON tst.TRST_SITR_ID = st.SITR_ID
              AND tst.TRST_TBTO_ID != 1
              AND ? BETWEEN tst.TRST_INICIO_VIGENCIA AND COALESCE(tst.TRST_FIM_VIGENCIA, ?)
            WHERE UPPER(REPLACE(REPLACE(REPLACE(td.TPDF_SIGLA, ' ', ''), '-', ''), '_', '')) = ?
              AND ? BETWEEN tdcl.TDCL_INICIO_VIGENCIA AND COALESCE(tdcl.TDCL_FIM_VIGENCIA, ?)
            ORDER BY st.SITR_CD ASC, ct.CLTR_CD ASC
            """,
            (d, d, sigla_normalizada, d, d),
        )

    def csts_is(self, data: date) -> list[tuple[Any, ...]]:
        d = _data_str(data)
        return self._exec(
            """
            SELECT DISTINCT st.SITR_ID, st.SITR_CD, st.SITR_DESCRICAO,
                   ct.CLTR_CD, ct.CLTR_DESCRICAO
            FROM CLASSIFICACAO_TRIBUTARIA ct
            JOIN SITUACAO_TRIBUTARIA st ON ct.CLTR_SITR_ID = st.SITR_ID
            JOIN TRIBUTO_SITUACAO_TRIBUTARIA tst ON tst.TRST_SITR_ID = st.SITR_ID
              AND tst.TRST_TBTO_ID = 1
              AND ? BETWEEN tst.TRST_INICIO_VIGENCIA AND COALESCE(tst.TRST_FIM_VIGENCIA, ?)
            ORDER BY st.SITR_CD ASC, ct.CLTR_CD ASC
            """,
            (d, d),
        )

    def tipos_dfe_agrupados(self, data: date) -> list[tuple[Any, ...]]:
        d = _data_str(data)
        return self._exec(
            """
            SELECT g.GRDF_ID, g.GRDF_DESCRICAO, td.TPDF_SIGLA, td.TPDF_DESCRICAO,
                   td.TPDF_TIPO, td.TPDF_B_POSSUI_TRATAMENTO_CALCULADORA,
                   td.TPDF_B_PERMITE_NCM_ZERO
            FROM TIPO_DFE td
            JOIN GRUPO_DFE g ON td.TPDF_GRDF_ID = g.GRDF_ID
            WHERE ? BETWEEN td.TPDF_INICIO_VIGENCIA AND COALESCE(td.TPDF_FIM_VIGENCIA, ?)
              AND ? BETWEEN g.GRDF_INICIO_VIGENCIA AND COALESCE(g.GRDF_FIM_VIGENCIA, ?)
            ORDER BY g.GRDF_ID ASC, td.TPDF_ID ASC
            """,
            (d, d, d, d),
        )

    def atores_agrupados(self, data: date, papel: str | None) -> list[tuple[Any, ...]]:
        d = _data_str(data)
        return self._exec(
            """
            SELECT g.GRAT_ID, g.GRAT_DESCRICAO, g.GRAT_ORDEM,
                   a.ATOR_ID, a.ATOR_DESCRICAO, a.ATOR_ORDEM
            FROM ATOR a
            JOIN GRUPO_ATOR g ON a.ATOR_GRAT_ID = g.GRAT_ID
            WHERE a.ATOR_INICIO_VIGENCIA <= ?
              AND (a.ATOR_FIM_VIGENCIA IS NULL OR a.ATOR_FIM_VIGENCIA >= ?)
              AND g.GRAT_INICIO_VIGENCIA <= ?
              AND (g.GRAT_FIM_VIGENCIA IS NULL OR g.GRAT_FIM_VIGENCIA >= ?)
              AND (
                  ? IS NULL OR EXISTS (
                      SELECT 1 FROM ATOR_CLASSIFICACAO ac
                      WHERE ac.ATCL_ATOR_ID = a.ATOR_ID
                        AND ac.ATCL_IN_PAPEL = ?
                        AND ac.ATCL_INICIO_VIGENCIA <= ?
                        AND (ac.ATCL_FIM_VIGENCIA IS NULL OR ac.ATCL_FIM_VIGENCIA >= ?)
                  )
              )
            ORDER BY g.GRAT_ORDEM ASC, a.ATOR_ORDEM ASC
            """,
            (d, d, d, d, papel, papel, d, d),
        )

    def listar_nbs_sem_vinculo(self, data: date) -> list[str]:
        d = _data_str(data)
        return [
            str(r[0])
            for r in self._exec(
                """
                SELECT ct.CLTR_CD
                FROM CLASSIFICACAO_TRIBUTARIA ct
                WHERE ct.CLTR_NOMENCLATURA LIKE '%NBS%'
                  AND ? BETWEEN ct.CLTR_INICIO_VIGENCIA AND COALESCE(ct.CLTR_FIM_VIGENCIA, ?)
                  AND ct.CLTR_ID NOT IN (
                    SELECT n.NBSA_CLTR_ID FROM NBS_APLICAVEL n
                    WHERE ? BETWEEN n.NBSA_INICIO_VIGENCIA AND COALESCE(n.NBSA_FIM_VIGENCIA, ?)
                  )
                """,
                (d, d, d, d),
            )
        ]

    def nbs_vinculadas(self, nbs: str, data: date) -> list[str]:
        d = _data_str(data)
        return [
            str(r[0])
            for r in self._exec(
                """
                SELECT ct.CLTR_CD
                FROM NBS_APLICAVEL n
                JOIN CLASSIFICACAO_TRIBUTARIA ct ON ct.CLTR_ID = n.NBSA_CLTR_ID
                LEFT JOIN EXCECAO_NBS_APLICAVEL e ON e.ENBS_NBSA_ID = n.NBSA_ID
                  AND ? BETWEEN e.ENBS_INICIO_VIGENCIA AND COALESCE(e.ENBS_FIM_VIGENCIA, ?)
                WHERE n.NBSA_NBS_CD = ?
                  AND ? BETWEEN n.NBSA_INICIO_VIGENCIA AND COALESCE(n.NBSA_FIM_VIGENCIA, ?)
                  AND ? BETWEEN ct.CLTR_INICIO_VIGENCIA AND COALESCE(ct.CLTR_FIM_VIGENCIA, ?)
                  AND e.ENBS_ID IS NULL
                """,
                (d, d, nbs, d, d, d, d),
            )
        ]

    def existe_vinculo_nbs_classificacao(self, id_cltr: int) -> bool:
        return bool(
            self._scalar(
                """
                SELECT CASE WHEN COUNT(*) > 0 THEN 1 ELSE 0 END
                FROM NBS_APLICAVEL n
                JOIN CLASSIFICACAO_TRIBUTARIA ct ON ct.CLTR_ID = n.NBSA_CLTR_ID
                WHERE ct.CLTR_ID = ?
                """,
                (id_cltr,),
            )
        )

    def nbs_aplicaveis_por_classificacao(
        self, id_cltr: int, data: date
    ) -> list[tuple[str, str]]:
        d = _data_str(data)
        return self._exec(
            """
            SELECT DISTINCT nbs.NBS_CD, nbs.NBS_DESCRICAO
            FROM NBS_APLICAVEL n
            JOIN NBS nbs ON nbs.NBS_CD = n.NBSA_NBS_CD
            LEFT JOIN EXCECAO_NBS_APLICAVEL e ON e.ENBS_NBSA_ID = n.NBSA_ID
              AND ? BETWEEN e.ENBS_INICIO_VIGENCIA AND COALESCE(e.ENBS_FIM_VIGENCIA, ?)
            JOIN CLASSIFICACAO_TRIBUTARIA ct ON ct.CLTR_ID = n.NBSA_CLTR_ID
            WHERE ct.CLTR_ID = ?
              AND ? BETWEEN n.NBSA_INICIO_VIGENCIA AND COALESCE(n.NBSA_FIM_VIGENCIA, ?)
              AND ? BETWEEN nbs.NBS_INICIO_VIGENCIA AND COALESCE(nbs.NBS_FIM_VIGENCIA, ?)
              AND ? BETWEEN ct.CLTR_INICIO_VIGENCIA AND COALESCE(ct.CLTR_FIM_VIGENCIA, ?)
              AND e.ENBS_ID IS NULL
              AND LENGTH(nbs.NBS_CD) = 9
            ORDER BY nbs.NBS_CD
            """,
            (d, d, id_cltr, d, d, d, d, d, d),
        )


class _AliquotaPadraoSqlite:
    def __init__(self, sql: _SqliteDadosAbertos) -> None:
        self._sql = sql

    def buscar_aliquota(
        self,
        id_tributo: int,
        codigo_uf: int | None,
        codigo_municipio: int | None,
        data: date,
    ) -> AliquotaResultado:
        row = self._sql.buscar_aliquota_padrao(
            id_tributo, codigo_uf, codigo_municipio, data
        )
        if row is None:
            raise AliquotaNaoEncontradaException()
        referencia, padrao, forma_nome = row
        forma = _forma_aplicacao(forma_nome)
        if padrao is None:
            return AliquotaResultado(referencia)
        if forma is None:
            raise AliquotaNaoEncontradaException()
        return AliquotaResultado(referencia, padrao, forma)


def _validar_ncm(ncm: str | None) -> None:
    if ncm is None:
        raise ValidacaoException("O campo NCM é obrigatório.")
    if not re.fullmatch(r"\d+", ncm):
        raise ValidacaoException("O campo NCM deve conter somente dígitos.")


def _validar_nbs(nbs: str | None) -> None:
    if nbs is None:
        raise ValidacaoException("O campo NBS é obrigatório.")
    if not re.fullmatch(r"\d+", nbs):
        raise ValidacaoException("O campo NBS deve conter somente dígitos.")


def _flag_sqlite(valor: Any, padrao: bool) -> bool:
    if isinstance(valor, bool):
        return valor
    if isinstance(valor, (int, float, Decimal)):
        return int(valor) != 0
    return padrao


class DadosAbertosService:
    def __init__(self, aliquota_padrao: BuscarAliquota | None = None) -> None:
        self._sql = _SqliteDadosAbertos()
        self._aliquota_padrao = aliquota_padrao or _AliquotaPadraoSqlite(self._sql)

    def consultar_ufs(self) -> list[UfDadosAbertos]:
        return [
            UfDadosAbertos(sigla=str(r[0]), nome=str(r[1]), codigo=int(r[2]))
            for r in self._sql.consultar_ufs()
        ]

    def consultar_municipios_por_sigla_uf(
        self, sigla_uf: str
    ) -> list[MunicipioDadosAbertos]:
        return [
            MunicipioDadosAbertos(codigo=int(r[0]), nome=str(r[1]))
            for r in self._sql.municipios_por_uf(sigla_uf)
        ]

    def consultar_situacoes_tributarias(
        self, id_tributo: int, data: date
    ) -> list[SituacaoTributariaDadosAbertos]:
        return [
            SituacaoTributariaDadosAbertos(
                id=int(r[0]), codigo=str(r[1]), descricao=str(r[2])
            )
            for r in self._sql.situacoes_por_tributo(id_tributo, data)
        ]

    def _tipos_dfe(self, id_cltr: int, data: date) -> list[TipoDfeClassificacaoDadosAbertos]:
        return [
            TipoDfeClassificacaoDadosAbertos(
                tipo=int(r[0]), sigla=str(r[1]), descricao=str(r[2])
            )
            for r in self._sql.tipos_dfe_classificacao(id_cltr, data)
        ]

    def consultar_classificacoes_tributarias_por_cst_e_tributo_tipo(
        self, cst: str, tributo_tipos: list[str], data: date
    ) -> list[ClassificacaoTributariaDadosAbertos]:
        out: list[ClassificacaoTributariaDadosAbertos] = []
        for row in self._sql.tratamento_por_cst_e_tributo_tipo(cst, tributo_tipos, data):
            id_cltr = int(row[8])
            out.append(
                ClassificacaoTributariaDadosAbertos(
                    codigo=str(row[0]),
                    descricao=str(row[1]),
                    tipo_aliquota=str(row[2]),
                    nomenclatura=str(row[3]),
                    descricao_tratamento_tributario=str(row[4]),
                    incompativel_com_suspensao=_flag(row[5]),
                    exige_grupo_desoneracao=_flag(row[6]),
                    possui_percentual_reducao=_flag(row[7]),
                    tipos_dfe_classificacao=self._tipos_dfe(id_cltr, data),
                    data_atualizacao=_parse_data_linha(row, 9),
                )
            )
        return out

    def consultar_classificacoes_tributarias_por_id_situacao_tributaria(
        self, id_situacao_tributaria: int, data: date
    ) -> list[ClassificacaoTributariaDadosAbertos]:
        out: list[ClassificacaoTributariaDadosAbertos] = []
        for row in self._sql.tratamento_por_id_situacao(id_situacao_tributaria, data):
            id_cltr = int(row[8])
            out.append(
                ClassificacaoTributariaDadosAbertos(
                    codigo=str(row[0]),
                    descricao=str(row[1]),
                    tipo_aliquota=str(row[2]),
                    nomenclatura=str(row[3]),
                    descricao_tratamento_tributario=str(row[4]),
                    incompativel_com_suspensao=_flag(row[5]),
                    exige_grupo_desoneracao=_flag(row[6]),
                    possui_percentual_reducao=_flag(row[7]),
                    tipos_dfe_classificacao=self._tipos_dfe(id_cltr, data),
                    data_atualizacao=_parse_data_linha(row, 9),
                )
            )
        return out

    def _map_cbs_ibs(self, row: tuple[Any, ...], data: date) -> ClassificacaoTributariaDadosAbertos:
        id_cltr = int(row[0])
        return ClassificacaoTributariaDadosAbertos(
            codigo=str(row[1]),
            descricao=str(row[2]),
            tipo_aliquota=str(row[3]),
            nomenclatura=str(row[4]),
            descricao_tratamento_tributario=str(row[5]),
            incompativel_com_suspensao=_flag(row[6]),
            exige_grupo_desoneracao=_flag(row[7]),
            possui_percentual_reducao=_flag(row[8]),
            indica_apropriacao_credito_adquirente_cbs=_flag(row[9]),
            indica_apropriacao_credito_adquirente_ibs=_flag(row[10]),
            indica_credito_presumido_fornecedor=_flag(row[11]),
            indica_credito_presumido_adquirente=_flag(row[12]),
            credito_operacao_antecedente=row[13] if row[13] is None else str(row[13]),
            percentual_reducao_cbs=convert_to_big_decimal(row[14]),
            percentual_reducao_ibs_uf=convert_to_big_decimal(row[15]),
            percentual_reducao_ibs_mun=convert_to_big_decimal(row[16]),
            tipos_dfe_classificacao=self._tipos_dfe(id_cltr, data),
            data_atualizacao=_parse_data_linha(row, 18),
        )

    def consultar_classificacoes_tributarias_cbs_ibs(
        self, data: date
    ) -> list[ClassificacaoTributariaDadosAbertos]:
        return [self._map_cbs_ibs(r, data) for r in self._sql.tratamento_cbs_ibs(None, data)]

    def consultar_classificacoes_tributarias_cbs_ibs_por_atores(
        self,
        data: date,
        fornecedor: int | None = None,
        adquirente: int | None = None,
        sigla_dfe: str | None = None,
    ) -> list[ClassificacaoTributariaDadosAbertos]:
        classificacoes = self.consultar_classificacoes_tributarias_cbs_ibs(data)
        if fornecedor is None and adquirente is None and sigla_dfe is None:
            return classificacoes
        sigla_norm = normalizar_sigla(sigla_dfe) if sigla_dfe else None
        codigos = set(
            self._sql.codigos_por_atores(data, fornecedor, adquirente, sigla_norm)
        )
        return [c for c in classificacoes if c.codigo in codigos]

    def consultar_classificacao_tributaria_cbs_ibs_por_codigo(
        self, c_class_trib: str, data: date
    ) -> ClassificacaoTributariaDadosAbertos:
        rows = self._sql.tratamento_cbs_ibs(c_class_trib, data)
        if not rows:
            raise ClassificacaoTributariaNaoEncontradaException(
                c_class_trib, "CBS e IBS", data
            )
        item = self._map_cbs_ibs(rows[0], data)
        row = rows[0]
        if len(row) > 19 and row[19] is not None:
            item.tipo_receita_bruta_simples_nacional = int(row[19])
        return item

    def _map_is(self, row: tuple[Any, ...], data: date) -> ClassificacaoTributariaDadosAbertos:
        id_cltr = int(row[0])
        return ClassificacaoTributariaDadosAbertos(
            codigo=str(row[1]),
            descricao=str(row[2]),
            tipo_aliquota=str(row[3]),
            nomenclatura=str(row[4]),
            descricao_tratamento_tributario=str(row[5]),
            incompativel_com_suspensao=_flag(row[6]),
            exige_grupo_desoneracao=_flag(row[7]),
            possui_percentual_reducao=_flag(row[8]),
            tipos_dfe_classificacao=self._tipos_dfe(id_cltr, data),
            data_atualizacao=_parse_data_linha(row, 10),
        )

    def consultar_classificacao_tributaria_is_por_codigo(
        self, c_class_trib: str, data: date
    ) -> ClassificacaoTributariaDadosAbertos:
        rows = self._sql.tratamento_is(c_class_trib, data)
        if not rows:
            raise ClassificacaoTributariaNaoEncontradaException(
                c_class_trib, "IS", data
            )
        return self._map_is(rows[0], data)

    def consultar_classificacoes_tributarias_imposto_seletivo(
        self, data: date
    ) -> list[ClassificacaoTributariaDadosAbertos]:
        return [self._map_is(r, data) for r in self._sql.tratamento_is(None, data)]

    def consultar_ncm(self, ncm: str, data: date) -> NcmDadosAbertos:
        _validar_ncm(ncm)
        if not self._sql.existe_ncm(ncm, data):
            raise NcmNaoEncontradaException(ncm, data)
        tem_av, ad_val = self._sql.aliquota_ad_valorem_produto(ncm, 1, data)
        tem_ar, ad_rem, unidade = self._sql.aliquota_ad_rem_produto(ncm, 1, data)
        return NcmDadosAbertos(
            tributado_pelo_imposto_seletivo=tem_av or tem_ar,
            tem_aliquota_ad_valorem=tem_av,
            tem_aliquota_ad_rem=tem_ar,
            aliquota_ad_valorem=ad_val if tem_av else None,
            aliquota_ad_rem=ad_rem if tem_ar else None,
            capitulo=self._sql.descricao_ncm(ncm, 2, data),
            posicao=self._sql.descricao_ncm(ncm, 4, data),
            subposicao=self._sql.descricao_ncm(ncm, 6, data),
            item=self._sql.descricao_ncm(ncm, 7, data),
            subitem=self._sql.descricao_ncm(ncm, 8, data),
            unidade=unidade,
        )

    def consultar_nbs(self, nbs: str, data: date) -> NbsDadosAbertos:
        _validar_nbs(nbs)
        if not self._sql.existe_nbs(nbs, data):
            raise NbsNaoEncontradaException(nbs, data)
        tem_av, ad_val = self._sql.aliquota_ad_valorem_servico(nbs, 1, data)
        return NbsDadosAbertos(
            tributado_pelo_imposto_seletivo=tem_av,
            tem_aliquota_ad_valorem=tem_av,
            aliquota_ad_valorem=ad_val if tem_av else None,
            capitulo=self._sql.descricao_nbs(nbs, 5, data),
            posicao=self._sql.descricao_nbs(nbs, 6, data),
            subposicao1=self._sql.descricao_nbs(nbs, 7, data),
            subposicao2=self._sql.descricao_nbs(nbs, 8, data),
            item=self._sql.descricao_nbs(nbs, 9, data),
        )

    def listar_nbs(self, data: date) -> list[NbsListaDadosAbertos]:
        return [
            NbsListaDadosAbertos(codigo=str(c), descricao=str(d))
            for c, d in self._sql.listar_nbs(data)
        ]

    def consultar_fundamentacoes_legais(
        self, data: date
    ) -> list[FundamentacaoClassificacaoDadosAbertos]:
        out: list[FundamentacaoClassificacaoDadosAbertos] = []
        for row in self._sql.fundamentacoes(data):
            id_situacao = int(row[4])
            id_tributo = self._sql.tributo_por_situacao(id_situacao, data)
            if id_tributo is None:
                raise TributoSituacaoTributariaNaoEncontradoException()
            if id_tributo == 1:
                continue
            out.append(
                FundamentacaoClassificacaoDadosAbertos(
                    codigo_classificacao_tributaria=str(row[0]),
                    descricao_classificacao_tributaria=str(row[1]),
                    codigo_situacao_tributaria=str(row[2]),
                    descricao_situacao_tributaria=str(row[3]),
                    conjunto_tributo="CBS e IBS",
                    texto=str(row[5]),
                    texto_curto=str(row[6]),
                    referencia_normativa=str(row[7]),
                )
            )
        return out

    def consultar_aliquota(
        self,
        id_tributo: int,
        codigo_uf: int | None,
        codigo_municipio: int | None,
        data: date,
    ) -> AliquotaDadosAbertos:
        aliquota = self._aliquota_padrao.buscar_aliquota(
            id_tributo, codigo_uf, codigo_municipio, data
        )
        return AliquotaDadosAbertos(
            aliquota_referencia=aliquota.valor_referencia,
            aliquota_propria=aliquota.valor_padrao,
            forma_aplicacao=aliquota.forma_aplicacao,
        )

    def _criticar_ncm(
        self,
        ncm: str,
        id_cltr: int,
        c_class_trib: str,
        data: date,
        tem_anexo: bool,
    ) -> None:
        if not tem_anexo:
            return
        if not self._sql.tem_ncm_aplicavel_vinculo(ncm, id_cltr, data):
            raise NcmNaoVinculadaException()
        if self._sql.tem_excecao_ncm(
            ncm, id_cltr, data
        ) and not self._sql.tem_ncm_sem_excecao(ncm, id_cltr, data):
            raise NcmNaoVinculadaException()

    def validar_ncm_aplicavel(
        self, c_class_trib: str, ncm: str, data_ocorrencia_fato_gerador: date
    ) -> NcmAplicavelSaida:
        _validar_ncm(ncm)
        if len(ncm) != 8:
            raise ValidacaoException("O campo NCM deve ter exatamente 8 dígitos.")
        cl = self._sql.classificacao_cbs_ibs(c_class_trib, data_ocorrencia_fato_gerador)
        if cl is None:
            raise ClassificacaoTributariaNaoEncontradaException(
                c_class_trib, "CBS e IBS", data_ocorrencia_fato_gerador
            )
        id_cltr, _, _ = cl
        tem_anexo = self._sql.tem_ncm_aplicavel(id_cltr, data_ocorrencia_fato_gerador)
        valido = True
        try:
            self._criticar_ncm(
                ncm, id_cltr, c_class_trib, data_ocorrencia_fato_gerador, tem_anexo
            )
        except NcmNaoVinculadaException:
            valido = False
        return NcmAplicavelSaida(
            c_class_trib=c_class_trib,
            ncm=ncm,
            data_ocorrencia_fato_gerador=data_ocorrencia_fato_gerador.isoformat(),
            valido=valido,
        )

    def _criticar_nbs(
        self,
        nbs: str,
        id_cltr: int,
        data: date,
        tem_anexo: bool,
    ) -> None:
        if not tem_anexo:
            return
        if not self._sql.tem_nbs_vinculo(nbs, id_cltr, data):
            raise NbsNaoVinculadaException()
        if self._sql.tem_excecao_nbs(
            nbs, id_cltr, data
        ) and not self._sql.tem_nbs_sem_excecao(nbs, id_cltr, data):
            raise NbsNaoVinculadaException()

    def validar_nbs_aplicavel(
        self, c_class_trib: str, nbs: str, data_ocorrencia_fato_gerador: date
    ) -> NbsAplicavelSaida:
        _validar_nbs(nbs)
        if len(nbs) != 9:
            raise ValidacaoException("O campo NBS deve ter exatamente 9 dígitos.")
        cl = self._sql.classificacao_cbs_ibs(c_class_trib, data_ocorrencia_fato_gerador)
        if cl is None:
            raise ClassificacaoTributariaNaoEncontradaException(
                c_class_trib, "CBS e IBS", data_ocorrencia_fato_gerador
            )
        id_cltr, _, _ = cl
        tem_anexo = self._sql.tem_nbs_aplicavel(id_cltr, data_ocorrencia_fato_gerador)
        valido = True
        try:
            self._criticar_nbs(
                nbs, id_cltr, data_ocorrencia_fato_gerador, tem_anexo
            )
        except NbsNaoVinculadaException:
            valido = False
        return NbsAplicavelSaida(
            c_class_trib=c_class_trib,
            nbs=nbs,
            data_ocorrencia_fato_gerador=data_ocorrencia_fato_gerador.isoformat(),
            valido=valido,
        )

    def consultar_redutores_compra_governamental(
        self,
    ) -> list[RedutorCompraGovernamentalDadosAbertos]:
        return [
            RedutorCompraGovernamentalDadosAbertos(
                valor=convert_to_big_decimal(r[0]) or Decimal(0),
                inicio_vigencia=date.fromisoformat(str(r[1])[:10]),
                fim_vigencia=_parse_data(r[2]),
            )
            for r in self._sql.redutores()
        ]

    def consultar_transferencias_cbs(self) -> list[TransferenciaCBSDadosAbertos]:
        return [
            TransferenciaCBSDadosAbertos(
                valor=convert_to_big_decimal(r[0]) or Decimal(0),
                inicio_vigencia=date.fromisoformat(str(r[1])[:10]),
                fim_vigencia=_parse_data(r[2]),
            )
            for r in self._sql.transferencias_cbs()
        ]

    def consultar_transferencias_ibs(self) -> list[TransferenciaIBSDadosAbertos]:
        return [
            TransferenciaIBSDadosAbertos(
                Decimal(0), date(2026, 1, 1), date(2026, 12, 31)
            ),
            TransferenciaIBSDadosAbertos(Decimal(100), date(2027, 1, 1), None),
        ]

    def get_warning_dados_simulados_por_data(
        self, data: date
    ) -> TipoWarningDadosSimulados | None:
        if data < date(2027, 1, 1):
            return None
        return TipoWarningDadosSimulados.CASO_GERAL

    def consultar_ncms_vigentes(self, data: date) -> list[NcmVigencia]:
        return [
            NcmVigencia(codigo=str(c), descricao=str(d))
            for c, d in self._sql.ncms_vigentes(data)
        ]

    def listar_classificacao_aplicavel_por_nbs(
        self, nbs: str, data: date
    ) -> list[str]:
        if not self._sql.existe_nbs(nbs, data):
            raise NbsNaoEncontradaException(nbs, data)
        out = list(self._sql.nbs_vinculadas(nbs, data))
        out.extend(self._sql.listar_nbs_sem_vinculo(data))
        return out

    def listar_nbs_aplicaveis_por_classificacao(
        self, c_class_trib: str, data: date
    ) -> list[NbsListaDadosAbertos]:
        cl = self._sql.classificacao_cbs_ibs(c_class_trib, data)
        if cl is None:
            raise ClassificacaoTributariaNaoEncontradaException(
                c_class_trib, "CBS e IBS", data
            )
        id_cltr, _, nomenclatura = cl
        if "NBS" not in nomenclatura:
            return []
        if not self._sql.existe_vinculo_nbs_classificacao(id_cltr):
            return self.listar_nbs(data)
        return [
            NbsListaDadosAbertos(codigo=str(c), descricao=str(d))
            for c, d in self._sql.nbs_aplicaveis_por_classificacao(id_cltr, data)
        ]

    def _agrupar_csts(
        self, rows: list[tuple[Any, ...]]
    ) -> list[SituacaoClassificacaoAninhado]:
        mapa: dict[str, SituacaoClassificacaoAninhado] = {}
        for row in rows:
            codigo_cst = str(row[1])
            if codigo_cst not in mapa:
                mapa[codigo_cst] = SituacaoClassificacaoAninhado(
                    id=int(row[0]) if row[0] is not None else None,
                    codigo=codigo_cst,
                    descricao=str(row[2]),
                )
            mapa[codigo_cst].classificacoes_tributarias.append(
                ClassificacaoTributariaResumo(
                    codigo=str(row[3]), descricao=str(row[4])
                )
            )
        return list(mapa.values())

    def consultar_csts_com_classificacoes_cbs_ibs(
        self, sigla_dfe: str | None, data: date
    ) -> list[SituacaoClassificacaoAninhado]:
        if sigla_dfe is None or not str(sigla_dfe).strip():
            rows = self._sql.csts_cbs_ibs(None, data)
        else:
            chave = _sigla_enum(sigla_dfe)
            rows = self._sql.csts_cbs_ibs(chave, data)
        return self._agrupar_csts(rows)

    def consultar_csts_com_classificacoes_is(
        self, sigla_dfe: str | None, data: date
    ) -> list[SituacaoClassificacaoAninhado]:
        if sigla_dfe is not None and str(sigla_dfe).strip():
            chave = _sigla_enum(sigla_dfe)
            if chave not in _IS_APLICAVEL_SIGLAS:
                return []
        return self._agrupar_csts(self._sql.csts_is(data))

    def consultar_validade_dfe_classificacao_tributaria(
        self, sigla_dfe: str, c_class_trib: str, data: date
    ) -> ValidadeDfeClassificacaoTributariaDadosAbertos:
        row = self._sql.validade_dfe_classificacao(c_class_trib, data)
        if row is None:
            raise ClassificacaoTributariaNaoEncontradaException(
                c_class_trib, sigla_dfe, data
            )
        if not isinstance(row[0], (int, float, Decimal)):
            raise ErroGenericoValidacaoException(
                "ID da classificação tributária inválido."
            )
        id_cltr = int(row[0])
        tipos = self._tipos_dfe(id_cltr, data)
        chave = _sigla_enum(sigla_dfe)
        valido = any(_corresponde_sigla(chave, t.sigla) for t in tipos)
        return ValidadeDfeClassificacaoTributariaDadosAbertos(
            sigla_dfe_informado=sigla_dfe,
            valido_para_sigla_dfe_informado=valido,
            nomenclatura=str(row[1]),
            exige_grupo_tributacao_regular=_flag(row[2]),
            permite_diferimento=_flag(row[3]),
            possibilidade_credito_presumido=int(row[4] or 0) == 1,
            exige_grupo_ibs_cbs=int(row[5] or 0) == 1,
        )

    def consultar_tipos_dfe_agrupados(
        self, data: date | None = None
    ) -> list[GrupoDfeDadosAbertos]:
        data_consulta = data if data is not None else date.today()
        grupos: dict[int, GrupoDfeDadosAbertos] = {}
        for row in self._sql.tipos_dfe_agrupados(data_consulta):
            grupo_id = int(row[0])
            if grupo_id not in grupos:
                grupos[grupo_id] = GrupoDfeDadosAbertos(
                    id=str(grupo_id), titulo=str(row[1])
                )
            grupo = grupos[grupo_id]
            grupo.tipos.append(
                TipoDfeDadosAbertos(
                    codigo=normalizar_sigla(str(row[2])),
                    titulo=str(row[3]),
                    modelo=str(int(row[4])) if row[4] is not None else None,
                    ordem=len(grupo.tipos) + 1,
                    suportado=_flag_sqlite(row[5], True),
                    permite_ncm_zero=_flag_sqlite(row[6], False),
                )
            )
        ordem = 1
        for g in grupos.values():
            g.ordem = ordem
            ordem += 1
        return list(grupos.values())

    def consultar_atores_agrupados(
        self, data: date, papel: PapelAtor | None = None
    ) -> list[GrupoAtorDadosAbertos]:
        papel_db = papel.value if papel else None
        grupos: dict[int, GrupoAtorDadosAbertos] = {}
        for row in self._sql.atores_agrupados(data, papel_db):
            gid = int(row[0])
            if gid not in grupos:
                grupos[gid] = GrupoAtorDadosAbertos(
                    id=gid, descricao=str(row[1]), ordem=int(row[2])
                )
            grupos[gid].atores.append(
                AtorDadosAbertos(id=int(row[3]), descricao=str(row[4]), ordem=int(row[5]))
            )
        return list(grupos.values())

    def _determinar_nomenclatura(
        self, sigla_dfe: str, c_class_trib: str, data: date
    ) -> str:
        cl = self._sql.classificacao_cbs_ibs(c_class_trib, data)
        if cl is None:
            raise ClassificacaoTributariaNaoEncontradaException(
                c_class_trib, "CBS e IBS", data
            )
        id_cltr, _, _ = cl
        tipos = self._tipos_dfe(id_cltr, data)
        chave = _sigla_enum(sigla_dfe)
        if not any(_corresponde_sigla(chave, t.sigla) for t in tipos):
            return NomenclaturaResultado.SEM.value
        ncm_a = self._sql.tem_ncm_aplicavel(id_cltr, data)
        nbs_a = self._sql.tem_nbs_aplicavel(id_cltr, data)
        if c_class_trib in _EXCECAO_CLASSIFICACOES:
            if chave in ("NFE", "NFCE"):
                return NomenclaturaResultado.EXCECAO_NCM.value
            if chave == "NFSE":
                return NomenclaturaResultado.EXCECAO_NBS.value
            return NomenclaturaResultado.SEM.value
        sigla_norm = normalizar_sigla(sigla_dfe)
        if sigla_norm in _NCM_APLICAVEL_SIGLAS and sigla_norm not in _NBS_APLICAVEL_SIGLAS:
            return NomenclaturaResultado.NCM.value if ncm_a else NomenclaturaResultado.SEM.value
        if sigla_norm in _NBS_APLICAVEL_SIGLAS:
            if ncm_a and nbs_a:
                return NomenclaturaResultado.MISTO.value
            if ncm_a:
                return NomenclaturaResultado.NCM.value
            if nbs_a:
                return NomenclaturaResultado.NBS.value
            return NomenclaturaResultado.SEM.value
        return NomenclaturaResultado.SEM.value

    def consultar_nomenclatura(
        self, sigla_dfe: str, c_class_trib: str, data: date
    ) -> NomenclaturaDadosAbertos:
        nomenclatura = self._determinar_nomenclatura(sigla_dfe, c_class_trib, data)
        sem = nomenclatura == NomenclaturaResultado.SEM.value
        chave = _sigla_enum(sigla_dfe)
        return NomenclaturaDadosAbertos(
            sigla_dfe=sigla_dfe,
            c_class_trib=c_class_trib,
            data=data,
            nomenclatura=nomenclatura,
            obrigatorio=not sem,
            ncm_opcional=sem and chave in ("NFE", "NFCE"),
            nbs_opcional=sem and chave == "NFSE",
        )