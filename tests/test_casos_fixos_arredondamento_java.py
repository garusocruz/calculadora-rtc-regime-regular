"""Casos fixos de arredondamento — espelho Teste_CasosFixosArredondamento (sem MockMvc)."""

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

from calculadora_rtc_regime_regular.arredondamento import formatar_aliquota, formatar_moeda
from calculadora_rtc_regime_regular.calculadora import ROCDomain
from calculadora_rtc_regime_regular.consumo import CalculadoraService
from calculadora_rtc_regime_regular.observabilidade import operacao_from_json
from calculadora_rtc_regime_regular.roc import ObjetoDomain

_CACHE = Path(__file__).resolve().parents[1] / ".cache/oficial/java/src/test/resources"

pytestmark = pytest.mark.skipif(not os.environ.get("CALC_DB"), reason="CALC_DB ausente")


def _load_json(nome: str) -> dict:
    return json.loads((_CACHE / "entradas/arredondamento" / f"{nome}.json").read_text(encoding="utf-8"))


def _moeda(valor: Decimal | None) -> str:
    assert valor is not None
    return formatar_moeda(valor)


def _aliq(valor: Decimal | None) -> str:
    assert valor is not None
    return formatar_aliquota(valor)


def _item(roc: ROCDomain, indice: int = 0) -> ObjetoDomain:
    assert roc.objetos
    return roc.objetos[indice]


def _tot(roc: ROCDomain):
    assert roc.total is not None
    assert roc.total.trib_calc is not None
    assert roc.total.trib_calc.ibscbs_tot is not None
    return roc.total.trib_calc.ibscbs_tot


@pytest.fixture(scope="module")
def svc() -> CalculadoraService:
    return CalculadoraService(calculo_ibs_habilitado=True)


def _calcular(svc: CalculadoraService, caso: str) -> ROCDomain:
    op = operacao_from_json(_load_json(caso))
    return svc.calcularTributos(op)


def test_t1EmpateParaOPar(svc: CalculadoraService) -> None:
    roc = _calcular(svc, "T1")
    item = _item(roc)
    grupo = item.get_grupo_ibscbs()
    assert grupo is not None
    cbs = item.get_g_cbs()
    uf = item.get_g_ibs_uf()
    assert cbs is not None and uf is not None
    assert _moeda(grupo.v_bc) == "25.00"
    assert _aliq(cbs.p_cbs) == "0.90"
    assert _moeda(cbs.v_cbs) == "0.22"
    assert _aliq(uf.p_ibs_uf) == "0.10"
    assert _moeda(uf.v_ibs_uf) == "0.02"
    assert _moeda(grupo.v_ibs) == "0.02"
    tot = _tot(roc)
    assert tot.g_cbs is not None and tot.g_ibs is not None
    assert _moeda(tot.g_cbs.v_cbs) == "0.22"
    assert _moeda(tot.g_ibs.v_ibs) == "0.02"


def test_t2VIbsSomaDasPartesPublicadas(svc: CalculadoraService) -> None:
    roc = _calcular(svc, "T2")
    item = _item(roc)
    grupo = item.get_grupo_ibscbs()
    uf = item.get_g_ibs_uf()
    mun = item.get_g_ibs_mun()
    cbs = item.get_g_cbs()
    assert grupo is not None and uf is not None and mun is not None and cbs is not None
    assert _moeda(uf.v_ibs_uf) == "0.01"
    assert _moeda(mun.v_ibs_mun) == "0.01"
    assert _moeda(grupo.v_ibs) == "0.02"
    assert _moeda(cbs.v_cbs) == "1.06"
    tot = _tot(roc)
    assert tot.g_ibs is not None and tot.g_cbs is not None
    assert tot.g_ibs.g_ibs_uf is not None and tot.g_ibs.g_ibs_mun is not None
    assert _moeda(tot.g_ibs.g_ibs_uf.v_ibs_uf) == "0.01"
    assert _moeda(tot.g_ibs.g_ibs_mun.v_ibs_mun) == "0.01"
    assert _moeda(tot.g_ibs.v_ibs) == "0.02"
    assert _moeda(tot.g_cbs.v_cbs) == "1.06"


def test_t3TotaisSomaDosItensPublicados(svc: CalculadoraService) -> None:
    roc = _calcular(svc, "T3")
    for indice in range(2):
        item = _item(roc, indice)
        grupo = item.get_grupo_ibscbs()
        uf = item.get_g_ibs_uf()
        cbs = item.get_g_cbs()
        assert grupo is not None and uf is not None and cbs is not None
        assert _moeda(cbs.v_cbs) == "0.13"
        assert _moeda(uf.v_ibs_uf) == "0.01"
        assert _moeda(grupo.v_ibs) == "0.01"
    tot = _tot(roc)
    assert tot.g_ibs is not None and tot.g_cbs is not None
    assert tot.g_ibs.g_ibs_uf is not None
    assert _moeda(tot.v_bc_ibscbs) == "28.00"
    assert _moeda(tot.g_cbs.v_cbs) == "0.26"
    assert _moeda(tot.g_ibs.g_ibs_uf.v_ibs_uf) == "0.02"
    assert _moeda(tot.g_ibs.v_ibs) == "0.02"


def test_t4ValorPelaAliquotaEfetivaPublicada(svc: CalculadoraService) -> None:
    roc = _calcular(svc, "T4")
    item = _item(roc)
    grupo = item.get_grupo_ibscbs()
    cbs = item.get_g_cbs()
    uf = item.get_g_ibs_uf()
    mun = item.get_g_ibs_mun()
    assert grupo is not None and cbs is not None and uf is not None and mun is not None
    assert cbs.g_red is not None and uf.g_red is not None and mun.g_red is not None
    assert _aliq(cbs.p_cbs) == "8.8123"
    assert _moeda(cbs.g_red.p_red_aliq) == "60.00"
    assert _aliq(cbs.g_red.p_aliq_efet) == "3.5249"
    assert _moeda(cbs.v_cbs) == "35249.00"
    assert _aliq(uf.g_red.p_aliq_efet) == "0.02"
    assert _moeda(uf.v_ibs_uf) == "200.00"
    assert _aliq(mun.g_red.p_aliq_efet) == "0.02"
    assert _moeda(mun.v_ibs_mun) == "200.00"
    assert _moeda(grupo.v_ibs) == "400.00"
    tot = _tot(roc)
    assert tot.g_cbs is not None and tot.g_ibs is not None
    assert _moeda(tot.g_cbs.v_cbs) == "35249.00"
    assert _moeda(tot.g_ibs.v_ibs) == "400.00"


def test_t5CompraDaUniao(svc: CalculadoraService) -> None:
    roc = _calcular(svc, "T5")
    assert roc.oper is not None and roc.oper.g_compra_gov is not None
    assert _moeda(roc.oper.g_compra_gov.p_redutor) == "0.00"
    item = _item(roc)
    grupo = item.get_grupo_ibscbs()
    cbs = item.get_g_cbs()
    uf = item.get_g_ibs_uf()
    mun = item.get_g_ibs_mun()
    assert grupo is not None and cbs is not None and uf is not None and mun is not None
    assert cbs.g_red is not None and uf.g_red is not None and mun.g_red is not None
    assert grupo.g_trib_compra_gov is not None
    compra = grupo.g_trib_compra_gov
    assert _aliq(cbs.p_cbs) == "8.80"
    assert _aliq(cbs.g_red.p_aliq_efet) == "8.90"
    assert _moeda(cbs.v_cbs) == "1.07"
    assert _aliq(uf.g_red.p_aliq_efet) == "0.00"
    assert _moeda(uf.v_ibs_uf) == "0.00"
    assert _aliq(mun.g_red.p_aliq_efet) == "0.00"
    assert _moeda(mun.v_ibs_mun) == "0.00"
    assert _moeda(grupo.v_ibs) == "0.00"
    assert _aliq(compra.p_aliq_cbs) == "8.80"
    assert _moeda(compra.v_trib_cbs) == "1.06"
    assert _aliq(compra.p_aliq_ibs_uf) == "0.05"
    assert _moeda(compra.v_trib_ibs_uf) == "0.01"
    assert _aliq(compra.p_aliq_ibs_mun) == "0.05"
    assert _moeda(compra.v_trib_ibs_mun) == "0.01"
    tot = _tot(roc)
    assert tot.g_cbs is not None
    assert _moeda(tot.g_cbs.v_cbs) == "1.07"


def test_issueTotalCbsSomaDosItens(svc: CalculadoraService) -> None:
    roc = _calcular(svc, "issue_total_cbs")
    for indice, v_cbs in ((0, "20.84"), (1, "6.21")):
        cbs = _item(roc, indice).get_g_cbs()
        assert cbs is not None
        assert _moeda(cbs.v_cbs) == v_cbs
    for indice, v_uf in ((0, "2.32"), (1, "0.69")):
        uf = _item(roc, indice).get_g_ibs_uf()
        assert uf is not None
        assert _moeda(uf.v_ibs_uf) == v_uf
    tot = _tot(roc)
    assert tot.g_ibs is not None and tot.g_cbs is not None
    assert tot.g_ibs.g_ibs_uf is not None
    assert _moeda(tot.v_bc_ibscbs) == "3006.31"
    assert _moeda(tot.g_cbs.v_cbs) == "27.05"
    assert _moeda(tot.g_ibs.g_ibs_uf.v_ibs_uf) == "3.01"
    assert _moeda(tot.g_ibs.v_ibs) == "3.01"