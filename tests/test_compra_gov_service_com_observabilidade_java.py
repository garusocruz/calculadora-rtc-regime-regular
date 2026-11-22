"""Paridade com CompraGovServiceComObservabilidadeTest (ObservabilidadeService)."""

from __future__ import annotations

import json
import os
from decimal import Decimal
from pathlib import Path

import pytest

os.environ.setdefault(
    "CALC_DB",
    "/home/garusotec/projects/lynko/libs/calculadora-rtc-regime-regular/.cache/oficial/java/calculadora/db/calculadora-pro.db",
)

from calculadora_rtc_regime_regular.consumo import ObservabilidadeService
from calculadora_rtc_regime_regular.observabilidade import operacao_from_json

_CACHE = Path(__file__).resolve().parents[1] / ".cache/oficial/java/src/test/resources"
_BASE_URL = "http://localhost:8080"
_ENTRADA = "entradas/calculoscorretos/compras-governamentais/entrada.json"

pytestmark = pytest.mark.skipif(not os.environ.get("CALC_DB"), reason="CALC_DB ausente")


def _dec(value: object) -> Decimal:
    return Decimal(str(value))


def _compat_itens_seletivo(operacao) -> None:
    for item in operacao.itens:
        seletivo = item.imposto_seletivo
        if seletivo is not None and not hasattr(seletivo, "valor_informado"):
            seletivo.valor_informado = seletivo.imposto_informado  # type: ignore[attr-defined]


def _cmp(actual: object, esperado: str) -> None:
    assert _dec(actual).compare(_dec(esperado)) == 0


def test_deveCalcularTributosCompraGov() -> None:
    entrada = json.loads((_CACHE / _ENTRADA).read_text(encoding="utf-8"))
    operacao = operacao_from_json(entrada)
    _compat_itens_seletivo(operacao)
    roc = ObservabilidadeService().processarOperacao(operacao, _BASE_URL)
    assert roc is not None

    compra_gov = roc.oper.g_compra_gov
    assert compra_gov is not None
    assert compra_gov.tp_ente_gov is not None
    assert compra_gov.tp_oper_gov is not None
    _cmp(compra_gov.p_redutor, "0.00")

    assert roc.objetos is not None and len(roc.objetos) == 1
    obj = roc.objetos[0]
    assert obj.n_obj == 1
    trib = obj.trib_calc
    assert trib is not None

    is_calc = trib.IS
    assert is_calc is not None
    _cmp(is_calc.v_bcis, "200.00")
    _cmp(is_calc.p_is, "14.00")
    _cmp(is_calc.p_is_espec, "21.30")
    _cmp(is_calc.q_trib, "1")
    _cmp(is_calc.v_is, "49.30")

    assert trib.IBSCBS is not None
    g = trib.IBSCBS.g_ibscbs
    assert g is not None
    _cmp(g.v_bc, "249.30")

    ibs_uf = g.g_ibs_uf
    assert ibs_uf is not None
    _cmp(ibs_uf.p_ibs_uf, "0.00")
    assert ibs_uf.g_red is not None
    _cmp(ibs_uf.g_red.p_red_aliq, "0.00")
    _cmp(ibs_uf.g_red.p_aliq_efet, "0.00")
    _cmp(ibs_uf.v_ibs_uf, "0.00")

    ibs_mun = g.g_ibs_mun
    assert ibs_mun is not None
    _cmp(ibs_mun.p_ibs_mun, "0.00")
    assert ibs_mun.g_red is not None
    _cmp(ibs_mun.g_red.p_red_aliq, "0.00")
    _cmp(ibs_mun.g_red.p_aliq_efet, "0.00")
    _cmp(ibs_mun.v_ibs_mun, "0.00")
    _cmp(g.v_ibs, "0.00")

    cbs = g.g_cbs
    assert cbs is not None
    _cmp(cbs.p_cbs, "0.00")
    assert cbs.g_red is not None
    _cmp(cbs.g_red.p_red_aliq, "0.00")
    _cmp(cbs.g_red.p_aliq_efet, "0.00")
    _cmp(cbs.v_cbs, "0.00")

    reg = g.g_trib_regular
    assert reg is not None
    _cmp(reg.p_aliq_efet_reg_ibs_uf, "1.08")
    _cmp(reg.v_trib_reg_ibs_uf, "2.69")
    _cmp(reg.p_aliq_efet_reg_ibs_mun, "0.00")
    _cmp(reg.v_trib_reg_ibs_mun, "0.00")
    _cmp(reg.p_aliq_efet_reg_cbs, "3.06")
    _cmp(reg.v_trib_reg_cbs, "7.63")

    tcg = g.g_trib_compra_gov
    assert tcg is not None
    _cmp(tcg.p_aliq_ibs_uf, "0.00")
    _cmp(tcg.v_trib_ibs_uf, "0.00")
    _cmp(tcg.p_aliq_ibs_mun, "0.00")
    _cmp(tcg.v_trib_ibs_mun, "0.00")
    _cmp(tcg.p_aliq_cbs, "0.00")
    _cmp(tcg.v_trib_cbs, "0.00")

    tot = roc.total.trib_calc
    assert tot is not None and tot.is_tot is not None
    _cmp(tot.is_tot.v_is, "49.30")
    assert tot.ibscbs_tot is not None
    _cmp(tot.ibscbs_tot.v_bc_ibscbs, "249.30")
    tot_ibs = tot.ibscbs_tot.g_ibs
    assert tot_ibs is not None
    _cmp(tot_ibs.g_ibs_uf.v_dif, "0.00")
    _cmp(tot_ibs.g_ibs_uf.v_dev_trib, "0.00")
    _cmp(tot_ibs.g_ibs_uf.v_ibs_uf, "0.00")
    _cmp(tot_ibs.g_ibs_mun.v_dif, "0.00")
    _cmp(tot_ibs.g_ibs_mun.v_dev_trib, "0.00")
    _cmp(tot_ibs.g_ibs_mun.v_ibs_mun, "0.00")
    _cmp(tot_ibs.v_ibs, "0.00")
    _cmp(tot_ibs.v_cred_pres, "0.00")
    _cmp(tot_ibs.v_cred_pres_cond_sus, "0.00")

    tot_cbs = tot.ibscbs_tot.g_cbs
    assert tot_cbs is not None
    _cmp(tot_cbs.v_dif, "0.00")
    _cmp(tot_cbs.v_dev_trib, "0.00")
    _cmp(tot_cbs.v_cbs, "0.00")
    _cmp(tot_cbs.v_cred_pres, "0.00")
    _cmp(tot_cbs.v_cred_pres_cond_sus, "0.00")

    mono = tot.ibscbs_tot.g_mono
    assert mono is not None
    _cmp(mono.v_ibs_mono, "0.00")
    _cmp(mono.v_cbs_mono, "0.00")
    _cmp(mono.v_ibs_mono_reten, "0.00")
    _cmp(mono.v_cbs_mono_reten, "0.00")
    _cmp(mono.v_ibs_mono_ret, "0.00")
    _cmp(mono.v_cbs_mono_ret, "0.00")