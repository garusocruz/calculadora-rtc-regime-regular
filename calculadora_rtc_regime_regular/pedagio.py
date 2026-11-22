"""CBS e IBS em operações de pedágio.

Pin ``f1eebd7ce3157423b1a6aaca7dc1d6c3395452c4``, ``PedagioService`` e totais de
``TributoTotalPedagioOutput`` / ``TotalPedagioOutput``. Consultas ao SQLite
oficial ficam atrás de callables injetáveis.
"""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass, field
from datetime import date, datetime
from decimal import Decimal
from enum import Enum

from calculadora_rtc_regime_regular.aliquota_resultado import AliquotaResultado, FormaAplicacao
from calculadora_rtc_regime_regular.arredondamento import (
    arredondar_aliquota_publicada,
    dividir,
    fracao_para_percentual,
    multiplicar,
    percentual_para_fracao,
    ratear_valor_fiscal,
)
from calculadora_rtc_regime_regular.base_calculo_service import CampoInvalido

ZERO = Decimal(0)

BuscaAliquotaPadrao = Callable[[int, int | None, int | None, date], AliquotaResultado]
BuscaUf = Callable[[str], int]
ValidaMunicipio = Callable[[int, str], None]


class Tributo(Enum):
    CBS = 2
    IBS_ESTADUAL = 3
    IBS_MUNICIPAL = 4


class TipoWarningDadosSimulados(Enum):
    CASO_GERAL = 1


class AliquotaNaoEncontrada(Exception):
    def __init__(
        self,
        id_tributo: int,
        codigo_uf: int | None,
        municipio: int | None,
        data: date,
    ) -> None:
        self.id_tributo = id_tributo
        self.codigo_uf = codigo_uf
        self.municipio = municipio
        self.data = data
        super().__init__(id_tributo, codigo_uf, municipio, data)


class UfNaoEncontrada(Exception):
    def __init__(self, sigla: str) -> None:
        self.sigla = sigla
        super().__init__(sigla)


class MunicipioNaoEncontrado(Exception):
    def __init__(self, codigo: int) -> None:
        self.codigo = codigo
        super().__init__(codigo)


class MunicipioNaoPertencente(Exception):
    def __init__(self, codigo: int, sigla_uf: str) -> None:
        self.codigo = codigo
        self.sigla_uf = sigla_uf
        super().__init__(codigo, sigla_uf)


@dataclass
class TrechoPedagioEntrada:
    numero: int
    municipio: int
    uf: str
    extensao: Decimal


@dataclass
class PedagioEntrada:
    data_hora_emissao: datetime
    codigo_municipio_origem: int
    uf_municipio_origem: str
    cst: str
    c_class_trib: str
    base_calculo: Decimal
    trechos: list[TrechoPedagioEntrada]

    @property
    def extensao_total(self) -> Decimal:
        total = ZERO
        for trecho in self.trechos:
            if trecho.extensao is not None:
                total += trecho.extensao
        return total


@dataclass(frozen=True)
class TributoPedagioSaida:
    aliquota: Decimal | None = None
    aliquota_efetiva: Decimal | None = None
    tributo_calculado: Decimal | None = None


@dataclass(frozen=True)
class TrechoPedagioSaida:
    numero: int
    uf: str | None = None
    municipio: int | None = None
    base_calculo: Decimal | None = None
    extensao_trecho: Decimal | None = None
    cbs: TributoPedagioSaida | None = None
    ibs_estadual: TributoPedagioSaida | None = None
    ibs_municipal: TributoPedagioSaida | None = None


@dataclass(frozen=True)
class TributoTotalPedagioSaida:
    base_calculo: Decimal | None = None
    valor_apurado: Decimal | None = None
    valor_devido: Decimal | None = None
    valor_tributo: Decimal | None = None
    valor_montante_desonerado: Decimal | None = None


@dataclass(frozen=True)
class TotalPedagioSaida:
    cbs_total: TributoTotalPedagioSaida | None = None
    ibs_estadual_total: TributoTotalPedagioSaida | None = None
    ibs_municipal_total: TributoTotalPedagioSaida | None = None


@dataclass(frozen=True)
class PedagioSaida:
    data_hora_emissao: datetime | None = None
    municipio_origem: int | None = None
    uf_municipio_origem: str | None = None
    cst: str | None = None
    c_class_trib: str | None = None
    base_calculo: Decimal | None = None
    extensao_total: Decimal | None = None
    trechos: list[TrechoPedagioSaida] = field(default_factory=list)
    total: TotalPedagioSaida | None = None


def totalizar_cbs(trechos: list[TrechoPedagioSaida], total_base_calculo: Decimal) -> TributoTotalPedagioSaida:
    return _valor_total_iva(trechos, total_base_calculo, lambda t: t.cbs)


def totalizar_ibs_estadual(trechos: list[TrechoPedagioSaida], total_base_calculo: Decimal) -> TributoTotalPedagioSaida:
    return _valor_total_iva(trechos, total_base_calculo, lambda t: t.ibs_estadual)


def totalizar_ibs_municipal(trechos: list[TrechoPedagioSaida], total_base_calculo: Decimal) -> TributoTotalPedagioSaida:
    return _valor_total_iva(trechos, total_base_calculo, lambda t: t.ibs_municipal)


def montar_total_pedagio(trechos: list[TrechoPedagioSaida]) -> TotalPedagioSaida:
    total_base_calculo = trechos[0].base_calculo
    assert total_base_calculo is not None
    return TotalPedagioSaida(
        cbs_total=totalizar_cbs(trechos, total_base_calculo),
        ibs_estadual_total=totalizar_ibs_estadual(trechos, total_base_calculo),
        ibs_municipal_total=totalizar_ibs_municipal(trechos, total_base_calculo),
    )


class AliquotaPadraoService:
    """Consulta alíquota padrão por tributo, UF, município e data."""

    def __init__(self, buscar: BuscaAliquotaPadrao) -> None:
        self._buscar = buscar

    def buscar_aliquota(
        self,
        id_tributo: int,
        codigo_uf: int | None,
        municipio: int | None,
        data: date,
    ) -> AliquotaResultado:
        resultado = self._buscar(id_tributo, codigo_uf, municipio, data)
        if resultado is None:
            raise AliquotaNaoEncontrada(id_tributo, codigo_uf, municipio, data)
        return resultado


class UfService:
    def __init__(self, buscar: BuscaUf) -> None:
        self._buscar = buscar

    def buscar(self, sigla: str) -> int:
        return self._buscar(sigla)


class MunicipioService:
    def __init__(self, validar: ValidaMunicipio) -> None:
        self._validar = validar

    def validar_municipio(self, codigo_municipio: int, sigla_uf: str) -> None:
        self._validar(codigo_municipio, sigla_uf)


class PedagioService:
    def __init__(
        self,
        aliquota_padrao: AliquotaPadraoService,
        uf: UfService,
        municipio: MunicipioService,
    ) -> None:
        self._aliquota_padrao = aliquota_padrao
        self._uf = uf
        self._municipio = municipio

    def calcular_cibs(self, operacao: PedagioEntrada) -> PedagioSaida:
        _validar_numeros_unicos(operacao)
        self._municipio.validar_municipio(operacao.codigo_municipio_origem, operacao.uf_municipio_origem)
        for trecho in operacao.trechos:
            self._municipio.validar_municipio(trecho.municipio, trecho.uf)

        trechos_pedagio = self._trechos_pedagio(operacao)
        return PedagioSaida(
            cst=operacao.cst,
            c_class_trib=operacao.c_class_trib,
            extensao_total=operacao.extensao_total,
            data_hora_emissao=operacao.data_hora_emissao,
            municipio_origem=operacao.codigo_municipio_origem,
            base_calculo=operacao.base_calculo,
            uf_municipio_origem=operacao.uf_municipio_origem,
            trechos=trechos_pedagio,
            total=montar_total_pedagio(trechos_pedagio),
        )

    def buscar_aliquota_padrao(
        self,
        tributo: Tributo,
        data: date,
        codigo_uf: int | None,
        codigo_municipio: int | None,
    ) -> Decimal | None:
        aliquota = self._aliquota_padrao.buscar_aliquota(tributo.value, codigo_uf, codigo_municipio, data)
        return percentual_para_fracao(aliquota.valor_aplicavel())

    def aviso_dados_simulados(self, operacao: PedagioEntrada) -> TipoWarningDadosSimulados | None:
        data_operacao = operacao.data_hora_emissao.date()
        if data_operacao < date(2027, 1, 1):
            return None
        return TipoWarningDadosSimulados.CASO_GERAL

    def _trechos_pedagio(self, operacao: PedagioEntrada) -> list[TrechoPedagioSaida]:
        extensao_total = operacao.extensao_total
        base_calculo_cibs = operacao.base_calculo
        data_fato_gerador = operacao.data_hora_emissao.date()

        trechos = sorted(operacao.trechos, key=lambda t: t.numero)

        aliquotas_cbs: list[Decimal] = []
        aliquotas_ibs_estadual: list[Decimal] = []
        aliquotas_ibs_municipal: list[Decimal] = []
        for trecho in trechos:
            codigo_uf = self._uf.buscar(trecho.uf)

            valor_cbs = self.buscar_aliquota_padrao(Tributo.CBS, data_fato_gerador, None, None)
            valor_ibs_estadual = self.buscar_aliquota_padrao(
                Tributo.IBS_ESTADUAL, data_fato_gerador, codigo_uf, None
            )
            valor_ibs_municipal = self.buscar_aliquota_padrao(
                Tributo.IBS_MUNICIPAL, data_fato_gerador, None, trecho.municipio
            )

            if valor_cbs is None or valor_ibs_estadual is None or valor_ibs_municipal is None:
                raise CampoInvalido("Erro ao obter alíquotas")

            aliquotas_cbs.append(valor_cbs)
            aliquotas_ibs_estadual.append(valor_ibs_estadual)
            aliquotas_ibs_municipal.append(valor_ibs_municipal)

        cbs = _ratear_tributo(trechos, aliquotas_cbs, base_calculo_cibs, extensao_total)
        ibs_estadual = _ratear_tributo(trechos, aliquotas_ibs_estadual, base_calculo_cibs, extensao_total)
        ibs_municipal = _ratear_tributo(trechos, aliquotas_ibs_municipal, base_calculo_cibs, extensao_total)

        saida: list[TrechoPedagioSaida] = []
        for indice, trecho in enumerate(trechos):
            saida.append(
                TrechoPedagioSaida(
                    numero=trecho.numero,
                    uf=trecho.uf,
                    municipio=trecho.municipio,
                    base_calculo=base_calculo_cibs,
                    cbs=cbs[indice],
                    ibs_estadual=ibs_estadual[indice],
                    ibs_municipal=ibs_municipal[indice],
                    extensao_trecho=trecho.extensao,
                )
            )
        return saida


def _ratear_tributo(
    trechos: list[TrechoPedagioEntrada],
    aliquotas: list[Decimal],
    base_calculo: Decimal,
    extensao_total: Decimal,
) -> list[TributoPedagioSaida]:
    parcelas_exatas: list[Decimal] = []
    for indice, trecho in enumerate(trechos):
        parcelas_exatas.append(
            dividir(
                multiplicar(multiplicar(base_calculo, aliquotas[indice]), trecho.extensao),
                extensao_total,
            )
            or ZERO
        )
    parcelas = ratear_valor_fiscal(parcelas_exatas)

    tributos: list[TributoPedagioSaida] = []
    for indice, trecho in enumerate(trechos):
        aliquota_efetiva = arredondar_aliquota_publicada(
            fracao_para_percentual(
                dividir(multiplicar(aliquotas[indice], trecho.extensao), extensao_total)
            )
        )
        tributos.append(
            TributoPedagioSaida(
                aliquota=fracao_para_percentual(aliquotas[indice]),
                aliquota_efetiva=aliquota_efetiva,
                tributo_calculado=parcelas[indice],
            )
        )
    return tributos


def _validar_numeros_unicos(operacao: PedagioEntrada) -> None:
    vistos: set[int] = set()
    for trecho in operacao.trechos:
        if trecho.numero in vistos:
            raise CampoInvalido(f"Número de trecho duplicado: {trecho.numero}")
        vistos.add(trecho.numero)


def _totalizar_iva(
    trechos: list[TrechoPedagioSaida],
    tributo_de: Callable[[TrechoPedagioSaida], TributoPedagioSaida | None],
) -> Decimal:
    total = ZERO
    for trecho in trechos:
        tributo = tributo_de(trecho)
        if tributo is None or tributo.tributo_calculado is None:
            continue
        total += tributo.tributo_calculado
    return total


def _valor_total_iva(
    trechos: list[TrechoPedagioSaida],
    total_base_calculo: Decimal,
    tributo_de: Callable[[TrechoPedagioSaida], TributoPedagioSaida | None],
) -> TributoTotalPedagioSaida:
    total_tributo = _totalizar_iva(trechos, tributo_de)
    return TributoTotalPedagioSaida(
        base_calculo=total_base_calculo,
        valor_apurado=total_tributo,
        valor_tributo=total_tributo,
        valor_devido=total_tributo,
    )


def _forma_aplicacao_de_texto(valor: str | None) -> FormaAplicacao | None:
    if valor is None:
        return None
    return FormaAplicacao[valor]


def buscar_aliquota_sqlite(
    id_tributo: int,
    codigo_uf: int | None,
    municipio: int | None,
    data: date,
    conexao,
) -> AliquotaResultado | None:
    consulta = """
        SELECT r.ALRE_VALOR, p.ALPA_VALOR, p.ALPA_FORMA_APLICACAO
        FROM ALIQUOTA_REFERENCIA r
        LEFT JOIN ALIQUOTA_PADRAO p
            ON p.ALPA_ALRE_ID = r.ALRE_ID
            AND (
                (? IS NULL AND p.ALPA_MUNI_CD IS NULL)
                OR (? IS NOT NULL AND p.ALPA_MUNI_CD = ?)
            )
            AND (
                (? IS NULL AND p.ALPA_UF_CD IS NULL)
                OR (? IS NOT NULL AND p.ALPA_UF_CD = ?)
            )
            AND p.ALPA_INICIO_VIGENCIA <= ?
            AND (p.ALPA_FIM_VIGENCIA IS NULL OR p.ALPA_FIM_VIGENCIA >= ?)
        WHERE r.ALRE_TBTO_ID = ?
            AND r.ALRE_INICIO_VIGENCIA <= ?
            AND (r.ALRE_FIM_VIGENCIA IS NULL OR r.ALRE_FIM_VIGENCIA >= ?)
        LIMIT 1
    """
    linha = conexao.execute(
        consulta,
        (
            municipio,
            municipio,
            municipio,
            codigo_uf,
            codigo_uf,
            codigo_uf,
            data.isoformat(),
            data.isoformat(),
            id_tributo,
            data.isoformat(),
            data.isoformat(),
        ),
    ).fetchone()
    if linha is None:
        return None
    referencia = Decimal(str(linha[0]))
    padrao = Decimal(str(linha[1])) if linha[1] is not None else None
    forma = _forma_aplicacao_de_texto(linha[2])
    return AliquotaResultado(referencia, padrao, forma)


def buscar_uf_sqlite(sigla: str, conexao) -> int | None:
    linha = conexao.execute(
        "SELECT UF_CD FROM UF WHERE UF_SIGLA = UPPER(?)",
        (sigla,),
    ).fetchone()
    if linha is None:
        return None
    return int(linha[0])


def validar_municipio_sqlite(codigo_municipio: int, sigla_uf: str, conexao) -> None:
    linha = conexao.execute(
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
    ).fetchone()
    if linha is None or linha[0] == 1:
        raise MunicipioNaoEncontrado(codigo_municipio)
    if linha[0] == 2:
        raise MunicipioNaoPertencente(codigo_municipio, sigla_uf)


def pedagio_com_banco(conexao) -> PedagioService:
    def buscar_aliquota(id_tributo: int, codigo_uf: int | None, municipio: int | None, data: date) -> AliquotaResultado:
        resultado = buscar_aliquota_sqlite(id_tributo, codigo_uf, municipio, data, conexao)
        if resultado is None:
            raise AliquotaNaoEncontrada(id_tributo, codigo_uf, municipio, data)
        return resultado

    def buscar_uf(sigla: str) -> int:
        codigo = buscar_uf_sqlite(sigla, conexao)
        if codigo is None:
            raise UfNaoEncontrada(sigla)
        return codigo

    def validar_municipio(codigo: int, sigla: str) -> None:
        validar_municipio_sqlite(codigo, sigla, conexao)

    return PedagioService(
        AliquotaPadraoService(buscar_aliquota),
        UfService(buscar_uf),
        MunicipioService(validar_municipio),
    )