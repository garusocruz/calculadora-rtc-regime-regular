"""Paridade com TributacaoCompraGovernamentalDomainTest (roc, compra governamental)."""

from __future__ import annotations

from datetime import date
from decimal import Decimal

import pytest

from calculadora_rtc_regime_regular.roc import (
    TipoEnteGovernamental,
    TributacaoCompraGovernamentalDomain,
    ZERO,
)

VBC = Decimal("1000.00")
_PARAM_IDS = [str(i) for i in range(1, 8)]


def d(value: str) -> Decimal:
    return Decimal(value)


def _criar_domain_base() -> TributacaoCompraGovernamentalDomain:
    return TributacaoCompraGovernamentalDomain(
        p_aliq_cbs=d("20.00"),
        v_trib_cbs=d("200.00"),
        p_aliq_ibs_uf=d("10.00"),
        v_trib_ibs_uf=d("100.00"),
        p_aliq_ibs_mun=d("5.00"),
        v_trib_ibs_mun=d("50.00"),
    )


def _valor_ou_zero(valor: Decimal | None) -> Decimal:
    return ZERO if valor is None else valor


def _somar_percentuais(domain: TributacaoCompraGovernamentalDomain) -> Decimal:
    return (
        _valor_ou_zero(domain.p_aliq_cbs)
        + _valor_ou_zero(domain.p_aliq_ibs_uf)
        + _valor_ou_zero(domain.p_aliq_ibs_mun)
    )


def _somar_valores(domain: TributacaoCompraGovernamentalDomain) -> Decimal:
    return (
        _valor_ou_zero(domain.v_trib_cbs)
        + _valor_ou_zero(domain.v_trib_ibs_uf)
        + _valor_ou_zero(domain.v_trib_ibs_mun)
    )


def _assert_resultado(
    resultado: TributacaoCompraGovernamentalDomain,
    esperado_p_aliq_cbs: Decimal,
    esperado_v_trib_cbs: Decimal,
    esperado_p_aliq_ibs_uf: Decimal,
    esperado_v_trib_ibs_uf: Decimal,
    esperado_p_aliq_ibs_mun: Decimal,
    esperado_v_trib_ibs_mun: Decimal,
) -> None:
    assert resultado.p_aliq_cbs == esperado_p_aliq_cbs
    assert resultado.v_trib_cbs == esperado_v_trib_cbs
    assert resultado.p_aliq_ibs_uf == esperado_p_aliq_ibs_uf
    assert resultado.v_trib_ibs_uf == esperado_v_trib_ibs_uf
    assert resultado.p_aliq_ibs_mun == esperado_p_aliq_ibs_mun
    assert resultado.v_trib_ibs_mun == esperado_v_trib_ibs_mun


def _assert_somas_conservadas(
    original: TributacaoCompraGovernamentalDomain,
    resultado: TributacaoCompraGovernamentalDomain,
) -> None:
    assert _somar_percentuais(resultado) == _somar_percentuais(original)
    assert _somar_valores(resultado) == _somar_valores(original)


def _cenarios_uniao() -> list[tuple]:
    return [
        (2027, ZERO, d("35.00"), d("350.00"), d("0.00"), d("0.00"), d("0.00"), d("0.00")),
        (2028, ZERO, d("35.00"), d("350.00"), d("0.00"), d("0.00"), d("0.00"), d("0.00")),
        (2029, d("10"), d("35.00"), d("350.00"), d("0.00"), d("0.00"), d("0.00"), d("0.00")),
        (2030, d("20"), d("35.00"), d("350.00"), d("0.00"), d("0.00"), d("0.00"), d("0.00")),
        (2031, d("30"), d("35.00"), d("350.00"), d("0.00"), d("0.00"), d("0.00"), d("0.00")),
        (2032, d("40"), d("35.00"), d("350.00"), d("0.00"), d("0.00"), d("0.00"), d("0.00")),
        (2033, d("100"), d("35.00"), d("350.00"), d("0.00"), d("0.00"), d("0.00"), d("0.00")),
    ]


def _cenarios_estado() -> list[tuple]:
    return [
        (2027, ZERO, d("20.00"), d("200.00"), d("15.00"), d("150.00"), d("0.00"), d("0.00")),
        (2028, ZERO, d("20.00"), d("200.00"), d("15.00"), d("150.00"), d("0.00"), d("0.00")),
        (2029, d("10"), d("18.00"), d("180.00"), d("17.00"), d("170.00"), d("0.00"), d("0.00")),
        (2030, d("20"), d("16.00"), d("160.00"), d("19.00"), d("190.00"), d("0.00"), d("0.00")),
        (2031, d("30"), d("14.00"), d("140.00"), d("21.00"), d("210.00"), d("0.00"), d("0.00")),
        (2032, d("40"), d("12.00"), d("120.00"), d("23.00"), d("230.00"), d("0.00"), d("0.00")),
        (2033, d("100"), d("0.00"), d("0.00"), d("35.00"), d("350.00"), d("0.00"), d("0.00")),
    ]


def _cenarios_municipio() -> list[tuple]:
    return [
        (2027, ZERO, d("20.00"), d("200.00"), d("0.00"), d("0.00"), d("15.00"), d("150.00")),
        (2028, ZERO, d("20.00"), d("200.00"), d("0.00"), d("0.00"), d("15.00"), d("150.00")),
        (2029, d("10"), d("18.00"), d("180.00"), d("0.00"), d("0.00"), d("17.00"), d("170.00")),
        (2030, d("20"), d("16.00"), d("160.00"), d("0.00"), d("0.00"), d("19.00"), d("190.00")),
        (2031, d("30"), d("14.00"), d("140.00"), d("0.00"), d("0.00"), d("21.00"), d("210.00")),
        (2032, d("40"), d("12.00"), d("120.00"), d("0.00"), d("0.00"), d("23.00"), d("230.00")),
        (2033, d("100"), d("0.00"), d("0.00"), d("0.00"), d("0.00"), d("35.00"), d("350.00")),
    ]


def test_compraDaUniao_valorPelaAliquotaPublicada_naoPelaSomaDoDetalhe() -> None:
    detalhe = TributacaoCompraGovernamentalDomain(
        p_aliq_cbs=d("8.8000"),
        v_trib_cbs=d("1.06"),
        p_aliq_ibs_uf=d("0.0500"),
        v_trib_ibs_uf=d("0.01"),
        p_aliq_ibs_mun=d("0.0500"),
        v_trib_ibs_mun=d("0.01"),
    )
    resultado = detalhe.get_valores_efetivos(
        TipoEnteGovernamental.UNIAO, ZERO, date(2027, 3, 15), d("12.00")
    )
    assert resultado is not None
    _assert_resultado(
        resultado, d("8.90"), d("1.07"), ZERO, ZERO, ZERO, ZERO
    )
    assert resultado.v_trib_cbs.as_tuple().exponent == -2


def test_transferenciaDaCbs_quemCedeArredonda_quemRecebeFechaPelaDiferenca() -> None:
    detalhe = TributacaoCompraGovernamentalDomain(p_aliq_cbs=d("1.2345"))
    estado = detalhe.get_valores_efetivos(
        TipoEnteGovernamental.ESTADO, d("10"), date(2029, 1, 1), VBC
    )
    assert estado is not None
    _assert_resultado(
        estado,
        d("1.1110"),
        d("11.11"),
        d("0.1235"),
        d("1.24"),
        ZERO,
        ZERO,
    )
    assert _somar_percentuais(estado) == d("1.2345")

    municipio = detalhe.get_valores_efetivos(
        TipoEnteGovernamental.MUNICIPIO, d("10"), date(2029, 1, 1), VBC
    )
    assert municipio is not None
    _assert_resultado(
        municipio,
        d("1.1110"),
        d("11.11"),
        ZERO,
        ZERO,
        d("0.1235"),
        d("1.24"),
    )
    assert _somar_percentuais(municipio) == d("1.2345")


def test_transferenciaDaCbs_estadoRecebeTambemOIbsDoMunicipio() -> None:
    detalhe = TributacaoCompraGovernamentalDomain(
        p_aliq_cbs=d("3.5249"),
        p_aliq_ibs_uf=d("2.9333"),
        p_aliq_ibs_mun=d("0.4938"),
    )
    resultado = detalhe.get_valores_efetivos(
        TipoEnteGovernamental.ESTADO, d("10"), date(2029, 1, 1), d("1234.57")
    )
    assert resultado is not None
    _assert_resultado(
        resultado,
        d("3.1724"),
        d("39.17"),
        d("3.7796"),
        d("46.66"),
        ZERO,
        ZERO,
    )
    assert _somar_percentuais(resultado) == _somar_percentuais(detalhe)


def test_deveRetornarNuloQuandoTipoEnteForNulo() -> None:
    domain = _criar_domain_base()
    assert domain.get_valores_efetivos(None, d("25"), date(2027, 1, 1), VBC) is None


def test_deveLancarExcecaoQuandoDataFatoGeradorForNula() -> None:
    with pytest.raises(TypeError, match="Data do fato gerador obrigatória"):
        _criar_domain_base().get_valores_efetivos(
            TipoEnteGovernamental.ESTADO, d("25"), None, VBC
        )


def test_deveLancarExcecaoQuandoPercentualTransferenciaForNulo() -> None:
    with pytest.raises(TypeError, match="Percentual de transferência da CBS obrigatória"):
        _criar_domain_base().get_valores_efetivos(
            TipoEnteGovernamental.ESTADO, None, date(2027, 1, 1), VBC
        )


def test_deveRetornarMesmaInstanciaAntesDe2027() -> None:
    domain = _criar_domain_base()
    resultado = domain.get_valores_efetivos(
        TipoEnteGovernamental.ESTADO, d("25"), date(2026, 12, 31), VBC
    )
    assert resultado is domain


def _run_cenario_parametrizado(
    tp_ente: TipoEnteGovernamental,
    ano: int,
    p_transferencia_cbs: Decimal,
    esperado_p_aliq_cbs: Decimal,
    esperado_v_trib_cbs: Decimal,
    esperado_p_aliq_ibs_uf: Decimal,
    esperado_v_trib_ibs_uf: Decimal,
    esperado_p_aliq_ibs_mun: Decimal,
    esperado_v_trib_ibs_mun: Decimal,
) -> None:
    domain = _criar_domain_base()
    resultado = domain.get_valores_efetivos(
        tp_ente, p_transferencia_cbs, date(ano, 1, 1), VBC
    )
    assert resultado is not None
    _assert_somas_conservadas(domain, resultado)
    _assert_resultado(
        resultado,
        esperado_p_aliq_cbs,
        esperado_v_trib_cbs,
        esperado_p_aliq_ibs_uf,
        esperado_v_trib_ibs_uf,
        esperado_p_aliq_ibs_mun,
        esperado_v_trib_ibs_mun,
    )


@pytest.mark.parametrize(
    "ano,p_transferencia_cbs,"
    "esperado_p_aliq_cbs,esperado_v_trib_cbs,"
    "esperado_p_aliq_ibs_uf,esperado_v_trib_ibs_uf,"
    "esperado_p_aliq_ibs_mun,esperado_v_trib_ibs_mun",
    _cenarios_uniao(),
    ids=_PARAM_IDS,
)
def test_deveConcentrarTudoNaCbsQuandoUniaoCompraAPartirDe2027(
    ano: int,
    p_transferencia_cbs: Decimal,
    esperado_p_aliq_cbs: Decimal,
    esperado_v_trib_cbs: Decimal,
    esperado_p_aliq_ibs_uf: Decimal,
    esperado_v_trib_ibs_uf: Decimal,
    esperado_p_aliq_ibs_mun: Decimal,
    esperado_v_trib_ibs_mun: Decimal,
) -> None:
    _run_cenario_parametrizado(
        TipoEnteGovernamental.UNIAO,
        ano,
        p_transferencia_cbs,
        esperado_p_aliq_cbs,
        esperado_v_trib_cbs,
        esperado_p_aliq_ibs_uf,
        esperado_v_trib_ibs_uf,
        esperado_p_aliq_ibs_mun,
        esperado_v_trib_ibs_mun,
    )


@pytest.mark.parametrize(
    "ano,p_transferencia_cbs,"
    "esperado_p_aliq_cbs,esperado_v_trib_cbs,"
    "esperado_p_aliq_ibs_uf,esperado_v_trib_ibs_uf,"
    "esperado_p_aliq_ibs_mun,esperado_v_trib_ibs_mun",
    _cenarios_estado(),
    ids=_PARAM_IDS,
)
def test_deveTransferirParaUfQuandoEstadoCompraAPartirDe2027(
    ano: int,
    p_transferencia_cbs: Decimal,
    esperado_p_aliq_cbs: Decimal,
    esperado_v_trib_cbs: Decimal,
    esperado_p_aliq_ibs_uf: Decimal,
    esperado_v_trib_ibs_uf: Decimal,
    esperado_p_aliq_ibs_mun: Decimal,
    esperado_v_trib_ibs_mun: Decimal,
) -> None:
    _run_cenario_parametrizado(
        TipoEnteGovernamental.ESTADO,
        ano,
        p_transferencia_cbs,
        esperado_p_aliq_cbs,
        esperado_v_trib_cbs,
        esperado_p_aliq_ibs_uf,
        esperado_v_trib_ibs_uf,
        esperado_p_aliq_ibs_mun,
        esperado_v_trib_ibs_mun,
    )


@pytest.mark.parametrize(
    "ano,p_transferencia_cbs,"
    "esperado_p_aliq_cbs,esperado_v_trib_cbs,"
    "esperado_p_aliq_ibs_uf,esperado_v_trib_ibs_uf,"
    "esperado_p_aliq_ibs_mun,esperado_v_trib_ibs_mun",
    _cenarios_municipio(),
    ids=_PARAM_IDS,
)
def test_deveTransferirParaMunicipioQuandoMunicipioCompraAPartirDe2027(
    ano: int,
    p_transferencia_cbs: Decimal,
    esperado_p_aliq_cbs: Decimal,
    esperado_v_trib_cbs: Decimal,
    esperado_p_aliq_ibs_uf: Decimal,
    esperado_v_trib_ibs_uf: Decimal,
    esperado_p_aliq_ibs_mun: Decimal,
    esperado_v_trib_ibs_mun: Decimal,
) -> None:
    _run_cenario_parametrizado(
        TipoEnteGovernamental.MUNICIPIO,
        ano,
        p_transferencia_cbs,
        esperado_p_aliq_cbs,
        esperado_v_trib_cbs,
        esperado_p_aliq_ibs_uf,
        esperado_v_trib_ibs_uf,
        esperado_p_aliq_ibs_mun,
        esperado_v_trib_ibs_mun,
    )


@pytest.mark.parametrize(
    "ano,p_transferencia_cbs,"
    "esperado_p_aliq_cbs,esperado_v_trib_cbs,"
    "esperado_p_aliq_ibs_uf,esperado_v_trib_ibs_uf,"
    "esperado_p_aliq_ibs_mun,esperado_v_trib_ibs_mun",
    _cenarios_estado(),
    ids=_PARAM_IDS,
)
def test_deveTransferirParaMunicipioQuandoDistritoFederalCompraAPartirDe2027(
    ano: int,
    p_transferencia_cbs: Decimal,
    esperado_p_aliq_cbs: Decimal,
    esperado_v_trib_cbs: Decimal,
    esperado_p_aliq_ibs_uf: Decimal,
    esperado_v_trib_ibs_uf: Decimal,
    esperado_p_aliq_ibs_mun: Decimal,
    esperado_v_trib_ibs_mun: Decimal,
) -> None:
    _run_cenario_parametrizado(
        TipoEnteGovernamental.DISTRITO_FEDERAL,
        ano,
        p_transferencia_cbs,
        esperado_p_aliq_cbs,
        esperado_v_trib_cbs,
        esperado_p_aliq_ibs_uf,
        esperado_v_trib_ibs_uf,
        esperado_p_aliq_ibs_mun,
        esperado_v_trib_ibs_mun,
    )


@pytest.mark.parametrize(
    "ano,p_transferencia_cbs,"
    "esperado_p_aliq_cbs,esperado_v_trib_cbs,"
    "esperado_p_aliq_ibs_uf,esperado_v_trib_ibs_uf,"
    "esperado_p_aliq_ibs_mun,esperado_v_trib_ibs_mun",
    _cenarios_municipio(),
    ids=_PARAM_IDS,
)
def test_deveTransferirParaMunicipioQuandoConsorcioPublicoCompraAPartirDe2027(
    ano: int,
    p_transferencia_cbs: Decimal,
    esperado_p_aliq_cbs: Decimal,
    esperado_v_trib_cbs: Decimal,
    esperado_p_aliq_ibs_uf: Decimal,
    esperado_v_trib_ibs_uf: Decimal,
    esperado_p_aliq_ibs_mun: Decimal,
    esperado_v_trib_ibs_mun: Decimal,
) -> None:
    _run_cenario_parametrizado(
        TipoEnteGovernamental.CONSORCIO_PUBLICO,
        ano,
        p_transferencia_cbs,
        esperado_p_aliq_cbs,
        esperado_v_trib_cbs,
        esperado_p_aliq_ibs_uf,
        esperado_v_trib_ibs_uf,
        esperado_p_aliq_ibs_mun,
        esperado_v_trib_ibs_mun,
    )


@pytest.mark.parametrize(
    "ano,p_transferencia_cbs,"
    "esperado_p_aliq_cbs,esperado_v_trib_cbs,"
    "esperado_p_aliq_ibs_uf,esperado_v_trib_ibs_uf,"
    "esperado_p_aliq_ibs_mun,esperado_v_trib_ibs_mun",
    _cenarios_municipio(),
    ids=_PARAM_IDS,
)
def test_deveTransferirParaMunicipioQuandoComiteGestorIbsCompraAPartirDe2027(
    ano: int,
    p_transferencia_cbs: Decimal,
    esperado_p_aliq_cbs: Decimal,
    esperado_v_trib_cbs: Decimal,
    esperado_p_aliq_ibs_uf: Decimal,
    esperado_v_trib_ibs_uf: Decimal,
    esperado_p_aliq_ibs_mun: Decimal,
    esperado_v_trib_ibs_mun: Decimal,
) -> None:
    _run_cenario_parametrizado(
        TipoEnteGovernamental.COMITE_GESTOR_IBS,
        ano,
        p_transferencia_cbs,
        esperado_p_aliq_cbs,
        esperado_v_trib_cbs,
        esperado_p_aliq_ibs_uf,
        esperado_v_trib_ibs_uf,
        esperado_p_aliq_ibs_mun,
        esperado_v_trib_ibs_mun,
    )