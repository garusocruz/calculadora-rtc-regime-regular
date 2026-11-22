from decimal import Decimal

import pytest

from calculadora_rtc_regime_regular.base_calculo_service import CampoInvalido
from calculadora_rtc_regime_regular.nfse_unificada import (
    Ajuste,
    EntradaUnificada,
    Locacao,
    OpcaoSimples,
    RegimeSimples,
    Situacao,
    calcular_unificada,
)


def test_regime_geral_deduz_iss_pis_e_cofins_em_2026() -> None:
    resultado = calcular_unificada(
        EntradaUnificada(
            2026,
            OpcaoSimples.NAO_OPTANTE,
            Situacao.COMUM,
            Decimal("1000.00"),
            Decimal("50.00"),
            Decimal("80.00"),
            Decimal("16.50"),
            Decimal("76.00"),
        )
    )
    assert resultado.base_rg == Decimal("777.50")
    assert resultado.base_sn is None
    assert resultado.erros == []


def test_mei_nao_calcula_e_recusa_documento() -> None:
    resultado = calcular_unificada(
        EntradaUnificada(2026, OpcaoSimples.MEI, Situacao.COMUM, Decimal("1000"), documentos=[Ajuste("101", Decimal("10"))])
    )
    assert resultado.base_rg is None and resultado.base_sn is None
    assert resultado.avisos == ["E1302: Operação MEI: bases de cálculo não aplicáveis"]
    assert resultado.erros[0].codigo == "E0436"


def test_optante_sem_regime_ainda_calcula_o_regime_geral() -> None:
    resultado = calcular_unificada(EntradaUnificada(2026, OpcaoSimples.OPTANTE, Situacao.COMUM, Decimal("1000")))
    assert resultado.erros[0].codigo == "EXXX-REGAP"
    assert resultado.base_rg == Decimal("1000.00")
    assert resultado.base_sn is None


def test_nao_optante_nao_recebe_regime() -> None:
    resultado = calcular_unificada(
        EntradaUnificada(2026, OpcaoSimples.NAO_OPTANTE, Situacao.COMUM, Decimal("100"), regime=RegimeSimples.PELO_SN)
    )
    assert resultado.erros[0].mensagem.startswith("Campo regApIBSCBSSN proibido")


def test_locacao_rateia_pela_copropriedade_e_ignora_iss() -> None:
    resultado = calcular_unificada(
        EntradaUnificada(
            2026,
            OpcaoSimples.NAO_OPTANTE,
            Situacao.LOCACAO,
            pis=Decimal("10"),
            iss=Decimal("99"),
            locacao=Locacao(Decimal("50"), Decimal("1000"), Decimal("100"), Decimal("40")),
            documentos=[Ajuste("101", Decimal("999"))],
        )
    )
    assert resultado.base_rg == Decimal("420.00")
    assert "Documentos de ajuste ignorados" in resultado.avisos[0]


def test_locacao_sem_grupo_rejeita() -> None:
    with pytest.raises(CampoInvalido, match="locacao obrigatório"):
        calcular_unificada(EntradaUnificada(2026, OpcaoSimples.NAO_OPTANTE, Situacao.LOCACAO, Decimal("100")))


def test_simples_deduz_ajuste_de_ibs_e_no_salao_o_parceiro() -> None:
    comum = calcular_unificada(
        EntradaUnificada(
            2026,
            OpcaoSimples.OPTANTE,
            Situacao.COMUM,
            Decimal("1000"),
            Decimal("100"),
            regime=RegimeSimples.PELO_SN,
            documentos=[Ajuste("101", Decimal("50")), Ajuste("9", Decimal("30"))],
        )
    )
    assert comum.base_rg == Decimal("850.00")
    assert comum.base_sn == Decimal("850.00")
    salao = calcular_unificada(
        EntradaUnificada(
            2026,
            OpcaoSimples.OPTANTE,
            Situacao.SALAO_PARCEIRO,
            Decimal("1000"),
            Decimal("100"),
            regime=RegimeSimples.PELO_SN,
            documentos=[Ajuste("101", Decimal("50")), Ajuste("9", Decimal("30"))],
        )
    )
    assert salao.base_sn == Decimal("820.00")
    regular = calcular_unificada(
        EntradaUnificada(
            2026,
            OpcaoSimples.OPTANTE,
            Situacao.SALAO_PARCEIRO,
            Decimal("1000"),
            Decimal("100"),
            regime=RegimeSimples.AMBOS_REGULARES,
            documentos=[Ajuste("101", Decimal("50")), Ajuste("9", Decimal("30"))],
        )
    )
    assert regular.base_sn == Decimal("850.00")


def test_tipo_desconhecido_e_199_sem_descricao_ficam_fora_da_soma() -> None:
    resultado = calcular_unificada(
        EntradaUnificada(
            2026,
            OpcaoSimples.NAO_OPTANTE,
            Situacao.COMUM,
            Decimal("1000"),
            documentos=[Ajuste("777", Decimal("40")), Ajuste("199", Decimal("70"))],
        )
    )
    assert resultado.base_rg == Decimal("1000.00")
    assert resultado.avisos[0].startswith("Tipo de ajuste '777'")
    assert resultado.erros[0].codigo == "LEIAUTE-XTP"


def test_ajuste_que_cobre_o_servico_e_base_negativa() -> None:
    estouro = calcular_unificada(
        EntradaUnificada(
            2026,
            OpcaoSimples.NAO_OPTANTE,
            Situacao.COMUM,
            Decimal("100"),
            documentos=[Ajuste("101", Decimal("100"))],
        )
    )
    assert estouro.erros[0].codigo == "E1534"
    assert "100.00" in estouro.erros[0].mensagem
    negativa = calcular_unificada(
        EntradaUnificada(2026, OpcaoSimples.NAO_OPTANTE, Situacao.COMUM, Decimal("10"), Decimal("40"))
    )
    assert negativa.base_rg == Decimal("-30.00")
    assert negativa.erros[0].codigo == "BASE-NEGATIVA"


def test_depois_de_2027_pis_e_cofins_saem_da_base_geral() -> None:
    resultado = calcular_unificada(
        EntradaUnificada(2027, OpcaoSimples.NAO_OPTANTE, Situacao.COMUM, Decimal("1000"), pis=Decimal("10"), cofins=Decimal("20"))
    )
    assert resultado.base_rg == Decimal("1000.00")


def test_rg12_oficial_base_unificada_nfse_locacao_copropriedade() -> None:
    """Pedido RG12_base_unificada_nfse.json — 1.000,05 × 33,33% → 333,32."""
    resultado = calcular_unificada(
        EntradaUnificada(
            2026,
            OpcaoSimples.NAO_OPTANTE,
            Situacao.LOCACAO,
            Decimal("1000.00"),
            Decimal("0.00"),
            Decimal("0.00"),
            Decimal("0.00"),
            Decimal("0.00"),
            locacao=Locacao(Decimal("33.33"), Decimal("1000.05"), Decimal("0.00"), Decimal("0.00")),
        )
    )
    assert resultado.base_rg == Decimal("333.32")
    assert resultado.base_sn is None


def test_optante_pendente_avisa_e_mei_nao_loca() -> None:
    pendente = calcular_unificada(
        EntradaUnificada(2026, OpcaoSimples.PENDENTE, Situacao.COMUM, Decimal("100"), regime=RegimeSimples.CBS_PELO_SN)
    )
    assert pendente.avisos == ["Optante pendente: cálculo realizado com ressalva"]
    assert pendente.base_sn == Decimal("100.00")
    mei = calcular_unificada(
        EntradaUnificada(
            2026,
            OpcaoSimples.MEI,
            Situacao.LOCACAO,
            locacao=Locacao(Decimal("100"), Decimal("10"), Decimal(0), Decimal(0)),
        )
    )
    assert any(erro.codigo == "EXXX-LOC-SN" for erro in mei.erros)
