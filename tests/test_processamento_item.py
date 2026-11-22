from datetime import date
from decimal import Decimal

import pytest

from calculadora_rtc_regime_regular.base_calculo import Componentes, Natureza, calcular
from calculadora_rtc_regime_regular.base_calculo_service import CampoInvalido
from calculadora_rtc_regime_regular.processamento_item import (
    AliquotaImpostoSeletivoModel,
    aplicar_defaults_quantidade_unidade,
    BaseCalculoComponentesInconsistenteException,
    ClassificacaoTributariaDTO,
    ErroGenericoValidacaoException,
    ID_TRIBUTO_CBS_IBS,
    ID_TRIBUTO_IS,
    ImpostoSeletivoInput,
    ItemOperacaoInput,
    OperacaoInput,
    ProcessamentoItemService,
    SituacaoTributariaNaoEncontradaException,
    SituacaoTributariaService,
    TratamentoClassificacaoDTO,
)


PROCESSAMENTO = ProcessamentoItemService()


def _operacao(tp_doc: int) -> OperacaoInput:
    return OperacaoInput(
        id="test",
        versao="1.0",
        tp_doc=tp_doc,
        municipio=1234567,
        uf="RS",
        data_fato_gerador=date(2026, 1, 1),
    )


def _componentes(**valores: Decimal | None) -> Componentes:
    return Componentes(**valores)


def _componentes_cenario() -> Componentes:
    return _componentes(
        vProd=Decimal("1000"),
        vFrete=Decimal("50"),
        vSeg=Decimal("20"),
        vDesc=Decimal("40"),
        vICMS=Decimal("180"),
    )


def test_quantidade_is_obrigatoria_com_ad_rem() -> None:
    item = ItemOperacaoInput()
    is_grupo = ImpostoSeletivoInput(unidade="UN")
    item.imposto_seletivo = is_grupo
    aliquota = AliquotaImpostoSeletivoModel(aliquota_ad_rem=Decimal(1))
    with pytest.raises(ErroGenericoValidacaoException, match="A quantidade do Imposto Seletivo deve ser informada"):
        PROCESSAMENTO.validar_quantidade_e_unidade(item, aliquota)


def test_quantidade_item_zero() -> None:
    item = ItemOperacaoInput(quantidade=Decimal(0), unidade="UN")
    aliquota = AliquotaImpostoSeletivoModel(aliquota_ad_rem=Decimal(1))
    with pytest.raises(ErroGenericoValidacaoException, match="A quantidade do item deve ser maior do que zero"):
        PROCESSAMENTO.validar_quantidade_e_unidade(item, aliquota)


def test_quantidade_item_negativa() -> None:
    item = ItemOperacaoInput(quantidade=Decimal("-1"), unidade="UN")
    aliquota = AliquotaImpostoSeletivoModel(aliquota_ad_rem=Decimal(1))
    with pytest.raises(ErroGenericoValidacaoException, match="A quantidade do item deve ser maior do que zero"):
        PROCESSAMENTO.validar_quantidade_e_unidade(item, aliquota)


def test_unidade_is_obrigatoria_com_ad_rem() -> None:
    item = ItemOperacaoInput(quantidade=Decimal(1))
    item.imposto_seletivo = ImpostoSeletivoInput(quantidade=Decimal(1))
    aliquota = AliquotaImpostoSeletivoModel(aliquota_ad_rem=Decimal(1))
    with pytest.raises(
        ErroGenericoValidacaoException,
        match="A unidade de medida do Imposto Seletivo deve ser informada para alíquota ad rem",
    ):
        PROCESSAMENTO.validar_quantidade_e_unidade(item, aliquota)


def test_nao_critica_unidade_diferente_da_aliquota() -> None:
    item = ItemOperacaoInput(quantidade=Decimal(1))
    item.imposto_seletivo = ImpostoSeletivoInput(quantidade=Decimal(1), unidade="KG")
    aliquota = AliquotaImpostoSeletivoModel(aliquota_ad_rem=Decimal(1), unidade_medida="UN")
    PROCESSAMENTO.validar_quantidade_e_unidade(item, aliquota)


def test_sem_ad_rem_nao_exige_quantidade_is() -> None:
    item = ItemOperacaoInput()
    PROCESSAMENTO.validar_quantidade_e_unidade(item, AliquotaImpostoSeletivoModel())


def test_quantidade_e_unidade_validos() -> None:
    item = ItemOperacaoInput(quantidade=Decimal(10), unidade="UN")
    aliquota = AliquotaImpostoSeletivoModel(aliquota_ad_rem=Decimal(1), unidade_medida="UN")
    PROCESSAMENTO.validar_quantidade_e_unidade(item, aliquota)


def test_bc_automatica_somente_componentes() -> None:
    op = _operacao(55)
    comp = _componentes_cenario()
    item = ItemOperacaoInput(
        numero=1,
        cst="000",
        c_class_trib="000001",
        ncm="24021000",
        g_componentes_bc=comp,
    )
    PROCESSAMENTO.validar_base_calculo_com_componentes(op, item, comp)
    assert item.base_calculo == Decimal("850")


def test_rejeita_bc_divergente() -> None:
    op = _operacao(55)
    comp = _componentes_cenario()
    item = ItemOperacaoInput(
        numero=1,
        cst="000",
        c_class_trib="000001",
        ncm="24021000",
        base_calculo=Decimal("900"),
        g_componentes_bc=comp,
    )
    with pytest.raises(BaseCalculoComponentesInconsistenteException, match="850.00"):
        PROCESSAMENTO.validar_base_calculo_com_componentes(op, item, comp)


def test_aceita_bc_consistente() -> None:
    op = _operacao(55)
    comp = _componentes_cenario()
    item = ItemOperacaoInput(
        numero=1,
        cst="000",
        c_class_trib="000001",
        ncm="24021000",
        base_calculo=Decimal("850"),
        g_componentes_bc=comp,
    )
    PROCESSAMENTO.validar_base_calculo_com_componentes(op, item, comp)


def test_rejeita_tp_doc_ausente() -> None:
    op = OperacaoInput(
        id="test",
        versao="1.0",
        municipio=1234567,
        uf="RS",
        data_fato_gerador=date(2026, 1, 1),
    )
    comp = _componentes(vProd=Decimal("1000"))
    item = ItemOperacaoInput(numero=1, cst="000", c_class_trib="000001", g_componentes_bc=comp)
    with pytest.raises(CampoInvalido):
        PROCESSAMENTO.validar_base_calculo_com_componentes(op, item, comp)


def test_rejeita_tp_doc_invalido() -> None:
    op = _operacao(57)
    comp = _componentes(vProd=Decimal("1000"))
    item = ItemOperacaoInput(numero=1, cst="000", c_class_trib="000001", g_componentes_bc=comp)
    with pytest.raises(CampoInvalido):
        PROCESSAMENTO.validar_base_calculo_com_componentes(op, item, comp)


def test_legado_com_bc_informada() -> None:
    item = ItemOperacaoInput(
        numero=1,
        cst="000",
        c_class_trib="000001",
        base_calculo=Decimal("850"),
    )
    PROCESSAMENTO.validar_base_calculo_legado(item)


def test_bc_is_automatica() -> None:
    op = _operacao(55)
    comp = _componentes_cenario()
    item = ItemOperacaoInput(
        numero=1,
        cst="000",
        c_class_trib="000001",
        ncm="24021000",
        g_componentes_bc=comp,
    )
    item.imposto_seletivo = ImpostoSeletivoInput(cst="000", c_class_trib="000000")
    PROCESSAMENTO.validar_base_calculo_com_componentes(op, item, comp)
    assert item.imposto_seletivo.base_calculo is not None
    assert item.base_calculo is None


def test_bc_is_inconsistente() -> None:
    op = _operacao(55)
    comp = _componentes_cenario()
    item = ItemOperacaoInput(
        numero=1,
        cst="000",
        c_class_trib="000001",
        ncm="24021000",
        g_componentes_bc=comp,
    )
    item.imposto_seletivo = ImpostoSeletivoInput(
        cst="000",
        c_class_trib="000000",
        base_calculo=Decimal("999.99"),
    )
    with pytest.raises(BaseCalculoComponentesInconsistenteException):
        PROCESSAMENTO.validar_base_calculo_com_componentes(op, item, comp)


def test_bc_is_consistente() -> None:
    op = _operacao(55)
    comp = _componentes_cenario()
    resultado = calcular(comp, 2026, Natureza.BEM, 55)
    item = ItemOperacaoInput(
        numero=1,
        cst="000",
        c_class_trib="000001",
        ncm="24021000",
        g_componentes_bc=comp,
    )
    item.imposto_seletivo = ImpostoSeletivoInput(
        cst="000",
        c_class_trib="000000",
        base_calculo=resultado.base_is,
    )
    PROCESSAMENTO.validar_base_calculo_com_componentes(op, item, comp)
    assert item.base_calculo is None


def test_defaults_quantidade_e_unidade() -> None:
    item = ItemOperacaoInput()
    aplicar_defaults_quantidade_unidade(item)
    assert item.quantidade == Decimal(1)
    assert item.unidade == "UN"
    parcial = ItemOperacaoInput(quantidade=Decimal("3"))
    aplicar_defaults_quantidade_unidade(parcial)
    assert parcial.quantidade == Decimal("3")
    assert parcial.unidade == "UN"


def test_situacao_tributaria_rejeita_cst_inexistente() -> None:
    servico = SituacaoTributariaService(existe_cst=lambda *_: False)
    with pytest.raises(SituacaoTributariaNaoEncontradaException, match="CBS e IBS"):
        servico.validar_cst("999", ID_TRIBUTO_CBS_IBS, date(2026, 1, 1))


def test_situacao_tributaria_cst_is() -> None:
    chamadas: list[tuple[str, int]] = []

    def existe(cst: str, tributo: int, _data: date) -> bool:
        chamadas.append((cst, tributo))
        return True

    SituacaoTributariaService(existe_cst=existe).validar_cst("100", ID_TRIBUTO_IS, date(2026, 1, 1))
    assert chamadas == [("100", ID_TRIBUTO_IS)]


def test_processar_item_aplica_defaults_e_valida_cst() -> None:
    registros: list[tuple[str, int]] = []
    sit = SituacaoTributariaService(
        existe_cst=lambda cst, trib, _d: registros.append((cst, trib)) or True
    )
    servico = ProcessamentoItemService(
        situacao_tributaria=sit,
        buscar_classificacao_cbs_ibs=lambda _c, _d: ClassificacaoTributariaDTO(1, "000001", "000"),
        buscar_tratamento_classificacao=lambda _i, _d: TratamentoClassificacaoDTO(),
    )
    item = ItemOperacaoInput(cst="000", c_class_trib="000001", base_calculo=Decimal("100"))
    resultado = servico.processar_item(_operacao(55), item, date(2026, 1, 1))
    assert item.quantidade == Decimal(1)
    assert item.unidade == "UN"
    assert (item.cst, ID_TRIBUTO_CBS_IBS) in registros
    assert resultado.tratamento_classificacao_cbs_ibs is not None


def test_processar_item_falha_cst_item() -> None:
    servico = ProcessamentoItemService(
        situacao_tributaria=SituacaoTributariaService(existe_cst=lambda *_: False),
    )
    item = ItemOperacaoInput(cst="000", c_class_trib="000001", base_calculo=Decimal("100"))
    with pytest.raises(SituacaoTributariaNaoEncontradaException):
        servico.processar_item(_operacao(55), item, date(2026, 1, 1))