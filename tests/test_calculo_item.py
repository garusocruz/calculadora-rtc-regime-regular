from datetime import date
from decimal import Decimal

import pytest

from calculadora_rtc_regime_regular.aliquota_resultado import AliquotaResultado, FormaAplicacao
from calculadora_rtc_regime_regular.calculo_item import (
    AliquotasNominais,
    CompraGovernamentalInconsistente,
    ItemOperacao,
    OperacaoCalculo,
    TratamentoClassificacaoItem,
    calcular_tributos,
)
from calculadora_rtc_regime_regular.cbs_ibs import Classificacao, Tratamento


def _tratamento(**extras: object) -> Tratamento:
    base = dict(
        expressao_aliquota="aliquota",
        expressao_base_calculo="baseCalculoInformada",
        expressao_aliquota_efetiva="aliquota*(1-percentualReducao)*(1-pRedutorCompraGov/100)",
        expressao_tributo_calculado="baseCalculo*aliquotaEfetiva",
        expressao_tributo_devido="tributoCalculado",
    )
    base.update(extras)
    return Tratamento(**base)  # type: ignore[arg-type]


def _operacao(
    *,
    base: Decimal = Decimal("100.00"),
    nbs: str | None = None,
    aliquotas: AliquotasNominais | None = None,
    ente: str | None = None,
    redutor: Decimal = Decimal(0),
    calculo_ibs: bool = False,
    quantidade: Decimal | None = None,
    tratamento: Tratamento | None = None,
    classificacao: Classificacao | None = None,
) -> tuple[OperacaoCalculo, dict]:
    dia = date(2026, 1, 1)
    tr = tratamento or _tratamento()
    cl = classificacao or Classificacao(1, "000001", "Padrão")
    op = OperacaoCalculo(
        data=dia,
        codigo_uf=35,
        codigo_municipio=3550308,
        tp_ente_gov=ente,
        p_redutor=redutor,
        item=ItemOperacao(
            base_calculo=base,
            cst="000",
            c_class_trib="000001",
            nbs=nbs,
            aliquotas_nominais=aliquotas,
            quantidade=quantidade,
        ),
        tratamento=TratamentoClassificacaoItem(tr, cl),
    )

    def buscar_padrao(id_tributo: int, uf: int | None, municipio: int | None, data: date) -> AliquotaResultado:
        if id_tributo == 2:
            return AliquotaResultado(Decimal("8.80"), Decimal("0"), FormaAplicacao.ACRESCIMO)
        if id_tributo == 3:
            return AliquotaResultado(Decimal("0.10"), Decimal("0"), FormaAplicacao.ACRESCIMO)
        return AliquotaResultado(Decimal("0.05"), Decimal("0"), FormaAplicacao.ACRESCIMO)

    kwargs = dict(
        calculo_ibs_habilitado=calculo_ibs,
        buscar_padrao=buscar_padrao,
    )
    return op, kwargs


def test_soma_v_ibs_no_grupo() -> None:
    op, kwargs = _operacao(calculo_ibs=True)
    tributos = calcular_tributos(op, **kwargs)
    assert tributos.ibs_cbs is not None
    grupo = tributos.ibs_cbs.grupo_ibs_cbs
    assert grupo is not None
    assert grupo.ibs_uf is not None and grupo.ibs_mun is not None
    assert grupo.valor_ibs == grupo.ibs_uf.valor + grupo.ibs_mun.valor


def test_ibs_somente_quando_habilitado_ou_nbs_ou_aliquota_informada() -> None:
    op_sem, kw_sem = _operacao()
    res_sem = calcular_tributos(op_sem, **kw_sem)
    assert res_sem.ibs_cbs is not None
    assert res_sem.ibs_cbs.grupo_ibs_cbs is not None
    assert res_sem.ibs_cbs.grupo_ibs_cbs.ibs_uf is None
    assert res_sem.ibs_cbs.grupo_ibs_cbs.ibs_mun is None

    op_nbs, kw_nbs = _operacao(nbs="123456789")
    res_nbs = calcular_tributos(op_nbs, **kw_nbs)
    assert res_nbs.ibs_cbs is not None and res_nbs.ibs_cbs.grupo_ibs_cbs is not None
    assert res_nbs.ibs_cbs.grupo_ibs_cbs.ibs_uf is not None

    op_nom, kw_nom = _operacao(
        aliquotas=AliquotasNominais(
            cbs=Decimal("8.8"),
            ibs_estadual=Decimal("0.1"),
            ibs_municipal=Decimal("0.05"),
        )
    )
    res_nom = calcular_tributos(op_nom, **kw_nom)
    assert res_nom.ibs_cbs is not None and res_nom.ibs_cbs.grupo_ibs_cbs is not None
    assert res_nom.ibs_cbs.grupo_ibs_cbs.ibs_mun is not None


def test_totalizadores_monofasia() -> None:
    tratamento = Tratamento(
        expressao_aliquota="aliquotaAdRemPrincipal",
        expressao_base_calculo="quantidade",
        expressao_aliquota_efetiva="aliquotaAdRemSecundaria",
        expressao_tributo_calculado="quantidade*aliquota",
        expressao_tributo_devido="tributoCalculado",
        possui_monofasia=True,
    )
    cl = Classificacao(
        9,
        "620001",
        "Uniforme setorial",
        grupo_monofasia_padrao=True,
        grupo_monofasia_reten=True,
        grupo_monofasia_diferimento=True,
    )
    op, kwargs = _operacao(
        tratamento=tratamento,
        classificacao=cl,
        base=Decimal("10"),
        quantidade=Decimal("2.5"),
        calculo_ibs=True,
    )
    tributos = calcular_tributos(op, **kwargs)
    assert tributos.ibs_cbs is not None
    mono = tributos.ibs_cbs.monofasia
    assert mono is not None
    assert tributos.ibs_cbs.grupo_ibs_cbs is None
    assert mono.padrao is not None
    assert mono.retencao is not None
    assert mono.diferimento is not None
    padrao = mono.padrao
    reten = mono.retencao
    diferido = mono.diferimento
    assert mono.total_ibs == padrao.valor_ibs + reten.valor_ibs - diferido.valor_ibs
    assert mono.total_cbs == padrao.valor_cbs + reten.valor_cbs - diferido.valor_cbs


def test_compra_governamental_inconsistente() -> None:
    op, kwargs = _operacao(ente="UNIAO", redutor=Decimal("20"), calculo_ibs=False)
    with pytest.raises(CompraGovernamentalInconsistente):
        calcular_tributos(op, **kwargs)


def test_compra_governamental_com_tres_tributos() -> None:
    op, kwargs = _operacao(ente="UNIAO", redutor=Decimal("20"), calculo_ibs=True)
    kwargs["percentual_transferencia_cbs"] = Decimal("50")
    tributos = calcular_tributos(op, **kwargs)
    grupo = tributos.ibs_cbs.grupo_ibs_cbs  # type: ignore[union-attr]
    assert grupo is not None
    assert grupo.compra_governamental is not None


def test_grupos_credito_transferencia_estorno_vazios() -> None:
    op, kwargs = _operacao(calculo_ibs=True)
    ibs = calcular_tributos(op, **kwargs).ibs_cbs
    assert ibs is not None
    assert ibs.transferencia_credito is None
    assert ibs.ajuste_competencia is None
    assert ibs.estorno_credito is None
    assert ibs.credito_presumido_operacao is None
    assert ibs.credito_presumido_ibs_zfm is None