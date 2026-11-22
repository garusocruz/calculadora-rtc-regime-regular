"""Paridade com TesteRegressaoVariosItensComObservabilidade (gabarito JSON)."""

from __future__ import annotations

import copy
import json
import os
from dataclasses import fields, is_dataclass
from decimal import Decimal
from enum import Enum
from pathlib import Path
from typing import Any

import pytest

os.environ.setdefault(
    "CALC_DB",
    "/home/garusotec/projects/lynko/libs/calculadora-rtc-regime-regular/.cache/oficial/java/calculadora/db/calculadora-pro.db",
)

from calculadora_rtc_regime_regular.calculadora import ROCDomain
from calculadora_rtc_regime_regular.consumo import ObservabilidadeService
from calculadora_rtc_regime_regular.observabilidade import operacao_from_json
from calculadora_rtc_regime_regular.roc import ObjetoDomain

_CACHE = Path(__file__).resolve().parents[1] / ".cache/oficial/java/src/test/resources"
_BASE_URL = "http://localhost:8080"
_ENTRADA = "entradas/calculoscorretos/varios_itens/Teste_Varios_Itens.json"
_GABARITO = "saidas/Teste_Varios_Itens.json"

pytestmark = pytest.mark.skipif(not os.environ.get("CALC_DB"), reason="CALC_DB ausente")

_CAMPOS_EXCLUIDOS = frozenset({"memoriaCalculo", "calculoSimulado", "estadoItem"})

_PY_JAVA_SEG = {
    "n_obj": "nObj",
    "trib_calc": "tribCalc",
    "v_bc": "vBC",
    "g_ibs_uf": "gIBSUF",
    "g_ibs_mun": "gIBSMun",
    "g_cbs": "gCBS",
    "g_ibscbs": "gIBSCBS",
    "g_ibscbs_mono": "gIBSCBSMono",
    "g_trib_regular": "gTribRegular",
    "g_trib_compra_gov": "gTribCompraGov",
    "g_red": "gRed",
    "g_dif": "gDif",
    "p_dif": "pDif",
    "memoria_calculo": "memoriaCalculo",
    "calculo_simulado": "calculoSimulado",
    "estado_item": "estadoItem",
    "g_dev_trib": "gDevTrib",
    "p_cbs": "pCBS",
    "v_cbs": "vCBS",
    "p_ibs_uf": "pIBSUF",
    "v_ibs_uf": "vIBSUF",
    "p_ibs_mun": "pIBSMun",
    "v_ibs_mun": "vIBSMun",
    "v_ibs": "vIBS",
    "c_class_trib": "cClassTrib",
    "c_class_trib_is": "cClassTribIS",
    "c_class_trib_reg": "cClassTribReg",
    "cst_reg": "CSTReg",
    "v_bcis": "vBCIS",
    "p_is": "pIS",
    "p_is_espec": "pISEspec",
    "ad_rem_is": "adRemIS",
    "u_trib": "uTrib",
    "q_trib": "qTrib",
    "v_is": "vIS",
    "p_red_aliq": "pRedAliq",
    "p_aliq_efet": "pAliqEfet",
    "p_aliq_efet_reg_cbs": "pAliqEfetRegCBS",
    "v_trib_reg_cbs": "vTribRegCBS",
    "p_aliq_efet_reg_ibs_uf": "pAliqEfetRegIBSUF",
    "v_trib_reg_ibs_uf": "vTribRegIBSUF",
    "p_aliq_efet_reg_ibs_mun": "pAliqEfetRegIBSMun",
    "v_trib_reg_ibs_mun": "vTribRegIBSMun",
    "v_bc_ibscbs": "vBCIBSCBS",
    "is_tot": "ISTot",
    "ibscbs_tot": "IBSCBSTot",
    "g_ibs": "gIBS",
    "g_mono": "gMono",
    "g_estorno_cred": "gEstornoCred",
    "v_dif": "vDif",
    "v_dev_trib": "vDevTrib",
    "v_cred_pres": "vCredPres",
    "v_cred_pres_cond_sus": "vCredPresCondSus",
    "v_ibs_mono": "vIBSMono",
    "v_cbs_mono": "vCBSMono",
    "v_ibs_mono_reten": "vIBSMonoReten",
    "v_cbs_mono_reten": "vCBSMonoReten",
    "v_ibs_mono_ret": "vIBSMonoRet",
    "v_cbs_mono_ret": "vCBSMonoRet",
    "g_mono_padrao": "gMonoPadrao",
    "q_bc_mono": "qBCMono",
    "ad_rem_cbs": "adRemCBS",
    "v_ibs_mono_dif": "vIBSMonoDif",
    "oper": "oper",
    "total": "total",
    "objetos": "objetos",
    "g_compra_gov": "gCompraGov",
    "tp_ente_gov": "tpEnteGov",
    "tp_oper_gov": "tpOperGov",
    "p_redutor": "pRedutor",
}


def _py_seg_java(seg: str) -> str:
    if seg in ("IS", "IBSCBS", "CST", "CSTIS"):
        return seg
    return _PY_JAVA_SEG.get(seg, seg)


def _dec(value: object) -> Decimal:
    return Decimal(str(value))


def _valor_json(v: Any) -> Any:
    if v is None:
        return None
    if isinstance(v, Decimal):
        s = format(v, "f")
        if "." in s:
            s = s.rstrip("0").rstrip(".") if "." in s else s
        return s if s else "0"
    if isinstance(v, Enum):
        return v.name if hasattr(v, "name") else str(v.value)
    if isinstance(v, bool):
        return v
    if isinstance(v, (int, str)):
        return v
    return v


def _roc_para_json(obj: Any) -> Any:
    if obj is None:
        return None
    if isinstance(obj, (str, int, bool, float)):
        return obj
    if isinstance(obj, Decimal):
        return _valor_json(obj)
    if isinstance(obj, Enum):
        return _valor_json(obj)
    if isinstance(obj, list):
        return [_roc_para_json(x) for x in obj]
    if is_dataclass(obj):
        out: dict[str, Any] = {}
        for f in fields(obj):
            val = getattr(obj, f.name)
            if val is None:
                continue
            py_key = f.name
            if py_key == "calculo_simulado" and val is False:
                continue
            java_key = _py_seg_java(py_key)
            if is_dataclass(val) or isinstance(val, list):
                serialized = _roc_para_json(val)
                if serialized is None or serialized == {} or serialized == []:
                    continue
                out[java_key] = serialized
            else:
                out[java_key] = _roc_para_json(val)
        return out if out else None
    if isinstance(obj, dict):
        return {k: _roc_para_json(v) for k, v in obj.items()}
    return obj


def _remover_excluidos(node: Any) -> None:
    if isinstance(node, dict):
        for k in list(node.keys()):
            if k in _CAMPOS_EXCLUIDOS:
                del node[k]
            else:
                _remover_excluidos(node[k])
    elif isinstance(node, list):
        for el in node:
            _remover_excluidos(el)


def _flatten(path: str, node: Any, out: dict[str, str]) -> None:
    if isinstance(node, dict):
        for k, v in node.items():
            _flatten(f"{path}.{k}" if path != "$" else f"$.{k}", v, out)
    elif isinstance(node, list):
        for i, el in enumerate(node):
            _flatten(f"{path}[{i}]", el, out)
    else:
        out[path] = str(node)


def _shim_seletivo(operacao) -> None:
    for item in operacao.itens:
        seletivo = item.imposto_seletivo
        if seletivo is not None and not hasattr(seletivo, "valor_informado"):
            seletivo.valor_informado = seletivo.imposto_informado  # type: ignore[attr-defined]


def _assert_gabarito(obtido_root: Any, gabarito_rel: str) -> None:
    esperado = copy.deepcopy(json.loads((_CACHE / gabarito_rel).read_text(encoding="utf-8")))
    obtido = _roc_para_json(obtido_root)
    _remover_excluidos(esperado)
    _remover_excluidos(obtido)
    flat_e: dict[str, str] = {}
    flat_o: dict[str, str] = {}
    _flatten("$", esperado, flat_e)
    _flatten("$", obtido, flat_o)
    diffs: list[str] = []
    for path, ev in flat_e.items():
        if path not in flat_o:
            diffs.append(f"{path}: ausente no obtido (esperado {ev})")
            continue
        os_ = flat_o[path]
        try:
            if _dec(os_).compare(_dec(ev)) != 0:
                diffs.append(f"{path}: esperado {ev}, obtido {os_}")
        except Exception:
            if str(os_) != str(ev):
                diffs.append(f"{path}: esperado {ev}, obtido {os_}")
    for path in flat_o:
        if path not in flat_e:
            diffs.append(f"{path}: inesperado {flat_o[path]}")
    assert not diffs, "Diferenças:\n" + "\n".join(diffs[:50])


def test_testRegressaoCalculoVariosItens() -> None:
    entrada = json.loads((_CACHE / _ENTRADA).read_text(encoding="utf-8"))
    operacao = operacao_from_json(entrada)
    _shim_seletivo(operacao)
    roc_obs = ObservabilidadeService().processarOperacao(operacao, _BASE_URL)
    adapter = ROCDomain(
        oper=roc_obs.oper,
        objetos=[ObjetoDomain(n_obj=o.n_obj, trib_calc=o.trib_calc) for o in roc_obs.objetos],
        total=roc_obs.total,
    )
    _assert_gabarito(adapter, _GABARITO)