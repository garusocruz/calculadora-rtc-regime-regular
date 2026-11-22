"""Paridade com Teste_NfseService_CalcularBaseCalculo (pin f1eebd7)."""

from __future__ import annotations

from decimal import Decimal

import pytest

from calculadora_rtc_regime_regular.base_calculo_service import CampoInvalido
from calculadora_rtc_regime_regular.nfse_base import EntradaNfse, calcular_base_nfse

_FQCN = "br.gov.serpro.rtc.testesunitarios.service.Teste_NfseService_CalcularBaseCalculo"


def _java(record_xml_attribute, method: str) -> None:
    record_xml_attribute("classname", _FQCN)
    record_xml_attribute("name", method)


def _nfse(**kwargs: object) -> Decimal:
    return calcular_base_nfse(EntradaNfse(**kwargs))  # type: ignore[arg-type]


def teste_calculoCorretoEm2026_PisCofinsnaoIntegram(record_xml_attribute) -> None:
    _java(record_xml_attribute, "teste_calculoCorretoEm2026_PisCofinsnaoIntegram")
    base = _nfse(
        ano=2026,
        valor_servico=Decimal("1000.00"),
        desconto_incondicional=Decimal("50.00"),
        reembolso=Decimal("20.00"),
        deducao=Decimal("10.00"),
        iss=Decimal("80.00"),
        pis=Decimal("16.50"),
        cofins=Decimal("76.00"),
    )
    assert base == Decimal("747.50")


def teste_calculoCorretoEm2027_SemPisCofinsSemIss(record_xml_attribute) -> None:
    _java(record_xml_attribute, "teste_calculoCorretoEm2027_SemPisCofinsSemIss")
    base = _nfse(
        ano=2027,
        valor_servico=Decimal("1000.00"),
        desconto_incondicional=Decimal("50.00"),
        reembolso=Decimal("20.00"),
        deducao=Decimal("10.00"),
        iss=Decimal("80.00"),
    )
    assert base == Decimal("840.00")


def teste_dataAPartirDe2033SemIss(record_xml_attribute) -> None:
    _java(record_xml_attribute, "teste_dataAPartirDe2033SemIss")
    assert _nfse(
        ano=2033,
        valor_servico=Decimal("1000.00"),
        desconto_incondicional=Decimal("50.00"),
        reembolso=Decimal("20.00"),
        deducao=Decimal("10.00"),
    ) == Decimal("920.00")


def teste_baseNegativaLancaExcecao(record_xml_attribute) -> None:
    _java(record_xml_attribute, "teste_baseNegativaLancaExcecao")
    with pytest.raises(CampoInvalido, match="Base de cálculo não pode ser negativa"):
        _nfse(ano=2026, valor_servico=Decimal("100.00"), desconto_incondicional=Decimal("200.00"))


def teste_todosCamposZeroRetornaZero(record_xml_attribute) -> None:
    _java(record_xml_attribute, "teste_todosCamposZeroRetornaZero")
    assert _nfse(ano=2026, valor_servico=Decimal(0)) == Decimal(0)


def teste_cadaCampoNaoIntegraCorretamente(record_xml_attribute) -> None:
    _java(record_xml_attribute, "teste_cadaCampoNaoIntegraCorretamente")
    assert _nfse(ano=2026, valor_servico=Decimal("1000.00"), desconto_incondicional=Decimal("100.00")) == Decimal(
        "900.00"
    )
    assert _nfse(ano=2026, valor_servico=Decimal("1000.00"), reembolso=Decimal("50.00")) == Decimal("950.00")
    assert _nfse(ano=2026, valor_servico=Decimal("1000.00"), deducao=Decimal("75.00")) == Decimal("925.00")
    assert _nfse(ano=2026, valor_servico=Decimal("1000.00"), iss=Decimal("80.00")) == Decimal("920.00")


def teste_transicao2026Para2027_PisCofinsLancaExcecaoEm2027(record_xml_attribute) -> None:
    _java(record_xml_attribute, "teste_transicao2026Para2027_PisCofinsLancaExcecaoEm2027")
    assert _nfse(
        ano=2026,
        valor_servico=Decimal("1000.00"),
        pis=Decimal("16.50"),
        cofins=Decimal("76.00"),
    ) == Decimal("907.50")
    with pytest.raises(CampoInvalido):
        _nfse(
            ano=2027,
            valor_servico=Decimal("1000.00"),
            pis=Decimal("16.50"),
            cofins=Decimal("76.00"),
        )


def teste_ano2027_PisLancaExcecao(record_xml_attribute) -> None:
    _java(record_xml_attribute, "teste_ano2027_PisLancaExcecao")
    with pytest.raises(CampoInvalido):
        _nfse(ano=2027, valor_servico=Decimal("500.00"), pis=Decimal("10.00"))


def teste_ano2027_CofinsLancaExcecao(record_xml_attribute) -> None:
    _java(record_xml_attribute, "teste_ano2027_CofinsLancaExcecao")
    with pytest.raises(CampoInvalido):
        _nfse(ano=2027, valor_servico=Decimal("500.00"), cofins=Decimal("20.00"))


def teste_ano2030_PisCofinsLancaExcecao(record_xml_attribute) -> None:
    _java(record_xml_attribute, "teste_ano2030_PisCofinsLancaExcecao")
    with pytest.raises(CampoInvalido):
        _nfse(
            ano=2030,
            valor_servico=Decimal("500.00"),
            pis=Decimal("10.00"),
            cofins=Decimal("20.00"),
        )


def teste_ano2033_IssLancaExcecao(record_xml_attribute) -> None:
    _java(record_xml_attribute, "teste_ano2033_IssLancaExcecao")
    with pytest.raises(CampoInvalido):
        _nfse(ano=2033, valor_servico=Decimal("1000.00"), iss=Decimal("80.00"))


def teste_anoAnterior2026_LancaExcecao(record_xml_attribute) -> None:
    _java(record_xml_attribute, "teste_anoAnterior2026_LancaExcecao")
    with pytest.raises(CampoInvalido, match="O ano do fato gerador deve ser 2026 ou superior"):
        _nfse(ano=2025, valor_servico=Decimal("1000.00"))


def teste_ano2020_LancaExcecao(record_xml_attribute) -> None:
    _java(record_xml_attribute, "teste_ano2020_LancaExcecao")
    with pytest.raises(CampoInvalido, match="O ano do fato gerador deve ser 2026 ou superior"):
        _nfse(ano=2020, valor_servico=Decimal("1000.00"))


def teste_ano2026_PrimeiroAnoValido(record_xml_attribute) -> None:
    _java(record_xml_attribute, "teste_ano2026_PrimeiroAnoValido")
    assert _nfse(
        ano=2026,
        valor_servico=Decimal("1000.00"),
        desconto_incondicional=Decimal("50.00"),
    ) == Decimal("950.00")


def teste_issComValorZeroNaoLancaExcecaoEm2033(record_xml_attribute) -> None:
    _java(record_xml_attribute, "teste_issComValorZeroNaoLancaExcecaoEm2033")
    assert _nfse(ano=2033, valor_servico=Decimal("1000.00"), iss=Decimal(0)) == Decimal("1000.00")


def teste_pisComValorZeroNaoLancaExcecaoEm2027(record_xml_attribute) -> None:
    _java(record_xml_attribute, "teste_pisComValorZeroNaoLancaExcecaoEm2027")
    assert _nfse(
        ano=2027,
        valor_servico=Decimal("1000.00"),
        pis=Decimal(0),
        cofins=Decimal(0),
    ) == Decimal("1000.00")


def teste_ano2032_IssDeveSerDeduzido(record_xml_attribute) -> None:
    _java(record_xml_attribute, "teste_ano2032_IssDeveSerDeduzido")
    assert _nfse(ano=2032, valor_servico=Decimal("1000.00"), iss=Decimal("50.00")) == Decimal("950.00")


def teste_mensagemErroMultiplosCampos(record_xml_attribute) -> None:
    _java(record_xml_attribute, "teste_mensagemErroMultiplosCampos")
    with pytest.raises(CampoInvalido) as erro:
        _nfse(
            ano=2027,
            valor_servico=Decimal("1000.00"),
            pis=Decimal("10.00"),
            cofins=Decimal("20.00"),
        )
    mensagem = str(erro.value)
    assert "Os seguintes campos não podem ser informados a partir de 2027:" in mensagem
    assert "PIS" in mensagem
    assert "COFINS" in mensagem


def teste_todosOsCamposQueNaoIntegram(record_xml_attribute) -> None:
    _java(record_xml_attribute, "teste_todosOsCamposQueNaoIntegram")
    assert _nfse(
        ano=2026,
        valor_servico=Decimal("2000.00"),
        desconto_incondicional=Decimal("100.00"),
        reembolso=Decimal("50.00"),
        deducao=Decimal("30.00"),
        iss=Decimal("80.00"),
        pis=Decimal("16.50"),
        cofins=Decimal("76.00"),
    ) == Decimal("1647.50")


def teste_validacaoOcorreAntesDoCalculo(record_xml_attribute) -> None:
    _java(record_xml_attribute, "teste_validacaoOcorreAntesDoCalculo")
    with pytest.raises(CampoInvalido) as erro:
        _nfse(
            ano=2025,
            valor_servico=Decimal("1000.00"),
            desconto_incondicional=Decimal("50.00"),
        )
    assert "ano do fato gerador" in str(erro.value)


def teste_ano2034_IssNaoDeveSerDeduzido(record_xml_attribute) -> None:
    _java(record_xml_attribute, "teste_ano2034_IssNaoDeveSerDeduzido")
    with pytest.raises(CampoInvalido):
        _nfse(
            ano=2034,
            valor_servico=Decimal("1000.00"),
            desconto_incondicional=Decimal("50.00"),
            iss=Decimal("80.00"),
        )


def teste_camposSempreSomados_ValidacaoAntecipada(record_xml_attribute) -> None:
    _java(record_xml_attribute, "teste_camposSempreSomados_ValidacaoAntecipada")
    assert _nfse(
        ano=2026,
        valor_servico=Decimal("1000.00"),
        pis=Decimal("10.00"),
        cofins=Decimal("20.00"),
        iss=Decimal("50.00"),
    ) == Decimal("920.00")


def teste_validacaoMetodoCentralizado(record_xml_attribute) -> None:
    _java(record_xml_attribute, "teste_validacaoMetodoCentralizado")
    with pytest.raises(CampoInvalido) as erro:
        _nfse(
            ano=2027,
            valor_servico=Decimal("1000.00"),
            pis=Decimal("10.00"),
            cofins=Decimal("20.00"),
        )
    mensagem = str(erro.value)
    assert "2027" in mensagem
    assert "PIS" in mensagem
    assert "COFINS" in mensagem


def teste_mensagemOrdenadaAlfabeticamente(record_xml_attribute) -> None:
    _java(record_xml_attribute, "teste_mensagemOrdenadaAlfabeticamente")
    with pytest.raises(CampoInvalido) as erro:
        _nfse(
            ano=2027,
            valor_servico=Decimal("1000.00"),
            pis=Decimal("10.00"),
            cofins=Decimal("20.00"),
        )
    mensagem = str(erro.value)
    assert mensagem.index("COFINS") < mensagem.index("PIS")


def teste_duasValidacoesSeparadas(record_xml_attribute) -> None:
    _java(record_xml_attribute, "teste_duasValidacoesSeparadas")
    with pytest.raises(CampoInvalido) as erro:
        _nfse(ano=2033, valor_servico=Decimal("1000.00"), pis=Decimal("10.00"))
    mensagem = str(erro.value)
    assert "PIS" in mensagem
    assert "2027" in mensagem
    assert "ISS" not in mensagem
    assert "2033" not in mensagem


def teste_constantes_AnoExtincao(record_xml_attribute) -> None:
    _java(record_xml_attribute, "teste_constantes_AnoExtincao")
    with pytest.raises(CampoInvalido):
        _nfse(ano=2027, valor_servico=Decimal("1000.00"), pis=Decimal("10.00"))
    with pytest.raises(CampoInvalido):
        _nfse(ano=2033, valor_servico=Decimal("1000.00"), iss=Decimal("50.00"))


def teste_todosOsCamposSempreDeduzidos2026(record_xml_attribute) -> None:
    _java(record_xml_attribute, "teste_todosOsCamposSempreDeduzidos2026")
    assert _nfse(
        ano=2026,
        valor_servico=Decimal("2000.00"),
        desconto_incondicional=Decimal("100.00"),
        reembolso=Decimal("50.00"),
        deducao=Decimal("30.00"),
        pis=Decimal("20.00"),
        cofins=Decimal("80.00"),
        iss=Decimal("60.00"),
    ) == Decimal("1660.00")


def teste_todosOsCamposSempreDeduzidos2032(record_xml_attribute) -> None:
    _java(record_xml_attribute, "teste_todosOsCamposSempreDeduzidos2032")
    assert _nfse(
        ano=2032,
        valor_servico=Decimal("1500.00"),
        desconto_incondicional=Decimal("100.00"),
        reembolso=Decimal("50.00"),
        deducao=Decimal("30.00"),
        iss=Decimal("60.00"),
    ) == Decimal("1260.00")