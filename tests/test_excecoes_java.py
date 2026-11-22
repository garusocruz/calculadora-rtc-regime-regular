"""Construtores de exceção de domínio (pin f1eebd7, Teste_ConcreteException)."""

from __future__ import annotations

from datetime import date

import pytest

from calculadora_rtc_regime_regular.aliquota_resultado import FormaAplicacaoNaoDefinida
from calculadora_rtc_regime_regular.base_calculo_service import CampoInvalido
from calculadora_rtc_regime_regular.calculadora import ClassificacaoTributariaNaoVinculadaTipoDfeException
from calculadora_rtc_regime_regular.cbs_ibs import TipoAliquotaDesconhecido
from calculadora_rtc_regime_regular.consultas import (
    AliquotaAdRemNaoEncontradaException,
    AliquotaReferenciaNaoEncontradaException,
    ErroInternoSistemaException,
    FundamentacaoClassificacaoNaoEncontradaException,
    MunicipioNaoEncontradoException,
    MunicipioNaoPertencenteException,
    PercentualReducaoNaoEncontradoException,
    SituacaoTributariaNaoEncontradaException,
    TipoDfeNaoEncontradoException,
    TratamentoClassificacaoNaoEncontradoException,
    UfNaoEncontradaException,
)
from calculadora_rtc_regime_regular.expressao import ErroAvaliadorExpressaoAritmeticaException
from calculadora_rtc_regime_regular.nomenclatura import (
    ClassificacaoTributariaNaoEncontradaException,
    NbsCompletoNaoInformadoException,
    NbsNaoVinculadaException,
    NcmCompletoNaoInformadoException,
    NcmNaoVinculadaException,
    NomenclaturaException,
    NomenclaturaIncompativelTipoDfeException,
    NomenclaturaNaoPermitidaTipoDfeException,
    NomenclaturaObrigatoriaNaoInformadaException,
)
from calculadora_rtc_regime_regular.processamento_item import (
    ClassificacaoTributariaNaoVinculadaSituacaoTributariaException,
    ImpostoSeletivoInformadoIndevidamenteException,
    ImpostoSeletivoNaoAdmitidoTipoDfeException,
    ImpostoSeletivoNaoInformadoException,
    IncompatibilidadeSuspensaoException,
    NbsNaoEncontradaException,
    NcmNaoEncontradaException,
    NcmNbsSimultaneasException,
    TributacaoRegularInformadaIndevidamenteException,
    TributacaoRegularNaoInformadaException,
)

_FQCN = "br.gov.serpro.rtc.testesunitarios.exception.Teste_ConcreteException"


def _java(record_xml_attribute, nome: str) -> None:
    record_xml_attribute("classname", _FQCN)
    record_xml_attribute("name", nome)


def _msg(exc: BaseException) -> str:
    return str(exc)


def test_Teste_NcmNaoVinculadaException(record_xml_attribute) -> None:
    _java(record_xml_attribute, "Teste_NcmNaoVinculadaException")
    ncm, c_class, tributo = "24021000", "200003", "CBS e IBS"
    exc = NcmNaoVinculadaException(ncm, c_class, tributo)
    assert _msg(exc) == (
        f"NCM de código {ncm} não vinculada à Classificação Tributária de código {c_class} ({tributo})"
    )


def test_Teste_ClassificacaoTributariaNaoEncontradaException(record_xml_attribute) -> None:
    _java(record_xml_attribute, "Teste_ClassificacaoTributariaNaoEncontradaException")
    c_class, tributo, data = "200003", "CBS e IBS", date.today()
    exc = ClassificacaoTributariaNaoEncontradaException(c_class, tributo, data)
    assert _msg(exc) == f"Classificação tributária não encontrada para código {c_class} e data {data} ({tributo})"


def test_Teste_TipoAliquotaDesconhecidoException(record_xml_attribute) -> None:
    _java(record_xml_attribute, "Teste_TipoAliquotaDesconhecidoException")
    tipo, c_class, cst = "Padrão", "000001", "000"
    exc = TipoAliquotaDesconhecido(tipo, c_class, cst)
    assert _msg(exc) == f"Tipo de alíquota ({tipo}) desconhecido para cClassTrib {c_class} e CST {cst}"


def test_Teste_AliquotaAdRemNaoEncontradaException(record_xml_attribute) -> None:
    _java(record_xml_attribute, "Teste_AliquotaAdRemNaoEncontradaException")
    ncm, id_tributo, data = "24021000", 2, date.today()
    exc = AliquotaAdRemNaoEncontradaException(ncm, id_tributo, data)
    assert _msg(exc) == f"Alíquota ad rem não encontrada para NCM {ncm} e data {data} (idTributo: {id_tributo})"


def test_Teste_SituacaoTributariaNaoEncontradaException(record_xml_attribute) -> None:
    _java(record_xml_attribute, "Teste_SituacaoTributariaNaoEncontradaException")
    codigo, tributo, data = "555", "CBS e IBS", date.today()
    exc = SituacaoTributariaNaoEncontradaException(codigo, tributo, data)
    assert _msg(exc) == f"Situação tributária (CST) não encontrada para código {codigo} e data {data} ({tributo})"


def test_Teste_NomenclaturaException(record_xml_attribute) -> None:
    _java(record_xml_attribute, "Teste_NomenclaturaException")
    texto = "Só se aplica a IBS..."
    exc = NomenclaturaException(texto)
    assert _msg(exc) == texto


def test_Teste_NbsNaoVinculadaException(record_xml_attribute) -> None:
    _java(record_xml_attribute, "Teste_NbsNaoVinculadaException")
    nbs, c_class, tributo = "114052200", "000001", "CBS e IBS"
    exc = NbsNaoVinculadaException(nbs, c_class, tributo)
    assert _msg(exc) == (
        f"NBS de código {nbs} não vinculada à Classificação Tributária de código {c_class} ({tributo})"
    )


def test_Teste_PercentualReducaoNaoEncontradoException(record_xml_attribute) -> None:
    _java(record_xml_attribute, "Teste_PercentualReducaoNaoEncontradoException")
    id_class, data = 1, date.today()
    exc = PercentualReducaoNaoEncontradoException(id_class, data)
    assert _msg(exc) == (
        f"Percentual de redução não encontrado para classificação tributária com id {id_class} e data {data}"
    )


def test_Teste_IncompatibilidadeSuspensaoException(record_xml_attribute) -> None:
    _java(record_xml_attribute, "Teste_IncompatibilidadeSuspensaoException")
    c_class, cst = "550001", "550"
    exc = IncompatibilidadeSuspensaoException(c_class, cst)
    assert _msg(exc) == (
        f"Classificação tributária (cClassTrib) {c_class} e situação tributária (CST) {cst} "
        "incompatíveis com suspensão"
    )


def test_Teste_TratamentoClassificacaoNaoEncontradoException(record_xml_attribute) -> None:
    _java(record_xml_attribute, "Teste_TratamentoClassificacaoNaoEncontradoException")
    id_class, data = 1, date.today()
    exc = TratamentoClassificacaoNaoEncontradoException(id_class, data)
    assert _msg(exc) == (
        f"Tratamento tributário não encontrado para classificação tributária com id {id_class} e data {data}"
    )


def test_Teste_ImpostoSeletivoNaoInformadoException(record_xml_attribute) -> None:
    _java(record_xml_attribute, "Teste_ImpostoSeletivoNaoInformadoException")
    ncm, data = "24021000", date.today()
    exc = ImpostoSeletivoNaoInformadoException("NCM", ncm, data)
    assert _msg(exc) == f"Dados do Imposto Seletivo devem ser informados para NCM {ncm} e data {data}"


def test_Teste_NcmNaoEncontradaException(record_xml_attribute) -> None:
    _java(record_xml_attribute, "Teste_NcmNaoEncontradaException")
    ncm, data = "24021000", date.today()
    exc = NcmNaoEncontradaException(ncm, data)
    assert _msg(exc) == f"NCM de código {ncm} não encontrada para a data {data}"


def test_Teste_AliquotaReferenciaNaoEncontradaException(record_xml_attribute) -> None:
    _java(record_xml_attribute, "Teste_AliquotaReferenciaNaoEncontradaException")
    id_tributo, data = 2, date.today()
    exc = AliquotaReferenciaNaoEncontradaException(id_tributo, data)
    assert _msg(exc) == (
        f"Alíquota de referência não encontrada para o tributo com id {id_tributo} e data {data}"
    )


def test_Teste_DesoneracaoNaoInformadaException(record_xml_attribute) -> None:
    _java(record_xml_attribute, "Teste_DesoneracaoNaoInformadaException")
    c_class, cst = "550001", "550"
    exc = TributacaoRegularNaoInformadaException(c_class, cst)
    assert _msg(exc) == f"Dados da tributação regular devem ser informados para cClassTrib {c_class} e CST {cst}"


def test_Teste_DesoneracaoInformadaIndevidamenteException(record_xml_attribute) -> None:
    _java(record_xml_attribute, "Teste_DesoneracaoInformadaIndevidamenteException")
    c_class, cst = "000001", "000"
    exc = TributacaoRegularInformadaIndevidamenteException(c_class, cst)
    assert _msg(exc) == (
        f"Dados da tributação regular informados indevidamente para cClassTrib {c_class} e CST {cst}"
    )


def test_Teste_FundamentacaoClassificacaoNaoEncontradaException(record_xml_attribute) -> None:
    _java(record_xml_attribute, "Teste_FundamentacaoClassificacaoNaoEncontradaException")
    id_class, data = 1, date.today()
    exc = FundamentacaoClassificacaoNaoEncontradaException(id_class, data)
    assert _msg(exc) == (
        f"Fundamentação legal não encontrada para classificação tributária de id {id_class} e data {data}"
    )


def test_Teste_ImpostoSeletivoInformadoIndevidamenteException(record_xml_attribute) -> None:
    _java(record_xml_attribute, "Teste_ImpostoSeletivoInformadoIndevidamenteException")
    ncm, data = "09024000", date.today()
    exc = ImpostoSeletivoInformadoIndevidamenteException(ncm, data)
    assert _msg(exc) == f"Dados do Imposto Seletivo informados indevidamente para NCM {ncm} e data {data}"


def test_Teste_NbsNaoEncontradaException(record_xml_attribute) -> None:
    _java(record_xml_attribute, "Teste_NbsNaoEncontradaException")
    nbs, data = "999999999", date.today()
    exc = NbsNaoEncontradaException(nbs, data)
    assert _msg(exc) == f"NBS de código {nbs} não encontrada para a data {data}"


def test_Teste_MunicipioNaoPertencenteException(record_xml_attribute) -> None:
    _java(record_xml_attribute, "Teste_MunicipioNaoPertencenteException")
    id_mun, uf = 430192, "RJ"
    exc = MunicipioNaoPertencenteException(id_mun, uf)
    assert _msg(exc) == f"Município de código {id_mun} não pertence à UF de sigla {uf}"


def test_Teste_UfNaoEncontradaException(record_xml_attribute) -> None:
    _java(record_xml_attribute, "Teste_UfNaoEncontradaException")
    uf = "RJ"
    exc = UfNaoEncontradaException(uf)
    assert _msg(exc) == f"UF de sigla {uf} não encontrada"


def test_Teste_ErroAvaliadorExpressaoAritmeticaException(record_xml_attribute) -> None:
    _java(record_xml_attribute, "Teste_ErroAvaliadorExpressaoAritmeticaException")
    erro = "Operador inválido"
    exc = ErroAvaliadorExpressaoAritmeticaException(erro)
    assert _msg(exc) == f"Erro na avaliação de expressão aritmética ({erro})"


def test_Teste_MunicipioNaoEncontradoException(record_xml_attribute) -> None:
    _java(record_xml_attribute, "Teste_MunicipioNaoEncontradoException")
    id_mun = 9999999
    exc = MunicipioNaoEncontradoException(id_mun)
    assert _msg(exc) == f"Município de código {id_mun} não encontrado"


def test_Teste_ErroInternoSistemaException(record_xml_attribute) -> None:
    _java(record_xml_attribute, "Teste_ErroInternoSistemaException")
    mensagem = "Erro interno no sistema"
    exc = ErroInternoSistemaException(mensagem)
    assert _msg(exc) == mensagem


def test_Teste_FormaAplicacaoNaoDefinidaException(record_xml_attribute) -> None:
    _java(record_xml_attribute, "Teste_FormaAplicacaoNaoDefinidaException")
    exc = FormaAplicacaoNaoDefinida()
    assert _msg(exc) == "Forma de aplicação da alíquota própria não definida"


def test_Teste_NcmNbsSimultaneasException(record_xml_attribute) -> None:
    _java(record_xml_attribute, "Teste_NcmNbsSimultaneasException")
    exc = NcmNbsSimultaneasException()
    assert _msg(exc) == "Não é permitido informar NCM e NBS simultaneamente para um item"


def test_Teste_NcmCompletoNaoInformadoException(record_xml_attribute) -> None:
    _java(record_xml_attribute, "Teste_NcmCompletoNaoInformadoException")
    exc = NcmCompletoNaoInformadoException()
    assert _msg(exc) == "NCM completo não informado"


def test_Teste_NbsCompletoNaoInformadoException(record_xml_attribute) -> None:
    _java(record_xml_attribute, "Teste_NbsCompletoNaoInformadoException")
    exc = NbsCompletoNaoInformadoException()
    assert _msg(exc) == "NBS completo não informado"


def test_Teste_CampoInvalidoException(record_xml_attribute) -> None:
    _java(record_xml_attribute, "Teste_CampoInvalidoException")
    msg = "Campo inválido"
    exc = CampoInvalido(msg)
    assert _msg(exc) == msg


def test_Teste_TipoDfeNaoEncontradoException(record_xml_attribute) -> None:
    _java(record_xml_attribute, "Teste_TipoDfeNaoEncontradoException")
    tp_doc, data = 99, date.today()
    exc = TipoDfeNaoEncontradoException(tp_doc, data)
    assert _msg(exc) == (
        f"Tipo de documento fiscal (tpDoc) de código {tp_doc} não encontrado ou fora de vigência na data {data}"
    )


def test_Teste_ClassificacaoTributariaNaoVinculadaTipoDfeException(record_xml_attribute) -> None:
    _java(record_xml_attribute, "Teste_ClassificacaoTributariaNaoVinculadaTipoDfeException")
    c_class, tp_doc, tributos = "200044", 55, "CBS e IBS"
    exc = ClassificacaoTributariaNaoVinculadaTipoDfeException(c_class, tp_doc, tributos)
    assert _msg(exc) == (
        f"Classificação Tributária de código {c_class} não vinculada ao tipo de "
        f"documento fiscal (tpDoc) {tp_doc} ({tributos})"
    )


def test_Teste_NomenclaturaIncompativelTipoDfeException(record_xml_attribute) -> None:
    _java(record_xml_attribute, "Teste_NomenclaturaIncompativelTipoDfeException")
    exc = NomenclaturaIncompativelTipoDfeException("NBS", "200043", "NFe")
    assert _msg(exc) == (
        "NBS não permitida para a Classificação Tributária de código 200043 no tipo de documento NFe"
    )


def test_Teste_NomenclaturaNaoPermitidaTipoDfeException(record_xml_attribute) -> None:
    _java(record_xml_attribute, "Teste_NomenclaturaNaoPermitidaTipoDfeException")
    exc = NomenclaturaNaoPermitidaTipoDfeException("200044", "NFCom")
    assert _msg(exc) == (
        "NCM/NBS não permitido para a Classificação Tributária de código 200044 "
        "no tipo de documento NFCom"
    )


def test_Teste_ImpostoSeletivoNaoAdmitidoTipoDfeException(record_xml_attribute) -> None:
    _java(record_xml_attribute, "Teste_ImpostoSeletivoNaoAdmitidoTipoDfeException")
    exc = ImpostoSeletivoNaoAdmitidoTipoDfeException(62, "NCM", "24021000")
    assert _msg(exc) == (
        "O tipo de documento fiscal (tpDoc) 62 não admite Imposto Seletivo, exigido para NCM de código 24021000"
    )


def test_Teste_NomenclaturaObrigatoriaNaoInformadaException(record_xml_attribute) -> None:
    _java(record_xml_attribute, "Teste_NomenclaturaObrigatoriaNaoInformadaException")
    exc = NomenclaturaObrigatoriaNaoInformadaException("200043", "NFSe")
    assert _msg(exc) == (
        "A Classificação Tributária de código 200043 exige NCM ou NBS completo para o tipo de documento NFSe"
    )


def test_Teste_ClassificacaoTributariaNaoVinculadaSituacaoTributariaException(
    record_xml_attribute,
) -> None:
    _java(record_xml_attribute, "Teste_ClassificacaoTributariaNaoVinculadaSituacaoTributariaException")
    c_class, cst, tributo = "000020", "000", "Imposto Seletivo"
    exc = ClassificacaoTributariaNaoVinculadaSituacaoTributariaException(c_class, cst, tributo)
    assert _msg(exc) == (
        f"Classificação tributária (cClassTrib) de código {c_class} não está vinculada à situação tributária "
        f"(CST) de código {cst} ({tributo})"
    )