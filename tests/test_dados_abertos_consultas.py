"""Integração DadosAbertosService com calculadora-pro.db (somente leitura)."""

from __future__ import annotations

import os
from datetime import date

import pytest

from calculadora_rtc_regime_regular.dados_abertos import (
    AliquotaNaoEncontradaException,
    ClassificacaoTributariaNaoEncontradaException,
    DadosAbertosService,
    NbsNaoEncontradaException,
    NcmNaoEncontradaException,
    SiglaDfeNaoEncontradaException,
    TipoWarningDadosSimulados,
    ValidacaoException,
)

pytestmark = pytest.mark.skipif(
    not os.environ.get("CALC_DB"),
    reason="CALC_DB não definido",
)

DATA_CBS = date(2026, 1, 15)
DATA_IS = date(2027, 1, 1)


@pytest.fixture(scope="module")
def servico() -> DadosAbertosService:
    return DadosAbertosService()


def test_consultar_ufs_encontrou(servico: DadosAbertosService) -> None:
    ufs = servico.consultar_ufs()
    assert len(ufs) == 28
    assert any(u.sigla == "SP" for u in ufs)


def test_consultar_municipios_por_sigla_uf(servico: DadosAbertosService) -> None:
    assert len(servico.consultar_municipios_por_sigla_uf("SP")) > 0
    assert servico.consultar_municipios_por_sigla_uf("XX") == []


def test_consultar_situacoes_tributarias(servico: DadosAbertosService) -> None:
    situacoes = servico.consultar_situacoes_tributarias(2, DATA_CBS)
    assert len(situacoes) > 0
    assert situacoes[0].codigo
    assert servico.consultar_situacoes_tributarias(99999, DATA_CBS) == []


def test_consultar_classificacoes_por_id_situacao(servico: DadosAbertosService) -> None:
    id_sit = servico.consultar_situacoes_tributarias(2, DATA_CBS)[0].id
    cls = servico.consultar_classificacoes_tributarias_por_id_situacao_tributaria(
        id_sit, DATA_CBS
    )
    assert len(cls) > 0
    assert servico.consultar_classificacoes_tributarias_por_id_situacao_tributaria(
        999999, DATA_CBS
    ) == []


def test_consultar_classificacoes_por_cst_e_tributo_tipo(
    servico: DadosAbertosService,
) -> None:
    cbs = servico.consultar_classificacoes_tributarias_por_cst_e_tributo_tipo(
        "000", ["CBS", "IBSUF", "IBSMun"], DATA_CBS
    )
    assert len(cbs) > 0
    is_cls = servico.consultar_classificacoes_tributarias_por_cst_e_tributo_tipo(
        "000", ["IS"], DATA_IS
    )
    assert len(is_cls) > 0
    assert (
        servico.consultar_classificacoes_tributarias_por_cst_e_tributo_tipo(
            "ZZZZ", ["CBS"], DATA_CBS
        )
        == []
    )


def test_consultar_ncm(servico: DadosAbertosService) -> None:
    ncm = servico.consultar_ncm("01012100", DATA_CBS)
    assert ncm.capitulo is not None
    with pytest.raises(NcmNaoEncontradaException):
        servico.consultar_ncm("24020009", DATA_IS)


def test_consultar_nbs(servico: DadosAbertosService) -> None:
    codigo = servico.listar_nbs(DATA_CBS)[0].codigo
    assert servico.consultar_nbs(codigo, DATA_CBS).capitulo is not None
    with pytest.raises(NbsNaoEncontradaException):
        servico.consultar_nbs("999999999", DATA_CBS)


def test_listar_nbs(servico: DadosAbertosService) -> None:
    assert len(servico.listar_nbs(DATA_CBS)) > 0
    assert servico.listar_nbs(date(1900, 1, 1)) == []


def test_consultar_fundamentacoes_legais(servico: DadosAbertosService) -> None:
    assert len(servico.consultar_fundamentacoes_legais(DATA_CBS)) > 0
    assert servico.consultar_fundamentacoes_legais(date(1900, 1, 1)) == []


def test_consultar_classificacoes_cbs_ibs(servico: DadosAbertosService) -> None:
    todas = servico.consultar_classificacoes_tributarias_cbs_ibs(DATA_CBS)
    assert len(todas) > 0
    codigo = todas[0].codigo
    unica = servico.consultar_classificacao_tributaria_cbs_ibs_por_codigo(
        codigo, DATA_CBS
    )
    assert unica.codigo == codigo
    with pytest.raises(ClassificacaoTributariaNaoEncontradaException):
        servico.consultar_classificacao_tributaria_cbs_ibs_por_codigo(
            "999999", DATA_CBS
        )


def test_consultar_classificacoes_cbs_ibs_por_atores(
    servico: DadosAbertosService,
) -> None:
    todas = servico.consultar_classificacoes_tributarias_cbs_ibs(DATA_CBS)
    filtradas = servico.consultar_classificacoes_tributarias_cbs_ibs_por_atores(
        DATA_CBS, fornecedor=1, adquirente=1, sigla_dfe="NFE"
    )
    assert 0 < len(filtradas) <= len(todas)
    assert (
        servico.consultar_classificacoes_tributarias_cbs_ibs_por_atores(
            DATA_CBS, sigla_dfe="CTESIMPLIFICADO"
        )
        == []
    )


def test_consultar_classificacao_is(servico: DadosAbertosService) -> None:
    lista = servico.consultar_classificacoes_tributarias_imposto_seletivo(DATA_IS)
    assert len(lista) > 0
    codigo = lista[0].codigo
    assert (
        servico.consultar_classificacao_tributaria_is_por_codigo(codigo, DATA_IS).codigo
        == codigo
    )
    assert servico.consultar_classificacoes_tributarias_imposto_seletivo(DATA_CBS) == []
    with pytest.raises(ClassificacaoTributariaNaoEncontradaException):
        servico.consultar_classificacao_tributaria_is_por_codigo("999999", DATA_IS)


def test_consultar_validade_dfe_classificacao_tributaria(
    servico: DadosAbertosService,
) -> None:
    ok = servico.consultar_validade_dfe_classificacao_tributaria(
        "NFE", "000001", DATA_CBS
    )
    assert ok.nomenclatura
    with pytest.raises(ClassificacaoTributariaNaoEncontradaException):
        servico.consultar_validade_dfe_classificacao_tributaria(
            "NFE", "999999", DATA_CBS
        )


def test_consultar_csts_com_classificacoes(servico: DadosAbertosService) -> None:
    cbs = servico.consultar_csts_com_classificacoes_cbs_ibs(None, DATA_CBS)
    assert len(cbs) > 0
    assert (
        servico.consultar_csts_com_classificacoes_cbs_ibs("NFE", DATA_CBS)[0].codigo
        in {c.codigo for c in cbs}
    )
    assert servico.consultar_csts_com_classificacoes_cbs_ibs("NFE", date(1900, 1, 1)) == []

    is_ok = servico.consultar_csts_com_classificacoes_is(None, DATA_IS)
    assert len(is_ok) > 0
    assert servico.consultar_csts_com_classificacoes_is("CTE", DATA_IS) == []


def test_consultar_redutores_e_transferencias(servico: DadosAbertosService) -> None:
    assert len(servico.consultar_redutores_compra_governamental()) > 0
    assert len(servico.consultar_transferencias_cbs()) > 0
    ibs = servico.consultar_transferencias_ibs()
    assert len(ibs) == 2
    assert ibs[0].valor == 0


def test_listar_nbs_e_classificacoes_aplicaveis(servico: DadosAbertosService) -> None:
    nbs_lista = servico.listar_nbs_aplicaveis_por_classificacao("000001", DATA_CBS)
    assert len(nbs_lista) > 0
    assert servico.listar_nbs_aplicaveis_por_classificacao("000003", DATA_CBS) == []
    with pytest.raises(ClassificacaoTributariaNaoEncontradaException):
        servico.listar_nbs_aplicaveis_por_classificacao("999999", DATA_CBS)

    nbs = nbs_lista[0].codigo
    codigos = servico.listar_classificacao_aplicavel_por_nbs(nbs, DATA_CBS)
    assert "000001" in codigos
    with pytest.raises(NbsNaoEncontradaException):
        servico.listar_classificacao_aplicavel_por_nbs("999999999", DATA_CBS)


def test_get_warning_dados_simulados_por_data(servico: DadosAbertosService) -> None:
    assert servico.get_warning_dados_simulados_por_data(DATA_CBS) is None
    assert (
        servico.get_warning_dados_simulados_por_data(DATA_IS)
        is TipoWarningDadosSimulados.CASO_GERAL
    )


def test_validar_nbs_e_ncm_aplicavel(servico: DadosAbertosService) -> None:
    nbs = servico.listar_nbs(DATA_CBS)[0].codigo
    assert servico.validar_nbs_aplicavel("000001", nbs, DATA_CBS).valido is True
    with pytest.raises(ValidacaoException):
        servico.validar_nbs_aplicavel("000001", "123", DATA_CBS)

    assert (
        servico.validar_ncm_aplicavel("000001", "01012100", DATA_CBS).valido is True
    )
    with pytest.raises(ValidacaoException):
        servico.validar_ncm_aplicavel("000001", "123", DATA_CBS)


def test_consultar_tipos_dfe_e_atores(servico: DadosAbertosService) -> None:
    grupos = servico.consultar_tipos_dfe_agrupados(DATA_CBS)
    assert len(grupos) > 0
    assert len(grupos[0].tipos) > 0
    assert servico.consultar_tipos_dfe_agrupados(date(1900, 1, 1)) == []

    atores = servico.consultar_atores_agrupados(DATA_CBS, None)
    assert len(atores) > 0
    assert servico.consultar_atores_agrupados(date(1900, 1, 1), None) == []


def test_consultar_nomenclatura(servico: DadosAbertosService) -> None:
    out = servico.consultar_nomenclatura("NFE", "000001", DATA_CBS)
    assert out.nomenclatura
    with pytest.raises(ClassificacaoTributariaNaoEncontradaException):
        servico.consultar_nomenclatura("NFE", "999999", DATA_CBS)
    with pytest.raises(SiglaDfeNaoEncontradaException):
        servico.consultar_nomenclatura("INVALIDO", "000001", DATA_CBS)


def test_consultar_ncms_vigentes(servico: DadosAbertosService) -> None:
    assert len(servico.consultar_ncms_vigentes(DATA_CBS)) > 0
    assert servico.consultar_ncms_vigentes(date(1900, 1, 1)) == []


def test_consultar_aliquota_banco_real(servico: DadosAbertosService) -> None:
    aliq = servico.consultar_aliquota(2, 35, 3550308, DATA_CBS)
    assert aliq.aliquota_referencia is not None
    with pytest.raises(AliquotaNaoEncontradaException):
        servico.consultar_aliquota(99999, 35, 3550308, DATA_CBS)