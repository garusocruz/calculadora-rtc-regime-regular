"""Tests ported from Java ROC domain (pin f1eebd7ce3157423b1a6aaca7dc1d6c3395452c4)."""

from __future__ import annotations

from datetime import date
from decimal import Decimal

import pytest

from calculadora_rtc_regime_regular.roc import (
    CBSTotalAccumulator,
    CBSTotalDomain,
    CBSDomain,
    CbsIbsOutput,
    CreditoPresumidoOperacaoDomain,
    DevolucaoTributosDomain,
    DiferimentoDomain,
    EstornoCreditoAccumulator,
    EstornoCreditoDomain,
    GrupoEtapaMonofasiaOutput,
    GrupoDiferimentoMonofasiaOutput,
    GrupoIBSCBSDomain,
    GrupoMonofasiaOutput,
    IBSCBSCreditoPresumidoDomain,
    IBSCBSDomain,
    IBSCBSTotalDomain,
    IBSMunDomain,
    IBSMunTotalAccumulator,
    IBSUFDomain,
    IBSUFTotalAccumulator,
    ImpostoSeletivoDomain,
    MonofasiaDiferimentoDomain,
    MonofasiaDomain,
    MonofasiaPadraoDomain,
    MonofasiaRetencaoDomain,
    MonofasiaRetidoAnteriormenteDomain,
    MonofasiaTotalAccumulator,
    ObjetoDomain,
    TipoEnteGovernamental,
    TributacaoCompraGovernamentalDomain,
    TributacaoRegularDomain,
    TributosDomain,
    ZERO,
)

ONE = Decimal(1)
TWO = Decimal(2)
TEN = Decimal(10)
VBC = Decimal("1000.00")


def d(value: str | Decimal) -> Decimal:
    return value if isinstance(value, Decimal) else Decimal(value)


# --- Teste_ObjetoDomain ---


def test_teste_inicializarObjetoDomainVazio_retornaDefaultsEFalse() -> None:
    obj = ObjetoDomain(n_obj=1)
    assert not obj.possui_imposto_seletivo()
    assert obj.get_imposto_seletivo() is None
    assert obj.get_valor_imposto_seletivo() == ZERO
    assert not obj.possui_base_calculo_ibscbs()
    assert obj.get_valor_base_calculo_ibscbs() == ZERO
    assert not obj.possui_cbs()
    assert obj.get_g_cbs() is None
    assert not obj.possui_cred_pres_cbs()
    assert obj.get_cred_pres_cbs() is None
    assert not obj.possui_cred_pres_ibs()
    assert not obj.possui_cred_pres_cond_sus_ibs()
    assert obj.get_v_cred_pres_ibs() == ZERO
    assert obj.get_v_cred_pres_cond_sus_ibs() == ZERO
    assert obj.get_grupo_ibscbs() is None
    assert not obj.possui_ibs_uf()
    assert obj.get_g_ibs_uf() is None
    assert not obj.possui_ibs_mun()
    assert obj.get_g_ibs_mun() is None
    assert not obj.possui_monofasia()
    assert obj.get_g_ibscbs_mono() is None
    assert not obj.possui_tributacao_regular()
    assert obj.get_tributacao_regular() is None
    assert not obj.possui_estorno_credito()
    assert obj.get_g_estorno_cred() is None


def test_teste_objetoDomainComTribCalc_delegaCorretamente() -> None:
    is_dom = ImpostoSeletivoDomain(v_is=d("50"))
    cbs = CBSDomain()
    grupo = GrupoIBSCBSDomain(g_cbs=cbs)
    ibscbs = IBSCBSDomain(g_ibscbs=grupo)
    tributos = TributosDomain(IS=is_dom, IBSCBS=ibscbs)
    obj = ObjetoDomain(n_obj=1, trib_calc=tributos)
    assert obj.possui_imposto_seletivo()
    assert obj.get_imposto_seletivo() is not None
    assert obj.get_valor_imposto_seletivo() == d("50")
    assert obj.possui_cbs()
    assert obj.get_g_cbs() is not None


def test_teste_compareTo_comparaCorretamente() -> None:
    obj1 = ObjetoDomain(n_obj=1)
    obj2 = ObjetoDomain(n_obj=2)
    obj3 = ObjetoDomain(n_obj=1)
    assert obj1 < obj2
    assert obj2 > obj1
    assert (obj1 < obj3) is False and (obj1 > obj3) is False


def test_teste_compareToComNull_objNullMenor() -> None:
    obj_null = ObjetoDomain(n_obj=None)
    obj1 = ObjetoDomain(n_obj=1)
    assert obj_null < obj1
    assert obj1 > obj_null


def test_teste_equalsEHashCode_consideraApenasNumeroDeObj() -> None:
    obj1 = ObjetoDomain(n_obj=1)
    obj2 = ObjetoDomain(n_obj=1, trib_calc=TributosDomain())
    assert obj1 == obj2
    assert hash(obj1) == hash(obj2)


# --- Teste_IBSCBSDomain ---


def test_teste_IBSCBSDomainVazio_retornaFalseENull() -> None:
    domain = IBSCBSDomain()
    assert not domain.possui_base_calculo_ibscbs()
    assert domain.get_valor_base_calculo_ibscbs() == ZERO
    assert not domain.possui_cbs()
    assert domain.get_g_cbs() is None
    assert domain.get_grupo_ibscbs() is None
    assert not domain.possui_ibs_uf()
    assert not domain.possui_ibs_mun()
    assert domain.get_g_ibs_uf() is None
    assert domain.get_g_ibs_mun() is None
    assert not domain.possui_tributacao_regular()
    assert domain.get_tributacao_regular() is None


def test_teste_IBSCBSDomainComGrupoIBSCBS_retornaDelegates() -> None:
    cbs = CBSDomain()
    ibs_uf = IBSUFDomain()
    ibs_mun = IBSMunDomain()
    trib_reg = TributacaoRegularDomain()
    grupo = GrupoIBSCBSDomain(g_cbs=cbs, g_ibs_uf=ibs_uf, g_ibs_mun=ibs_mun, g_trib_regular=trib_reg)
    domain = IBSCBSDomain(g_ibscbs=grupo)
    assert domain.possui_cbs()
    assert domain.get_g_cbs() is not None
    assert domain.possui_ibs_uf()
    assert domain.possui_ibs_mun()
    assert domain.get_g_ibs_uf() is not None
    assert domain.get_g_ibs_mun() is not None
    assert domain.possui_tributacao_regular()
    assert domain.get_tributacao_regular() is not None
    assert domain.get_grupo_ibscbs() is not None


def test_teste_possuiMonofasiaComGIBSCBSMono_retornaTrue() -> None:
    domain = IBSCBSDomain(g_ibscbs_mono=MonofasiaDomain())
    assert domain.possui_monofasia()


def test_teste_possuiMonofasiaSemGIBSCBSMono_retornaFalse() -> None:
    assert not IBSCBSDomain().possui_monofasia()


def test_teste_possuiEstornoCreditoComEstorno_retornaTrue() -> None:
    assert IBSCBSDomain(g_estorno_cred=EstornoCreditoDomain()).possui_estorno_credito()


def test_teste_possuiEstornoCreditoSemEstorno_retornaFalse() -> None:
    assert not IBSCBSDomain().possui_estorno_credito()


def test_teste_IBSCBSDomainSemCredPresOper_retornaFalse() -> None:
    domain = IBSCBSDomain()
    assert not domain.possui_cred_pres_cbs()
    assert domain.get_cred_pres_cbs() is None
    assert not domain.possui_cred_pres_ibs()
    assert domain.get_v_cred_pres_ibs() == ZERO
    assert not domain.possui_cred_pres_cond_sus_ibs()
    assert domain.get_v_cred_pres_cond_sus_ibs() == ZERO


def test_teste_IBSCBSDomainComCredPresOper_retornaTrue() -> None:
    cred_pres = CreditoPresumidoOperacaoDomain(g_cbs_cred_pres=IBSCBSCreditoPresumidoDomain())
    domain = IBSCBSDomain(g_cred_pres_oper=cred_pres)
    assert domain.possui_cred_pres_cbs()
    assert domain.get_cred_pres_cbs() is not None


def test_teste_IBSCBSDomainComCredPresOperEValor_retornaTrueEValor() -> None:
    ibs_cred = IBSCBSCreditoPresumidoDomain(v_cred_pres=d("25.00"))
    cred_pres = CreditoPresumidoOperacaoDomain(g_ibs_cred_pres=ibs_cred)
    domain = IBSCBSDomain(g_cred_pres_oper=cred_pres)
    assert domain.possui_cred_pres_ibs()
    assert domain.get_v_cred_pres_ibs() == d("25.00")


# --- Teste_TributosDomain ---


def test_teste_inicializacaoSemImpostoSeletivo_retornaFalse() -> None:
    tributos = TributosDomain()
    assert not tributos.possui_imposto_seletivo()
    assert tributos.get_valor_imposto_seletivo() == ZERO


def test_teste_inicializacaoComImpostoSeletivo_retornaTrue() -> None:
    tributos = TributosDomain(IS=ImpostoSeletivoDomain(v_is=d("100")))
    assert tributos.possui_imposto_seletivo()
    assert tributos.get_valor_imposto_seletivo() == d("100")


def test_teste_inicializacaoSemIBSCBS_retornaDefaultsNullEZero() -> None:
    tributos = TributosDomain()
    assert not tributos.possui_base_calculo_ibscbs()
    assert tributos.get_valor_base_calculo_ibscbs() == ZERO
    assert not tributos.possui_cbs()
    assert tributos.get_g_cbs() is None
    assert not tributos.possui_monofasia()
    assert tributos.get_g_ibscbs_mono() is None
    assert not tributos.possui_estorno_credito()
    assert tributos.get_g_estorno_cred() is None


def test_teste_inicializacaoComIBSCBSComGrupo_retornaDelegates() -> None:
    grupo = GrupoIBSCBSDomain(
        g_cbs=CBSDomain(),
        g_ibs_uf=IBSUFDomain(),
        g_ibs_mun=IBSMunDomain(),
        g_trib_regular=TributacaoRegularDomain(),
    )
    ibscbs = IBSCBSDomain(g_ibscbs=grupo)
    tributos = TributosDomain(IBSCBS=ibscbs)
    assert tributos.possui_cbs()
    assert tributos.possui_ibs_uf()
    assert tributos.possui_tributacao_regular()


def test_teste_inicializacaoComMonofasia_retornaTrue() -> None:
    tributos = TributosDomain(IBSCBS=IBSCBSDomain(g_ibscbs_mono=MonofasiaDomain()))
    assert tributos.possui_monofasia()
    assert tributos.get_g_ibscbs_mono() is not None


def test_teste_inicializacaoComEstornoCredito_retornaTrue() -> None:
    tributos = TributosDomain(IBSCBS=IBSCBSDomain(g_estorno_cred=EstornoCreditoDomain()))
    assert tributos.possui_estorno_credito()
    assert tributos.get_g_estorno_cred() is not None


# --- Teste_CreditoPresumidoOperacaoDomain ---


def test_teste_possuiCredPresCbsSemDados_retornaFalse() -> None:
    assert not CreditoPresumidoOperacaoDomain().possui_cred_pres_cbs()


def test_teste_possuiCredPresCbsComDados_retornaTrue() -> None:
    domain = CreditoPresumidoOperacaoDomain(g_cbs_cred_pres=IBSCBSCreditoPresumidoDomain())
    assert domain.possui_cred_pres_cbs()


def test_teste_possuiCredPresIbsComValor_retornaTrue() -> None:
    ibs = IBSCBSCreditoPresumidoDomain(v_cred_pres=d("10.00"))
    domain = CreditoPresumidoOperacaoDomain(g_ibs_cred_pres=ibs)
    assert domain.possui_cred_pres_ibs()


def test_teste_getVCredPresCondSusIbsComDados_retornaValor() -> None:
    ibs = IBSCBSCreditoPresumidoDomain(v_cred_pres_cond_sus=d("7.75"))
    domain = CreditoPresumidoOperacaoDomain(g_ibs_cred_pres=ibs)
    assert domain.get_v_cred_pres_cond_sus_ibs() == d("7.75")


# --- MonofasiaDomainTest ---


def test_testGettersMonofasiaPadrao() -> None:
    monofasia = MonofasiaDomain(g_mono_padrao=MonofasiaPadraoDomain(v_ibs_mono=d("792.50"), v_cbs_mono=d("792.50")))
    assert monofasia.get_v_ibs_mono() == d("792.50")
    assert monofasia.get_v_cbs_mono() == d("792.50")
    assert monofasia.get_v_ibs_mono_reten() == ZERO


def test_testTotalizadoresZero() -> None:
    monofasia = MonofasiaDomain()
    assert monofasia.get_v_tot_ibs_mono_item() == ZERO
    assert monofasia.get_v_tot_cbs_mono_item() == ZERO


# --- IBSCBSTotalDomainTest ---


def test_testMonofasiaSemTributacaoRegular_DeveConterCamposObrigatoriosZerados() -> None:
    objeto = ObjetoDomain(
        n_obj=1,
        trib_calc=TributosDomain(
            IBSCBS=IBSCBSDomain(
                CST="620",
                c_class_trib="620001",
                g_ibscbs_mono=MonofasiaDomain(
                    g_mono_padrao=MonofasiaPadraoDomain(
                        q_bc_mono=d("1000"),
                        ad_rem_ibs=d("0.7925"),
                        ad_rem_cbs=d("0.7925"),
                        v_ibs_mono=d("792.50"),
                        v_cbs_mono=d("792.50"),
                    ),
                    v_tot_ibs_mono_item=d("792.50"),
                    v_tot_cbs_mono_item=d("792.50"),
                ),
            )
        ),
    )
    total = IBSCBSTotalDomain.create([objeto])
    assert total is not None
    assert total.v_bc_ibscbs == ZERO
    assert total.g_ibs is not None
    assert total.g_ibs.g_ibs_uf is not None
    assert total.g_ibs.g_ibs_uf.v_dif == ZERO
    assert total.g_cbs is not None
    assert total.g_cbs.v_cbs == ZERO
    assert total.g_mono is not None
    assert total.g_mono.v_ibs_mono == d("792.50")
    assert total.g_mono.v_cbs_mono == d("792.50")


# --- CBSTotalAccumulatorTest ---


def test_testDefaultConstructor() -> None:
    total = CBSTotalAccumulator().to_cbs_total()
    assert total.v_dif == ZERO
    assert total.v_cbs == ZERO


def test_testFromMethodWithValues() -> None:
    cbs = CBSDomain(
        g_dif=DiferimentoDomain(v_dif=TEN),
        g_dev_trib=DevolucaoTributosDomain(v_dev_trib=ONE),
        v_cbs=d("5.00"),
    )
    cred = IBSCBSCreditoPresumidoDomain(v_cred_pres=TWO, v_cred_pres_cond_sus=d("3.97"))
    total = CBSTotalAccumulator.from_fields(cbs, cred).to_cbs_total()
    assert total.v_dif == TEN
    assert total.v_dev_trib == ONE
    assert total.v_cbs == d("5.00")
    assert total.v_cred_pres == TWO


def test_testAddMethod() -> None:
    result = CBSTotalAccumulator(ONE, ONE, ONE, ONE, ONE).add(
        CBSTotalAccumulator(TEN, TEN, TEN, TEN, TEN)
    )
    total = result.to_cbs_total()
    onze = d("11.00")
    assert total.v_dif == onze
    assert total.v_cbs == onze


# --- IBSUFTotalAccumulator / IBSMun / Monofasia / Estorno (spot check) ---


def test_testFromMethodWithValues_ibs_uf() -> None:
    ibs_uf = IBSUFDomain(
        g_dif=DiferimentoDomain(v_dif=TEN),
        g_dev_trib=DevolucaoTributosDomain(v_dev_trib=ONE),
        v_ibs_uf=Decimal(5),
    )
    total = IBSUFTotalAccumulator.from_fields(ibs_uf).to_ibs_uf_total()
    assert total.v_dif == TEN
    assert total.v_ibs_uf == Decimal(5)


def test_teste_addValor_somaCorretamente_estorno() -> None:
    total = EstornoCreditoAccumulator(TEN, ONE).add(
        EstornoCreditoAccumulator(d("5"), d("2"))
    ).to_estorno_credito_domain_total()
    assert total.v_ibs_est_cred == d("15")
    assert total.v_cbs_est_cred == d("3")


# --- TributacaoCompraGovernamentalDomainTest ---


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
    assert resultado.p_aliq_cbs == d("8.90")
    assert resultado.v_trib_cbs == d("1.07")
    assert resultado.p_aliq_ibs_uf == ZERO


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
    assert resultado.p_aliq_cbs == d("3.1724")
    assert resultado.v_trib_cbs == d("39.17")
    assert resultado.p_aliq_ibs_uf == d("3.7796")
    assert resultado.v_trib_ibs_uf == d("46.66")


def test_transferenciaDaCbs_quemCedeArredonda_quemRecebeFechaPelaDiferenca() -> None:
    detalhe = TributacaoCompraGovernamentalDomain(p_aliq_cbs=d("1.2345"))
    estado = detalhe.get_valores_efetivos(
        TipoEnteGovernamental.ESTADO, d("10"), date(2029, 1, 1), VBC
    )
    assert estado is not None
    assert estado.p_aliq_cbs == d("1.1110")
    assert estado.v_trib_cbs == d("11.11")
    assert estado.p_aliq_ibs_uf == d("0.1235")
    municipio = detalhe.get_valores_efetivos(
        TipoEnteGovernamental.MUNICIPIO, d("10"), date(2029, 1, 1), VBC
    )
    assert municipio is not None
    assert municipio.p_aliq_ibs_mun == d("0.1235")


def test_deveRetornarNuloQuandoTipoEnteForNulo() -> None:
    domain = _criar_domain_base()
    assert domain.get_valores_efetivos(None, d("25"), date(2027, 1, 1), VBC) is None


def test_deveLancarExcecaoQuandoDataFatoGeradorForNula() -> None:
    with pytest.raises(TypeError, match="Data do fato gerador"):
        _criar_domain_base().get_valores_efetivos(
            TipoEnteGovernamental.ESTADO, d("25"), None, VBC
        )


def test_deveLancarExcecaoQuandoPercentualTransferenciaForNulo() -> None:
    with pytest.raises(TypeError, match="transferência"):
        _criar_domain_base().get_valores_efetivos(
            TipoEnteGovernamental.ESTADO, None, date(2027, 1, 1), VBC
        )


def test_deveRetornarMesmaInstanciaAntesDe2027() -> None:
    domain = _criar_domain_base()
    resultado = domain.get_valores_efetivos(
        TipoEnteGovernamental.ESTADO, d("25"), date(2026, 12, 31), VBC
    )
    assert resultado is domain


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


CENARIOS_UNIAO = _cenarios_uniao()
CENARIOS_ESTADO = _cenarios_estado()
CENARIOS_MUNICIPIO = _cenarios_municipio()


@pytest.mark.parametrize(
    "ano,p_trans,p_cbs,v_cbs,p_uf,v_uf,p_mun,v_mun",
    CENARIOS_UNIAO,
)
def test_deveConcentrarTudoNaCbsQuandoUniaoCompraAPartirDe2027(
    ano: int,
    p_trans: Decimal,
    p_cbs: Decimal,
    v_cbs: Decimal,
    p_uf: Decimal,
    v_uf: Decimal,
    p_mun: Decimal,
    v_mun: Decimal,
) -> None:
    domain = _criar_domain_base()
    resultado = domain.get_valores_efetivos(
        TipoEnteGovernamental.UNIAO, p_trans, date(ano, 1, 1), VBC
    )
    assert resultado is not None
    _assert_resultado(resultado, p_cbs, v_cbs, p_uf, v_uf, p_mun, v_mun)


@pytest.mark.parametrize(
    "ano,p_trans,p_cbs,v_cbs,p_uf,v_uf,p_mun,v_mun",
    CENARIOS_ESTADO,
)
def test_deveTransferirParaUfQuandoEstadoCompraAPartirDe2027(
    ano: int,
    p_trans: Decimal,
    p_cbs: Decimal,
    v_cbs: Decimal,
    p_uf: Decimal,
    v_uf: Decimal,
    p_mun: Decimal,
    v_mun: Decimal,
) -> None:
    domain = _criar_domain_base()
    resultado = domain.get_valores_efetivos(
        TipoEnteGovernamental.ESTADO, p_trans, date(ano, 1, 1), VBC
    )
    assert resultado is not None
    _assert_resultado(resultado, p_cbs, v_cbs, p_uf, v_uf, p_mun, v_mun)


@pytest.mark.parametrize(
    "ano,p_trans,p_cbs,v_cbs,p_uf,v_uf,p_mun,v_mun",
    CENARIOS_MUNICIPIO,
)
def test_deveTransferirParaMunicipioQuandoMunicipioCompraAPartirDe2027(
    ano: int,
    p_trans: Decimal,
    p_cbs: Decimal,
    v_cbs: Decimal,
    p_uf: Decimal,
    v_uf: Decimal,
    p_mun: Decimal,
    v_mun: Decimal,
) -> None:
    domain = _criar_domain_base()
    resultado = domain.get_valores_efetivos(
        TipoEnteGovernamental.MUNICIPIO, p_trans, date(ano, 1, 1), VBC
    )
    assert resultado is not None
    _assert_resultado(resultado, p_cbs, v_cbs, p_uf, v_uf, p_mun, v_mun)


# --- Teste_MonofasiaDomainExpanded (ROC create + merge) ---


def test_teste_monofasiaPadraoComCBSIBS_retornaCBSIBS() -> None:
    resultado = MonofasiaPadraoDomain.create(
        _cbs_mono("10.0000", "1.10", "11.00"),
        _cbs_mono("20.0000", "2.20", "22.00"),
        _cbs_mono("99.0000", "9.99", "99.00"),
    )
    assert resultado is not None
    assert resultado.q_bc_mono == d("20.0000")
    assert resultado.v_ibs_mono == d("22.00")
    assert resultado.v_cbs_mono == d("11.00")


def test_teste_criacaoMonofasicaComNull_retornaNull() -> None:
    assert MonofasiaPadraoDomain.create(None, None, None) is None
    assert MonofasiaRetencaoDomain.create(None, None, None) is None


def test_teste_mergeGrupoEtapaMonofasiaExistenteComNull_retornaGrupoExistente() -> None:
    grupo = GrupoEtapaMonofasiaOutput(quantidade=d("1"), aliquota_ad_rem=d("1.10"), valor=d("11"))
    assert GrupoEtapaMonofasiaOutput.merge(None, grupo) is grupo
    assert GrupoEtapaMonofasiaOutput.merge(grupo, None) is grupo


def test_teste_mergeGrupoEtapaMonofasia_retornaSomandoValoresECompletandoNulls() -> None:
    g1 = GrupoEtapaMonofasiaOutput(valor=d("1.25"))
    g2 = GrupoEtapaMonofasiaOutput(quantidade=d("2"), aliquota_ad_rem=d("2.20"), valor=d("2.75"))
    resultado = GrupoEtapaMonofasiaOutput.merge(g1, g2)
    assert resultado is not None
    assert resultado.quantidade == d("2")
    assert resultado.valor == d("4.00")


def _criar_domain_base() -> TributacaoCompraGovernamentalDomain:
    return TributacaoCompraGovernamentalDomain(
        p_aliq_cbs=d("20.00"),
        v_trib_cbs=d("200.00"),
        p_aliq_ibs_uf=d("10.00"),
        v_trib_ibs_uf=d("100.00"),
        p_aliq_ibs_mun=d("5.00"),
        v_trib_ibs_mun=d("50.00"),
    )


def _assert_resultado(
    resultado: TributacaoCompraGovernamentalDomain,
    p_cbs: Decimal,
    v_cbs: Decimal,
    p_uf: Decimal,
    v_uf: Decimal,
    p_mun: Decimal,
    v_mun: Decimal,
) -> None:
    assert resultado.p_aliq_cbs == p_cbs
    assert resultado.v_trib_cbs == v_cbs
    assert resultado.p_aliq_ibs_uf == p_uf
    assert resultado.v_trib_ibs_uf == v_uf
    assert resultado.p_aliq_ibs_mun == p_mun
    assert resultado.v_trib_ibs_mun == v_mun


def _cbs_mono(q: str, aliq: str, val: str) -> CbsIbsOutput:
    return CbsIbsOutput(
        grupo_monofasia=GrupoMonofasiaOutput(
            tributo_monofasico=GrupoEtapaMonofasiaOutput(
                quantidade=d(q),
                aliquota_ad_rem=d(aliq),
                valor=d(val),
            )
        )
    )