"""Paridade com Teste_DadosAbertosService_ConsultarAliquota (pin f1eebd7)."""

from __future__ import annotations

from datetime import date
from decimal import Decimal
from unittest.mock import Mock

import pytest

from calculadora_rtc_regime_regular.aliquota_resultado import AliquotaResultado, FormaAplicacao
from calculadora_rtc_regime_regular.dados_abertos import DadosAbertosService

_FQCN = "br.gov.serpro.rtc.testesunitarios.service.Teste_DadosAbertosService_ConsultarAliquota"


def _java(record_xml_attribute, method: str) -> None:
    record_xml_attribute("classname", _FQCN)
    record_xml_attribute("name", method)


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


def teste_ConsultarAliquota_SemValorPadrao_DeveRetornarApenasReferencia(
    record_xml_attribute,
    servico: DadosAbertosService,
    aliquota_padrao_mock: Mock,
    id_tributo: int,
    codigo_uf: int,
    codigo_municipio: int,
    data_ref: date,
) -> None:
    _java(record_xml_attribute, "teste_ConsultarAliquota_SemValorPadrao_DeveRetornarApenasReferencia")
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


def teste_ConsultarAliquota_ComAcrescimo_DeveRetornarAliquotaPropria(
    record_xml_attribute,
    servico: DadosAbertosService,
    aliquota_padrao_mock: Mock,
    id_tributo: int,
    codigo_uf: int,
    codigo_municipio: int,
    data_ref: date,
) -> None:
    _java(record_xml_attribute, "teste_ConsultarAliquota_ComAcrescimo_DeveRetornarAliquotaPropria")
    aliquota_padrao_mock.buscar_aliquota.return_value = AliquotaResultado(
        Decimal("10.00"), Decimal("2.00"), FormaAplicacao.ACRESCIMO
    )

    resultado = servico.consultar_aliquota(id_tributo, codigo_uf, codigo_municipio, data_ref)

    assert resultado.aliquota_referencia == Decimal("10.00")
    assert resultado.aliquota_propria == Decimal("12.00")
    assert resultado.forma_aplicacao is FormaAplicacao.ACRESCIMO
    aliquota_padrao_mock.buscar_aliquota.assert_called_once_with(
        id_tributo, codigo_uf, codigo_municipio, data_ref
    )


def teste_ConsultarAliquota_ComDecrescimo_DeveRetornarAliquotaPropria(
    record_xml_attribute,
    servico: DadosAbertosService,
    aliquota_padrao_mock: Mock,
    id_tributo: int,
    codigo_uf: int,
    codigo_municipio: int,
    data_ref: date,
) -> None:
    _java(record_xml_attribute, "teste_ConsultarAliquota_ComDecrescimo_DeveRetornarAliquotaPropria")
    aliquota_padrao_mock.buscar_aliquota.return_value = AliquotaResultado(
        Decimal("15.00"), Decimal("3.00"), FormaAplicacao.DECRESCIMO
    )

    resultado = servico.consultar_aliquota(id_tributo, codigo_uf, codigo_municipio, data_ref)

    assert resultado.aliquota_referencia == Decimal("15.00")
    assert resultado.aliquota_propria == Decimal("12.00")
    assert resultado.forma_aplicacao is FormaAplicacao.DECRESCIMO
    aliquota_padrao_mock.buscar_aliquota.assert_called_once_with(
        id_tributo, codigo_uf, codigo_municipio, data_ref
    )


def teste_ConsultarAliquota_ComSubstituicao_DeveRetornarAliquotaPropria(
    record_xml_attribute,
    servico: DadosAbertosService,
    aliquota_padrao_mock: Mock,
    id_tributo: int,
    codigo_uf: int,
    codigo_municipio: int,
    data_ref: date,
) -> None:
    _java(record_xml_attribute, "teste_ConsultarAliquota_ComSubstituicao_DeveRetornarAliquotaPropria")
    valor_padrao = Decimal("8.50")
    aliquota_padrao_mock.buscar_aliquota.return_value = AliquotaResultado(
        Decimal("10.00"), valor_padrao, FormaAplicacao.SUBSTITUICAO
    )

    resultado = servico.consultar_aliquota(id_tributo, codigo_uf, codigo_municipio, data_ref)

    assert resultado.aliquota_referencia == Decimal("10.00")
    assert resultado.aliquota_propria == valor_padrao
    assert resultado.forma_aplicacao is FormaAplicacao.SUBSTITUICAO
    aliquota_padrao_mock.buscar_aliquota.assert_called_once_with(
        id_tributo, codigo_uf, codigo_municipio, data_ref
    )


def teste_ConsultarAliquota_ComValorPadraoZero_ComAcrescimo_DeveRetornarZero(
    record_xml_attribute,
    servico: DadosAbertosService,
    aliquota_padrao_mock: Mock,
    id_tributo: int,
    codigo_uf: int,
    codigo_municipio: int,
    data_ref: date,
) -> None:
    _java(record_xml_attribute, "teste_ConsultarAliquota_ComValorPadraoZero_ComAcrescimo_DeveRetornarZero")
    aliquota_padrao_mock.buscar_aliquota.return_value = AliquotaResultado(
        Decimal("12.00"), Decimal("0.00"), FormaAplicacao.ACRESCIMO
    )

    resultado = servico.consultar_aliquota(id_tributo, codigo_uf, codigo_municipio, data_ref)

    assert resultado.aliquota_referencia == Decimal("12.00")
    assert resultado.aliquota_propria == Decimal("12.00")
    assert resultado.forma_aplicacao is FormaAplicacao.ACRESCIMO


def teste_ConsultarAliquota_ComValoresDecimais_DevePreservarPrecisao(
    record_xml_attribute,
    servico: DadosAbertosService,
    aliquota_padrao_mock: Mock,
    id_tributo: int,
    codigo_uf: int,
    codigo_municipio: int,
    data_ref: date,
) -> None:
    _java(record_xml_attribute, "teste_ConsultarAliquota_ComValoresDecimais_DevePreservarPrecisao")
    aliquota_padrao_mock.buscar_aliquota.return_value = AliquotaResultado(
        Decimal("12.345"), Decimal("1.155"), FormaAplicacao.ACRESCIMO
    )

    resultado = servico.consultar_aliquota(id_tributo, codigo_uf, codigo_municipio, data_ref)

    assert resultado.aliquota_referencia == Decimal("12.345")
    assert resultado.aliquota_propria == Decimal("13.500")


def teste_ConsultarAliquota_ParaDiferentesTributos_DeveRetornarCorreto(
    record_xml_attribute,
    servico: DadosAbertosService,
    aliquota_padrao_mock: Mock,
    codigo_uf: int,
    codigo_municipio: int,
    data_ref: date,
) -> None:
    _java(record_xml_attribute, "teste_ConsultarAliquota_ParaDiferentesTributos_DeveRetornarCorreto")
    id_tributo_ibs = 3
    aliquota_padrao_mock.buscar_aliquota.return_value = AliquotaResultado(
        Decimal("17.50"), Decimal("0.50"), FormaAplicacao.DECRESCIMO
    )

    resultado = servico.consultar_aliquota(id_tributo_ibs, codigo_uf, codigo_municipio, data_ref)

    assert resultado.aliquota_referencia == Decimal("17.50")
    assert resultado.aliquota_propria == Decimal("17.00")
    assert resultado.forma_aplicacao is FormaAplicacao.DECRESCIMO


def teste_ConsultarAliquota_ParaDiferentesUfs_DeveRetornarCorreto(
    record_xml_attribute,
    servico: DadosAbertosService,
    aliquota_padrao_mock: Mock,
    id_tributo: int,
    data_ref: date,
) -> None:
    _java(record_xml_attribute, "teste_ConsultarAliquota_ParaDiferentesUfs_DeveRetornarCorreto")
    codigo_uf_rj = 33
    codigo_municipio_rj = 3304557
    valor_padrao = Decimal("9.00")
    aliquota_padrao_mock.buscar_aliquota.return_value = AliquotaResultado(
        Decimal("11.00"), valor_padrao, FormaAplicacao.SUBSTITUICAO
    )

    resultado = servico.consultar_aliquota(id_tributo, codigo_uf_rj, codigo_municipio_rj, data_ref)

    assert resultado.aliquota_referencia == Decimal("11.00")
    assert resultado.aliquota_propria == valor_padrao


def teste_ConsultarAliquota_ParaDiferentesDatas_DeveRetornarCorreto(
    record_xml_attribute,
    servico: DadosAbertosService,
    aliquota_padrao_mock: Mock,
    id_tributo: int,
    codigo_uf: int,
    codigo_municipio: int,
) -> None:
    _java(record_xml_attribute, "teste_ConsultarAliquota_ParaDiferentesDatas_DeveRetornarCorreto")
    data_futura = date(2027, 6, 15)
    valor_referencia = Decimal("13.00")
    aliquota_padrao_mock.buscar_aliquota.return_value = AliquotaResultado(valor_referencia)

    resultado = servico.consultar_aliquota(id_tributo, codigo_uf, codigo_municipio, data_futura)

    assert resultado.aliquota_referencia == valor_referencia
    assert resultado.aliquota_propria is None


def teste_ConsultarAliquota_ComSubstituicaoZero_DeveRetornarZero(
    record_xml_attribute,
    servico: DadosAbertosService,
    aliquota_padrao_mock: Mock,
    id_tributo: int,
    codigo_uf: int,
    codigo_municipio: int,
    data_ref: date,
) -> None:
    _java(record_xml_attribute, "teste_ConsultarAliquota_ComSubstituicaoZero_DeveRetornarZero")
    aliquota_padrao_mock.buscar_aliquota.return_value = AliquotaResultado(
        Decimal("10.00"), Decimal(0), FormaAplicacao.SUBSTITUICAO
    )

    resultado = servico.consultar_aliquota(id_tributo, codigo_uf, codigo_municipio, data_ref)

    assert resultado.aliquota_referencia == Decimal("10.00")
    assert resultado.aliquota_propria == Decimal(0)
    assert resultado.forma_aplicacao is FormaAplicacao.SUBSTITUICAO


def teste_ConsultarAliquota_VerificaChamadaCorretaAoService(
    record_xml_attribute,
    servico: DadosAbertosService,
    aliquota_padrao_mock: Mock,
    id_tributo: int,
    codigo_uf: int,
    codigo_municipio: int,
    data_ref: date,
) -> None:
    _java(record_xml_attribute, "teste_ConsultarAliquota_VerificaChamadaCorretaAoService")
    aliquota_padrao_mock.buscar_aliquota.return_value = AliquotaResultado(Decimal("12.00"))

    servico.consultar_aliquota(id_tributo, codigo_uf, codigo_municipio, data_ref)

    aliquota_padrao_mock.buscar_aliquota.assert_called_once_with(
        id_tributo, codigo_uf, codigo_municipio, data_ref
    )