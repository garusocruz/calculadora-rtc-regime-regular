"""Serviços de consulta ao SQLite oficial (pin f1eebd7ce3157423b1a6aaca7dc1d6c3395452c4).

Transcrição dos serviços de domínio Java em
``br.gov.serpro.rtc.domain.service`` / ``domain.repository``, sem Spring.
"""

from __future__ import annotations

import sqlite3
from dataclasses import dataclass
from datetime import date
from decimal import Decimal
from enum import Enum
from typing import Any

from calculadora_rtc_regime_regular.banco import conectar

ZERO = Decimal(0)

_ERRO_MULTIPLOS_VALORES = (
    "Consulta retornou múltiplos valores quando apenas um era esperado."
)


# --- exceções (mensagens espelhando Java) ---


class ErroGenericoValidacaoException(Exception):
    def __init__(self, mensagem: str) -> None:
        super().__init__(mensagem)


class AliquotaReferenciaNaoEncontradaException(Exception):
    def __init__(self, id_tributo: int, data: date) -> None:
        super().__init__(
            f"Alíquota de referência não encontrada para o tributo com id {id_tributo} e data {data}"
        )


class AliquotaAdRemNaoEncontradaException(Exception):
    def __init__(self, ncm: str, id_tributo: int, data: date) -> None:
        super().__init__(
            f"Alíquota ad rem não encontrada para NCM {ncm} e data {data} (idTributo: {id_tributo})"
        )


class ErroInternoSistemaException(RuntimeError):
    def __init__(self, mensagem: str) -> None:
        super().__init__(mensagem)


class PercentualReducaoNaoEncontradoException(Exception):
    def __init__(self, id_classificacao: int, data: date) -> None:
        super().__init__(
            f"Percentual de redução não encontrado para classificação tributária com id {id_classificacao} e data {data}"
        )


class FundamentacaoClassificacaoNaoEncontradaException(Exception):
    def __init__(self, id_classificacao: int, data: date) -> None:
        super().__init__(
            f"Fundamentação legal não encontrada para classificação tributária de id {id_classificacao} e data {data}"
        )


class SituacaoTributariaNaoEncontradaException(Exception):
    def __init__(self, codigo: str, tributo: str, data: date) -> None:
        super().__init__(
            f"Situação tributária (CST) não encontrada para código {codigo} e data {data} ({tributo})"
        )


class TipoDfeNaoEncontradoException(Exception):
    def __init__(self, tp_doc: int, data: date) -> None:
        super().__init__(
            f"Tipo de documento fiscal (tpDoc) de código {tp_doc} não encontrado ou fora de vigência na data {data}"
        )


class TipoDfeNaoTratadoException(Exception):
    def __init__(self, tipo: "TipoDfe") -> None:
        super().__init__(
            f"Tipo de documento fiscal (tpDoc) de código {tipo.tipo} ({tipo.sigla}) "
            "não possui tratamento implementado na calculadora"
        )


class TratamentoClassificacaoNaoEncontradoException(Exception):
    def __init__(self, id_classificacao: int, data: date) -> None:
        super().__init__(
            f"Tratamento tributário não encontrado para classificação tributária com id {id_classificacao} e data {data}"
        )


class TratamentoTributarioNaoEncontradoException(Exception):
    def __init__(self, id_tratamento: int) -> None:
        super().__init__(f"Tratamento tributário com id {id_tratamento} não encontrado")


class UfNaoEncontradaException(Exception):
    def __init__(self, sigla: str) -> None:
        super().__init__(f"UF de sigla {sigla} não encontrada")


class MunicipioNaoEncontradoException(Exception):
    def __init__(self, codigo: int) -> None:
        super().__init__(f"Município de código {codigo} não encontrado")


class MunicipioNaoPertencenteException(Exception):
    def __init__(self, codigo: int, sigla_uf: str) -> None:
        super().__init__(
            f"Município de código {codigo} não pertence à UF de sigla {sigla_uf}"
        )


class IllegalStateError(Exception):
    pass


class TributoSituacaoTributariaNaoEncontradoException(Exception):
    def __init__(
        self, id_tributo: int | None, id_situacao: int, data: date
    ) -> None:
        super().__init__(
            f"Tributo com id s{id_tributo} não encontrado para situação tributária com id {id_situacao} e data {data}"
        )


# --- enums ---


class TributoEnum(Enum):
    IS = (1, "Imposto Seletivo")
    CBS = (2, "CBS")
    IBS_ESTADUAL = (3, "IBS Estadual")
    IBS_MUNICIPAL = (4, "IBS Municipal")

    def __init__(self, codigo: int, nome: str) -> None:
        self.codigo = codigo
        self.nome = nome


class TipoEnteGovernamental(Enum):
    UNIAO = 1
    ESTADO = 2
    MUNICIPIO = 3


# --- DTOs / entidades ---


@dataclass(frozen=True)
class AliquotaAdRemDTO:
    valor: Decimal | None
    unidade_medida: str


@dataclass(frozen=True)
class AliquotaAdValoremDTO:
    valor: Decimal | None


@dataclass(frozen=True)
class FundamentacaoClassificacaoDTO:
    texto_curto: str
    memoria_calculo: str


@dataclass(frozen=True)
class TratamentoClassificacaoDTO:
    id_tratamento_tributario: int
    id_classificacao_tributaria: int
    in_incompativel_com_suspensao: bool
    in_exige_grupo_desoneracao: bool


@dataclass
class Uf:
    codigo: int
    sigla: str
    nome: str


@dataclass
class Municipio:
    codigo: int
    nome: str
    uf: Uf


@dataclass
class SituacaoTributaria:
    id: int
    codigo: str
    descricao: str
    in_grupo_ibs_cbs: bool
    in_grupo_ibs_cbs_mono: bool
    in_grupo_reducao: bool
    in_grupo_diferimento: bool
    in_grupo_transferencia_credito: bool
    in_grupo_credito_presumido_ibs_zfm: bool
    in_grupo_ajuste_competencia: bool
    inicio_vigencia: date
    fim_vigencia: date | None


@dataclass
class TipoDfe:
    id: int
    tipo: int
    sigla: str
    descricao: str
    inicio_vigencia: date
    fim_vigencia: date | None
    permite_ncm_zero: bool
    possui_tratamento: bool


@dataclass
class TratamentoTributario:
    id: int
    descricao: str
    expressao_aliquota: str | None
    expressao_aliquota_efetiva: str | None
    expressao_base_calculo: str
    expressao_tributo_calculado: str
    expressao_tributo_devido: str
    expressao_percentual_diferimento: str | None
    expressao_valor_diferimento: str | None
    in_incompativel_com_suspensao: bool
    in_exige_grupo_desoneracao: bool
    in_possui_percentual_reducao: bool
    in_possui_ajuste: bool
    in_possui_redutor: bool
    in_possui_monofasia: bool
    inicio_vigencia: date
    fim_vigencia: date | None


@dataclass
class VersaoBaseDados:
    id: int
    data: date
    descricao: str
    numero_versao: str


@dataclass
class FundamentacaoClassificacao:
    id: int
    id_classificacao_tributaria: int
    id_fundamentacao_legal: int
    inicio_vigencia: date
    fim_vigencia: date | None


# --- helpers ---


def _data_str(data: date) -> str:
    return data.isoformat()


def _para_decimal(valor: object) -> Decimal | None:
    if valor is None:
        return None
    if isinstance(valor, Decimal):
        return valor
    if isinstance(valor, bool):
        return Decimal(int(valor))
    if isinstance(valor, int):
        return Decimal(valor)
    if isinstance(valor, float):
        return Decimal(str(valor))
    if isinstance(valor, str):
        try:
            return Decimal(valor)
        except Exception:
            return None
    try:
        return Decimal(str(valor))
    except Exception:
        return None


def _flag(valor: object) -> bool:
    if isinstance(valor, bool):
        return valor
    if isinstance(valor, (int, float, Decimal)):
        return int(valor) != 0
    return bool(valor)


def _parse_data(valor: object) -> date:
    if isinstance(valor, date):
        return valor
    return date.fromisoformat(str(valor)[:10])


class _ConexaoConsulta:
    def __init__(self, conexao: sqlite3.Connection | None = None) -> None:
        self._conexao = conexao

    def _abrir(self) -> sqlite3.Connection:
        return self._conexao or conectar()

    def _executar(
        self, sql: str, params: tuple[Any, ...] = ()
    ) -> list[tuple[Any, ...]]:
        if self._conexao is not None:
            return list(self._conexao.execute(sql, params).fetchall())
        with conectar() as conn:
            return list(conn.execute(sql, params).fetchall())

    def _um(
        self, sql: str, params: tuple[Any, ...] = ()
    ) -> tuple[Any, ...] | None:
        linhas = self._executar(sql, params)
        return linhas[0] if linhas else None

    def _escalar(self, sql: str, params: tuple[Any, ...] = ()) -> Any:
        linha = self._um(sql, params)
        return linha[0] if linha else None


# --- repositórios (SQL nativo equivalente às @Query Java) ---


class _AliquotaAdRemProdutoRepositorio(_ConexaoConsulta):
    def buscar_aliquota_ad_rem(
        self, ncm: str, id_tributo: int, data: date
    ) -> AliquotaAdRemDTO | None:
        d = _data_str(data)
        linha = self._um(
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
        if not linha:
            return None
        return AliquotaAdRemDTO(_para_decimal(linha[0]), linha[1])


class _AliquotaAdValoremProdutoRepositorio(_ConexaoConsulta):
    def buscar_aliquota_ad_valorem(
        self, ncm: str, id_tributo: int, data: date
    ) -> AliquotaAdValoremDTO | None:
        d = _data_str(data)
        linha = self._um(
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
        if not linha:
            return None
        return AliquotaAdValoremDTO(_para_decimal(linha[0]))

    def existe_ncm_ad_valorem(
        self, ncm: str, tributo: TributoEnum, data: date
    ) -> bool:
        d = _data_str(data)
        return bool(
            self._escalar(
                """
                SELECT COUNT(1) > 0
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
                """,
                (
                    ncm,
                    ncm,
                    tributo.codigo,
                    d,
                    d,
                    ncm,
                    d,
                    d,
                    d,
                    d,
                ),
            )
        )


class _AliquotaAdValoremServicoRepositorio(_ConexaoConsulta):
    def buscar_aliquota_ad_valorem_dto(
        self,
        nbs: str,
        id_tributo: int,
        id_classificacao_tributaria: int | None,
        data: date,
    ) -> AliquotaAdValoremDTO | None:
        d = _data_str(data)
        linhas = self._executar(
            """
            SELECT av.AADV_VALOR
            FROM ALIQUOTA_AD_VALOREM_SERVICO a
            JOIN ALIQUOTA_AD_VALOREM av ON a.AAVS_AADV_ID = av.AADV_ID
            WHERE EXISTS (SELECT 1 FROM NBS n WHERE n.NBS_CD = ?)
              AND a.AAVS_NBS_CD = SUBSTR(?, 1, LENGTH(a.AAVS_NBS_CD))
              AND av.AADV_TBTO_ID = ?
              AND (? IS NULL OR av.AADV_CLTR_ID = ?)
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
            """,
            (
                nbs,
                nbs,
                id_tributo,
                id_classificacao_tributaria,
                id_classificacao_tributaria,
                d,
                d,
                nbs,
                d,
                d,
                d,
                d,
            ),
        )
        if not linhas:
            return None
        if len(linhas) > 1:
            raise ErroGenericoValidacaoException(_ERRO_MULTIPLOS_VALORES)
        return AliquotaAdValoremDTO(_para_decimal(linhas[0][0]))

    def existe_nbs_ad_valorem(
        self, nbs: str, tributo: TributoEnum, data: date
    ) -> bool:
        d = _data_str(data)
        return bool(
            self._escalar(
                """
                SELECT COUNT(1) > 0
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
                """,
                (
                    nbs,
                    nbs,
                    tributo.codigo,
                    d,
                    d,
                    nbs,
                    d,
                    d,
                    d,
                    d,
                ),
            )
        )

    def buscar_aliquota_ad_valorem_por_classificacao_tributaria(
        self, id_tributo: int, id_classificacao_tributaria: int, data: date
    ) -> Decimal | None:
        d = _data_str(data)
        linhas = self._executar(
            """
            SELECT av.AADV_VALOR
            FROM ALIQUOTA_AD_VALOREM av
            WHERE av.AADV_TBTO_ID = ?
              AND av.AADV_CLTR_ID = ?
              AND ? BETWEEN av.AADV_INICIO_VIGENCIA AND COALESCE(av.AADV_FIM_VIGENCIA, ?)
            """,
            (id_tributo, id_classificacao_tributaria, d, d),
        )
        if not linhas:
            return None
        if len(linhas) > 1:
            raise ErroGenericoValidacaoException(_ERRO_MULTIPLOS_VALORES)
        return _para_decimal(linhas[0][0])


class _AliquotaReferenciaRepositorio(_ConexaoConsulta):
    def buscar(self, id_tributo: int, data: date) -> Decimal | None:
        d = _data_str(data)
        return _para_decimal(
            self._escalar(
                """
                SELECT ar.ALRE_VALOR
                FROM ALIQUOTA_REFERENCIA ar
                WHERE ar.ALRE_TBTO_ID = ?
                  AND ? BETWEEN ar.ALRE_INICIO_VIGENCIA AND COALESCE(ar.ALRE_FIM_VIGENCIA, ?)
                """,
                (id_tributo, d, d),
            )
        )


class _PercentualReducaoRepositorio(_ConexaoConsulta):
    def buscar(
        self, id_classificacao_tributaria: int, id_tributo: int, data: date
    ) -> Decimal | None:
        d = _data_str(data)
        return _para_decimal(
            self._escalar(
                """
                SELECT PERE_VALOR
                FROM PERCENTUAL_REDUCAO
                WHERE PERE_CLTR_ID = ?
                  AND PERE_TBTO_ID = ?
                  AND PERE_INICIO_VIGENCIA <= ?
                  AND (PERE_FIM_VIGENCIA IS NULL OR PERE_FIM_VIGENCIA >= ?)
                """,
                (id_classificacao_tributaria, id_tributo, d, d),
            )
        )


class _FundamentacaoClassificacaoRepositorio(_ConexaoConsulta):
    def buscar(
        self, id_classificacao_tributaria: int, data: date
    ) -> FundamentacaoClassificacaoDTO | None:
        d = _data_str(data)
        linha = self._um(
            """
            SELECT fl.FDLG_TEXTO_CURTO, ct.CLTR_MEMORIA_CALCULO
            FROM FUNDAMENTACAO_CLASSIFICACAO fc
            JOIN FUNDAMENTACAO_LEGAL fl ON fc.FDCL_FDLG_ID = fl.FDLG_ID
            JOIN CLASSIFICACAO_TRIBUTARIA ct ON fc.FDCL_CLTR_ID = ct.CLTR_ID
            WHERE fc.FDCL_CLTR_ID = ?
              AND ? BETWEEN fc.FDCL_INICIO_VIGENCIA AND COALESCE(fc.FDCL_FIM_VIGENCIA, ?)
            """,
            (id_classificacao_tributaria, d, d),
        )
        if not linha:
            return None
        return FundamentacaoClassificacaoDTO(linha[0], linha[1])

    def buscar_todas(self, data: date) -> list[FundamentacaoClassificacao]:
        d = _data_str(data)
        linhas = self._executar(
            """
            SELECT fc.FDCL_ID, fc.FDCL_CLTR_ID, fc.FDCL_FDLG_ID,
                   fc.FDCL_INICIO_VIGENCIA, fc.FDCL_FIM_VIGENCIA
            FROM FUNDAMENTACAO_CLASSIFICACAO fc
            JOIN CLASSIFICACAO_TRIBUTARIA ct ON fc.FDCL_CLTR_ID = ct.CLTR_ID
            WHERE ? BETWEEN fc.FDCL_INICIO_VIGENCIA AND COALESCE(fc.FDCL_FIM_VIGENCIA, ?)
            ORDER BY ct.CLTR_CD
            """,
            (d, d),
        )
        return [
            FundamentacaoClassificacao(
                id=int(r[0]),
                id_classificacao_tributaria=int(r[1]),
                id_fundamentacao_legal=int(r[2]),
                inicio_vigencia=_parse_data(r[3]),
                fim_vigencia=_parse_data(r[4]) if r[4] else None,
            )
            for r in linhas
        ]


class _RedutorCompraGovernamentalRepositorio(_ConexaoConsulta):
    def buscar_valor_redutor(self, data: date) -> Decimal | None:
        d = _data_str(data)
        return _para_decimal(
            self._escalar(
                """
                SELECT RCGO_VALOR
                FROM REDUTOR_COMPRA_GOVERNAMENTAL
                WHERE RCGO_INICIO_VIGENCIA <= ?
                  AND (RCGO_FIM_VIGENCIA IS NULL OR RCGO_FIM_VIGENCIA >= ?)
                """,
                (d, d),
            )
        )


class _SituacaoTributariaRepositorio(_ConexaoConsulta):
    def existe_cst(self, cst: str, id_tributo: int, data: date) -> bool:
        d = _data_str(data)
        return bool(
            self._escalar(
                """
                SELECT EXISTS (
                    SELECT 1
                    FROM TRIBUTO_SITUACAO_TRIBUTARIA t
                    JOIN SITUACAO_TRIBUTARIA s ON t.TRST_SITR_ID = s.SITR_ID
                    WHERE t.TRST_TBTO_ID = ?
                      AND s.SITR_CD = ?
                      AND ? BETWEEN t.TRST_INICIO_VIGENCIA AND COALESCE(t.TRST_FIM_VIGENCIA, ?)
                      AND ? BETWEEN s.SITR_INICIO_VIGENCIA AND COALESCE(s.SITR_FIM_VIGENCIA, ?)
                )
                """,
                (id_tributo, cst, d, d, d, d),
            )
        )

    def consultar_situacao_tributaria_por_codigo(
        self, cst: str, id_tributo: int, data: date
    ) -> SituacaoTributaria | None:
        d = _data_str(data)
        linha = self._um(
            """
            SELECT s.SITR_ID, s.SITR_CD, s.SITR_DESCRICAO,
                   s.SITR_IND_GIBSCBS, s.SITR_IND_GIBSCBSMONO,
                   s.SITR_IND_GRED, s.SITR_IND_GDIF, s.SITR_IND_GTRANSFCRED,
                   s.SITR_IND_GCREDPRESIBSZFM, s.SITR_IND_GAJUSTECOMPET,
                   s.SITR_INICIO_VIGENCIA, s.SITR_FIM_VIGENCIA
            FROM SITUACAO_TRIBUTARIA s
            JOIN TRIBUTO_SITUACAO_TRIBUTARIA tst ON tst.TRST_SITR_ID = s.SITR_ID
            JOIN TRIBUTO t ON t.TBTO_ID = tst.TRST_TBTO_ID
            WHERE COALESCE(s.SITR_CD, '') = COALESCE(?, '')
              AND COALESCE(t.TBTO_ID, 0) = COALESCE(?, 0)
              AND COALESCE(?, '') BETWEEN COALESCE(tst.TRST_INICIO_VIGENCIA, '') AND COALESCE(tst.TRST_FIM_VIGENCIA, ?)
              AND COALESCE(?, '') BETWEEN COALESCE(s.SITR_INICIO_VIGENCIA, '') AND COALESCE(s.SITR_FIM_VIGENCIA, ?)
              AND COALESCE(?, '') BETWEEN COALESCE(t.TBTO_INICIO_VIGENCIA, '') AND COALESCE(t.TBTO_FIM_VIGENCIA, ?)
            LIMIT 1
            """,
            (cst, id_tributo, d, d, d, d, d, d),
        )
        if not linha:
            return None
        return SituacaoTributaria(
            id=int(linha[0]),
            codigo=linha[1],
            descricao=linha[2],
            in_grupo_ibs_cbs=_flag(linha[3]),
            in_grupo_ibs_cbs_mono=_flag(linha[4]),
            in_grupo_reducao=_flag(linha[5]),
            in_grupo_diferimento=_flag(linha[6]),
            in_grupo_transferencia_credito=_flag(linha[7]),
            in_grupo_credito_presumido_ibs_zfm=_flag(linha[8]),
            in_grupo_ajuste_competencia=_flag(linha[9]),
            inicio_vigencia=_parse_data(linha[10]),
            fim_vigencia=_parse_data(linha[11]) if linha[11] else None,
        )


class _TipoDfeRepositorio(_ConexaoConsulta):
    def buscar_por_tipo(self, tipo: int, data: date) -> TipoDfe | None:
        d = _data_str(data)
        linha = self._um(
            """
            SELECT TPDF_ID, TPDF_TIPO, TPDF_SIGLA, TPDF_DESCRICAO,
                   TPDF_INICIO_VIGENCIA, TPDF_FIM_VIGENCIA,
                   TPDF_B_PERMITE_NCM_ZERO, TPDF_B_POSSUI_TRATAMENTO_CALCULADORA
            FROM TIPO_DFE
            WHERE TPDF_TIPO = ?
              AND ? BETWEEN TPDF_INICIO_VIGENCIA AND COALESCE(TPDF_FIM_VIGENCIA, ?)
            """,
            (tipo, d, d),
        )
        if not linha:
            return None
        return TipoDfe(
            id=int(linha[0]),
            tipo=int(linha[1]),
            sigla=linha[2],
            descricao=linha[3],
            inicio_vigencia=_parse_data(linha[4]),
            fim_vigencia=_parse_data(linha[5]) if linha[5] else None,
            permite_ncm_zero=_flag(linha[6]),
            possui_tratamento=_flag(linha[7]),
        )


class _TransferenciaCBSRepositorio(_ConexaoConsulta):
    def get_percentual_transferencia(self, data: date) -> Decimal | None:
        d = _data_str(data)
        return _para_decimal(
            self._escalar(
                """
                SELECT TCEG_VALOR
                FROM TRANSFERENCIA_CBS_ENTE_GOV
                WHERE TCEG_INICIO_VIGENCIA <= ?
                  AND (TCEG_FIM_VIGENCIA IS NULL OR TCEG_FIM_VIGENCIA >= ?)
                """,
                (d, d),
            )
        )


class _TratamentoClassificacaoRepositorio(_ConexaoConsulta):
    def buscar_tratamento_classificacao(
        self, id_classificacao_tributaria: int, data: date
    ) -> TratamentoClassificacaoDTO | None:
        d = _data_str(data)
        linha = self._um(
            """
            SELECT tt.TRTR_ID, tc.TRCL_CLTR_ID,
                   tt.TRTR_IN_INCOMPATIVEL_COM_SUSPENSAO,
                   tt.TRTR_IN_EXIGE_GRUPO_DESONERACAO
            FROM TRATAMENTO_CLASSIFICACAO tc
            JOIN TRATAMENTO_TRIBUTARIO tt ON tc.TRCL_TRTR_ID = tt.TRTR_ID
            WHERE tc.TRCL_CLTR_ID = ?
              AND tc.TRCL_INICIO_VIGENCIA <= ?
              AND (tc.TRCL_FIM_VIGENCIA IS NULL OR tc.TRCL_FIM_VIGENCIA >= ?)
            """,
            (id_classificacao_tributaria, d, d),
        )
        if not linha:
            return None
        return TratamentoClassificacaoDTO(
            id_tratamento_tributario=int(linha[0]),
            id_classificacao_tributaria=int(linha[1]),
            in_incompativel_com_suspensao=_flag(linha[2]),
            in_exige_grupo_desoneracao=_flag(linha[3]),
        )


class _TratamentoTributarioRepositorio(_ConexaoConsulta):
    def find_by_id(self, id_tratamento: int) -> TratamentoTributario | None:
        linha = self._um(
            """
            SELECT TRTR_ID, TRTR_DESCRICAO, TRTR_EXPRESSAO_ALIQUOTA,
                   TRTR_EXPRESSAO_ALIQUOTA_EFETIVA, TRTR_EXPRESSAO_BASE_CALCULO,
                   TRTR_EXPRESSAO_TRIBUTO_CALCULADO, TRTR_EXPRESSAO_TRIBUTO_DEVIDO,
                   TRTR_EXPRESSAO_PERCENTUAL_DIFERIMENTO, TRTR_EXPRESSAO_VALOR_DIFERIMENTO,
                   TRTR_IN_INCOMPATIVEL_COM_SUSPENSAO, TRTR_IN_EXIGE_GRUPO_DESONERACAO,
                   TRTR_IN_POSSUI_PERCENTUAL_REDUCAO, TRTR_IN_POSSUI_AJUSTE,
                   TRTR_IN_POSSUI_REDUTOR, TRTR_IN_POSSUI_MONOFASIA,
                   TRTR_INICIO_VIGENCIA, TRTR_FIM_VIGENCIA
            FROM TRATAMENTO_TRIBUTARIO
            WHERE TRTR_ID = ?
            """,
            (id_tratamento,),
        )
        if not linha:
            return None
        return TratamentoTributario(
            id=int(linha[0]),
            descricao=linha[1],
            expressao_aliquota=linha[2],
            expressao_aliquota_efetiva=linha[3],
            expressao_base_calculo=linha[4],
            expressao_tributo_calculado=linha[5],
            expressao_tributo_devido=linha[6],
            expressao_percentual_diferimento=linha[7],
            expressao_valor_diferimento=linha[8],
            in_incompativel_com_suspensao=_flag(linha[9]),
            in_exige_grupo_desoneracao=_flag(linha[10]),
            in_possui_percentual_reducao=_flag(linha[11]),
            in_possui_ajuste=_flag(linha[12]),
            in_possui_redutor=_flag(linha[13]),
            in_possui_monofasia=_flag(linha[14]),
            inicio_vigencia=_parse_data(linha[15]),
            fim_vigencia=_parse_data(linha[16]) if linha[16] else None,
        )


class _TributoSituacaoTributariaRepositorio(_ConexaoConsulta):
    def consultar_por_id_situacao_tributaria(
        self, id_situacao_tributaria: int, data: date
    ) -> int | None:
        d = _data_str(data)
        val = self._escalar(
            """
            SELECT t.TRST_TBTO_ID
            FROM TRIBUTO_SITUACAO_TRIBUTARIA t
            JOIN SITUACAO_TRIBUTARIA s ON t.TRST_SITR_ID = s.SITR_ID
            WHERE t.TRST_SITR_ID = ?
              AND ? BETWEEN t.TRST_INICIO_VIGENCIA AND COALESCE(t.TRST_FIM_VIGENCIA, ?)
            LIMIT 1
            """,
            (id_situacao_tributaria, d, d),
        )
        return int(val) if val is not None else None


class _VersaoBaseDadosRepositorio(_ConexaoConsulta):
    def find_top_by_order_by_id_desc(self) -> VersaoBaseDados | None:
        linha = self._um(
            """
            SELECT VRBD_ID, VRBD_DATA, VRBD_DESCRICAO, VRBD_VERSAO_BASE_DADO
            FROM VERSAO_BASE_DADO
            ORDER BY VRBD_ID DESC
            LIMIT 1
            """
        )
        if not linha:
            return None
        return VersaoBaseDados(
            id=int(linha[0]),
            data=_parse_data(linha[1]),
            descricao=linha[2],
            numero_versao=linha[3],
        )


class _UfRepositorio(_ConexaoConsulta):
    def consultar_todos(self) -> list[Uf]:
        return [
            Uf(codigo=int(r[0]), sigla=r[1], nome=r[2])
            for r in self._executar(
                "SELECT UF_CD, UF_SIGLA, UF_NOME FROM UF ORDER BY UF_SIGLA"
            )
        ]

    def consultar_por_sigla(self, sigla: str) -> int | None:
        codigo = self._escalar(
            "SELECT UF_CD FROM UF WHERE UF_SIGLA = UPPER(?)",
            (sigla,),
        )
        return int(codigo) if codigo is not None else None

    def existe_uf(self, sigla: str) -> bool:
        return bool(
            self._escalar(
                "SELECT EXISTS (SELECT 1 FROM UF u WHERE u.UF_SIGLA = UPPER(?))",
                (sigla,),
            )
        )


class _MunicipioRepositorio(_ConexaoConsulta):
    def consultar_todos_por_sigla_uf(self, uf: str) -> list[Municipio]:
        linhas = self._executar(
            """
            SELECT m.MUNI_CD, m.MUNI_NOME, u.UF_CD, u.UF_SIGLA, u.UF_NOME
            FROM MUNICIPIO m
            JOIN UF u ON m.MUNI_UF_CD = u.UF_CD
            WHERE LOWER(u.UF_SIGLA) = LOWER(?)
            ORDER BY m.MUNI_NOME
            """,
            (uf,),
        )
        return [
            Municipio(
                codigo=int(r[0]),
                nome=r[1],
                uf=Uf(codigo=int(r[2]), sigla=r[3], nome=r[4]),
            )
            for r in linhas
        ]

    def validar_municipio(self, codigo_municipio: int, sigla_uf: str) -> int:
        resultado = self._escalar(
            """
            SELECT
            CASE
                WHEN COUNT(m.MUNI_CD) = 0 THEN 1
                WHEN COUNT(m.MUNI_CD) > 0 AND LOWER(u.UF_SIGLA) != LOWER(?) THEN 2
                ELSE 0
            END
            FROM MUNICIPIO m
            JOIN UF u ON m.MUNI_UF_CD = u.UF_CD
            WHERE m.MUNI_CD = ?
            """,
            (sigla_uf, codigo_municipio),
        )
        return int(resultado) if resultado is not None else 1

    def buscar_sigla_uf(self, codigo_municipio: int) -> str | None:
        sigla = self._escalar(
            """
            SELECT u.UF_SIGLA
            FROM MUNICIPIO m
            JOIN UF u ON m.MUNI_UF_CD = u.UF_CD
            WHERE m.MUNI_CD = ?
            """,
            (codigo_municipio,),
        )
        return str(sigla) if sigla is not None else None


# --- serviços (espelho das classes Java) ---


class AliquotaAdRemProdutoService:
    def __init__(self, conexao: sqlite3.Connection | None = None) -> None:
        self._repo = _AliquotaAdRemProdutoRepositorio(conexao)

    def buscar_aliquota_ad_rem(
        self, ncm: str, id_tributo: int, data: date
    ) -> AliquotaAdRemDTO | None:
        return self._repo.buscar_aliquota_ad_rem(ncm, id_tributo, data)


class AliquotaAdValoremProdutoService:
    def __init__(self, conexao: sqlite3.Connection | None = None) -> None:
        self._repo = _AliquotaAdValoremProdutoRepositorio(conexao)

    def buscar_aliquota_ad_valorem(
        self, ncm: str, id_tributo: int, data: date
    ) -> AliquotaAdValoremDTO | None:
        return self._repo.buscar_aliquota_ad_valorem(ncm, id_tributo, data)

    def existe_ncm_ad_valorem(
        self, ncm: str, tributo: TributoEnum, data: date
    ) -> bool:
        return self._repo.existe_ncm_ad_valorem(ncm, tributo, data)


class AliquotaAdValoremServicoService:
    def __init__(self, conexao: sqlite3.Connection | None = None) -> None:
        self._repo = _AliquotaAdValoremServicoRepositorio(conexao)

    def buscar_aliquota_ad_valorem(
        self,
        nbs: str,
        id_tributo: int,
        id_classificacao_tributaria: int | None,
        data: date,
    ) -> Decimal | None:
        dto = self.buscar_aliquota_ad_valorem_dto(
            nbs, id_tributo, id_classificacao_tributaria, data
        )
        return dto.valor if dto is not None else None

    def buscar_aliquota_ad_valorem_dto(
        self,
        nbs: str,
        id_tributo: int,
        id_classificacao_tributaria: int | None,
        data: date,
    ) -> AliquotaAdValoremDTO | None:
        return self._repo.buscar_aliquota_ad_valorem_dto(
            nbs, id_tributo, id_classificacao_tributaria, data
        )

    def existe_nbs_ad_valorem(
        self, nbs: str, tributo: TributoEnum, data: date
    ) -> bool:
        return self._repo.existe_nbs_ad_valorem(nbs, tributo, data)

    def buscar_aliquota_ad_valorem_por_classificacao_tributaria(
        self, id_tributo: int, id_classificacao_tributaria: int, data: date
    ) -> Decimal | None:
        return self._repo.buscar_aliquota_ad_valorem_por_classificacao_tributaria(
            id_tributo, id_classificacao_tributaria, data
        )


class AliquotaReferenciaService:
    def __init__(self, conexao: sqlite3.Connection | None = None) -> None:
        self._repo = _AliquotaReferenciaRepositorio(conexao)

    def buscar(self, id_tributo: int, data: date) -> Decimal:
        aliquota = self._repo.buscar(id_tributo, data)
        if aliquota is None:
            raise AliquotaReferenciaNaoEncontradaException(id_tributo, data)
        return aliquota


class PercentualReducaoService:
    def __init__(self, conexao: sqlite3.Connection | None = None) -> None:
        self._repo = _PercentualReducaoRepositorio(conexao)

    def buscar(
        self, id_classificacao_tributaria: int, id_tributo: int, data: date
    ) -> Decimal:
        percentual = self._repo.buscar(id_classificacao_tributaria, id_tributo, data)
        if percentual is None:
            raise PercentualReducaoNaoEncontradoException(
                id_classificacao_tributaria, data
            )
        return percentual


class FundamentacaoClassificacaoService:
    def __init__(self, conexao: sqlite3.Connection | None = None) -> None:
        self._repo = _FundamentacaoClassificacaoRepositorio(conexao)

    def buscar(
        self, id_classificacao_tributaria: int, data: date
    ) -> FundamentacaoClassificacaoDTO:
        dto = self._repo.buscar(id_classificacao_tributaria, data)
        if dto is None:
            raise FundamentacaoClassificacaoNaoEncontradaException(
                id_classificacao_tributaria, data
            )
        return dto

    def buscar_todas(self, data: date) -> list[FundamentacaoClassificacao]:
        return self._repo.buscar_todas(data)


class RedutorCompraGovernamentalService:
    def __init__(self, conexao: sqlite3.Connection | None = None) -> None:
        self._repo = _RedutorCompraGovernamentalRepositorio(conexao)

    def buscar_valor_redutor(
        self, tp_ente_gov: TipoEnteGovernamental | None, data: date
    ) -> Decimal:
        if tp_ente_gov is None:
            return ZERO
        valor = self._repo.buscar_valor_redutor(data)
        if valor is None:
            raise RuntimeError("Redutor de compra governamental não encontrada.")
        return valor


class SituacaoTributariaService:
    def __init__(self, conexao: sqlite3.Connection | None = None) -> None:
        self._repo = _SituacaoTributariaRepositorio(conexao)

    def validar_cst(self, cst: str, id_tributo: int, data: date) -> None:
        if not self._repo.existe_cst(cst, id_tributo, data):
            tributo = "Imposto Seletivo" if id_tributo == 1 else "CBS e IBS"
            raise SituacaoTributariaNaoEncontradaException(cst, tributo, data)

    def consultar_situacao_tributaria_por_codigo(
        self, cst: str, id_tributo: int, data: date
    ) -> SituacaoTributaria | None:
        return self._repo.consultar_situacao_tributaria_por_codigo(
            cst, id_tributo, data
        )


class TipoDfeService:
    def __init__(self, conexao: sqlite3.Connection | None = None) -> None:
        self._repo = _TipoDfeRepositorio(conexao)

    def buscar_por_tipo(self, tp_doc: int | None, data: date) -> TipoDfe | None:
        if tp_doc is None:
            return None
        tipo = self._repo.buscar_por_tipo(tp_doc, data)
        if tipo is None:
            raise TipoDfeNaoEncontradoException(tp_doc, data)
        if not tipo.possui_tratamento:
            raise TipoDfeNaoTratadoException(tipo)
        return tipo


class TransferenciaCBSService:
    def __init__(self, conexao: sqlite3.Connection | None = None) -> None:
        self._repo = _TransferenciaCBSRepositorio(conexao)

    def get_percentual_transferencia(self, data: date) -> Decimal:
        valor = self._repo.get_percentual_transferencia(data)
        if valor is None:
            raise RuntimeError(
                "Percentual de transferência de CBS para ente federativo não encontrada."
            )
        return valor


class TratamentoClassificacaoService:
    def __init__(self, conexao: sqlite3.Connection | None = None) -> None:
        self._repo = _TratamentoClassificacaoRepositorio(conexao)

    def buscar_tratamento_classificacao(
        self, id_classificacao_tributaria: int, data: date
    ) -> TratamentoClassificacaoDTO:
        dto = self._repo.buscar_tratamento_classificacao(id_classificacao_tributaria, data)
        if dto is None:
            raise TratamentoClassificacaoNaoEncontradoException(
                id_classificacao_tributaria, data
            )
        return dto


class TratamentoTributarioService:
    def __init__(self, conexao: sqlite3.Connection | None = None) -> None:
        self._repo = _TratamentoTributarioRepositorio(conexao)

    def buscar(self, id_tratamento: int) -> TratamentoTributario:
        entidade = self._repo.find_by_id(id_tratamento)
        if entidade is None:
            raise TratamentoTributarioNaoEncontradoException(id_tratamento)
        return entidade


class TributoSituacaoTributariaService:
    def __init__(self, conexao: sqlite3.Connection | None = None) -> None:
        self._repo = _TributoSituacaoTributariaRepositorio(conexao)

    def consultar_por_id_situacao_tributaria(
        self, id_situacao_tributaria: int, data: date
    ) -> int:
        id_tributo = self._repo.consultar_por_id_situacao_tributaria(
            id_situacao_tributaria, data
        )
        if id_tributo is None:
            raise TributoSituacaoTributariaNaoEncontradoException(
                id_tributo, id_situacao_tributaria, data
            )
        return id_tributo


class VersaoBaseDadosService:
    def __init__(self, conexao: sqlite3.Connection | None = None) -> None:
        self._repo = _VersaoBaseDadosRepositorio(conexao)

    def get_ultima_versao(self) -> VersaoBaseDados:
        versao = self._repo.find_top_by_order_by_id_desc()
        if versao is None:
            raise IllegalStateError("Nenhuma versão de base de dados encontrada")
        return versao


class UfService:
    def __init__(self, conexao: sqlite3.Connection | None = None) -> None:
        self._repo = _UfRepositorio(conexao)

    def consultar_todos(self) -> list[Uf]:
        return self._repo.consultar_todos()

    def buscar(self, sigla: str) -> int:
        codigo = self._repo.consultar_por_sigla(sigla)
        if codigo is None:
            raise UfNaoEncontradaException(sigla)
        return codigo

    def validar_uf(self, sigla: str) -> None:
        if not self._repo.existe_uf(sigla):
            raise UfNaoEncontradaException(sigla)


class MunicipioService:
    def __init__(self, conexao: sqlite3.Connection | None = None) -> None:
        self._repo = _MunicipioRepositorio(conexao)

    def consultar_todos_por_sigla_uf(self, uf: str) -> list[Municipio]:
        return self._repo.consultar_todos_por_sigla_uf(uf)

    def validar_municipio(self, codigo_municipio: int, sigla_uf: str) -> None:
        resultado = self._repo.validar_municipio(codigo_municipio, sigla_uf)
        if resultado == 1:
            raise MunicipioNaoEncontradoException(codigo_municipio)
        if resultado == 2:
            raise MunicipioNaoPertencenteException(codigo_municipio, sigla_uf)

    def buscar_uf_por_municipio(self, codigo_municipio: int) -> str:
        sigla = self._repo.buscar_sigla_uf(codigo_municipio)
        if sigla is None:
            raise MunicipioNaoEncontradoException(codigo_municipio)
        return sigla