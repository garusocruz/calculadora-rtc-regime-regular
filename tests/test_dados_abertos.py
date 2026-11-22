"""Unit tests ported from Java DadosAbertosService (pin f1eebd7ce3157423b1a6aaca7dc1d6c3395452c4)."""

from __future__ import annotations

from datetime import date
from decimal import Decimal
from pathlib import Path
from unittest.mock import Mock

import pytest

from calculadora_rtc_regime_regular.aliquota_resultado import AliquotaResultado, FormaAplicacao
from calculadora_rtc_regime_regular.dados_abertos import DadosAbertosService, convert_to_big_decimal


@pytest.fixture
def id_tributo() -> int:
    return 2


@pytest.fixture
def codigo_uf() -> int:
    return 35


@pytest.fixture
def codigo_municipio() -> int:
    return 3550308


@pytest.fixture
def data_ref() -> date:
    return date(2026, 1, 15)


@pytest.fixture
def aliquota_padrao_mock() -> Mock:
    return Mock()


@pytest.fixture
def servico(aliquota_padrao_mock: Mock) -> DadosAbertosService:
    return DadosAbertosService(aliquota_padrao=aliquota_padrao_mock)


def test_consultar_aliquota_sem_valor_padrao_retorna_apenas_referencia(
    servico: DadosAbertosService,
    aliquota_padrao_mock: Mock,
    id_tributo: int,
    codigo_uf: int,
    codigo_municipio: int,
    data_ref: date,
) -> None:
    valor_referencia = Decimal("12.00")
    aliquota_padrao_mock.buscar_aliquota.return_value = AliquotaResultado(valor_referencia)

    resultado = servico.consultar_aliquota(id_tributo, codigo_uf, codigo_municipio, data_ref)

    assert resultado is not None
    assert resultado.aliquota_referencia == valor_referencia
    assert resultado.aliquota_propria is None
    assert resultado.forma_aplicacao is None
    aliquota_padrao_mock.buscar_aliquota.assert_called_once_with(
        id_tributo, codigo_uf, codigo_municipio, data_ref
    )


def test_consultar_aliquota_com_acrescimo(
    servico: DadosAbertosService,
    aliquota_padrao_mock: Mock,
    id_tributo: int,
    codigo_uf: int,
    codigo_municipio: int,
    data_ref: date,
) -> None:
    aliquota_padrao_mock.buscar_aliquota.return_value = AliquotaResultado(
        Decimal("10.00"), Decimal("2.00"), FormaAplicacao.ACRESCIMO
    )

    resultado = servico.consultar_aliquota(id_tributo, codigo_uf, codigo_municipio, data_ref)

    assert resultado.aliquota_referencia == Decimal("10.00")
    assert resultado.aliquota_propria == Decimal("12.00")
    assert resultado.forma_aplicacao is FormaAplicacao.ACRESCIMO


def test_consultar_aliquota_com_decrescimo(
    servico: DadosAbertosService,
    aliquota_padrao_mock: Mock,
    id_tributo: int,
    codigo_uf: int,
    codigo_municipio: int,
    data_ref: date,
) -> None:
    aliquota_padrao_mock.buscar_aliquota.return_value = AliquotaResultado(
        Decimal("15.00"), Decimal("3.00"), FormaAplicacao.DECRESCIMO
    )

    resultado = servico.consultar_aliquota(id_tributo, codigo_uf, codigo_municipio, data_ref)

    assert resultado.aliquota_propria == Decimal("12.00")
    assert resultado.forma_aplicacao is FormaAplicacao.DECRESCIMO


def test_consultar_aliquota_com_substituicao(
    servico: DadosAbertosService,
    aliquota_padrao_mock: Mock,
    id_tributo: int,
    codigo_uf: int,
    codigo_municipio: int,
    data_ref: date,
) -> None:
    valor_padrao = Decimal("8.50")
    aliquota_padrao_mock.buscar_aliquota.return_value = AliquotaResultado(
        Decimal("10.00"), valor_padrao, FormaAplicacao.SUBSTITUICAO
    )

    resultado = servico.consultar_aliquota(id_tributo, codigo_uf, codigo_municipio, data_ref)

    assert resultado.aliquota_propria == valor_padrao
    assert resultado.forma_aplicacao is FormaAplicacao.SUBSTITUICAO


def test_consultar_aliquota_valor_padrao_zero_acrescimo(
    servico: DadosAbertosService,
    aliquota_padrao_mock: Mock,
    id_tributo: int,
    codigo_uf: int,
    codigo_municipio: int,
    data_ref: date,
) -> None:
    aliquota_padrao_mock.buscar_aliquota.return_value = AliquotaResultado(
        Decimal("12.00"), Decimal("0.00"), FormaAplicacao.ACRESCIMO
    )

    resultado = servico.consultar_aliquota(id_tributo, codigo_uf, codigo_municipio, data_ref)

    assert resultado.aliquota_propria == Decimal("12.00")
    assert resultado.forma_aplicacao is FormaAplicacao.ACRESCIMO


def test_consultar_aliquota_preserva_precisao_decimal(
    servico: DadosAbertosService,
    aliquota_padrao_mock: Mock,
    id_tributo: int,
    codigo_uf: int,
    codigo_municipio: int,
    data_ref: date,
) -> None:
    aliquota_padrao_mock.buscar_aliquota.return_value = AliquotaResultado(
        Decimal("12.345"), Decimal("1.155"), FormaAplicacao.ACRESCIMO
    )

    resultado = servico.consultar_aliquota(id_tributo, codigo_uf, codigo_municipio, data_ref)

    assert resultado.aliquota_referencia == Decimal("12.345")
    assert resultado.aliquota_propria == Decimal("13.500")


def test_consultar_aliquota_ibs(
    servico: DadosAbertosService,
    aliquota_padrao_mock: Mock,
    codigo_uf: int,
    codigo_municipio: int,
    data_ref: date,
) -> None:
    id_tributo_ibs = 3
    aliquota_padrao_mock.buscar_aliquota.return_value = AliquotaResultado(
        Decimal("17.50"), Decimal("0.50"), FormaAplicacao.DECRESCIMO
    )

    resultado = servico.consultar_aliquota(id_tributo_ibs, codigo_uf, codigo_municipio, data_ref)

    assert resultado.aliquota_propria == Decimal("17.00")
    assert resultado.forma_aplicacao is FormaAplicacao.DECRESCIMO


def test_consultar_aliquota_outra_uf(
    servico: DadosAbertosService,
    aliquota_padrao_mock: Mock,
    id_tributo: int,
    data_ref: date,
) -> None:
    codigo_uf_rj = 33
    codigo_municipio_rj = 3304557
    valor_padrao = Decimal("9.00")
    aliquota_padrao_mock.buscar_aliquota.return_value = AliquotaResultado(
        Decimal("11.00"), valor_padrao, FormaAplicacao.SUBSTITUICAO
    )

    resultado = servico.consultar_aliquota(id_tributo, codigo_uf_rj, codigo_municipio_rj, data_ref)

    assert resultado.aliquota_propria == valor_padrao


def test_consultar_aliquota_data_futura(
    servico: DadosAbertosService,
    aliquota_padrao_mock: Mock,
    id_tributo: int,
    codigo_uf: int,
    codigo_municipio: int,
) -> None:
    data_futura = date(2027, 6, 15)
    valor_referencia = Decimal("13.00")
    aliquota_padrao_mock.buscar_aliquota.return_value = AliquotaResultado(valor_referencia)

    resultado = servico.consultar_aliquota(id_tributo, codigo_uf, codigo_municipio, data_futura)

    assert resultado.aliquota_referencia == valor_referencia
    assert resultado.aliquota_propria is None


def test_consultar_aliquota_substituicao_zero(
    servico: DadosAbertosService,
    aliquota_padrao_mock: Mock,
    id_tributo: int,
    codigo_uf: int,
    codigo_municipio: int,
    data_ref: date,
) -> None:
    aliquota_padrao_mock.buscar_aliquota.return_value = AliquotaResultado(
        Decimal("10.00"), Decimal(0), FormaAplicacao.SUBSTITUICAO
    )

    resultado = servico.consultar_aliquota(id_tributo, codigo_uf, codigo_municipio, data_ref)

    assert resultado.aliquota_propria == Decimal(0)
    assert resultado.forma_aplicacao is FormaAplicacao.SUBSTITUICAO


def test_consultar_aliquota_verifica_chamada_ao_service(
    servico: DadosAbertosService,
    aliquota_padrao_mock: Mock,
    id_tributo: int,
    codigo_uf: int,
    codigo_municipio: int,
    data_ref: date,
) -> None:
    aliquota_padrao_mock.buscar_aliquota.return_value = AliquotaResultado(Decimal("12.00"))

    servico.consultar_aliquota(id_tributo, codigo_uf, codigo_municipio, data_ref)

    aliquota_padrao_mock.buscar_aliquota.assert_called_once_with(
        id_tributo, codigo_uf, codigo_municipio, data_ref
    )


def test_float_convertido_pelo_texto_do_numero() -> None:
    assert convert_to_big_decimal(float(0.365)) == Decimal("0.365")
    assert convert_to_big_decimal(float(123.4567)) == Decimal("123.4567")
    assert convert_to_big_decimal(float(60)) == Decimal("60.0")


def test_demais_tipos_preservam_valor() -> None:
    assert convert_to_big_decimal(0.365) == Decimal("0.365")
    assert convert_to_big_decimal(Decimal("0.365")) == Decimal("0.365")
    assert convert_to_big_decimal("0.365") == Decimal("0.365")
    assert convert_to_big_decimal(60) == Decimal("60")
    assert convert_to_big_decimal(60) == Decimal("60")
    assert convert_to_big_decimal(None) is None
    assert convert_to_big_decimal("não é número") is None


_DB = (
    Path(__file__).resolve().parents[1]
    / ".cache/oficial/java/calculadora/db/calculadora-pro.db"
)
_DATA = date(2027, 1, 1)
_NCM = "09024000"
_NBS = "102020000"
_C_CLASS_TRIB = "000001"
_ID_ST_CBS_IBS = 2
_ID_ST_IS = 1


@pytest.fixture
def servico_db(monkeypatch: pytest.MonkeyPatch) -> DadosAbertosService:
    if not _DB.is_file():
        pytest.skip("calculadora-pro.db ausente")
    monkeypatch.setenv("CALC_DB", str(_DB))
    return DadosAbertosService()


def test_consultar_ufs_no_banco(servico_db: DadosAbertosService) -> None:
    ufs = servico_db.consultar_ufs()
    assert len(ufs) == 28
    assert all(u.sigla and u.nome for u in ufs)


def test_consultar_municipios_ac(servico_db: DadosAbertosService) -> None:
    mun = servico_db.consultar_municipios_por_sigla_uf("AC")
    assert mun
    assert all(m.codigo and m.nome for m in mun)


def test_consultar_situacoes_cbs_e_is(servico_db: DadosAbertosService) -> None:
    cbs = servico_db.consultar_situacoes_tributarias(_ID_ST_CBS_IBS, _DATA)
    is_ = servico_db.consultar_situacoes_tributarias(_ID_ST_IS, _DATA)
    assert cbs and is_
    assert all(s.codigo for s in cbs)


def test_consultar_classificacoes_cbs_ibs_e_is(servico_db: DadosAbertosService) -> None:
    cbs = servico_db.consultar_classificacoes_tributarias_cbs_ibs(_DATA)
    is_ = servico_db.consultar_classificacoes_tributarias_imposto_seletivo(_DATA)
    assert len(cbs) > 100
    assert len(is_) > 10
    assert cbs[0].codigo and cbs[0].tipos_dfe_classificacao is not None


def test_consultar_ncm_e_nbs(servico_db: DadosAbertosService) -> None:
    ncm = servico_db.consultar_ncm(_NCM, _DATA)
    assert ncm.tributado_pelo_imposto_seletivo is False
    ncm_is = servico_db.consultar_ncm("24021000", _DATA)
    assert ncm_is.tributado_pelo_imposto_seletivo is True
    assert ncm_is.tem_aliquota_ad_valorem and ncm_is.aliquota_ad_valorem is None
    nbs = servico_db.consultar_nbs(_NBS, _DATA)
    assert nbs.tributado_pelo_imposto_seletivo is False


def test_consultar_fundamentacoes_legais(servico_db: DadosAbertosService) -> None:
    itens = servico_db.consultar_fundamentacoes_legais(_DATA)
    assert itens
    assert all(f.conjunto_tributo == "CBS e IBS" for f in itens)


def test_validar_ncm_e_nbs_aplicavel(servico_db: DadosAbertosService) -> None:
    assert servico_db.validar_ncm_aplicavel(
        _C_CLASS_TRIB, _NCM, _DATA
    ).valido is True
    assert servico_db.validar_nbs_aplicavel(
        _C_CLASS_TRIB, _NBS, _DATA
    ).valido is True


def test_classificacao_por_codigo(servico_db: DadosAbertosService) -> None:
    cbs = servico_db.consultar_classificacao_tributaria_cbs_ibs_por_codigo(
        _C_CLASS_TRIB, _DATA
    )
    assert cbs.codigo == _C_CLASS_TRIB