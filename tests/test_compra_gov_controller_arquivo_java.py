"""Paridade CompraGovControllerArquivoTest — CalculadoraService (sem MockMvc)."""

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

from calculadora_rtc_regime_regular.calculadora import CalculadoraService, CompraGovernamentalInput, OperacaoCalculadoraInput
from calculadora_rtc_regime_regular.observabilidade import operacao_from_json
from calculadora_rtc_regime_regular.roc import TipoEnteGovernamental

from test_calculos_corretos_java import _PY_JAVA_SEG, _shim_seletivo

_CACHE = Path(__file__).resolve().parents[1] / ".cache/oficial/java/src/test/resources"
_TESTES = "entradas/calculoscorretos/compras-governamentais/testes"

pytestmark = pytest.mark.skipif(not os.environ.get("CALC_DB"), reason="CALC_DB ausente")

_CAMPOS_EXCLUIDOS = frozenset({"memoriaCalculo", "calculoSimulado", "estadoItem"})

_EXTRA_PY_JAVA = {
    **_PY_JAVA_SEG,
    "p_aliq_ibs_uf": "pAliqIBSUF",
    "v_trib_ibs_uf": "vTribIBSUF",
    "p_aliq_ibs_mun": "pAliqIBSMun",
    "v_trib_ibs_mun": "vTribIBSMun",
    "p_aliq_cbs": "pAliqCBS",
    "v_trib_cbs": "vTribCBS",
}

_TP_OPER_VALID = frozenset(range(1, 6))

_SUCESSO = (
    ("cenario_01_uniao_input.json", "cenario_01_uniao_output_regime_geral.json"),
    ("cenario_02_estado_input.json", "cenario_02_estado_output_regime_geral.json"),
    ("cenario_03_distrito_federal_input.json", "cenario_03_distrito_federal_output_regime_geral.json"),
    ("cenario_04_municipio_input.json", "cenario_04_municipio_output_regime_geral.json"),
    ("cenario_05_consorcio_input.json", "cenario_05_consorcio_output_regime_geral.json"),
    ("cenario_06_comite_gestor_input.json", "cenario_06_comite_gestor_output_regime_geral.json"),
)

_FALHA = (
    "cenario_00_tipo_ente_invalido_input.json",
    "cenario_00_tipo_operacao_invalido_input.json",
)


def _surefire_calc_ids() -> list[str]:
    return [f"deveCalcularTributosCompraGovViaEndpoint(String, String)[{i}]" for i in range(1, 7)]


def _surefire_fail_ids() -> list[str]:
    return [f"deveFalharComValoresInvalidos(String)[{i}]" for i in range(1, 3)]


def _dec(value: object) -> Decimal:
    return Decimal(str(value))


def _py_seg_java(seg: str) -> str:
    if seg in ("IS", "IBSCBS", "CST", "CSTIS"):
        return seg
    return _EXTRA_PY_JAVA.get(seg, seg)


def _valor_json(v: Any) -> Any:
    if v is None:
        return None
    if isinstance(v, Decimal):
        s = format(v, "f")
        if "." in s:
            s = s.rstrip("0").rstrip(".") if "." in s else s
        return s if s else "0"
    if isinstance(v, TipoEnteGovernamental):
        return v.value
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


def assert_gabarito_compra_gov(obtido_root: Any, gabarito_rel: str) -> None:
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


def operacao_arquivo(nome: str) -> OperacaoCalculadoraInput:
    payload = json.loads((_CACHE / _TESTES / nome).read_text(encoding="utf-8"))
    g = payload.pop("gCompraGov", None)
    if g is not None:
        tp_ente = int(g["tpEnteGov"])
        tp_oper = g.get("tpOperGov")
        if tp_oper is not None and tp_oper not in _TP_OPER_VALID:
            raise ValueError(f"tpOperGov inválido: {tp_oper}")
        g_compra = CompraGovernamentalInput(
            tp_ente_gov=TipoEnteGovernamental(tp_ente),
            tp_oper_gov=tp_oper,
        )
    else:
        g_compra = None
    base = operacao_from_json(payload)
    if g_compra is not None:
        base.g_compra_gov = g_compra
    _shim_seletivo(base)
    return base


@pytest.fixture(scope="module")
def svc() -> CalculadoraService:
    return CalculadoraService(calculo_ibs_habilitado=True)


@pytest.mark.parametrize("par", _SUCESSO, ids=_surefire_calc_ids())
def test_deveCalcularTributosCompraGovViaEndpoint(par: tuple[str, str], svc: CalculadoraService) -> None:
    entrada, saida = par
    roc = svc.calcular_tributos(operacao_arquivo(entrada))
    assert_gabarito_compra_gov(roc, f"{_TESTES}/{saida}")


@pytest.mark.parametrize("arquivo", _FALHA, ids=_surefire_fail_ids())
def test_deveFalharComValoresInvalidos(arquivo: str) -> None:
    with pytest.raises(ValueError):
        operacao_arquivo(arquivo)