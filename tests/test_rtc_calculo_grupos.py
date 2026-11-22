from datetime import date
from decimal import Decimal

from calculadora_rtc_regime_regular.aliquota_resultado import AliquotaResultado, FormaAplicacao
from calculadora_rtc_regime_regular.cbs_ibs import (
    Classificacao,
    Tributo,
    Tratamento,
    calcular_cbs_ibs,
)
from calculadora_rtc_regime_regular.imposto_seletivo import (
    AliquotaSeletivo,
    TratamentoSeletivo,
    calcular_imposto_seletivo,
)


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


def test_sem_aliquota_informada_usa_a_padrao_buscada() -> None:
    dia = date(2026, 1, 1)

    def buscar(id_tributo: int, uf: int | None, municipio: int | None, data: date) -> AliquotaResultado:
        assert (id_tributo, uf, municipio, data) == (1, 35, 3550308, dia)
        return AliquotaResultado(Decimal("26.50"), Decimal("1.50"), FormaAplicacao.ACRESCIMO)

    resultado = calcular_cbs_ibs(
        aliquota_informada=None,
        base_informada=Decimal("1000.00"),
        imposto_seletivo_calculado=Decimal(0),
        imposto_seletivo_informado=None,
        redutor_compra_gov=Decimal(0),
        tratamento=_tratamento(),
        classificacao=Classificacao(1, "000001", "Padrão"),
        id_tributo=1,
        codigo_uf=35,
        codigo_municipio=3550308,
        data=dia,
        buscar_padrao=buscar,
    )
    assert resultado is not None
    assert resultado.aliquota == Decimal("28.0000")
    assert resultado.tributo_calculado == Decimal("280.00")
    assert resultado.tributo_devido == Decimal("280.00")


def test_tributacao_regular_zera_o_tributo_publicado_e_calcula_o_grupo() -> None:
    resultado = calcular_cbs_ibs(
        aliquota_informada=Decimal("10"),
        base_informada=Decimal("200.00"),
        imposto_seletivo_calculado=Decimal(0),
        imposto_seletivo_informado=None,
        redutor_compra_gov=Decimal(0),
        tratamento=_tratamento(possui_percentual_reducao=True),
        classificacao=Classificacao(1, "200022", "Padrão", grupo_reducao=True),
        percentual_reducao=Decimal("40"),
        tem_tributacao_regular=True,
        cst_regular="000",
        c_class_trib_regular="000001",
    )
    assert resultado is not None
    assert resultado.aliquota == Decimal(0)
    assert resultado.tributo_calculado == Decimal(0)
    assert resultado.tributo_devido == Decimal(0)
    assert resultado.reducao is None
    assert resultado.tributacao_regular is not None
    assert resultado.tributacao_regular.cst == "000"
    assert resultado.tributacao_regular.c_class_trib == "000001"
    assert resultado.tributacao_regular.base_calculo == Decimal("200.00")
    assert resultado.tributacao_regular.aliquota_efetiva == Decimal("6.0000")
    assert resultado.tributacao_regular.tributo_devido == Decimal("12.00")


def test_compra_governamental_publica_a_aliquota_efetiva_do_tributo() -> None:
    resultado = calcular_cbs_ibs(
        aliquota_informada=Decimal("10"),
        base_informada=Decimal("100.00"),
        imposto_seletivo_calculado=Decimal(0),
        imposto_seletivo_informado=None,
        redutor_compra_gov=Decimal("20"),
        tratamento=_tratamento(),
        classificacao=Classificacao(1, "000001", "Padrão"),
        tributo=Tributo.CBS,
        ente_governamental="UNIAO",
    )
    assert resultado is not None
    assert resultado.compra_governamental is not None
    assert resultado.compra_governamental.aliquota_cbs == Decimal("8.0000")
    assert resultado.compra_governamental.tributo_cbs == Decimal("8.00")
    assert resultado.tributo_devido == Decimal("8.00")


def test_monofasia_padrao_usa_a_aliquota_ad_rem_sem_arredondar_a_quantidade() -> None:
    resultado = calcular_cbs_ibs(
        aliquota_informada=None,
        base_informada=Decimal("10"),
        imposto_seletivo_calculado=Decimal(0),
        imposto_seletivo_informado=None,
        redutor_compra_gov=Decimal(0),
        tratamento=Tratamento(
            expressao_aliquota="aliquotaAdRemPrincipal",
            expressao_base_calculo="quantidade",
            expressao_aliquota_efetiva="aliquotaAdRemSecundaria",
            expressao_tributo_calculado="quantidade*aliquota",
            expressao_tributo_devido="tributoCalculado",
            possui_monofasia=True,
        ),
        classificacao=Classificacao(9, "620001", "Uniforme setorial", grupo_monofasia_padrao=True),
        quantidade=Decimal("2.5"),
    )
    assert resultado is not None
    assert resultado.base_calculo == Decimal("2.5")
    assert resultado.monofasia is not None
    assert resultado.monofasia.padrao is not None
    assert resultado.monofasia.padrao.quantidade == Decimal("2.5")
    assert resultado.monofasia.padrao.aliquota_ad_rem == Decimal("0.7925")
    assert resultado.monofasia.padrao.valor == Decimal("1.98")
    assert resultado.monofasia.retencao is None


def test_imposto_seletivo_arredonda_base_e_aliquota_antes_do_produto() -> None:
    resultado = calcular_imposto_seletivo(
        cst="000",
        c_class_trib="000001",
        unidade="L",
        base_informada=Decimal("10.006"),
        quantidade=Decimal("2"),
        imposto_seletivo_informado=None,
        aliquota=AliquotaSeletivo(Decimal("10.12344"), Decimal("1.23456")),
        tratamento=TratamentoSeletivo(
            expressao_base_calculo="baseCalculoInformada",
            expressao_tributo_calculado="baseCalculo*aliquotaAdValorem+quantidade*aliquotaAdRem",
            expressao_tributo_devido="tributoCalculado",
        ),
    )
    assert resultado.base_calculo == Decimal("10.01")
    assert resultado.aliquota_ad_valorem == Decimal("10.1234")
    assert resultado.aliquota_ad_rem == Decimal("1.2346")
    assert resultado.valor == Decimal("3.48")
