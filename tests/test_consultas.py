"""Testes dos serviços de consulta (pin f1eebd7ce3157423b1a6aaca7dc1d6c3395452c4)."""

from __future__ import annotations

import os
from datetime import date
from decimal import Decimal

import pytest

# CALC_DB precisa estar definido antes de qualquer uso de conectar() nos serviços.
os.environ.setdefault(
    "CALC_DB",
    "/home/garusotec/projects/lynko/libs/calculadora-rtc-regime-regular/.cache/oficial/java/calculadora/db/calculadora-pro.db",
)

from calculadora_rtc_regime_regular.consultas import (  # noqa: E402
    AliquotaAdRemProdutoService,
    AliquotaAdValoremProdutoService,
    AliquotaAdValoremServicoService,
    AliquotaReferenciaService,
    FundamentacaoClassificacaoService,
    MunicipioService,
    PercentualReducaoService,
    RedutorCompraGovernamentalService,
    SituacaoTributariaService,
    TipoDfeService,
    TransferenciaCBSService,
    TratamentoClassificacaoService,
    TratamentoTributarioService,
    TributoEnum,
    TributoSituacaoTributariaService,
    TipoEnteGovernamental,
    UfService,
    VersaoBaseDadosService,
    AliquotaReferenciaNaoEncontradaException,
    FundamentacaoClassificacaoNaoEncontradaException,
    PercentualReducaoNaoEncontradoException,
    SituacaoTributariaNaoEncontradaException,
    TipoDfeNaoEncontradoException,
    UfNaoEncontradaException,
    MunicipioNaoEncontradoException,
    MunicipioNaoPertencenteException,
    TipoDfeNaoTratadoException,
    TratamentoClassificacaoNaoEncontradoException,
    TratamentoTributarioNaoEncontradoException,
    TributoSituacaoTributariaNaoEncontradoException,
)


@pytest.fixture
def data_vigente() -> date:
    return date(2026, 1, 15)


@pytest.fixture
def data_ad_rem() -> date:
    return date(2027, 6, 15)


@pytest.fixture
def data_ad_valorem_produto() -> date:
    return date(2027, 6, 15)


# --- AliquotaAdRemProdutoService ---


def test_buscar_aliquota_ad_rem_encontrada(data_ad_rem: date) -> None:
    svc = AliquotaAdRemProdutoService()
    dto = svc.buscar_aliquota_ad_rem("24021000", 1, data_ad_rem)
    assert dto is not None
    assert dto.unidade_medida == "VN"


def test_buscar_aliquota_ad_rem_ausente(data_vigente: date) -> None:
    svc = AliquotaAdRemProdutoService()
    assert svc.buscar_aliquota_ad_rem("24021000", 1, data_vigente) is None


# --- AliquotaAdValoremProdutoService ---


def test_buscar_aliquota_ad_valorem_produto_encontrada(
    data_ad_valorem_produto: date,
) -> None:
    svc = AliquotaAdValoremProdutoService()
    dto = svc.buscar_aliquota_ad_valorem("87032100", 1, data_ad_valorem_produto)
    assert dto is not None


def test_buscar_aliquota_ad_valorem_produto_ausente(data_vigente: date) -> None:
    svc = AliquotaAdValoremProdutoService()
    assert svc.buscar_aliquota_ad_valorem("87032100", 1, data_vigente) is None


def test_existe_ncm_ad_valorem_verdadeiro(data_ad_valorem_produto: date) -> None:
    svc = AliquotaAdValoremProdutoService()
    assert svc.existe_ncm_ad_valorem("87032100", TributoEnum.IS, data_ad_valorem_produto)


def test_existe_ncm_ad_valorem_falso(data_vigente: date) -> None:
    svc = AliquotaAdValoremProdutoService()
    assert not svc.existe_ncm_ad_valorem("87032100", TributoEnum.IS, data_vigente)


# --- AliquotaAdValoremServicoService ---


def test_buscar_aliquota_ad_valorem_servico_por_classificacao_encontrada(
    data_vigente: date,
) -> None:
    svc = AliquotaAdValoremServicoService()
    assert svc.buscar_aliquota_ad_valorem_por_classificacao_tributaria(
        2, 5, data_vigente
    ) == Decimal("0.9")


def test_buscar_aliquota_ad_valorem_servico_por_classificacao_ausente(
    data_vigente: date,
) -> None:
    svc = AliquotaAdValoremServicoService()
    assert (
        svc.buscar_aliquota_ad_valorem_por_classificacao_tributaria(
            2, 99999, data_vigente
        )
        is None
    )


def test_buscar_aliquota_ad_valorem_dto_nbs_ausente(data_vigente: date) -> None:
    svc = AliquotaAdValoremServicoService()
    assert (
        svc.buscar_aliquota_ad_valorem_dto("101011100", 2, None, data_vigente) is None
    )


def test_existe_nbs_ad_valorem_falso(data_vigente: date) -> None:
    svc = AliquotaAdValoremServicoService()
    assert not svc.existe_nbs_ad_valorem("101011100", TributoEnum.CBS, data_vigente)


def test_buscar_aliquota_ad_valorem_nbs_retorno_none(data_vigente: date) -> None:
    svc = AliquotaAdValoremServicoService()
    assert svc.buscar_aliquota_ad_valorem("101011100", 2, None, data_vigente) is None


# --- AliquotaReferenciaService ---


def test_buscar_aliquota_referencia_encontrada(data_vigente: date) -> None:
    svc = AliquotaReferenciaService()
    assert svc.buscar(2, data_vigente) == Decimal("0.9")


def test_buscar_aliquota_referencia_ausente(data_vigente: date) -> None:
    svc = AliquotaReferenciaService()
    with pytest.raises(AliquotaReferenciaNaoEncontradaException):
        svc.buscar(999, data_vigente)


# --- PercentualReducaoService ---


def test_buscar_percentual_reducao_encontrado(data_vigente: date) -> None:
    svc = PercentualReducaoService()
    assert svc.buscar(1, 2, data_vigente) == Decimal("0.0")


def test_buscar_percentual_reducao_ausente(data_vigente: date) -> None:
    svc = PercentualReducaoService()
    with pytest.raises(PercentualReducaoNaoEncontradoException):
        svc.buscar(99999, 2, data_vigente)


# --- FundamentacaoClassificacaoService ---


def test_buscar_fundamentacao_encontrada(data_vigente: date) -> None:
    svc = FundamentacaoClassificacaoService()
    dto = svc.buscar(1, data_vigente)
    assert dto.texto_curto == "LC 214/2025"
    assert "[base_calculo]" in dto.memoria_calculo


def test_buscar_fundamentacao_ausente(data_vigente: date) -> None:
    svc = FundamentacaoClassificacaoService()
    with pytest.raises(FundamentacaoClassificacaoNaoEncontradaException):
        svc.buscar(99999, data_vigente)


def test_buscar_todas_fundamentacoes_nao_vazio(data_vigente: date) -> None:
    svc = FundamentacaoClassificacaoService()
    assert len(svc.buscar_todas(data_vigente)) > 0


# --- RedutorCompraGovernamentalService ---


def test_redutor_ente_nulo_retorna_zero(data_vigente: date) -> None:
    svc = RedutorCompraGovernamentalService()
    assert svc.buscar_valor_redutor(None, data_vigente) == Decimal(0)


def test_redutor_encontrado(data_vigente: date) -> None:
    svc = RedutorCompraGovernamentalService()
    assert svc.buscar_valor_redutor(TipoEnteGovernamental.UNIAO, data_vigente) == Decimal(
        "0.0"
    )


def test_redutor_ausente() -> None:
    svc = RedutorCompraGovernamentalService()
    with pytest.raises(RuntimeError, match="Redutor de compra governamental não encontrada."):
        svc.buscar_valor_redutor(TipoEnteGovernamental.UNIAO, date(2020, 1, 1))


# --- SituacaoTributariaService ---


def test_validar_cst_encontrado(data_vigente: date) -> None:
    svc = SituacaoTributariaService()
    svc.validar_cst("000", 2, data_vigente)


def test_validar_cst_ausente(data_vigente: date) -> None:
    svc = SituacaoTributariaService()
    with pytest.raises(SituacaoTributariaNaoEncontradaException):
        svc.validar_cst("999", 2, data_vigente)


def test_consultar_situacao_tributaria_encontrada(data_vigente: date) -> None:
    svc = SituacaoTributariaService()
    st = svc.consultar_situacao_tributaria_por_codigo("000", 2, data_vigente)
    assert st is not None
    assert st.codigo == "000"


def test_consultar_situacao_tributaria_ausente(data_vigente: date) -> None:
    svc = SituacaoTributariaService()
    assert svc.consultar_situacao_tributaria_por_codigo("999", 2, data_vigente) is None


# --- TipoDfeService ---


def test_buscar_tipo_dfe_encontrado(data_vigente: date) -> None:
    svc = TipoDfeService()
    tipo = svc.buscar_por_tipo(55, data_vigente)
    assert tipo is not None
    assert tipo.sigla == "NF-e"


def test_buscar_tipo_dfe_ausente(data_vigente: date) -> None:
    svc = TipoDfeService()
    with pytest.raises(TipoDfeNaoEncontradoException):
        svc.buscar_por_tipo(99999, data_vigente)


def test_buscar_tipo_dfe_sem_tratamento(data_vigente: date) -> None:
    svc = TipoDfeService()
    with pytest.raises(TipoDfeNaoTratadoException):
        svc.buscar_por_tipo(77, data_vigente)


def test_buscar_tipo_dfe_tpdoc_nulo(data_vigente: date) -> None:
    svc = TipoDfeService()
    assert svc.buscar_por_tipo(None, data_vigente) is None


# --- TransferenciaCBSService ---


def test_percentual_transferencia_encontrado(data_vigente: date) -> None:
    svc = TransferenciaCBSService()
    assert svc.get_percentual_transferencia(data_vigente) == Decimal("0.0")


def test_percentual_transferencia_ausente() -> None:
    svc = TransferenciaCBSService()
    with pytest.raises(
        RuntimeError,
        match="Percentual de transferência de CBS para ente federativo não encontrada.",
    ):
        svc.get_percentual_transferencia(date(2020, 1, 1))


# --- TratamentoClassificacaoService ---


def test_tratamento_classificacao_encontrado(data_vigente: date) -> None:
    svc = TratamentoClassificacaoService()
    dto = svc.buscar_tratamento_classificacao(1, data_vigente)
    assert dto.id_classificacao_tributaria == 1


def test_tratamento_classificacao_ausente(data_vigente: date) -> None:
    svc = TratamentoClassificacaoService()
    with pytest.raises(TratamentoClassificacaoNaoEncontradoException):
        svc.buscar_tratamento_classificacao(99999, data_vigente)


# --- TratamentoTributarioService ---


def test_tratamento_tributario_encontrado() -> None:
    svc = TratamentoTributarioService()
    tr = svc.buscar(1)
    assert tr.id == 1


def test_tratamento_tributario_ausente() -> None:
    svc = TratamentoTributarioService()
    with pytest.raises(TratamentoTributarioNaoEncontradoException):
        svc.buscar(99999)


# --- TributoSituacaoTributariaService ---


def test_tributo_situacao_encontrado(data_vigente: date) -> None:
    svc = TributoSituacaoTributariaService()
    assert svc.consultar_por_id_situacao_tributaria(1, data_vigente) == 2


def test_tributo_situacao_ausente(data_vigente: date) -> None:
    svc = TributoSituacaoTributariaService()
    with pytest.raises(TributoSituacaoTributariaNaoEncontradoException):
        svc.consultar_por_id_situacao_tributaria(99999, data_vigente)


# --- VersaoBaseDadosService ---


def test_versao_base_dados_encontrada() -> None:
    svc = VersaoBaseDadosService()
    versao = svc.get_ultima_versao()
    assert versao.numero_versao.startswith("V")


# --- UfService / MunicipioService ---


def test_uf_consultar_todos() -> None:
    svc = UfService()
    ufs = svc.consultar_todos()
    assert len(ufs) == 28
    assert any(u.sigla == "SP" for u in ufs)


def test_municipio_consultar_todos_por_uf() -> None:
    svc = MunicipioService()
    municipios = svc.consultar_todos_por_sigla_uf("SP")
    assert len(municipios) > 0
    assert all(m.uf.sigla == "SP" for m in municipios)


def test_municipio_uf_inexistente() -> None:
    svc = MunicipioService()
    assert svc.consultar_todos_por_sigla_uf("ZZ") == []


def test_uf_buscar_e_validar() -> None:
    svc = UfService()
    assert svc.buscar("sp") == svc.buscar("SP")
    svc.validar_uf("SP")
    with pytest.raises(UfNaoEncontradaException, match="ZZ"):
        svc.buscar("ZZ")
    with pytest.raises(UfNaoEncontradaException, match="ZZ"):
        svc.validar_uf("ZZ")


def test_municipio_validar_e_resolver_uf() -> None:
    svc = MunicipioService()
    amostra = svc.consultar_todos_por_sigla_uf("SP")[0]
    svc.validar_municipio(amostra.codigo, "sp")
    assert svc.buscar_uf_por_municipio(amostra.codigo) == "SP"
    with pytest.raises(MunicipioNaoPertencenteException):
        svc.validar_municipio(amostra.codigo, "RJ")
    with pytest.raises(MunicipioNaoEncontradoException, match="código 0"):
        svc.validar_municipio(0, "SP")
    with pytest.raises(MunicipioNaoEncontradoException, match="código 0"):
        svc.buscar_uf_por_municipio(0)