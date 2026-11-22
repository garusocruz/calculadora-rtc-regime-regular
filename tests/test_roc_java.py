"""Domínio ROC espelhando @Test Java (pin f1eebd7ce3157423b1a6aaca7dc1d6c3395452c4)."""

from __future__ import annotations

from decimal import Decimal

from calculadora_rtc_regime_regular.roc import (
    CBSDomain,
    CbsIbsOutput,
    CreditoPresumidoOperacaoDomain,
    EstornoCreditoAccumulator,
    EstornoCreditoDomain,
    GrupoDiferimentoMonofasiaOutput,
    GrupoEtapaMonofasiaOutput,
    GrupoIBSCBSDomain,
    GrupoMonofasiaOutput,
    IBSCBSCreditoPresumidoDomain,
    IBSCBSDomain,
    IBSMunDomain,
    IBSUFDomain,
    ImpostoSeletivoDomain,
    MonofasiaDiferimentoDomain,
    MonofasiaDomain,
    MonofasiaPadraoDomain,
    MonofasiaRetencaoDomain,
    MonofasiaRetidoAnteriormenteDomain,
    ObjetoDomain,
    TributacaoRegularDomain,
    TributosDomain,
    ZERO,
)

_FQCN = "br.gov.serpro.rtc.testesunitarios.domain"
ONE = Decimal(1)
TEN = Decimal(10)


def d(value: str | Decimal) -> Decimal:
    return value if isinstance(value, Decimal) else Decimal(value)


def _java(record_xml_attribute, class_name: str, method: str) -> None:
    record_xml_attribute("classname", f"{_FQCN}.{class_name}")
    record_xml_attribute("name", method)


def _etapa(q: str, aliq: str, val: str) -> GrupoEtapaMonofasiaOutput:
    return GrupoEtapaMonofasiaOutput(quantidade=d(q), aliquota_ad_rem=d(aliq), valor=d(val))


def _cbs_mono(q: str, aliq: str, val: str) -> CbsIbsOutput:
    return CbsIbsOutput(
        grupo_monofasia=GrupoMonofasiaOutput(tributo_monofasico=_etapa(q, aliq, val))
    )


def _cbs_retencao(q: str, aliq: str, val: str) -> CbsIbsOutput:
    return CbsIbsOutput(
        grupo_monofasia=GrupoMonofasiaOutput(tributo_sujeito_retencao=_etapa(q, aliq, val))
    )


def _cbs_retido(q: str, aliq: str, val: str) -> CbsIbsOutput:
    return CbsIbsOutput(
        grupo_monofasia=GrupoMonofasiaOutput(tributo_retido=_etapa(q, aliq, val))
    )


def _cbs_diferido(p: str, val: str) -> CbsIbsOutput:
    return CbsIbsOutput(
        grupo_monofasia=GrupoMonofasiaOutput(
            tributo_diferido=GrupoDiferimentoMonofasiaOutput(
                percentual_diferimento=d(p), valor_diferimento=d(val)
            )
        )
    )


# --- Teste_ObjetoDomain ---


def test_teste_inicializarObjetoDomainVazio_retornaDefaultsEFalse(record_xml_attribute) -> None:
    _java(record_xml_attribute, "Teste_ObjetoDomain", "teste_inicializarObjetoDomainVazio_retornaDefaultsEFalse")
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


def test_teste_objetoDomainComTribCalc_delegaCorretamente(record_xml_attribute) -> None:
    _java(record_xml_attribute, "Teste_ObjetoDomain", "teste_objetoDomainComTribCalc_delegaCorretamente")
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


def test_teste_compareTo_comparaCorretamente(record_xml_attribute) -> None:
    _java(record_xml_attribute, "Teste_ObjetoDomain", "teste_compareTo_comparaCorretamente")
    obj1 = ObjetoDomain(n_obj=1)
    obj2 = ObjetoDomain(n_obj=2)
    obj3 = ObjetoDomain(n_obj=1)
    assert obj1 < obj2
    assert obj2 > obj1
    assert (obj1 < obj3) is False and (obj1 > obj3) is False


def test_teste_compareToComNull_objNullMenor(record_xml_attribute) -> None:
    _java(record_xml_attribute, "Teste_ObjetoDomain", "teste_compareToComNull_objNullMenor")
    obj_null = ObjetoDomain(n_obj=None)
    obj1 = ObjetoDomain(n_obj=1)
    assert obj_null < obj1
    assert obj1 > obj_null


def test_teste_equalsEHashCode_consideraApenasNumeroDeObj(record_xml_attribute) -> None:
    _java(record_xml_attribute, "Teste_ObjetoDomain", "teste_equalsEHashCode_consideraApenasNumeroDeObj")
    obj1 = ObjetoDomain(n_obj=1)
    obj2 = ObjetoDomain(n_obj=1, trib_calc=TributosDomain())
    assert obj1 == obj2
    assert hash(obj1) == hash(obj2)


# --- Teste_IBSCBSDomain ---


def test_teste_IBSCBSDomainVazio_retornaFalseENull(record_xml_attribute) -> None:
    _java(record_xml_attribute, "Teste_IBSCBSDomain", "teste_IBSCBSDomainVazio_retornaFalseENull")
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


def test_teste_IBSCBSDomainComGrupoIBSCBS_retornaDelegates(record_xml_attribute) -> None:
    _java(record_xml_attribute, "Teste_IBSCBSDomain", "teste_IBSCBSDomainComGrupoIBSCBS_retornaDelegates")
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


def test_teste_possuiMonofasiaComGIBSCBSMono_retornaTrue(record_xml_attribute) -> None:
    _java(record_xml_attribute, "Teste_IBSCBSDomain", "teste_possuiMonofasiaComGIBSCBSMono_retornaTrue")
    assert IBSCBSDomain(g_ibscbs_mono=MonofasiaDomain()).possui_monofasia()


def test_teste_possuiMonofasiaSemGIBSCBSMono_retornaFalse(record_xml_attribute) -> None:
    _java(record_xml_attribute, "Teste_IBSCBSDomain", "teste_possuiMonofasiaSemGIBSCBSMono_retornaFalse")
    assert not IBSCBSDomain().possui_monofasia()


def test_teste_possuiEstornoCreditoComEstorno_retornaTrue(record_xml_attribute) -> None:
    _java(record_xml_attribute, "Teste_IBSCBSDomain", "teste_possuiEstornoCreditoComEstorno_retornaTrue")
    assert IBSCBSDomain(g_estorno_cred=EstornoCreditoDomain()).possui_estorno_credito()


def test_teste_possuiEstornoCreditoSemEstorno_retornaFalse(record_xml_attribute) -> None:
    _java(record_xml_attribute, "Teste_IBSCBSDomain", "teste_possuiEstornoCreditoSemEstorno_retornaFalse")
    assert not IBSCBSDomain().possui_estorno_credito()


def test_teste_IBSCBSDomainSemCredPresOper_retornaFalse(record_xml_attribute) -> None:
    _java(record_xml_attribute, "Teste_IBSCBSDomain", "teste_IBSCBSDomainSemCredPresOper_retornaFalse")
    domain = IBSCBSDomain()
    assert not domain.possui_cred_pres_cbs()
    assert domain.get_cred_pres_cbs() is None
    assert not domain.possui_cred_pres_ibs()
    assert domain.get_v_cred_pres_ibs() == ZERO
    assert not domain.possui_cred_pres_cond_sus_ibs()
    assert domain.get_v_cred_pres_cond_sus_ibs() == ZERO


def test_teste_IBSCBSDomainComCredPresOper_retornaTrue(record_xml_attribute) -> None:
    _java(record_xml_attribute, "Teste_IBSCBSDomain", "teste_IBSCBSDomainComCredPresOper_retornaTrue")
    cred_pres = CreditoPresumidoOperacaoDomain(g_cbs_cred_pres=IBSCBSCreditoPresumidoDomain())
    domain = IBSCBSDomain(g_cred_pres_oper=cred_pres)
    assert domain.possui_cred_pres_cbs()
    assert domain.get_cred_pres_cbs() is not None


def test_teste_IBSCBSDomainComCredPresOperEValor_retornaTrueEValor(record_xml_attribute) -> None:
    _java(record_xml_attribute, "Teste_IBSCBSDomain", "teste_IBSCBSDomainComCredPresOperEValor_retornaTrueEValor")
    ibs_cred = IBSCBSCreditoPresumidoDomain(v_cred_pres=d("25.00"))
    cred_pres = CreditoPresumidoOperacaoDomain(g_ibs_cred_pres=ibs_cred)
    domain = IBSCBSDomain(g_cred_pres_oper=cred_pres)
    assert domain.possui_cred_pres_ibs()
    assert domain.get_v_cred_pres_ibs() == d("25.00")


# --- Teste_TributosDomain ---


def test_teste_inicializacaoSemImpostoSeletivo_retornaFalse(record_xml_attribute) -> None:
    _java(record_xml_attribute, "Teste_TributosDomain", "teste_inicializacaoSemImpostoSeletivo_retornaFalse")
    tributos = TributosDomain()
    assert not tributos.possui_imposto_seletivo()
    assert tributos.get_valor_imposto_seletivo() == ZERO


def test_teste_inicializacaoComImpostoSeletivo_retornaTrue(record_xml_attribute) -> None:
    _java(record_xml_attribute, "Teste_TributosDomain", "teste_inicializacaoComImpostoSeletivo_retornaTrue")
    tributos = TributosDomain(IS=ImpostoSeletivoDomain(v_is=d("100")))
    assert tributos.possui_imposto_seletivo()
    assert tributos.get_valor_imposto_seletivo() == d("100")


def test_teste_inicializacaoSemIBSCBS_retornaDefaultsNullEZero(record_xml_attribute) -> None:
    _java(record_xml_attribute, "Teste_TributosDomain", "teste_inicializacaoSemIBSCBS_retornaDefaultsNullEZero")
    tributos = TributosDomain()
    assert not tributos.possui_base_calculo_ibscbs()
    assert tributos.get_valor_base_calculo_ibscbs() == ZERO
    assert not tributos.possui_cbs()
    assert tributos.get_g_cbs() is None
    assert not tributos.possui_cred_pres_cbs()
    assert tributos.get_cred_pres_cbs() is None
    assert not tributos.possui_cred_pres_ibs()
    assert tributos.get_v_cred_pres_ibs() == ZERO
    assert not tributos.possui_cred_pres_cond_sus_ibs()
    assert tributos.get_v_cred_pres_cond_sus_ibs() == ZERO
    assert tributos.get_grupo_ibscbs() is None
    assert not tributos.possui_ibs_uf()
    assert not tributos.possui_ibs_mun()
    assert tributos.get_g_ibs_uf() is None
    assert tributos.get_g_ibs_mun() is None
    assert not tributos.possui_monofasia()
    assert tributos.get_g_ibscbs_mono() is None
    assert not tributos.possui_tributacao_regular()
    assert tributos.get_tributacao_regular() is None
    assert not tributos.possui_estorno_credito()
    assert tributos.get_g_estorno_cred() is None


def test_teste_inicializacaoComIBSCBSComGrupo_retornaDelegates(record_xml_attribute) -> None:
    _java(record_xml_attribute, "Teste_TributosDomain", "teste_inicializacaoComIBSCBSComGrupo_retornaDelegates")
    grupo = GrupoIBSCBSDomain(
        g_cbs=CBSDomain(),
        g_ibs_uf=IBSUFDomain(),
        g_ibs_mun=IBSMunDomain(),
        g_trib_regular=TributacaoRegularDomain(),
    )
    ibscbs = IBSCBSDomain(g_ibscbs=grupo)
    tributos = TributosDomain(IBSCBS=ibscbs)
    assert tributos.possui_cbs()
    assert tributos.get_g_cbs() is not None
    assert tributos.possui_ibs_uf()
    assert tributos.get_g_ibs_uf() is not None
    assert tributos.possui_ibs_mun()
    assert tributos.get_g_ibs_mun() is not None
    assert tributos.possui_tributacao_regular()
    assert tributos.get_tributacao_regular() is not None
    assert tributos.get_grupo_ibscbs() is not None


def test_teste_inicializacaoComMonofasia_retornaTrue(record_xml_attribute) -> None:
    _java(record_xml_attribute, "Teste_TributosDomain", "teste_inicializacaoComMonofasia_retornaTrue")
    tributos = TributosDomain(IBSCBS=IBSCBSDomain(g_ibscbs_mono=MonofasiaDomain()))
    assert tributos.possui_monofasia()
    assert tributos.get_g_ibscbs_mono() is not None


def test_teste_inicializacaoComEstornoCredito_retornaTrue(record_xml_attribute) -> None:
    _java(record_xml_attribute, "Teste_TributosDomain", "teste_inicializacaoComEstornoCredito_retornaTrue")
    tributos = TributosDomain(IBSCBS=IBSCBSDomain(g_estorno_cred=EstornoCreditoDomain()))
    assert tributos.possui_estorno_credito()
    assert tributos.get_g_estorno_cred() is not None


# --- Teste_CreditoPresumidoOperacaoDomain ---


def test_teste_possuiCredPresCbsSemDados_retornaFalse(record_xml_attribute) -> None:
    _java(record_xml_attribute, "Teste_CreditoPresumidoOperacaoDomain", "teste_possuiCredPresCbsSemDados_retornaFalse")
    assert not CreditoPresumidoOperacaoDomain().possui_cred_pres_cbs()


def test_teste_possuiCredPresCbsComDados_retornaTrue(record_xml_attribute) -> None:
    _java(record_xml_attribute, "Teste_CreditoPresumidoOperacaoDomain", "teste_possuiCredPresCbsComDados_retornaTrue")
    domain = CreditoPresumidoOperacaoDomain(g_cbs_cred_pres=IBSCBSCreditoPresumidoDomain())
    assert domain.possui_cred_pres_cbs()


def test_teste_possuiCredPresIbsSemDados_retornaFalse(record_xml_attribute) -> None:
    _java(record_xml_attribute, "Teste_CreditoPresumidoOperacaoDomain", "teste_possuiCredPresIbsSemDados_retornaFalse")
    assert not CreditoPresumidoOperacaoDomain().possui_cred_pres_ibs()


def test_teste_possuiCredPresIbsComDadosVazios_retornaFalse(record_xml_attribute) -> None:
    _java(
        record_xml_attribute,
        "Teste_CreditoPresumidoOperacaoDomain",
        "teste_possuiCredPresIbsComDadosVazios_retornaFalse",
    )
    domain = CreditoPresumidoOperacaoDomain(g_ibs_cred_pres=IBSCBSCreditoPresumidoDomain())
    assert not domain.possui_cred_pres_ibs()


def test_teste_possuiCredPresIbsComValor_retornaTrue(record_xml_attribute) -> None:
    _java(record_xml_attribute, "Teste_CreditoPresumidoOperacaoDomain", "teste_possuiCredPresIbsComValor_retornaTrue")
    domain = CreditoPresumidoOperacaoDomain(
        g_ibs_cred_pres=IBSCBSCreditoPresumidoDomain(v_cred_pres=d("10.00"))
    )
    assert domain.possui_cred_pres_ibs()


def test_teste_getVCredPresIbsSemDados_retornaZero(record_xml_attribute) -> None:
    _java(record_xml_attribute, "Teste_CreditoPresumidoOperacaoDomain", "teste_getVCredPresIbsSemDados_retornaZero")
    assert CreditoPresumidoOperacaoDomain().get_v_cred_pres_ibs() == ZERO


def test_teste_getVCredPresIbsComDados_retornaValor(record_xml_attribute) -> None:
    _java(record_xml_attribute, "Teste_CreditoPresumidoOperacaoDomain", "teste_getVCredPresIbsComDados_retornaValor")
    domain = CreditoPresumidoOperacaoDomain(
        g_ibs_cred_pres=IBSCBSCreditoPresumidoDomain(v_cred_pres=d("42.50"))
    )
    assert domain.get_v_cred_pres_ibs() == d("42.50")


def test_teste_possuiCredPresCondSusIbsSemDados_retornaFalse(record_xml_attribute) -> None:
    _java(
        record_xml_attribute,
        "Teste_CreditoPresumidoOperacaoDomain",
        "teste_possuiCredPresCondSusIbsSemDados_retornaFalse",
    )
    assert not CreditoPresumidoOperacaoDomain().possui_cred_pres_cond_sus_ibs()


def test_teste_possuiCredPresCondSusIbsComValor_retornaTrue(record_xml_attribute) -> None:
    _java(
        record_xml_attribute,
        "Teste_CreditoPresumidoOperacaoDomain",
        "teste_possuiCredPresCondSusIbsComValor_retornaTrue",
    )
    domain = CreditoPresumidoOperacaoDomain(
        g_ibs_cred_pres=IBSCBSCreditoPresumidoDomain(v_cred_pres_cond_sus=d("5.00"))
    )
    assert domain.possui_cred_pres_cond_sus_ibs()


def test_teste_getVCredPresCondSusIbsSemDados_retornaZero(record_xml_attribute) -> None:
    _java(
        record_xml_attribute,
        "Teste_CreditoPresumidoOperacaoDomain",
        "teste_getVCredPresCondSusIbsSemDados_retornaZero",
    )
    assert CreditoPresumidoOperacaoDomain().get_v_cred_pres_cond_sus_ibs() == ZERO


def test_teste_getVCredPresCondSusIbsComDados_retornaValor(record_xml_attribute) -> None:
    _java(
        record_xml_attribute,
        "Teste_CreditoPresumidoOperacaoDomain",
        "teste_getVCredPresCondSusIbsComDados_retornaValor",
    )
    domain = CreditoPresumidoOperacaoDomain(
        g_ibs_cred_pres=IBSCBSCreditoPresumidoDomain(v_cred_pres_cond_sus=d("7.75"))
    )
    assert domain.get_v_cred_pres_cond_sus_ibs() == d("7.75")


# --- Teste_EstornoCreditoAccumulator ---


def test_teste_construtorPadrao_inicializaComZeros(record_xml_attribute) -> None:
    _java(record_xml_attribute, "Teste_EstornoCreditoAccumulator", "teste_construtorPadrao_inicializaComZeros")
    total = EstornoCreditoAccumulator().to_estorno_credito_domain_total()
    assert total.v_ibs_est_cred == ZERO
    assert total.v_cbs_est_cred == ZERO


def test_teste_construtorComValores_preservaValores(record_xml_attribute) -> None:
    _java(record_xml_attribute, "Teste_EstornoCreditoAccumulator", "teste_construtorComValores_preservaValores")
    total = EstornoCreditoAccumulator(TEN, ONE).to_estorno_credito_domain_total()
    assert total.v_ibs_est_cred == TEN
    assert total.v_cbs_est_cred == ONE


def test_teste_construtorComNulls_substituiPorZeros(record_xml_attribute) -> None:
    _java(record_xml_attribute, "Teste_EstornoCreditoAccumulator", "teste_construtorComNulls_substituiPorZeros")
    total = EstornoCreditoAccumulator(None, None).to_estorno_credito_domain_total()
    assert total.v_ibs_est_cred == ZERO
    assert total.v_cbs_est_cred == ZERO


def test_teste_fromNull_inicializaComZeros(record_xml_attribute) -> None:
    _java(record_xml_attribute, "Teste_EstornoCreditoAccumulator", "teste_fromNull_inicializaComZeros")
    total = EstornoCreditoAccumulator.from_fields(None).to_estorno_credito_domain_total()
    assert total.v_ibs_est_cred == ZERO
    assert total.v_cbs_est_cred == ZERO


def test_teste_fromDomain_extraiValores(record_xml_attribute) -> None:
    _java(record_xml_attribute, "Teste_EstornoCreditoAccumulator", "teste_fromDomain_extraiValores")
    domain = EstornoCreditoDomain(v_ibs_est_cred=d("5.50"), v_cbs_est_cred=d("3.25"))
    total = EstornoCreditoAccumulator.from_fields(domain).to_estorno_credito_domain_total()
    assert total.v_ibs_est_cred == d("5.50")
    assert total.v_cbs_est_cred == d("3.25")


def test_teste_fromDomainComCamposNulos_inicializaComZeros(record_xml_attribute) -> None:
    _java(
        record_xml_attribute,
        "Teste_EstornoCreditoAccumulator",
        "teste_fromDomainComCamposNulos_inicializaComZeros",
    )
    total = EstornoCreditoAccumulator.from_fields(EstornoCreditoDomain()).to_estorno_credito_domain_total()
    assert total.v_ibs_est_cred == ZERO
    assert total.v_cbs_est_cred == ZERO


def test_teste_addNull_adicionaZero(record_xml_attribute) -> None:
    _java(record_xml_attribute, "Teste_EstornoCreditoAccumulator", "teste_addNull_adicionaZero")
    total = EstornoCreditoAccumulator(TEN, ONE).add(None).to_estorno_credito_domain_total()
    assert total.v_ibs_est_cred == TEN
    assert total.v_cbs_est_cred == ONE


def test_teste_addValor_somaCorretamente(record_xml_attribute) -> None:
    _java(record_xml_attribute, "Teste_EstornoCreditoAccumulator", "teste_addValor_somaCorretamente")
    result = EstornoCreditoAccumulator(TEN, ONE).add(EstornoCreditoAccumulator(d("5"), d("2")))
    total = result.to_estorno_credito_domain_total()
    assert total.v_ibs_est_cred == d("15")
    assert total.v_cbs_est_cred == d("3")


# --- Teste_MonofasiaDomainExpanded ---


def test_teste_builderMonofasia_inicializaComZeros(record_xml_attribute) -> None:
    _java(record_xml_attribute, "Teste_MonofasiaDomainExpanded", "teste_builderMonofasia_inicializaComZeros")
    padrao = MonofasiaPadraoDomain()
    retencao = MonofasiaRetencaoDomain()
    retido = MonofasiaRetidoAnteriormenteDomain()
    diferimento = MonofasiaDiferimentoDomain()
    assert padrao.q_bc_mono == ZERO
    assert padrao.ad_rem_ibs == ZERO
    assert padrao.ad_rem_cbs == ZERO
    assert padrao.v_ibs_mono == ZERO
    assert padrao.v_cbs_mono == ZERO
    assert retencao.q_bc_mono_reten == ZERO
    assert retencao.ad_rem_ibs_reten == ZERO
    assert retencao.ad_rem_cbs_reten == ZERO
    assert retencao.v_ibs_mono_reten == ZERO
    assert retencao.v_cbs_mono_reten == ZERO
    assert retido.q_bc_mono_ret == ZERO
    assert retido.ad_rem_ibs_ret == ZERO
    assert retido.ad_rem_cbs_ret == ZERO
    assert retido.v_ibs_mono_ret == ZERO
    assert retido.v_cbs_mono_ret == ZERO
    assert diferimento.p_dif_ibs == ZERO
    assert diferimento.v_ibs_mono_dif == ZERO
    assert diferimento.p_dif_cbs == ZERO
    assert diferimento.v_cbs_mono_dif == ZERO


def test_teste_criacaoMonofasicaComNull_retornaNull(record_xml_attribute) -> None:
    _java(record_xml_attribute, "Teste_MonofasiaDomainExpanded", "teste_criacaoMonofasicaComNull_retornaNull")
    assert MonofasiaPadraoDomain.create(None, None, None) is None
    assert MonofasiaRetencaoDomain.create(None, None, None) is None
    assert MonofasiaRetidoAnteriormenteDomain.create(None, None, None) is None
    assert MonofasiaDiferimentoDomain.create(None, None, None) is None


def test_teste_monofasiaPadraoComCBSIBS_retornaCBSIBS(record_xml_attribute) -> None:
    _java(record_xml_attribute, "Teste_MonofasiaDomainExpanded", "teste_monofasiaPadraoComCBSIBS_retornaCBSIBS")
    resultado = MonofasiaPadraoDomain.create(
        _cbs_mono("10.0000", "1.10", "11.00"),
        _cbs_mono("20.0000", "2.20", "22.00"),
        _cbs_mono("99.0000", "9.99", "99.00"),
    )
    assert resultado is not None
    assert resultado.q_bc_mono == d("20.0000")
    assert resultado.ad_rem_ibs == d("2.20")
    assert resultado.v_ibs_mono == d("22.00")
    assert resultado.ad_rem_cbs == d("1.10")
    assert resultado.v_cbs_mono == d("11.00")


def test_teste_monofasiaPadraoCriadaComCBSNull_retornaCBSZero(record_xml_attribute) -> None:
    _java(record_xml_attribute, "Teste_MonofasiaDomainExpanded", "teste_monofasiaPadraoCriadaComCBSNull_retornaCBSZero")
    resultado = MonofasiaPadraoDomain.create(
        None,
        _cbs_mono("30.0000", "3.30", "33.00"),
        _cbs_mono("88.0000", "8.80", "88.00"),
    )
    assert resultado is not None
    assert resultado.q_bc_mono == d("30.0000")
    assert resultado.ad_rem_ibs == d("3.30")
    assert resultado.v_ibs_mono == d("33.00")
    assert resultado.ad_rem_cbs == ZERO
    assert resultado.v_cbs_mono == ZERO


def test_teste_monofasiaRetencaoComCBSIBS_retornaCBSIBS(record_xml_attribute) -> None:
    _java(record_xml_attribute, "Teste_MonofasiaDomainExpanded", "teste_monofasiaRetencaoComCBSIBS_retornaCBSIBS")
    resultado = MonofasiaRetencaoDomain.create(
        _cbs_retencao("40.0000", "4.40", "44.00"),
        _cbs_retencao("50.0000", "5.50", "55.00"),
        _cbs_retencao("77.0000", "7.70", "77.00"),
    )
    assert resultado is not None
    assert resultado.q_bc_mono_reten == d("50.0000")
    assert resultado.ad_rem_ibs_reten == d("5.50")
    assert resultado.v_ibs_mono_reten == d("55.00")
    assert resultado.ad_rem_cbs_reten == d("4.40")
    assert resultado.v_cbs_mono_reten == d("44.00")


def test_teste_monofasiaRetencaoCriadaComCBSNull_retornaCBSZero(record_xml_attribute) -> None:
    _java(record_xml_attribute, "Teste_MonofasiaDomainExpanded", "teste_monofasiaRetencaoCriadaComCBSNull_retornaCBSZero")
    resultado = MonofasiaRetencaoDomain.create(
        None,
        _cbs_retencao("60.0000", "6.60", "66.00"),
        _cbs_retencao("76.0000", "7.60", "76.00"),
    )
    assert resultado is not None
    assert resultado.q_bc_mono_reten == d("60.0000")
    assert resultado.ad_rem_ibs_reten == d("6.60")
    assert resultado.v_ibs_mono_reten == d("66.00")
    assert resultado.ad_rem_cbs_reten == ZERO
    assert resultado.v_cbs_mono_reten == ZERO


def test_teste_monofasiaRetidaComCBSIBS_retornaCBSIBS(record_xml_attribute) -> None:
    _java(record_xml_attribute, "Teste_MonofasiaDomainExpanded", "teste_monofasiaRetidaComCBSIBS_retornaCBSIBS")
    resultado = MonofasiaRetidoAnteriormenteDomain.create(
        _cbs_retido("70.0000", "7.70", "77.00"),
        _cbs_retido("80.0000", "8.80", "88.00"),
        _cbs_retido("66.0000", "6.60", "66.00"),
    )
    assert resultado is not None
    assert resultado.q_bc_mono_ret == d("80.0000")
    assert resultado.ad_rem_ibs_ret == d("8.80")
    assert resultado.v_ibs_mono_ret == d("88.00")
    assert resultado.ad_rem_cbs_ret == d("7.70")
    assert resultado.v_cbs_mono_ret == d("77.00")


def test_teste_monofasiaRetidaCriadaComCBSNull_retornaCBSZero(record_xml_attribute) -> None:
    _java(record_xml_attribute, "Teste_MonofasiaDomainExpanded", "teste_monofasiaRetidaCriadaComCBSNull_retornaCBSZero")
    resultado = MonofasiaRetidoAnteriormenteDomain.create(
        None,
        _cbs_retido("90.0000", "9.90", "99.00"),
        _cbs_retido("55.0000", "5.50", "55.00"),
    )
    assert resultado is not None
    assert resultado.q_bc_mono_ret == d("90.0000")
    assert resultado.ad_rem_ibs_ret == d("9.90")
    assert resultado.v_ibs_mono_ret == d("99.00")
    assert resultado.ad_rem_cbs_ret == ZERO
    assert resultado.v_cbs_mono_ret == ZERO


def test_teste_monofasiaDiferimentoComCBSIBS_retornaCBSIBS(record_xml_attribute) -> None:
    _java(record_xml_attribute, "Teste_MonofasiaDomainExpanded", "teste_monofasiaDiferimentoComCBSIBS_retornaCBSIBS")
    resultado = MonofasiaDiferimentoDomain.create(
        _cbs_diferido("10.00", "11.00"),
        _cbs_diferido("20.00", "22.00"),
        _cbs_diferido("99.00", "99.00"),
    )
    assert resultado is not None
    assert resultado.p_dif_ibs == d("20.00")
    assert resultado.v_ibs_mono_dif == d("22.00")
    assert resultado.p_dif_cbs == d("10.00")
    assert resultado.v_cbs_mono_dif == d("11.00")


def test_teste_monofasiaDiferimentoCriadaComCBSNull_retornaCBSZero(record_xml_attribute) -> None:
    _java(
        record_xml_attribute,
        "Teste_MonofasiaDomainExpanded",
        "teste_monofasiaDiferimentoCriadaComCBSNull_retornaCBSZero",
    )
    resultado = MonofasiaDiferimentoDomain.create(
        None,
        _cbs_diferido("30.00", "33.00"),
        _cbs_diferido("88.00", "88.00"),
    )
    assert resultado is not None
    assert resultado.p_dif_ibs == d("30.00")
    assert resultado.v_ibs_mono_dif == d("33.00")
    assert resultado.p_dif_cbs == ZERO
    assert resultado.v_cbs_mono_dif == ZERO


def test_teste_mergeGrupoEtapaMonofasiaExistenteComNull_retornaGrupoExistente(record_xml_attribute) -> None:
    _java(
        record_xml_attribute,
        "Teste_MonofasiaDomainExpanded",
        "teste_mergeGrupoEtapaMonofasiaExistenteComNull_retornaGrupoExistente",
    )
    grupo = GrupoEtapaMonofasiaOutput(quantidade=d("1.0000"), aliquota_ad_rem=d("1.10"), valor=d("11.00"))
    assert GrupoEtapaMonofasiaOutput.merge(None, grupo) is grupo
    assert GrupoEtapaMonofasiaOutput.merge(grupo, None) is grupo


def test_teste_mergeGrupoEtapaMonofasia_retornaSomandoValoresECompletandoNulls(record_xml_attribute) -> None:
    _java(
        record_xml_attribute,
        "Teste_MonofasiaDomainExpanded",
        "teste_mergeGrupoEtapaMonofasia_retornaSomandoValoresECompletandoNulls",
    )
    g1 = GrupoEtapaMonofasiaOutput(valor=d("1.25"))
    g2 = GrupoEtapaMonofasiaOutput(quantidade=d("2.0000"), aliquota_ad_rem=d("2.20"), valor=d("2.75"))
    resultado = GrupoEtapaMonofasiaOutput.merge(g1, g2)
    assert resultado is not None
    assert resultado.quantidade == d("2.0000")
    assert resultado.aliquota_ad_rem == d("2.20")
    assert resultado.valor == d("4.00")


def test_teste_mergeGrupoDiferimentoMonofasiaExistenteComNull_retornaGrupoExistente(record_xml_attribute) -> None:
    _java(
        record_xml_attribute,
        "Teste_MonofasiaDomainExpanded",
        "teste_mergeGrupoDiferimentoMonofasiaExistenteComNull_retornaGrupoExistente",
    )
    grupo = GrupoDiferimentoMonofasiaOutput(percentual_diferimento=d("5.00"), valor_diferimento=d("10.00"))
    assert GrupoDiferimentoMonofasiaOutput.merge(None, grupo) is grupo
    assert GrupoDiferimentoMonofasiaOutput.merge(grupo, None) is grupo


def test_teste_mergeGrupoDiferimentoMonofasia_retornaSomandoValoresECompletandoPercentual(record_xml_attribute) -> None:
    _java(
        record_xml_attribute,
        "Teste_MonofasiaDomainExpanded",
        "teste_mergeGrupoDiferimentoMonofasia_retornaSomandoValoresECompletandoPercentual",
    )
    g1 = GrupoDiferimentoMonofasiaOutput(valor_diferimento=d("1.25"))
    g2 = GrupoDiferimentoMonofasiaOutput(percentual_diferimento=d("7.50"), valor_diferimento=d("2.75"))
    resultado = GrupoDiferimentoMonofasiaOutput.merge(g1, g2)
    assert resultado is not None
    assert resultado.percentual_diferimento == d("7.50")
    assert resultado.valor_diferimento == d("4.00")