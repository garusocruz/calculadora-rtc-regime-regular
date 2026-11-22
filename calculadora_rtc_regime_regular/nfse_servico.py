"""NFS-e — indicador, local, classificações e validação (pin f1eebd7, ``NfseService``)."""

from __future__ import annotations

import re
import sqlite3
from dataclasses import dataclass
from datetime import date
from enum import Enum
from typing import Any

from calculadora_rtc_regime_regular.banco import conectar
from calculadora_rtc_regime_regular.base_calculo_service import CampoInvalido
from calculadora_rtc_regime_regular.dados_abertos import NbsNaoEncontradaException

CCLASSTRIB_FALLBACK = "000001"


class IndicadorOperacaoNaoEncontradoException(Exception):
    def __init__(self, c_ind_op: str, data: date) -> None:
        super().__init__(
            f"Indicador de operação '{c_ind_op}' não encontrado para a data {data}"
        )


class LocalFornecimento(Enum):
    LOCAL_1 = (1, "Endereço diverso do fornecedor, adquirente ou destinatário")
    LOCAL_2 = (2, "Local da prestação do serviço diverso do estabelecimento do fornecedor")
    LOCAL_3 = (3, "Endereço do destinatário")
    LOCAL_4 = (4, "Endereço fornecido para entrega do bem")
    LOCAL_5 = (5, "Estabelecimento do fornecedor como local da prestação")
    LOCAL_6 = (6, "Local do porto como local da prestação")
    LOCAL_7 = (
        7,
        "Local da prestação correspondente à extensão da via explorada, proporcionalmente ao território dos entes tributantes",
    )
    LOCAL_8 = (8, "Local da retirada do bem")
    LOCAL_9 = (9, "Local de início do transporte")
    LOCAL_10 = (
        10,
        "Local do domicílio principal do destinatário residente ou domiciliado no País, caso o adquirente não seja residente ou domiciliado no País",
    )
    LOCAL_11 = (
        11,
        "Local do domicílio principal do adquirente residente ou domiciliado no País. Nas aquisições indicadas no art. 11, §4º, II, considera-se domicílio principal do adquirente o estabelecimento matriz",
    )
    LOCAL_12 = (12, "local do domicílio principal do destinatário residente ou domiciliado no País")
    LOCAL_13 = (13, "Local do evento a que se refere o serviço")
    LOCAL_14 = (14, "Localidade do imóvel")
    LOCAL_15 = (
        15,
        "Estabelecimento do fornecedor como o local da entrega ou disponibilização do bem ao destinatário",
    )
    LOCAL_16 = (16, "Local da realização da operação e sua retirada")
    LOCAL_17 = (
        17,
        "Endereço do destinatário fornecido para entrega ou disponibilização (assim considerado o destino final indicado pelo adquirente)",
    )
    LOCAL_18 = (18, "Local onde se encontra o bem móvel material")
    LOCAL_19 = (19, "Local onde se encontra o bem móvel material (Local da retirada)")
    LOCAL_20 = (20, "Local do domicílio principal do adquirente (estabelecimento matriz)")
    LOCAL_21 = (21, "Domicílio principal do destinatário")
    LOCAL_22 = (22, "Local de instalação do terminal")
    LOCAL_23 = (
        23,
        "Local do domicílio principal do adquirente (assim considerada a matriz), nas aquisições realizadas de forma centralizada por contribuinte sujeito ao regime regular do IBS e da CBS que possui mais de um estabelecimento e que não estejam sujeitas a vedação à apropriação de créditos",
    )
    LOCAL_24 = (24, "Local da entrega ou disponibilização")
    LOCAL_25 = (
        25,
        "Local do estabelecimento principal do adquirente (assim considerada a matriz), conforme §4º do art. 11",
    )
    LOCAL_26 = (
        26,
        "Local do estabelecimento do agente ou de seus representados que figurem na posição devedora da liquidação financeira apurada pela Câmara de Comercialização de Energia Elétrica",
    )
    LOCAL_27 = (27, "Local do estabelecimento principal do fornecedor")
    LOCAL_28 = (28, "Local do estabelecimento principal do adquirente")
    LOCAL_29 = (29, "Localidade do Imóvel (BICE)")

    @property
    def codigo(self) -> int:
        return self.value[0]

    @property
    def descricao(self) -> str:
        return self.value[1]

    @classmethod
    def from_codigo(cls, codigo: int) -> LocalFornecimento:
        for lf in cls:
            if lf.codigo == codigo:
                return lf
        raise ValueError(f"Código inválido: {codigo}")


class LocalIncidencia(Enum):
    LOCAL_1 = (1, "Endereço do Destinatário")
    LOCAL_2 = (2, "Endereço do Tomador/Adquirente")
    LOCAL_3 = (3, "Estabelecimento do Prestador/Fornecedor")
    LOCAL_4 = (4, "Local da Prestação")
    LOCAL_5 = (5, "Local do Evento")
    LOCAL_6 = (6, "Localidade do Imóvel")
    LOCAL_7 = (7, "Localização do Trecho")

    @property
    def codigo(self) -> int:
        return self.value[0]

    @property
    def descricao(self) -> str:
        return self.value[1]

    @classmethod
    def from_codigo(cls, codigo: int) -> LocalIncidencia:
        for li in cls:
            if li.codigo == codigo:
                return li
        raise ValueError(f"Código inválido: {codigo}")


@dataclass
class NfseLocalOperacaoSaida:
    c_ind_op: str
    data_ocorrencia_fato_gerador: date
    codigo_local_fornecimento: LocalFornecimento | None
    local_fornecimento: str | None
    codigo_local_incidencia: LocalIncidencia | None
    local_incidencia: str | None


@dataclass
class NfseIndicadorOperacaoSaida:
    c_ind_op: str
    tipo_operacao: str | None
    codigo_local_fornecimento: LocalFornecimento | None
    local_fornecimento: str | None
    codigo_local_incidencia: LocalIncidencia | None
    local_incidencia: str | None
    prestacao_servico_onerosa: bool | None = None
    adquirente_exterior: bool | None = None


@dataclass
class NfseSituacaoClassificacaoSaida:
    codigo_situacao_tributaria: str
    descricao_situacao_tributaria: str
    codigo_classificacao_tributaria: str
    descricao_classificacao_tributaria: str


@dataclass
class NfseValidacaoIndicadorOperacaoEntrada:
    nbs: str
    c_class_trib: str
    c_ind_op: str
    data_ocorrencia_fato_gerador: date
    c_trib_nac: str | None = None


@dataclass
class NfseValidacaoIndicadorOperacaoSaida:
    c_ind_op: str
    c_class_trib: str
    nbs: str
    data_ocorrencia_fato_gerador: date
    valido: bool
    c_trib_nac: str | None = None


def _data_str(data: date) -> str:
    return data.isoformat()


def _parse_data_query(valor: date | str | None, nome_param: str) -> date:
    if nome_param == "dataOcorrenciaFatoGerador":
        msg_obrigatorio = "O campo dataOcorrenciaFatoGerador é obrigatório"
    else:
        msg_obrigatorio = "O campo data é obrigatório"
    if valor is None:
        raise CampoInvalido(msg_obrigatorio)
    if isinstance(valor, date):
        return valor
    try:
        return date.fromisoformat(str(valor))
    except (TypeError, ValueError):
        raise CampoInvalido(f"Parâmetro inválido [{nome_param}: {valor}]") from None


def _validar_c_ind_op(c_ind_op: str | None) -> str:
    if c_ind_op is None or not str(c_ind_op).strip():
        raise CampoInvalido("O campo cIndOp é obrigatório")
    texto = str(c_ind_op).strip()
    if not re.fullmatch(r"\d{6}", texto):
        raise CampoInvalido("O campo cIndOp deve conter exatamente 6 dígitos numéricos")
    return texto


def _validar_nbs_consulta(nbs: str | None) -> str:
    if nbs is None or not str(nbs).strip():
        raise CampoInvalido("O campo nbs é obrigatório")
    texto = str(nbs).strip()
    if not re.fullmatch(r"\d{9}", texto):
        raise CampoInvalido("O código NBS deve conter exatamente 9 dígitos numéricos")
    return texto


def formatar_c_trib_nac(c_trib_nac: str | None) -> str | None:
    if c_trib_nac is None or c_trib_nac == "":
        return None
    if len(c_trib_nac) == 4:
        primeiro = str(int(c_trib_nac[:2]))
        return f"{primeiro}.{c_trib_nac[2:4]}"
    if len(c_trib_nac) == 6:
        primeiro = str(int(c_trib_nac[:2]))
        return f"{primeiro}.{c_trib_nac[2:4]}.{c_trib_nac[4:6]}"
    return None


class _NfseRepositorio:
    def __init__(self, conexao: sqlite3.Connection) -> None:
        self._conexao = conexao

    def existe_nbs(self, nbs: str, data: date) -> bool:
        d = _data_str(data)
        row = self._conexao.execute(
            """
            SELECT EXISTS (
                SELECT 1 FROM NBS n
                WHERE n.NBS_CD = ?
                  AND ? BETWEEN n.NBS_INICIO_VIGENCIA AND COALESCE(n.NBS_FIM_VIGENCIA, ?)
            )
            """,
            (nbs, d, d),
        ).fetchone()
        return bool(row[0]) if row else False

    def validar_combinacao_existe(
        self,
        nbs: str,
        c_class_trib: str,
        c_ind_op: str,
        c_trib_nac: str | None,
        data: str,
    ) -> int:
        row = self._conexao.execute(
            """
            SELECT EXISTS (
                SELECT 1
                FROM CLASSIF_NBS_INDOP_LC c
                INNER JOIN CLASSIFICACAO_TRIBUTARIA ct ON c.CNIL_CLTR_ID = ct.CLTR_ID
                INNER JOIN INDICADOR_OPERACAO_IBS_CBS io ON c.CNIL_IOIC_ID = io.IOIC_ID
                WHERE c.CNIL_NBS_CD = ?
                  AND ct.CLTR_CD = ?
                  AND io.IOIC_CD = ?
                  AND (? IS NULL OR c.CNIL_LSLC_CD = ?)
                  AND c.CNIL_INICIO_VIGENCIA <= ?
                  AND (c.CNIL_FIM_VIGENCIA IS NULL
                       OR c.CNIL_FIM_VIGENCIA >= ?)
            )
            """,
            (nbs, c_class_trib, c_ind_op, c_trib_nac, c_trib_nac, data, data),
        ).fetchone()
        return int(row[0]) if row else 0

    def buscar_local_operacao_por_ind_op(
        self, c_ind_op: str, data: str
    ) -> tuple[Any, Any] | None:
        return self._conexao.execute(
            """
            SELECT
                io.IOIC_CD_LOCAL_FORNECIMENTO_DFE,
                io.IOIC_CD_LOCAL_INCIDENCIA
            FROM INDICADOR_OPERACAO_IBS_CBS io
            WHERE io.IOIC_CD = ?
              AND ? BETWEEN io.IOIC_INICIO_VIGENCIA AND COALESCE(io.IOIC_FIM_VIGENCIA, ?)
            """,
            (c_ind_op, data, data),
        ).fetchone()

    def buscar_indicador_operacao_por_data(self, data: str) -> list[tuple[Any, ...]]:
        return self._conexao.execute(
            """
            SELECT
                io.IOIC_CD,
                io.IOIC_TIPO_OPERACAO,
                io.IOIC_CD_LOCAL_FORNECIMENTO_DFE,
                io.IOIC_LOCAL_INCIDENCIA,
                io.IOIC_CD_LOCAL_INCIDENCIA,
                NULL,
                NULL
            FROM INDICADOR_OPERACAO_IBS_CBS io
            WHERE io.IOIC_TIPO_OPERACAO IS NOT NULL
              AND ? BETWEEN io.IOIC_INICIO_VIGENCIA AND COALESCE(io.IOIC_FIM_VIGENCIA, ?)
            ORDER BY io.IOIC_CD
            """,
            (data, data),
        ).fetchall()

    def buscar_indicador_operacao_por_data_com_nbs(
        self, data: str, nbs: str
    ) -> list[tuple[Any, ...]]:
        return self._conexao.execute(
            """
            SELECT DISTINCT
                io.IOIC_CD,
                io.IOIC_TIPO_OPERACAO,
                io.IOIC_CD_LOCAL_FORNECIMENTO_DFE,
                io.IOIC_LOCAL_INCIDENCIA,
                io.IOIC_CD_LOCAL_INCIDENCIA,
                c.CNIL_IN_PS_ONEROSA,
                c.CNIL_IN_ADQ_EXTERIOR
            FROM INDICADOR_OPERACAO_IBS_CBS io
                INNER JOIN CLASSIF_NBS_INDOP_LC c ON io.IOIC_ID = c.CNIL_IOIC_ID
            WHERE c.CNIL_NBS_CD = ?
              AND ? BETWEEN io.IOIC_INICIO_VIGENCIA AND COALESCE(io.IOIC_FIM_VIGENCIA, ?)
              AND ? BETWEEN c.CNIL_INICIO_VIGENCIA AND COALESCE(c.CNIL_FIM_VIGENCIA, ?)
              AND io.IOIC_TIPO_OPERACAO IS NOT NULL
            ORDER BY io.IOIC_CD
            """,
            (nbs, data, data, data, data),
        ).fetchall()

    def buscar_situacoes_classificacoes_por_nbs_e_data(
        self, nbs: str, data: str
    ) -> list[NfseSituacaoClassificacaoSaida]:
        rows = self._conexao.execute(
            """
            SELECT DISTINCT
                st.SITR_CD AS codigoSituacaoTributaria,
                st.SITR_DESCRICAO AS descricaoSituacaoTributaria,
                ct.CLTR_CD AS codigoClassificacaoTributaria,
                ct.CLTR_DESCRICAO AS descricaoClassificacaoTributaria
            FROM CLASSIF_NBS_INDOP_LC c
                INNER JOIN CLASSIFICACAO_TRIBUTARIA ct ON c.CNIL_CLTR_ID = ct.CLTR_ID
                INNER JOIN SITUACAO_TRIBUTARIA st ON ct.CLTR_SITR_ID = st.SITR_ID
            WHERE c.CNIL_NBS_CD = ?
              AND ? BETWEEN c.CNIL_INICIO_VIGENCIA AND COALESCE(c.CNIL_FIM_VIGENCIA, ?)
              AND ? BETWEEN ct.CLTR_INICIO_VIGENCIA AND COALESCE(ct.CLTR_FIM_VIGENCIA, ?)
              AND ? BETWEEN st.SITR_INICIO_VIGENCIA AND COALESCE(st.SITR_FIM_VIGENCIA, ?)
            ORDER BY ct.CLTR_CD, st.SITR_CD
            """,
            (nbs, data, data, data, data, data, data),
        ).fetchall()
        return [
            NfseSituacaoClassificacaoSaida(
                codigo_situacao_tributaria=row[0],
                descricao_situacao_tributaria=row[1],
                codigo_classificacao_tributaria=row[2],
                descricao_classificacao_tributaria=row[3],
            )
            for row in rows
        ]

    def buscar_situacao_classificacao_por_classificacao(
        self, codigo_classificacao: str, data: str
    ) -> NfseSituacaoClassificacaoSaida | None:
        row = self._conexao.execute(
            """
            SELECT
                st.SITR_CD AS codigoSituacaoTributaria,
                st.SITR_DESCRICAO AS descricaoSituacaoTributaria,
                ct.CLTR_CD AS codigoClassificacaoTributaria,
                ct.CLTR_DESCRICAO AS descricaoClassificacaoTributaria
            FROM CLASSIFICACAO_TRIBUTARIA ct
            INNER JOIN SITUACAO_TRIBUTARIA st ON ct.CLTR_SITR_ID = st.SITR_ID
            WHERE ct.CLTR_CD = ?
              AND ? BETWEEN ct.CLTR_INICIO_VIGENCIA AND COALESCE(ct.CLTR_FIM_VIGENCIA, ?)
              AND ? BETWEEN st.SITR_INICIO_VIGENCIA AND COALESCE(st.SITR_FIM_VIGENCIA, ?)
            LIMIT 1
            """,
            (codigo_classificacao, data, data, data, data),
        ).fetchone()
        if not row:
            return None
        return NfseSituacaoClassificacaoSaida(
            codigo_situacao_tributaria=row[0],
            descricao_situacao_tributaria=row[1],
            codigo_classificacao_tributaria=row[2],
            descricao_classificacao_tributaria=row[3],
        )


def _map_indicador(row: tuple[Any, ...]) -> NfseIndicadorOperacaoSaida:
    lf = LocalFornecimento.from_codigo(int(row[2])) if row[2] is not None else None
    li = LocalIncidencia.from_codigo(int(row[4])) if row[4] is not None else None
    ps_onerosa: bool | None = None
    adq_ext: bool | None = None
    if row[5] is not None:
        ps_onerosa = int(row[5]) == 1
    if row[6] is not None:
        adq_ext = int(row[6]) == 1
    return NfseIndicadorOperacaoSaida(
        c_ind_op=row[0],
        tipo_operacao=row[1],
        codigo_local_fornecimento=lf,
        local_fornecimento=lf.descricao if lf else None,
        codigo_local_incidencia=li,
        local_incidencia=li.descricao if li else None,
        prestacao_servico_onerosa=ps_onerosa,
        adquirente_exterior=adq_ext,
    )


class NfseServico:
    def __init__(self, conexao: sqlite3.Connection | None = None) -> None:
        self._conexao_externa = conexao

    def validar_indicador_operacao(
        self, entrada: NfseValidacaoIndicadorOperacaoEntrada
    ) -> NfseValidacaoIndicadorOperacaoSaida:
        c_trib_nac_formatado = formatar_c_trib_nac(entrada.c_trib_nac)
        data_str = _data_str(entrada.data_ocorrencia_fato_gerador)
        with self._conexao() as conexao:
            repo = _NfseRepositorio(conexao)
            resultado = repo.validar_combinacao_existe(
                entrada.nbs,
                entrada.c_class_trib,
                entrada.c_ind_op,
                c_trib_nac_formatado,
                data_str,
            )
        return NfseValidacaoIndicadorOperacaoSaida(
            c_ind_op=entrada.c_ind_op,
            c_class_trib=entrada.c_class_trib,
            nbs=entrada.nbs,
            c_trib_nac=entrada.c_trib_nac,
            data_ocorrencia_fato_gerador=entrada.data_ocorrencia_fato_gerador,
            valido=resultado == 1,
        )

    def consultar_local_operacao(
        self,
        c_ind_op: str | None,
        data_ocorrencia_fato_gerador: date | str | None,
    ) -> NfseLocalOperacaoSaida:
        c_ind_op = _validar_c_ind_op(c_ind_op)
        data_ocorrencia_fato_gerador = _parse_data_query(
            data_ocorrencia_fato_gerador, "dataOcorrenciaFatoGerador"
        )
        data_str = _data_str(data_ocorrencia_fato_gerador)
        with self._conexao() as conexao:
            repo = _NfseRepositorio(conexao)
            row = repo.buscar_local_operacao_por_ind_op(c_ind_op, data_str)
        if row is None:
            raise IndicadorOperacaoNaoEncontradoException(c_ind_op, data_ocorrencia_fato_gerador)
        local_fornecimento = (
            LocalFornecimento.from_codigo(int(row[0])) if row[0] is not None else None
        )
        local_incidencia = (
            LocalIncidencia.from_codigo(int(row[1])) if row[1] is not None else None
        )
        return NfseLocalOperacaoSaida(
            c_ind_op=c_ind_op,
            data_ocorrencia_fato_gerador=data_ocorrencia_fato_gerador,
            codigo_local_fornecimento=local_fornecimento,
            local_fornecimento=local_fornecimento.descricao if local_fornecimento else None,
            codigo_local_incidencia=local_incidencia,
            local_incidencia=local_incidencia.descricao if local_incidencia else None,
        )

    def consultar_indicador_operacao(
        self, data_ocorrencia_fato_gerador: date, nbs: str | None = None
    ) -> list[NfseIndicadorOperacaoSaida]:
        data_str = _data_str(data_ocorrencia_fato_gerador)
        with self._conexao() as conexao:
            repo = _NfseRepositorio(conexao)
            if nbs:
                if not repo.existe_nbs(nbs, data_ocorrencia_fato_gerador):
                    raise NbsNaoEncontradaException(nbs, data_ocorrencia_fato_gerador)
                raw = repo.buscar_indicador_operacao_por_data_com_nbs(data_str, nbs)
                if not raw:
                    raw = repo.buscar_indicador_operacao_por_data(data_str)
            else:
                raw = repo.buscar_indicador_operacao_por_data(data_str)
        return [_map_indicador(row) for row in raw]

    def consultar_situacoes_classificacoes_por_nbs(
        self, nbs: str | None, data: date | str | None
    ) -> list[NfseSituacaoClassificacaoSaida]:
        nbs = _validar_nbs_consulta(nbs)
        data = _parse_data_query(data, "data")
        data_str = _data_str(data)
        with self._conexao() as conexao:
            repo = _NfseRepositorio(conexao)
            if not repo.existe_nbs(nbs, data):
                raise NbsNaoEncontradaException(nbs, data)
            resultado = repo.buscar_situacoes_classificacoes_por_nbs_e_data(nbs, data_str)
            if not resultado:
                fallback = repo.buscar_situacao_classificacao_por_classificacao(
                    CCLASSTRIB_FALLBACK, data_str
                )
                if fallback is None:
                    return []
                resultado = [fallback]
        return resultado

    def _conexao(self) -> Any:
        if self._conexao_externa is not None:
            from contextlib import nullcontext

            return nullcontext(self._conexao_externa)
        return conectar()


def nfse_com_banco(conexao: sqlite3.Connection) -> NfseServico:
    return NfseServico(conexao)