"""Paridade com ``Teste_BaseCalculoUnificadaNfse_Controller`` (bases RG/SN, sem MockMvc)."""

from __future__ import annotations

from decimal import Decimal

from calculadora_rtc_regime_regular.nfse_unificada import (
    Ajuste,
    EntradaUnificada,
    Locacao,
    OpcaoSimples,
    RegimeSimples,
    Situacao,
    calcular_unificada,
)

_D = Decimal


def teste_cenario1_comum_nao_optante() -> None:
    r = calcular_unificada(
        EntradaUnificada(
            2026,
            OpcaoSimples.NAO_OPTANTE,
            Situacao.COMUM,
            _D("100.00"),
            _D("5.00"),
            _D("5.00"),
            _D("5.00"),
            _D("5.00"),
        )
    )
    assert r.base_rg == _D("80.00")
    assert r.base_sn is None


def teste_cenario2_salaoParceiro_nao_optante() -> None:
    r = calcular_unificada(
        EntradaUnificada(
            2026,
            OpcaoSimples.NAO_OPTANTE,
            Situacao.SALAO_PARCEIRO,
            _D("100.00"),
            _D("5.00"),
            _D("5.00"),
            _D("5.00"),
            _D("5.00"),
        )
    )
    assert r.base_rg == _D("80.00")
    assert r.base_sn is None


def teste_cenario3_locacao_nao_optante() -> None:
    r = calcular_unificada(
        EntradaUnificada(
            2026,
            OpcaoSimples.NAO_OPTANTE,
            Situacao.LOCACAO,
            pis=_D("5.00"),
            cofins=_D("5.00"),
            locacao=Locacao(_D("10.00"), _D("1000.00"), _D("5.00"), _D("5.00")),
        )
    )
    assert r.base_rg == _D("89.00")
    assert r.base_sn is None


def teste_cenario4_baseNegativa() -> None:
    r = calcular_unificada(
        EntradaUnificada(
            2026,
            OpcaoSimples.NAO_OPTANTE,
            Situacao.COMUM,
            _D("0"),
            _D("1.313"),
            documentos=[Ajuste("101", _D("0"))],
        )
    )
    assert r.base_rg == _D("-1.31")
    assert r.base_sn is None
    assert r.erros[0].codigo == "BASE-NEGATIVA"


def teste_cenario5_locacao_optante_com_erro() -> None:
    r = calcular_unificada(
        EntradaUnificada(
            2026,
            OpcaoSimples.OPTANTE,
            Situacao.LOCACAO,
            regime=RegimeSimples.PELO_SN,
            pis=_D("5.00"),
            cofins=_D("5.00"),
            locacao=Locacao(_D("10.00"), _D("1000.00"), _D("5.00"), _D("5.00")),
        )
    )
    assert r.base_rg == _D("89.00")
    assert r.base_sn == _D("99.50")
    assert r.erros[0].codigo == "EXXX-LOC-SN"


def teste_cenario6_salaoParceiro_regAp3() -> None:
    r = calcular_unificada(
        EntradaUnificada(
            2026,
            OpcaoSimples.OPTANTE,
            Situacao.SALAO_PARCEIRO,
            _D("100"),
            _D("5"),
            _D("5"),
            _D("5"),
            _D("5"),
            RegimeSimples.AMBOS_REGULARES,
        )
    )
    assert r.base_rg == _D("80.0")
    assert r.base_sn == _D("95.0")


def teste_cenario7_salaoParceiro_docTipo102() -> None:
    r = calcular_unificada(
        EntradaUnificada(
            2026,
            OpcaoSimples.OPTANTE,
            Situacao.SALAO_PARCEIRO,
            _D("100"),
            _D("5"),
            _D("5"),
            _D("5"),
            _D("5"),
            RegimeSimples.AMBOS_REGULARES,
            documentos=[Ajuste("102", _D("5"))],
        )
    )
    assert r.base_rg == _D("75.0")
    assert r.base_sn == _D("90.0")


def teste_cenario8_salaoParceiro_docTipo102_e_9() -> None:
    r = calcular_unificada(
        EntradaUnificada(
            2026,
            OpcaoSimples.OPTANTE,
            Situacao.SALAO_PARCEIRO,
            _D("100"),
            _D("5"),
            _D("5"),
            _D("5"),
            _D("5"),
            RegimeSimples.AMBOS_REGULARES,
            documentos=[Ajuste("102", _D("5")), Ajuste("9", _D("3"))],
        )
    )
    assert r.base_rg == _D("75.0")
    assert r.base_sn == _D("90.0")


def teste_camposZerados() -> None:
    r = calcular_unificada(
        EntradaUnificada(2026, OpcaoSimples.NAO_OPTANTE, Situacao.COMUM, _D("0"), _D("0"))
    )
    assert r.base_rg == _D("0.0")
    assert r.base_sn is None


def teste_ano2027_pisCofinsForaVigencia() -> None:
    r = calcular_unificada(
        EntradaUnificada(
            2027,
            OpcaoSimples.OPTANTE,
            Situacao.COMUM,
            _D("100"),
            _D("10"),
            regime=RegimeSimples.PELO_SN,
        )
    )
    assert r.base_rg == _D("90.0")
    assert r.base_sn == _D("90.0")


def teste_ano2033_issqnExtinto() -> None:
    r = calcular_unificada(
        EntradaUnificada(
            2033,
            OpcaoSimples.OPTANTE,
            Situacao.COMUM,
            _D("100"),
            _D("10"),
            _D("15"),
            regime=RegimeSimples.PELO_SN,
        )
    )
    assert r.base_rg == _D("90.0")
    assert r.base_sn == _D("90.0")


def teste_e1534_somaAjustesExcedeServico() -> None:
    r = calcular_unificada(
        EntradaUnificada(
            2026,
            OpcaoSimples.OPTANTE,
            Situacao.COMUM,
            _D("50"),
            _D("10"),
            regime=RegimeSimples.PELO_SN,
            documentos=[Ajuste("101", _D("50"))],
        )
    )
    assert r.erros[0].codigo == "E1534"
    assert r.base_rg == _D("-10.0")


def teste_regApObrigatorio() -> None:
    r = calcular_unificada(EntradaUnificada(2026, OpcaoSimples.OPTANTE, Situacao.COMUM, _D("100")))
    assert r.base_rg == _D("100.00")
    assert r.base_sn is None
    assert r.erros[0].codigo == "EXXX-REGAP"


def teste_tipo199SemDescricao() -> None:
    r = calcular_unificada(
        EntradaUnificada(
            2026,
            OpcaoSimples.OPTANTE,
            Situacao.COMUM,
            _D("100"),
            regime=RegimeSimples.PELO_SN,
            documentos=[Ajuste("199", _D("10"))],
        )
    )
    assert r.base_rg == _D("100.0")
    assert r.base_sn == _D("100.0")
    assert r.erros[0].codigo == "LEIAUTE-XTP"


def teste_tipo199ComDescricao() -> None:
    r = calcular_unificada(
        EntradaUnificada(
            2026,
            OpcaoSimples.NAO_OPTANTE,
            Situacao.COMUM,
            _D("100"),
            documentos=[Ajuste("199", _D("10"), "Ajuste personalizado")],
        )
    )
    assert r.base_rg == _D("90.0")
    assert r.erros == []


def teste_camposNulos_tratadosComoZero() -> None:
    r = calcular_unificada(EntradaUnificada(2026, OpcaoSimples.NAO_OPTANTE, Situacao.COMUM))
    assert r.base_rg == _D("0.00")
    assert r.base_sn is None


def teste_cenario_sucesso_comum_optante_regAp1() -> None:
    r = calcular_unificada(
        EntradaUnificada(
            2026,
            OpcaoSimples.OPTANTE,
            Situacao.COMUM,
            _D("500"),
            _D("20"),
            _D("15"),
            _D("0.65"),
            _D("3.00"),
            RegimeSimples.PELO_SN,
        )
    )
    assert r.base_rg == _D("461.35")
    assert r.base_sn == _D("480.0")


def teste_cenario_sucesso_comum_optante_regAp2_docTipo9() -> None:
    r = calcular_unificada(
        EntradaUnificada(
            2026,
            OpcaoSimples.OPTANTE,
            Situacao.COMUM,
            _D("500"),
            _D("20"),
            _D("15"),
            _D("0.65"),
            _D("3.00"),
            RegimeSimples.CBS_PELO_SN,
            documentos=[Ajuste("9", _D("15"))],
        )
    )
    assert r.base_rg == _D("461.35")
    assert r.base_sn == _D("480.0")


def teste_cenario_sucesso_salaoParceiro_regAp1_docTipo9() -> None:
    r = calcular_unificada(
        EntradaUnificada(
            2026,
            OpcaoSimples.OPTANTE,
            Situacao.SALAO_PARCEIRO,
            _D("500"),
            _D("20"),
            _D("15"),
            _D("0.65"),
            _D("3.00"),
            RegimeSimples.PELO_SN,
            documentos=[Ajuste("9", _D("15"))],
        )
    )
    assert r.base_rg == _D("461.35")
    assert r.base_sn == _D("465.0")


def teste_cenario_sucesso_optante_pendente() -> None:
    r = calcular_unificada(
        EntradaUnificada(2026, OpcaoSimples.PENDENTE, Situacao.COMUM, _D("200"), _D("10"))
    )
    assert r.base_rg == _D("190.00")
    assert r.base_sn is None
    assert r.avisos


def teste_cenario_sucesso_locacao_optante_regAp1_vs_2() -> None:
    r = calcular_unificada(
        EntradaUnificada(
            2026,
            OpcaoSimples.OPTANTE,
            Situacao.LOCACAO,
            regime=RegimeSimples.CBS_PELO_SN,
            pis=_D("0.65"),
            cofins=_D("3.00"),
            locacao=Locacao(_D("50"), _D("800"), _D("80"), _D("10")),
        )
    )
    assert r.base_rg == _D("351.35")
    assert r.base_sn == _D("360.0")


def teste_cenario_sucesso_todos_cinzeros() -> None:
    r = calcular_unificada(
        EntradaUnificada(
            2026,
            OpcaoSimples.OPTANTE,
            Situacao.COMUM,
            _D("0"),
            _D("0"),
            _D("0"),
            _D("0"),
            _D("0"),
            RegimeSimples.PELO_SN,
        )
    )
    assert r.base_rg == _D("0.0")
    assert r.base_sn == _D("0.0")


def teste_cenario_sucesso_multiplos_docs() -> None:
    r = calcular_unificada(
        EntradaUnificada(
            2026,
            OpcaoSimples.OPTANTE,
            Situacao.COMUM,
            _D("500"),
            _D("20"),
            regime=RegimeSimples.PELO_SN,
            documentos=[
                Ajuste("101", _D("10")),
                Ajuste("102", _D("5")),
                Ajuste("9", _D("8")),
            ],
        )
    )
    assert r.base_rg == _D("465.0")
    assert r.base_sn == _D("465.0")


def teste_cenario_sucesso_locacao_optante_docs_ignored() -> None:
    r = calcular_unificada(
        EntradaUnificada(
            2026,
            OpcaoSimples.OPTANTE,
            Situacao.LOCACAO,
            regime=RegimeSimples.PELO_SN,
            pis=_D("5"),
            cofins=_D("5"),
            locacao=Locacao(_D("10"), _D("1000"), _D("5"), _D("5")),
            documentos=[Ajuste("101", _D("50"))],
        )
    )
    assert r.base_rg == _D("89.0")
    assert r.base_sn == _D("99.5")
    assert r.avisos


def teste_cenario_sucesso_tipo0_ajuste() -> None:
    r = calcular_unificada(
        EntradaUnificada(
            2026,
            OpcaoSimples.OPTANTE,
            Situacao.COMUM,
            _D("100"),
            regime=RegimeSimples.PELO_SN,
            documentos=[Ajuste("0", _D("20"))],
        )
    )
    assert r.base_rg == _D("100.0")
    assert r.base_sn == _D("100.0")


def teste_cenario_sucesso_arredondamento_3_decimais() -> None:
    r = calcular_unificada(
        EntradaUnificada(
            2026,
            OpcaoSimples.OPTANTE,
            Situacao.COMUM,
            _D("100.777"),
            _D("5.444"),
            regime=RegimeSimples.PELO_SN,
        )
    )
    assert r.base_rg == _D("95.33")
    assert r.base_sn == _D("95.33")