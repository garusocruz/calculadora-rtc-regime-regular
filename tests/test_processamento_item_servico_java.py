"""Espelho JUnit de ``ProcessamentoItemServiceTest`` (pin f1eebd7), sem Spring."""

from __future__ import annotations

from datetime import date
from decimal import Decimal

import pytest

from calculadora_rtc_regime_regular.base_calculo import Componentes, Natureza, calcular
from calculadora_rtc_regime_regular.base_calculo_service import CampoInvalido
from calculadora_rtc_regime_regular.processamento_item import (
    AliquotaImpostoSeletivoModel,
    BaseCalculoComponentesInconsistenteException,
    ErroGenericoValidacaoException,
    ImpostoSeletivoInput,
    ItemOperacaoInput,
    OperacaoInput,
    ProcessamentoItemService,
    criar_processamento_item_servico_minimo,
)


def _servico_processamento_item() -> ProcessamentoItemService:
    return criar_processamento_item_servico_minimo()


def _operacao(tp_doc: int) -> OperacaoInput:
    return OperacaoInput(
        id="test",
        versao="1.0",
        tp_doc=tp_doc,
        municipio=1234567,
        uf="RS",
        data_fato_gerador=date(2026, 1, 1),
    )


def _componentes_cenario() -> Componentes:
    return Componentes(
        vProd=Decimal("1000"),
        vFrete=Decimal("50"),
        vSeg=Decimal("20"),
        vDesc=Decimal("40"),
        vICMS=Decimal("180"),
    )


def _item_com_componentes(comp: Componentes) -> ItemOperacaoInput:
    return ItemOperacaoInput(
        numero=1,
        cst="000",
        c_class_trib="000001",
        ncm="24021000",
        g_componentes_bc=comp,
    )


# --- validarQuantidadeEUnidade ---


def test_deve_lancar_erro_quando_quantidade_nao_informada() -> None:
    servico = _servico_processamento_item()
    item = ItemOperacaoInput()
    item.imposto_seletivo = ImpostoSeletivoInput(unidade="UN")
    aliquota = AliquotaImpostoSeletivoModel(aliquota_ad_rem=Decimal(1))
    with pytest.raises(
        ErroGenericoValidacaoException,
        match="A quantidade do Imposto Seletivo deve ser informada para alíquota ad rem",
    ):
        servico.validar_quantidade_e_unidade(item, aliquota)


def test_deve_lancar_erro_quando_quantidade_igual_a_zero() -> None:
    servico = _servico_processamento_item()
    item = ItemOperacaoInput(quantidade=Decimal(0), unidade="UN")
    aliquota = AliquotaImpostoSeletivoModel(aliquota_ad_rem=Decimal(1), unidade_medida="UN")
    with pytest.raises(
        ErroGenericoValidacaoException,
        match="A quantidade do item deve ser maior do que zero",
    ):
        servico.validar_quantidade_e_unidade(item, aliquota)


def test_deve_lancar_erro_quando_quantidade_menor_que_zero() -> None:
    servico = _servico_processamento_item()
    item = ItemOperacaoInput(quantidade=Decimal("-1"), unidade="UN")
    aliquota = AliquotaImpostoSeletivoModel(aliquota_ad_rem=Decimal(1), unidade_medida="UN")
    with pytest.raises(
        ErroGenericoValidacaoException,
        match="A quantidade do item deve ser maior do que zero",
    ):
        servico.validar_quantidade_e_unidade(item, aliquota)


def test_deve_lancar_erro_quando_unidade_nao_informada() -> None:
    servico = _servico_processamento_item()
    item = ItemOperacaoInput(quantidade=Decimal(1))
    item.imposto_seletivo = ImpostoSeletivoInput(quantidade=Decimal(1))
    aliquota = AliquotaImpostoSeletivoModel(aliquota_ad_rem=Decimal(1))
    with pytest.raises(
        ErroGenericoValidacaoException,
        match="A unidade de medida do Imposto Seletivo deve ser informada para alíquota ad rem",
    ):
        servico.validar_quantidade_e_unidade(item, aliquota)


def test_nao_deve_criticar_unidade_diferente_da_aliquota() -> None:
    servico = _servico_processamento_item()
    item = ItemOperacaoInput(quantidade=Decimal(1))
    item.imposto_seletivo = ImpostoSeletivoInput(quantidade=Decimal(1), unidade="KG")
    aliquota = AliquotaImpostoSeletivoModel(aliquota_ad_rem=Decimal(1), unidade_medida="UN")
    servico.validar_quantidade_e_unidade(item, aliquota)


def test_nao_deve_lancar_erro_quando_nao_houver_aliquota_ad_rem() -> None:
    servico = _servico_processamento_item()
    servico.validar_quantidade_e_unidade(ItemOperacaoInput(), AliquotaImpostoSeletivoModel())


def test_nao_deve_lancar_erro_quando_tudo_valido() -> None:
    servico = _servico_processamento_item()
    item = ItemOperacaoInput(quantidade=Decimal(10), unidade="UN")
    aliquota = AliquotaImpostoSeletivoModel(aliquota_ad_rem=Decimal(1), unidade_medida="UN")
    servico.validar_quantidade_e_unidade(item, aliquota)


# --- validarBaseCalculoComComponentes / legado ---


def test_deve_calcular_bc_automaticamente_quando_somente_componentes_informados() -> None:
    servico = _servico_processamento_item()
    op = _operacao(55)
    comp = _componentes_cenario()
    item = _item_com_componentes(comp)
    servico.validar_base_calculo_com_componentes(op, item, comp)
    assert item.base_calculo == Decimal("850")


def test_deve_rejeitar_bc_divergente_dos_componentes() -> None:
    servico = _servico_processamento_item()
    op = _operacao(55)
    comp = _componentes_cenario()
    item = _item_com_componentes(comp)
    item.base_calculo = Decimal("900")
    with pytest.raises(BaseCalculoComponentesInconsistenteException, match="850.00"):
        servico.validar_base_calculo_com_componentes(op, item, comp)


def test_deve_aceitar_bc_consistente_com_componentes() -> None:
    servico = _servico_processamento_item()
    op = _operacao(55)
    comp = _componentes_cenario()
    item = _item_com_componentes(comp)
    item.base_calculo = Decimal("850")
    servico.validar_base_calculo_com_componentes(op, item, comp)


def test_deve_rejeitar_quando_tp_doc_nao_informado_com_componentes() -> None:
    servico = _servico_processamento_item()
    op = OperacaoInput(
        id="test",
        versao="1.0",
        municipio=1234567,
        uf="RS",
        data_fato_gerador=date(2026, 1, 1),
    )
    comp = Componentes(vProd=Decimal("1000"))
    item = ItemOperacaoInput(numero=1, cst="000", c_class_trib="000001", g_componentes_bc=comp)
    with pytest.raises(CampoInvalido):
        servico.validar_base_calculo_com_componentes(op, item, comp)


def test_deve_rejeitar_quando_tp_doc_invalido_com_componentes() -> None:
    servico = _servico_processamento_item()
    op = _operacao(57)
    comp = Componentes(vProd=Decimal("1000"))
    item = ItemOperacaoInput(numero=1, cst="000", c_class_trib="000001", g_componentes_bc=comp)
    with pytest.raises(CampoInvalido):
        servico.validar_base_calculo_com_componentes(op, item, comp)


def test_deve_manter_comportamento_legado_quando_sem_componentes() -> None:
    servico = _servico_processamento_item()
    item = ItemOperacaoInput(
        numero=1,
        cst="000",
        c_class_trib="000001",
        base_calculo=Decimal("850"),
    )
    servico.validar_base_calculo_legado(item)


def test_deve_calcular_base_is_automaticamente_quando_imposto_seletivo_informado_sem_base_is() -> None:
    servico = _servico_processamento_item()
    op = _operacao(55)
    comp = _componentes_cenario()
    item = _item_com_componentes(comp)
    item.imposto_seletivo = ImpostoSeletivoInput(cst="000", c_class_trib="000000")
    servico.validar_base_calculo_com_componentes(op, item, comp)
    assert item.imposto_seletivo.base_calculo is not None
    assert item.base_calculo is None


def test_deve_lancar_excecao_quando_base_is_declarada_inconsistente_com_componentes() -> None:
    servico = _servico_processamento_item()
    op = _operacao(55)
    comp = _componentes_cenario()
    item = _item_com_componentes(comp)
    item.imposto_seletivo = ImpostoSeletivoInput(
        cst="000",
        c_class_trib="000000",
        base_calculo=Decimal("999.99"),
    )
    with pytest.raises(BaseCalculoComponentesInconsistenteException):
        servico.validar_base_calculo_com_componentes(op, item, comp)


def test_deve_aceitar_quando_base_is_declarada_consistente_com_componentes() -> None:
    servico = _servico_processamento_item()
    op = _operacao(55)
    comp = _componentes_cenario()
    resultado = calcular(comp, 2026, Natureza.BEM, 55)
    item = _item_com_componentes(comp)
    item.imposto_seletivo = ImpostoSeletivoInput(
        cst="000",
        c_class_trib="000000",
        base_calculo=resultado.base_is,
    )
    servico.validar_base_calculo_com_componentes(op, item, comp)
    assert item.base_calculo is None