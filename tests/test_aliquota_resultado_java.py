"""Paridade com Teste_AliquotaResultadoDTO (identidade JUnit via teste_*)."""

from datetime import date
from decimal import Decimal

import pytest

from calculadora_rtc_regime_regular.aliquota_resultado import (
    AliquotaNegativa,
    AliquotaPadraoNaoEncontrada,
    AliquotaReferenciaNaoEncontrada,
    AliquotaResultado,
    FormaAplicacao,
    FormaAplicacaoNaoDefinida,
)
from calculadora_rtc_regime_regular.cbs_ibs import buscar_aliquota_padrao


def teste_CriacaoComApenasValorReferencia_DeveFuncionar() -> None:
    resultado = AliquotaResultado(Decimal("10.50"))
    assert resultado.valor_referencia == Decimal("10.50")
    assert resultado.valor_padrao is None
    assert resultado.forma_aplicacao is None


def teste_ValorAplicavel_SemValorPadrao_DeveRetornarValorReferencia() -> None:
    resultado = AliquotaResultado(Decimal("15.75"))
    assert resultado.valor_aplicavel() == Decimal("15.75")


def teste_CriacaoComAcrescimo_DeveAplicarCorretamente() -> None:
    resultado = AliquotaResultado(Decimal("100.00"), Decimal("5.00"), FormaAplicacao.ACRESCIMO)
    assert resultado.valor_padrao == Decimal("105.00")
    assert resultado.valor_referencia == Decimal("100.00")


def teste_ValorAplicavel_ComAcrescimo_DeveRetornarValorPadraoCalculado() -> None:
    dto = AliquotaResultado(Decimal("50.00"), Decimal("10.00"), FormaAplicacao.ACRESCIMO)
    assert dto.valor_aplicavel() == Decimal("60.00")


def teste_CriacaoComDecrescimo_DeveAplicarCorretamente() -> None:
    resultado = AliquotaResultado(Decimal("100.00"), Decimal("15.00"), FormaAplicacao.DECRESCIMO)
    assert resultado.valor_padrao == Decimal("85.00")
    assert resultado.valor_referencia == Decimal("100.00")


def teste_ValorAplicavel_ComDecrescimo_DeveRetornarValorPadraoCalculado() -> None:
    dto = AliquotaResultado(Decimal("80.00"), Decimal("20.00"), FormaAplicacao.DECRESCIMO)
    assert dto.valor_aplicavel() == Decimal("60.00")


def teste_CriacaoComValorReferenciaNull_DeveLancarExcecao() -> None:
    with pytest.raises(AliquotaReferenciaNaoEncontrada):
        AliquotaResultado(None, Decimal("10.00"), FormaAplicacao.ACRESCIMO)  # type: ignore[arg-type]


def teste_CriacaoComValorPadraoSemFormaAplicacao_DeveLancarExcecao() -> None:
    with pytest.raises(FormaAplicacaoNaoDefinida):
        AliquotaResultado(Decimal("100.00"), Decimal("10.00"), None)


def teste_CriacaoComFormaAplicacaoSemValorPadrao_DeveLancarExcecao() -> None:
    with pytest.raises(AliquotaPadraoNaoEncontrada):
        AliquotaResultado(Decimal("100.00"), None, FormaAplicacao.ACRESCIMO)


def teste_AcrescimoComValoresDecimais_DeveCalcularPrecisamente() -> None:
    dto = AliquotaResultado(Decimal("12.345"), Decimal("2.655"), FormaAplicacao.ACRESCIMO)
    assert dto.valor_padrao == Decimal("15.000")


def teste_DecrescimoComValoresDecimais_DeveCalcularPrecisamente() -> None:
    dto = AliquotaResultado(Decimal("25.750"), Decimal("5.250"), FormaAplicacao.DECRESCIMO)
    assert dto.valor_padrao == Decimal("20.500")


def teste_AcrescimoComValorZero_DeveManterValorReferencia() -> None:
    dto = AliquotaResultado(Decimal("50.00"), Decimal(0), FormaAplicacao.ACRESCIMO)
    assert dto.valor_padrao == Decimal("50.00")
    assert dto.valor_aplicavel() == Decimal("50.00")


def teste_DecrescimoComValorZero_DeveManterValorReferencia() -> None:
    dto = AliquotaResultado(Decimal("50.00"), Decimal(0), FormaAplicacao.DECRESCIMO)
    assert dto.valor_padrao == Decimal("50.00")
    assert dto.valor_aplicavel() == Decimal("50.00")


def teste_ValorReferenciaNegativo_DeveLancarExcecao() -> None:
    with pytest.raises(AliquotaNegativa):
        AliquotaResultado(Decimal("-10.00"))


def teste_ValorPadraoNegativo_DeveLancarExcecao() -> None:
    with pytest.raises(AliquotaNegativa):
        AliquotaResultado(Decimal("100.00"), Decimal("-10.00"), FormaAplicacao.ACRESCIMO)


def teste_DecrescimoResultadoNegativo_DeveLancarExcecao() -> None:
    with pytest.raises(AliquotaNegativa):
        AliquotaResultado(Decimal("10.00"), Decimal("15.00"), FormaAplicacao.DECRESCIMO)


def teste_ValoresComMuitasCasasDecimais_DevePreservarPrecisao() -> None:
    dto = AliquotaResultado(Decimal("123.456789"), Decimal("0.000001"), FormaAplicacao.ACRESCIMO)
    assert dto.valor_padrao == Decimal("123.456790")


def teste_RecordEquality_MesmosValores_DeveSerIgual() -> None:
    dto1 = AliquotaResultado(Decimal("100.00"), Decimal("10.00"), FormaAplicacao.ACRESCIMO)
    dto2 = AliquotaResultado(Decimal("100.00"), Decimal("10.00"), FormaAplicacao.ACRESCIMO)
    assert dto1 == dto2
    assert hash(dto1) == hash(dto2)


def teste_RecordToString_DeveConterInformacoes() -> None:
    dto = AliquotaResultado(Decimal("50.00"))
    texto = str(dto)
    assert "50.00" in texto


def teste_CriacaoComSubstituicao_DeveManterValorPadrao() -> None:
    dto = AliquotaResultado(Decimal("100.00"), Decimal("25.00"), FormaAplicacao.SUBSTITUICAO)
    assert dto.valor_padrao == Decimal("25.00")
    assert dto.valor_referencia == Decimal("100.00")


def teste_ValorAplicavel_ComSubstituicao_DeveRetornarValorPadrao() -> None:
    dto = AliquotaResultado(Decimal("50.00"), Decimal("30.00"), FormaAplicacao.SUBSTITUICAO)
    assert dto.valor_aplicavel() == Decimal("30.00")


def teste_SubstituicaoComValorMaiorQueReferencia_DevePermitir() -> None:
    dto = AliquotaResultado(Decimal("10.00"), Decimal("50.00"), FormaAplicacao.SUBSTITUICAO)
    assert dto.valor_aplicavel() == Decimal("50.00")


def teste_SubstituicaoComValorMenorQueReferencia_DevePermitir() -> None:
    dto = AliquotaResultado(Decimal("80.00"), Decimal("15.00"), FormaAplicacao.SUBSTITUICAO)
    assert dto.valor_aplicavel() == Decimal("15.00")


def teste_SubstituicaoComValoresDecimais_DevePreservarPrecisao() -> None:
    dto = AliquotaResultado(Decimal("45.678"), Decimal("12.345"), FormaAplicacao.SUBSTITUICAO)
    assert dto.valor_aplicavel() == Decimal("12.345")


def teste_SubstituicaoComValorZero_DevePermitir() -> None:
    dto = AliquotaResultado(Decimal("50.00"), Decimal(0), FormaAplicacao.SUBSTITUICAO)
    assert dto.valor_aplicavel() == Decimal(0)


def teste_AcrescimoComValoresGrandes_DeveCalcularCorretamente() -> None:
    dto = AliquotaResultado(Decimal("9999999.99"), Decimal("0.01"), FormaAplicacao.ACRESCIMO)
    assert dto.valor_aplicavel() == Decimal("10000000.00")


def teste_DecrescimoComValoresIguais_DeveResultarZero() -> None:
    dto = AliquotaResultado(Decimal("100.00"), Decimal("100.00"), FormaAplicacao.DECRESCIMO)
    assert dto.valor_aplicavel() == Decimal("0.00")


def teste_AcrescimoComValorReferenciaZero_DeveResultarValorPadrao() -> None:
    dto = AliquotaResultado(Decimal(0), Decimal("25.00"), FormaAplicacao.ACRESCIMO)
    assert dto.valor_aplicavel() == Decimal("25.00")


def teste_DecrescimoComValorReferenciaZero_DeveResultarNegativo() -> None:
    with pytest.raises(AliquotaNegativa):
        AliquotaResultado(Decimal(0), Decimal("10.00"), FormaAplicacao.DECRESCIMO)


def teste_SubstituicaoComValorIgualReferencia_DevePermitir() -> None:
    dto = AliquotaResultado(Decimal("75.50"), Decimal("75.50"), FormaAplicacao.SUBSTITUICAO)
    assert dto.valor_aplicavel() == Decimal("75.50")


def teste_AcrescimoComMuitasCasasDecimais_DevePreservarTodasCasas() -> None:
    dto = AliquotaResultado(Decimal("1.123456789"), Decimal("2.876543211"), FormaAplicacao.ACRESCIMO)
    assert dto.valor_padrao == Decimal("4.000000000")


def teste_DecrescimoComResultadoMuitoPequeno_DevePreservarPrecisao() -> None:
    dto = AliquotaResultado(Decimal("10.000001"), Decimal("10.000000"), FormaAplicacao.DECRESCIMO)
    assert dto.valor_aplicavel() == Decimal("0.000001")


def teste_ValorReferenciaZeroSemValorPadrao_DevePermitir() -> None:
    dto = AliquotaResultado(Decimal(0))
    assert dto.valor_aplicavel() == Decimal(0)


def teste_AcrescimoComValoresFracionarios_DeveCalcularCorretamente() -> None:
    assert AliquotaResultado(Decimal("0.5"), Decimal("0.3"), FormaAplicacao.ACRESCIMO).valor_aplicavel() == Decimal("0.8")


def teste_DecrescimoComValoresFracionarios_DeveCalcularCorretamente() -> None:
    assert AliquotaResultado(Decimal("0.9"), Decimal("0.4"), FormaAplicacao.DECRESCIMO).valor_aplicavel() == Decimal("0.5")


def teste_SubstituicaoComValorFracionario_DevePreservar() -> None:
    assert AliquotaResultado(Decimal("10.0"), Decimal("0.25"), FormaAplicacao.SUBSTITUICAO).valor_aplicavel() == Decimal("0.25")


def teste_ValorReferenciaUmCentavo_ComAcrescimo_DeveCalcular() -> None:
    assert AliquotaResultado(Decimal("0.01"), Decimal("0.01"), FormaAplicacao.ACRESCIMO).valor_padrao == Decimal("0.02")


def teste_MultiplasCriacoesComMesmosValores_DevemSerIndependentes() -> None:
    referencia = Decimal("100.00")
    padrao = Decimal("10.00")
    assert AliquotaResultado(referencia, padrao, FormaAplicacao.ACRESCIMO).valor_padrao == Decimal("110.00")
    assert AliquotaResultado(referencia, padrao, FormaAplicacao.DECRESCIMO).valor_padrao == Decimal("90.00")
    assert AliquotaResultado(referencia, padrao, FormaAplicacao.SUBSTITUICAO).valor_padrao == Decimal("10.00")
