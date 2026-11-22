"""Paridade com Teste_CalculoCbsIbsService_BuscarAliquotaPadrao (CalculoCbsIbsService)."""

from datetime import date
from decimal import Decimal

from calculadora_rtc_regime_regular.aliquota_resultado import AliquotaResultado, FormaAplicacao
from calculadora_rtc_regime_regular.cbs_ibs import buscar_aliquota_padrao

_ID_TRIBUTO = 1
_CODIGO_UF = 35
_CODIGO_MUNICIPIO = 3550308
_DATA = date(2026, 1, 1)


def _buscar_fixo(dto: AliquotaResultado):
    def buscar(
        id_tributo: int,
        codigo_uf: int | None,
        codigo_municipio: int | None,
        data: date,
    ) -> AliquotaResultado:
        return dto

    return buscar


def teste_BuscarAliquotaPadrao_SemValorPadrao() -> None:
    dto = AliquotaResultado(Decimal("26.50"))
    resultado = buscar_aliquota_padrao(_ID_TRIBUTO, _CODIGO_UF, _CODIGO_MUNICIPIO, _DATA, _buscar_fixo(dto))
    assert resultado is not None
    assert resultado == Decimal("0.265")


def teste_BuscarAliquotaPadrao_ComAcrescimo() -> None:
    dto = AliquotaResultado(Decimal("26.50"), Decimal("1.50"), FormaAplicacao.ACRESCIMO)
    resultado = buscar_aliquota_padrao(_ID_TRIBUTO, _CODIGO_UF, _CODIGO_MUNICIPIO, _DATA, _buscar_fixo(dto))
    assert resultado is not None
    assert resultado == Decimal("0.28")


def teste_BuscarAliquotaPadrao_ComDecrescimo() -> None:
    dto = AliquotaResultado(Decimal("26.50"), Decimal("1.50"), FormaAplicacao.DECRESCIMO)
    resultado = buscar_aliquota_padrao(_ID_TRIBUTO, _CODIGO_UF, _CODIGO_MUNICIPIO, _DATA, _buscar_fixo(dto))
    assert resultado is not None
    assert resultado == Decimal("0.25")


def teste_BuscarAliquotaPadrao_ComSubstituicao() -> None:
    dto = AliquotaResultado(Decimal("26.50"), Decimal("12.75"), FormaAplicacao.SUBSTITUICAO)
    resultado = buscar_aliquota_padrao(_ID_TRIBUTO, _CODIGO_UF, _CODIGO_MUNICIPIO, _DATA, _buscar_fixo(dto))
    assert resultado is not None
    assert resultado == Decimal("0.1275")


def teste_BuscarAliquotaPadrao_ValorZero() -> None:
    dto = AliquotaResultado(Decimal("0.00"))
    resultado = buscar_aliquota_padrao(_ID_TRIBUTO, _CODIGO_UF, _CODIGO_MUNICIPIO, _DATA, _buscar_fixo(dto))
    assert resultado is not None
    assert resultado == Decimal("0")


def teste_BuscarAliquotaPadrao_PrecisaoDecimal() -> None:
    dto = AliquotaResultado(Decimal("17.345"))
    resultado = buscar_aliquota_padrao(_ID_TRIBUTO, _CODIGO_UF, _CODIGO_MUNICIPIO, _DATA, _buscar_fixo(dto))
    assert resultado is not None
    assert resultado == Decimal("0.17345")


def teste_BuscarAliquotaPadrao_TributoIBS() -> None:
    id_tributo_ibs = 2
    dto = AliquotaResultado(Decimal("25.00"))
    resultado = buscar_aliquota_padrao(id_tributo_ibs, _CODIGO_UF, _CODIGO_MUNICIPIO, _DATA, _buscar_fixo(dto))
    assert resultado is not None
    assert resultado == Decimal("0.25")


def teste_BuscarAliquotaPadrao_UFDiferente() -> None:
    codigo_uf_rj = 33
    dto = AliquotaResultado(Decimal("24.00"))
    resultado = buscar_aliquota_padrao(_ID_TRIBUTO, codigo_uf_rj, _CODIGO_MUNICIPIO, _DATA, _buscar_fixo(dto))
    assert resultado is not None
    assert resultado == Decimal("0.24")


def teste_BuscarAliquotaPadrao_DataDiferente() -> None:
    data_futura = date(2027, 6, 15)
    dto = AliquotaResultado(Decimal("28.00"))
    resultado = buscar_aliquota_padrao(_ID_TRIBUTO, _CODIGO_UF, _CODIGO_MUNICIPIO, data_futura, _buscar_fixo(dto))
    assert resultado is not None
    assert resultado == Decimal("0.28")


def teste_BuscarAliquotaPadrao_SubstituicaoPorZero() -> None:
    dto = AliquotaResultado(Decimal("26.50"), Decimal("0.00"), FormaAplicacao.SUBSTITUICAO)
    resultado = buscar_aliquota_padrao(_ID_TRIBUTO, _CODIGO_UF, _CODIGO_MUNICIPIO, _DATA, _buscar_fixo(dto))
    assert resultado is not None
    assert resultado == Decimal("0")


def teste_BuscarAliquotaPadrao_AcrescimoComPrecisao() -> None:
    dto = AliquotaResultado(Decimal("15.123"), Decimal("2.877"), FormaAplicacao.ACRESCIMO)
    resultado = buscar_aliquota_padrao(_ID_TRIBUTO, _CODIGO_UF, _CODIGO_MUNICIPIO, _DATA, _buscar_fixo(dto))
    assert resultado is not None
    assert resultado == Decimal("0.18")


def teste_BuscarAliquotaPadrao_DecrescimoComPrecisao() -> None:
    dto = AliquotaResultado(Decimal("20.500"), Decimal("5.250"), FormaAplicacao.DECRESCIMO)
    resultado = buscar_aliquota_padrao(_ID_TRIBUTO, _CODIGO_UF, _CODIGO_MUNICIPIO, _DATA, _buscar_fixo(dto))
    assert resultado is not None
    assert resultado == Decimal("0.1525")


def teste_BuscarAliquotaPadrao_VerificaDivisaoPor100() -> None:
    dto = AliquotaResultado(Decimal("100.00"))
    resultado = buscar_aliquota_padrao(_ID_TRIBUTO, _CODIGO_UF, _CODIGO_MUNICIPIO, _DATA, _buscar_fixo(dto))
    assert resultado is not None
    assert resultado == Decimal("1.0000")


def teste_BuscarAliquotaPadrao_VerificaChamadaAoService() -> None:
    dto = AliquotaResultado(Decimal("26.50"))
    chamadas: list[tuple[int, int | None, int | None, date]] = []

    def buscar(
        id_tributo: int,
        codigo_uf: int | None,
        codigo_municipio: int | None,
        data: date,
    ) -> AliquotaResultado:
        chamadas.append((id_tributo, codigo_uf, codigo_municipio, data))
        return dto

    buscar_aliquota_padrao(_ID_TRIBUTO, _CODIGO_UF, _CODIGO_MUNICIPIO, _DATA, buscar)
    assert len(chamadas) == 1
    assert chamadas[0] == (_ID_TRIBUTO, _CODIGO_UF, _CODIGO_MUNICIPIO, _DATA)