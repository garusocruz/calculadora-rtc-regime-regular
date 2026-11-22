from datetime import date, datetime
from decimal import Decimal
from pathlib import Path
from unittest.mock import Mock

import pytest

from calculadora_rtc_regime_regular.aliquota_resultado import AliquotaResultado, FormaAplicacao
from calculadora_rtc_regime_regular.banco import conectar
from calculadora_rtc_regime_regular.pedagio import (
    AliquotaPadraoService,
    MunicipioService,
    PedagioEntrada,
    PedagioService,
    Tributo,
    TributoPedagioSaida,
    TrechoPedagioEntrada,
    TrechoPedagioSaida,
    UfService,
    pedagio_com_banco,
    totalizar_cbs,
    totalizar_ibs_estadual,
    totalizar_ibs_municipal,
)

_BANCO_OFICIAL = (
    Path(__file__).resolve().parent.parent
    / ".cache/oficial/java/calculadora/db/calculadora-pro.db"
)

SEMENTE_ARREDONDAMENTO = 20261117
MUNICIPIOS_ARREDONDAMENTO = [
    (3550308, "SP"),
    (3509502, "SP"),
    (3304557, "RJ"),
    (4313409, "RS"),
    (1200013, "AC"),
]


class _GeradorJavaRandom:
    """Mesma LCG que ``java.util.Random`` para reproduzir os pedidos do teste Java."""

    def __init__(self, semente: int) -> None:
        self._seed = (semente ^ 0x5DEECE66D) & ((1 << 48) - 1)

    def _next(self, bits: int) -> int:
        self._seed = (self._seed * 0x5DEECE66D + 0xB) & ((1 << 48) - 1)
        return self._seed >> (48 - bits)

    def next_int(self, bound: int) -> int:
        if bound <= 0:
            raise ValueError(bound)
        candidate = self._next(31)
        limite = bound - 1
        if (bound & limite) == 0:
            return int((bound * candidate) >> 31)
        while True:
            resto = candidate % bound
            if candidate - resto + limite >= 0:
                return resto
            candidate = self._next(31)


@pytest.fixture
def servico_pedagio_banco(monkeypatch: pytest.MonkeyPatch) -> PedagioService:
    if not _BANCO_OFICIAL.is_file():
        pytest.skip("calculadora-pro.db oficial ausente no cache")
    monkeypatch.setenv("CALC_DB", str(_BANCO_OFICIAL))
    with conectar() as conexao:
        yield pedagio_com_banco(conexao)


@pytest.fixture
def data_operacao() -> date:
    return date(2026, 1, 15)


def _montar_servico(aliquota: Mock) -> PedagioService:
    return PedagioService(
        AliquotaPadraoService(aliquota),
        UfService(Mock()),
        MunicipioService(Mock()),
    )


def test_buscar_aliquota_padrao_cbs_aliquota_normal(data_operacao: date) -> None:
    mock_buscar = Mock(
        return_value=AliquotaResultado(Decimal(0), Decimal("12"), FormaAplicacao.SUBSTITUICAO)
    )
    servico = _montar_servico(mock_buscar)

    resultado = servico.buscar_aliquota_padrao(Tributo.CBS, data_operacao, None, None)

    assert resultado is not None
    assert resultado == Decimal("0.12")
    mock_buscar.assert_called_once_with(Tributo.CBS.value, None, None, data_operacao)


def test_buscar_aliquota_padrao_ibs_estadual_com_codigo_uf(data_operacao: date) -> None:
    mock_buscar = Mock(
        return_value=AliquotaResultado(Decimal(0), Decimal("17.5"), FormaAplicacao.SUBSTITUICAO)
    )
    servico = _montar_servico(mock_buscar)
    codigo_uf_sp = 35

    resultado = servico.buscar_aliquota_padrao(Tributo.IBS_ESTADUAL, data_operacao, codigo_uf_sp, None)

    assert resultado == Decimal("0.175")
    mock_buscar.assert_called_once_with(Tributo.IBS_ESTADUAL.value, codigo_uf_sp, None, data_operacao)


def test_buscar_aliquota_padrao_ibs_municipal_com_codigo_municipio(data_operacao: date) -> None:
    mock_buscar = Mock(return_value=AliquotaResultado(Decimal(0), Decimal(5), FormaAplicacao.SUBSTITUICAO))
    servico = _montar_servico(mock_buscar)
    codigo_municipio_sp = 3550308

    resultado = servico.buscar_aliquota_padrao(Tributo.IBS_MUNICIPAL, data_operacao, None, codigo_municipio_sp)

    assert resultado == Decimal("0.05")
    mock_buscar.assert_called_once_with(Tributo.IBS_MUNICIPAL.value, None, codigo_municipio_sp, data_operacao)


def test_buscar_aliquota_padrao_com_acrescimo(data_operacao: date) -> None:
    mock_buscar = Mock(
        return_value=AliquotaResultado(Decimal(10), Decimal(2), FormaAplicacao.ACRESCIMO)
    )
    servico = _montar_servico(mock_buscar)

    resultado = servico.buscar_aliquota_padrao(Tributo.CBS, data_operacao, None, None)

    assert resultado == Decimal("0.12")


def test_buscar_aliquota_padrao_com_decrescimo(data_operacao: date) -> None:
    mock_buscar = Mock(
        return_value=AliquotaResultado(Decimal(15), Decimal(3), FormaAplicacao.DECRESCIMO)
    )
    servico = _montar_servico(mock_buscar)

    resultado = servico.buscar_aliquota_padrao(Tributo.CBS, data_operacao, None, None)

    assert resultado == Decimal("0.12")


def test_buscar_aliquota_padrao_aliquota_zero(data_operacao: date) -> None:
    mock_buscar = Mock(
        return_value=AliquotaResultado(Decimal(0), Decimal(0), FormaAplicacao.SUBSTITUICAO)
    )
    servico = _montar_servico(mock_buscar)

    resultado = servico.buscar_aliquota_padrao(Tributo.CBS, data_operacao, None, None)

    assert resultado == Decimal(0)


def test_buscar_aliquota_padrao_valor_com_muitas_decimais(data_operacao: date) -> None:
    mock_buscar = Mock(
        return_value=AliquotaResultado(Decimal(0), Decimal("12.34567890123"), FormaAplicacao.SUBSTITUICAO)
    )
    servico = _montar_servico(mock_buscar)

    resultado = servico.buscar_aliquota_padrao(Tributo.CBS, data_operacao, None, None)

    assert resultado == Decimal("0.1234567890123")


def test_buscar_aliquota_padrao_conversao_exata_sem_arredondamento(data_operacao: date) -> None:
    mock_buscar = Mock(
        return_value=AliquotaResultado(Decimal(0), Decimal("12.34123456785"), FormaAplicacao.SUBSTITUICAO)
    )
    servico = _montar_servico(mock_buscar)

    resultado = servico.buscar_aliquota_padrao(Tributo.CBS, data_operacao, None, None)

    assert resultado == Decimal("0.1234123456785")


def test_buscar_aliquota_padrao_datas_diferentes(data_operacao: date) -> None:
    data_2025 = date(2025, 12, 31)
    data_2026 = date(2026, 1, 1)

    mock_buscar = Mock(
        side_effect=[
            AliquotaResultado(Decimal(0), Decimal(10), FormaAplicacao.SUBSTITUICAO),
            AliquotaResultado(Decimal(0), Decimal(12), FormaAplicacao.SUBSTITUICAO),
        ]
    )
    servico = _montar_servico(mock_buscar)

    resultado_2025 = servico.buscar_aliquota_padrao(Tributo.CBS, data_2025, None, None)
    resultado_2026 = servico.buscar_aliquota_padrao(Tributo.CBS, data_2026, None, None)

    assert resultado_2025 == Decimal("0.1")
    assert resultado_2026 == Decimal("0.12")


def test_buscar_aliquota_padrao_tres_tributos_diferentes(data_operacao: date) -> None:
    codigo_uf = 35
    codigo_municipio = 3550308

    def buscar(id_tributo: int, codigo_uf_param: int | None, municipio: int | None, data: date) -> AliquotaResultado:
        if id_tributo == Tributo.CBS.value:
            return AliquotaResultado(Decimal(0), Decimal(12), FormaAplicacao.SUBSTITUICAO)
        if id_tributo == Tributo.IBS_ESTADUAL.value:
            assert codigo_uf_param == codigo_uf
            return AliquotaResultado(Decimal(0), Decimal("17.5"), FormaAplicacao.SUBSTITUICAO)
        if id_tributo == Tributo.IBS_MUNICIPAL.value:
            assert municipio == codigo_municipio
            return AliquotaResultado(Decimal(0), Decimal(5), FormaAplicacao.SUBSTITUICAO)
        raise AssertionError(id_tributo)

    servico = _montar_servico(buscar)

    valor_cbs = servico.buscar_aliquota_padrao(Tributo.CBS, data_operacao, None, None)
    valor_ibs_estadual = servico.buscar_aliquota_padrao(Tributo.IBS_ESTADUAL, data_operacao, codigo_uf, None)
    valor_ibs_municipal = servico.buscar_aliquota_padrao(Tributo.IBS_MUNICIPAL, data_operacao, None, codigo_municipio)

    assert valor_cbs == Decimal("0.12")
    assert valor_ibs_estadual == Decimal("0.175")
    assert valor_ibs_municipal == Decimal("0.05")


def _criar_trecho(cbs_calc: Decimal, ibs_est_calc: Decimal, ibs_mun_calc: Decimal) -> TrechoPedagioSaida:
    return TrechoPedagioSaida(
        numero=1,
        cbs=TributoPedagioSaida(tributo_calculado=cbs_calc),
        ibs_estadual=TributoPedagioSaida(tributo_calculado=ibs_est_calc),
        ibs_municipal=TributoPedagioSaida(tributo_calculado=ibs_mun_calc),
    )


def test_totaliza_cbs_retorna_tributo_trechos() -> None:
    trechos = [
        _criar_trecho(Decimal(10), Decimal(5), Decimal(3)),
        _criar_trecho(Decimal(20), Decimal(15), Decimal(7)),
    ]
    total_bc = Decimal(100)

    total = totalizar_cbs(trechos, total_bc)

    assert total.base_calculo == total_bc
    assert total.valor_apurado == Decimal(30)
    assert total.valor_devido == Decimal(30)
    assert total.valor_tributo == Decimal(30)


def test_totaliza_ibs_estadual_retorna_soma_tributo_trechos() -> None:
    trechos = [
        _criar_trecho(Decimal(10), Decimal(5), Decimal(3)),
        _criar_trecho(Decimal(20), Decimal(15), Decimal(7)),
    ]
    total_bc = Decimal(200)

    total = totalizar_ibs_estadual(trechos, total_bc)

    assert total.base_calculo == total_bc
    assert total.valor_apurado == Decimal(20)


def test_totaliza_ibs_municipal_retorna_soma_tributo_trechos() -> None:
    trechos = [
        _criar_trecho(Decimal(10), Decimal(5), Decimal(3)),
        _criar_trecho(Decimal(20), Decimal(15), Decimal(7)),
    ]
    total_bc = Decimal(300)

    total = totalizar_ibs_municipal(trechos, total_bc)

    assert total.base_calculo == total_bc
    assert total.valor_apurado == Decimal(10)


def test_totaliza_cbs_retorna_valores_apurado_e_devido() -> None:
    trechos = [_criar_trecho(Decimal(42), Decimal(21), Decimal(10))]
    total = totalizar_cbs(trechos, Decimal(500))

    assert total.valor_apurado == Decimal(42)
    assert total.valor_devido == Decimal(42)


def test_aviso_dados_simulados() -> None:
    mock_buscar = Mock()
    servico = _montar_servico(mock_buscar)
    from calculadora_rtc_regime_regular.pedagio import PedagioEntrada, TipoWarningDadosSimulados

    antes = PedagioEntrada(
        datetime(2026, 12, 31, 12, 0),
        1,
        "SP",
        "000",
        "000001",
        Decimal(100),
        [],
    )
    depois = PedagioEntrada(
        datetime(2027, 1, 1, 0, 0),
        1,
        "SP",
        "000",
        "000001",
        Decimal(100),
        [],
    )

    assert servico.aviso_dados_simulados(antes) is None
    assert servico.aviso_dados_simulados(depois) == TipoWarningDadosSimulados.CASO_GERAL


def _entrada_t6() -> PedagioEntrada:
    return PedagioEntrada(
        datetime.fromisoformat("2026-10-20T10:00:00-03:00"),
        3550308,
        "SP",
        "000",
        "000001",
        Decimal("200"),
        [
            TrechoPedagioEntrada(1, 3550308, "SP", Decimal(10)),
            TrechoPedagioEntrada(2, 3509502, "SP", Decimal(13)),
            TrechoPedagioEntrada(3, 3304557, "RJ", Decimal(10)),
        ],
    )


def test_t6_pedagio_parcelas_e_totais_casos_fixos(servico_pedagio_banco: PedagioService) -> None:
    saida = servico_pedagio_banco.calcular_cibs(_entrada_t6())
    trechos = sorted(saida.trechos, key=lambda t: t.numero)

    assert saida.total is not None
    assert saida.total.cbs_total is not None
    assert saida.total.ibs_estadual_total is not None
    assert saida.total.ibs_municipal_total is not None

    assert saida.total.cbs_total.valor_tributo == Decimal("1.80")
    assert trechos[0].cbs is not None and trechos[0].cbs.tributo_calculado == Decimal("0.55")
    assert trechos[1].cbs is not None and trechos[1].cbs.tributo_calculado == Decimal("0.71")
    assert trechos[2].cbs is not None and trechos[2].cbs.tributo_calculado == Decimal("0.54")

    assert saida.total.ibs_estadual_total.valor_tributo == Decimal("0.20")
    assert trechos[0].ibs_estadual is not None and trechos[0].ibs_estadual.tributo_calculado == Decimal("0.06")
    assert trechos[1].ibs_estadual is not None and trechos[1].ibs_estadual.tributo_calculado == Decimal("0.08")
    assert trechos[2].ibs_estadual is not None and trechos[2].ibs_estadual.tributo_calculado == Decimal("0.06")

    assert saida.total.ibs_municipal_total.valor_tributo == Decimal("0.00")
    for trecho in trechos:
        assert trecho.ibs_municipal is not None
        assert trecho.ibs_municipal.tributo_calculado == Decimal("0.00")

    assert trechos[0].cbs is not None and trechos[0].cbs.aliquota_efetiva == Decimal("0.2727")
    assert trechos[1].cbs is not None and trechos[1].cbs.aliquota_efetiva == Decimal("0.3545")
    assert trechos[2].cbs is not None and trechos[2].cbs.aliquota_efetiva == Decimal("0.2727")
    assert trechos[0].cbs.aliquota == Decimal("0.9")
    assert trechos[0].ibs_estadual is not None and trechos[0].ibs_estadual.aliquota == Decimal("0.1")


def test_pedagio_parcelas_somam_total_em_pedidos_sorteados(servico_pedagio_banco: PedagioService) -> None:
    gerador = _GeradorJavaRandom(SEMENTE_ARREDONDAMENTO)
    pares = (
        ("cbs", "cbs_total"),
        ("ibs_estadual", "ibs_estadual_total"),
        ("ibs_municipal", "ibs_municipal_total"),
    )
    for _ in range(300):
        quantidade = 1 + gerador.next_int(8)
        base = Decimal(1 + gerador.next_int(50_000_000)).scaleb(-2)
        trechos: list[TrechoPedagioEntrada] = []
        for numero in range(1, quantidade + 1):
            municipio, uf = MUNICIPIOS_ARREDONDAMENTO[gerador.next_int(len(MUNICIPIOS_ARREDONDAMENTO))]
            extensao = Decimal(1 + gerador.next_int(500_000)).scaleb(-gerador.next_int(4))
            trechos.append(TrechoPedagioEntrada(numero, municipio, uf, extensao))
        entrada = PedagioEntrada(
            datetime(2026, 10, 20, 10, 0),
            3550308,
            "SP",
            "000",
            "000001",
            base,
            trechos,
        )
        saida = servico_pedagio_banco.calcular_cibs(entrada)
        assert saida.total is not None
        for campo, total_campo in pares:
            soma = Decimal(0)
            for trecho in saida.trechos:
                detalhe = getattr(trecho, campo)
                assert detalhe is not None and detalhe.tributo_calculado is not None
                assert detalhe.tributo_calculado.as_tuple().exponent == -2
                assert detalhe.aliquota_efetiva is not None
                assert detalhe.aliquota_efetiva.as_tuple().exponent == -4
                soma += detalhe.tributo_calculado
            total = getattr(saida.total, total_campo)
            assert total is not None and total.valor_tributo is not None
            assert soma == total.valor_tributo