"""Testes de memória de cálculo e tokenizer (pin f1eebd7ce3157423b1a6aaca7dc1d6c3395452c4)."""

from __future__ import annotations

import os
from datetime import date
from decimal import Decimal

import pytest

os.environ.setdefault(
    "CALC_DB",
    "/home/garusotec/projects/lynko/libs/calculadora-rtc-regime-regular/.cache/oficial/java/calculadora/db/calculadora-pro.db",
)

from calculadora_rtc_regime_regular.consultas import (  # noqa: E402
    TratamentoClassificacaoDTO,
    TratamentoClassificacaoService,
)
from calculadora_rtc_regime_regular.memoria import (  # noqa: E402
    MemoriaCalculoService,
    TokenizerService,
    TributoCbsIbsMemoria,
    formatar_moeda,
    formatar_percentual,
    tokenize,
)
from calculadora_rtc_regime_regular.roc import (  # noqa: E402
    CBSDomain,
    GrupoIBSCBSDomain,
    IBSCBSDomain,
    ImpostoSeletivoDomain,
)

_TRATAMENTO = TratamentoClassificacaoDTO(
    id_tratamento_tributario=1,
    id_classificacao_tributaria=1,
    in_incompativel_com_suspensao=False,
    in_exige_grupo_desoneracao=False,
)
_DATA = date(2026, 1, 15)


@pytest.mark.parametrize(
    ("valor", "esperado"),
    [
        (Decimal("247.30000000"), "247,30"),
        (Decimal("1234.5"), "1.234,50"),
    ],
)
def test_formatar_moeda_em_pt_br(valor: Decimal, esperado: str) -> None:
    assert formatar_moeda(valor) == esperado


@pytest.mark.parametrize(
    ("valor", "esperado"),
    [
        (Decimal("8.4"), "8,40"),
        (Decimal("0.05"), "0,05"),
        (Decimal("0.0375"), "0,0375"),
    ],
)
def test_formatar_percentual_em_pt_br(valor: Decimal, esperado: str) -> None:
    assert formatar_percentual(valor) == esperado


def test_formatar_nulo_como_zero() -> None:
    assert formatar_moeda(None) == "0,00"
    assert formatar_percentual(None) == "0,00"


def test_tokenize_placeholders() -> None:
    tokens = tokenize("Base [base_calculo] com alíquota [aliquota_ad_valorem].")
    assert [t.key for t in tokens] == [None, "base_calculo", None, "aliquota_ad_valorem", None]
    assert tokens[0].text == "Base "


def test_substituir_placeholders() -> None:
    tokenizer = TokenizerService()
    texto = tokenizer.substituir_placeholders(
        "Norma [norma], base [base_calculo].",
        {"norma": "LC 214", "base_calculo": "10,00"},
    )
    assert texto == "Norma LC 214, base 10,00."


def test_substituir_sem_colchetes_retorna_original() -> None:
    assert TokenizerService().substituir_placeholders("literal", {}) == "literal"


def test_memoria_desabilitada_retorna_none() -> None:
    svc = MemoriaCalculoService(memoria_calculo_habilitada=False)
    assert (
        svc.gerar_memoria_calculo_cbs_ibs(
            _TRATAMENTO,
            TributoCbsIbsMemoria(base_calculo=Decimal("10")),
            Decimal("10"),
            Decimal("1"),
            "UN",
            _DATA,
        )
        is None
    )


def test_gerar_memoria_cbs_ibs_com_banco() -> None:
    svc = MemoriaCalculoService()
    tributo = TributoCbsIbsMemoria(
        base_calculo=Decimal("200"),
        aliquota=Decimal("8.4"),
    )
    memoria = svc.gerar_memoria_calculo_cbs_ibs(
        _TRATAMENTO,
        tributo,
        Decimal("200"),
        Decimal("1"),
        "UN",
        _DATA,
    )
    assert memoria is not None
    assert "LC 214/2025" in memoria
    assert "200,00" in memoria
    assert "8,40" in memoria


def test_gerar_memoria_cbs_ibs_tributo_nulo_usa_base_informada() -> None:
    svc = MemoriaCalculoService()
    memoria = svc.gerar_memoria_calculo_cbs_ibs(
        _TRATAMENTO,
        None,
        Decimal("150.5"),
        None,
        None,
        _DATA,
    )
    assert memoria is not None
    assert "150,50" in memoria


def test_gerar_memoria_imposto_seletivo_com_banco() -> None:
    svc = MemoriaCalculoService()
    tributo = ImpostoSeletivoDomain(
        v_bcis=Decimal("200"),
        p_is=Decimal("13"),
        p_is_espec=Decimal("21.3"),
    )
    svc.gerar_memoria_calculo_imposto_seletivo(
        _TRATAMENTO, tributo, Decimal("2"), "UN", _DATA
    )
    assert tributo.memoria_calculo is not None
    assert "200,00" in tributo.memoria_calculo
    assert "13,00" in tributo.memoria_calculo or "13,0000" in tributo.memoria_calculo


def test_anexa_memoria_no_grupo_ibscbs() -> None:
    svc = MemoriaCalculoService()
    ibscbs = IBSCBSDomain(
        CST="000",
        c_class_trib="000001",
        g_ibscbs=GrupoIBSCBSDomain(v_bc=Decimal("200"), g_cbs=CBSDomain(p_cbs=Decimal("0.9"))),
    )
    svc.anexar_memoria_ibscbs(
        _TRATAMENTO,
        ibscbs,
        Decimal("200"),
        Decimal("1"),
        "UN",
        _DATA,
        calcular_ibs_estadual=False,
        calcular_ibs_municipal=False,
    )
    assert ibscbs.memoria_calculo is not None
    assert ibscbs.memoria_calculo.cbs
    assert ibscbs.memoria_calculo.ibs_uf is None
    assert ibscbs.memoria_calculo.ibs_mun is None


def test_grupos_opcionais_reducao_no_template() -> None:
    svc = MemoriaCalculoService()
    tratamento = TratamentoClassificacaoService().buscar_tratamento_classificacao(
        7, _DATA
    )
    tributo = TributoCbsIbsMemoria(
        base_calculo=Decimal("100"),
        aliquota=Decimal("1"),
        grupo_reducao=type("Reducao", (), {"p_red_aliq": Decimal("50")})(),
    )
    memoria = svc.gerar_memoria_calculo_cbs_ibs(
        tratamento, tributo, Decimal("100"), Decimal("3"), "KG", _DATA
    )
    assert memoria is not None
    assert "50,00" in memoria
    assert "redução" in memoria