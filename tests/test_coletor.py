"""Testes dos coletores de observabilidade (pin f1eebd7ce3157423b1a6aaca7dc1d6c3395452c4)."""

from __future__ import annotations

from datetime import date

import pytest

from calculadora_rtc_regime_regular.coletor import (
    ErroDetalhe,
    EstadoItemEnum,
    GlobalCollector,
    ItemCollector,
)
from calculadora_rtc_regime_regular.processamento_item import NcmNaoEncontradaException


def test_novo_collector_nao_tem_erros() -> None:
    collector = GlobalCollector()
    assert collector.has_erros_globais() is False
    assert collector.get_erros_globais() == ()
    assert collector.get_item_collectors() == ()


def test_add_erro_global_marca_has_erros_true() -> None:
    collector = GlobalCollector()
    collector.add_erro_global("type", "title", "code", "#/campo", "detail")
    assert collector.has_erros_globais() is True
    erros = collector.get_erros_globais()
    assert len(erros) == 1
    erro = erros[0]
    assert erro.type == "type"
    assert erro.title == "title"
    assert erro.code == "code"
    assert erro.pointer == "#/campo"
    assert erro.detail == "detail"


def test_get_erros_globais_retorna_lista_imutavel() -> None:
    collector = GlobalCollector()
    collector.add_erro_global("t", "t", "c", "#", "d")
    with pytest.raises(AttributeError):
        collector.get_erros_globais().append(  # type: ignore[attr-defined]
            ErroDetalhe("a", "b", "c", "d", "e")
        )


def test_add_item_collector_funciona() -> None:
    collector = GlobalCollector()
    item = ItemCollector(0, "http://localhost")
    collector.add_item_collector(item)
    assert len(collector.get_item_collectors()) == 1


def test_add_multiplos_item_collectors() -> None:
    collector = GlobalCollector()
    for i in range(3):
        collector.add_item_collector(ItemCollector(i, "http://localhost"))
    assert len(collector.get_item_collectors()) == 3


def test_get_item_collectors_retorna_lista_imutavel() -> None:
    collector = GlobalCollector()
    with pytest.raises(AttributeError):
        collector.get_item_collectors().append(ItemCollector(0, ""))  # type: ignore[attr-defined]


def test_multiplos_erros_globais() -> None:
    collector = GlobalCollector()
    for i in range(3):
        collector.add_erro_global(f"t{i}", f"title{i}", f"c{i}", f"#/{i}", f"d{i}")
    assert len(collector.get_erros_globais()) == 3


def test_erros_globais_preservam_ordem() -> None:
    collector = GlobalCollector()
    collector.add_erro_global("t1", "title1", "CODE-1", "#/1", "d1")
    collector.add_erro_global("t2", "title2", "CODE-2", "#/2", "d2")
    assert [e.code for e in collector.get_erros_globais()] == ["CODE-1", "CODE-2"]


def test_collector_com_itens_e_erros_globais_simultaneos() -> None:
    collector = GlobalCollector()
    collector.add_erro_global("t", "title", "c", "#", "d")
    collector.add_item_collector(ItemCollector(0, "http://localhost"))
    assert collector.has_erros_globais() is True
    assert len(collector.get_item_collectors()) == 1


def test_item_collector_estado_inicial() -> None:
    item = ItemCollector(0, "http://localhost")
    assert item.estado is EstadoItemEnum.CALCULADO
    assert item.has_erros() is False


def test_add_erro_validacao() -> None:
    item = ItemCollector(2, "https://api.exemplo")
    item.add_erro_validacao("VAL-001", "ncm", "campo obrigatório")
    assert item.estado is EstadoItemEnum.INCONSISTENCIA_ENTRADA
    erro = item.get_erros()[0]
    assert erro.code == "VAL-001"
    assert erro.title == "Campo obrigatório não informado"
    assert erro.pointer == "#/itens/2/ncm"
    assert (
        erro.type
        == "https://api.exemplo/api/calculadora/observabilidade/erros?codigo=VAL-001"
    )


def test_add_erro_validacao_campo_nulo() -> None:
    item = ItemCollector(1, "http://localhost")
    item.add_erro_validacao("VAL-000", None, "detalhe")
    assert item.get_erros()[0].pointer == "#/itens/1"


def test_add_erro_mapeado_reg() -> None:
    item = ItemCollector(0, "http://localhost")
    item.add_erro(NcmNaoEncontradaException("99999999", date(2026, 1, 1)))
    erro = item.get_erros()[0]
    assert erro.code == "REG-002"
    assert erro.pointer == "#/itens/0/ncm"
    assert erro.title == "NCM não encontrada"
    assert item.estado is EstadoItemEnum.INCONSISTENCIA_ENTRADA


def test_add_erro_desconhecido_cal_999() -> None:
    item = ItemCollector(5, "http://localhost")
    item.add_erro(RuntimeError("falha"))
    erro = item.get_erros()[0]
    assert erro.code == "CAL-999"
    assert erro.pointer == "#/itens/5"
    assert item.estado is EstadoItemEnum.FALHA_TECNICA


def test_get_erros_item_imutavel() -> None:
    item = ItemCollector(0, "http://localhost")
    item.add_erro_validacao("VAL-002", "nbs", "x")
    with pytest.raises(AttributeError):
        item.get_erros().append(ErroDetalhe("a", "b", "c", "d", "e"))  # type: ignore[attr-defined]