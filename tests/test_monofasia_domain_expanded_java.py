"""Paridade com ``Teste_MonofasiaDomainExpanded`` (domínio ROC)."""

from __future__ import annotations

from decimal import Decimal

from calculadora_rtc_regime_regular.roc import (
    CbsIbsOutput,
    GrupoDiferimentoMonofasiaOutput,
    GrupoEtapaMonofasiaOutput,
    GrupoMonofasiaOutput,
    MonofasiaDiferimentoDomain,
    MonofasiaPadraoDomain,
    MonofasiaRetencaoDomain,
    MonofasiaRetidoAnteriormenteDomain,
    ZERO,
)

def d(value: str | Decimal) -> Decimal:
    return value if isinstance(value, Decimal) else Decimal(value)

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

def test_teste_builderMonofasia_inicializaComZeros() -> None:
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

def test_teste_criacaoMonofasicaComNull_retornaNull() -> None:
    assert MonofasiaPadraoDomain.create(None, None, None) is None
    assert MonofasiaRetencaoDomain.create(None, None, None) is None
    assert MonofasiaRetidoAnteriormenteDomain.create(None, None, None) is None
    assert MonofasiaDiferimentoDomain.create(None, None, None) is None

def test_teste_monofasiaPadraoComCBSIBS_retornaCBSIBS() -> None:
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

def test_teste_monofasiaPadraoCriadaComCBSNull_retornaCBSZero() -> None:
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

def test_teste_monofasiaRetencaoComCBSIBS_retornaCBSIBS() -> None:
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

def test_teste_monofasiaRetencaoCriadaComCBSNull_retornaCBSZero() -> None:
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

def test_teste_monofasiaRetidaComCBSIBS_retornaCBSIBS() -> None:
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

def test_teste_monofasiaRetidaCriadaComCBSNull_retornaCBSZero() -> None:
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

def test_teste_monofasiaDiferimentoComCBSIBS_retornaCBSIBS() -> None:
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

def test_teste_monofasiaDiferimentoCriadaComCBSNull_retornaCBSZero() -> None:
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

def test_teste_mergeGrupoEtapaMonofasiaExistenteComNull_retornaGrupoExistente() -> None:
    grupo = GrupoEtapaMonofasiaOutput(quantidade=d("1.0000"), aliquota_ad_rem=d("1.10"), valor=d("11.00"))
    assert GrupoEtapaMonofasiaOutput.merge(None, grupo) is grupo
    assert GrupoEtapaMonofasiaOutput.merge(grupo, None) is grupo

def test_teste_mergeGrupoEtapaMonofasia_retornaSomandoValoresECompletandoNulls() -> None:
    g1 = GrupoEtapaMonofasiaOutput(valor=d("1.25"))
    g2 = GrupoEtapaMonofasiaOutput(quantidade=d("2.0000"), aliquota_ad_rem=d("2.20"), valor=d("2.75"))
    resultado = GrupoEtapaMonofasiaOutput.merge(g1, g2)
    assert resultado is not None
    assert resultado.quantidade == d("2.0000")
    assert resultado.aliquota_ad_rem == d("2.20")
    assert resultado.valor == d("4.00")

def test_teste_mergeGrupoDiferimentoMonofasiaExistenteComNull_retornaGrupoExistente() -> None:
    grupo = GrupoDiferimentoMonofasiaOutput(percentual_diferimento=d("5.00"), valor_diferimento=d("10.00"))
    assert GrupoDiferimentoMonofasiaOutput.merge(None, grupo) is grupo
    assert GrupoDiferimentoMonofasiaOutput.merge(grupo, None) is grupo

def test_teste_mergeGrupoDiferimentoMonofasia_retornaSomandoValoresECompletandoPercentual() -> None:
    g1 = GrupoDiferimentoMonofasiaOutput(valor_diferimento=d("1.25"))
    g2 = GrupoDiferimentoMonofasiaOutput(percentual_diferimento=d("7.50"), valor_diferimento=d("2.75"))
    resultado = GrupoDiferimentoMonofasiaOutput.merge(g1, g2)
    assert resultado is not None
    assert resultado.percentual_diferimento == d("7.50")
    assert resultado.valor_diferimento == d("4.00")
