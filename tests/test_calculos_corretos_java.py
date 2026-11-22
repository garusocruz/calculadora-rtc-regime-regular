"""Casos dourados Java → serviço Python (pin f1eebd7). Sem MockMvc."""

from __future__ import annotations

import copy
import json
import os
import re
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

from calculadora_rtc_regime_regular.coletor import ErrosCalculoException
from calculadora_rtc_regime_regular.processamento_item import AliquotasNominaisNaoInformadasException
from calculadora_rtc_regime_regular.consumo import CalculadoraService, ObservabilidadeService
from calculadora_rtc_regime_regular.observabilidade import ObservabilidadeROCDomain, operacao_from_json
from calculadora_rtc_regime_regular.calculadora import OperacaoCalculadoraInput, ROCDomain
from dataclasses import replace

_CACHE = Path(__file__).resolve().parents[1] / ".cache/oficial/java/src/test/resources"
_BASE_URL = "http://localhost:8080"

pytestmark = pytest.mark.skipif(not os.environ.get("CALC_DB"), reason="CALC_DB ausente")


def _java(record_xml_attribute, fqcn: str, method: str) -> None:
    record_xml_attribute("classname", fqcn)
    record_xml_attribute("name", method)


def _dec(value: object) -> Decimal:
    return Decimal(str(value))


def _cmp(actual: object, expected: str | Decimal) -> None:
    assert _dec(actual).compare(_dec(expected)) == 0


def _load_json(rel: str) -> dict:
    return json.loads((_CACHE / rel).read_text(encoding="utf-8"))


def _shim_seletivo(operacao) -> None:
    for item in operacao.itens:
        seletivo = item.imposto_seletivo
        if seletivo is not None and not hasattr(seletivo, "valor_informado"):
            seletivo.valor_informado = seletivo.imposto_informado  # type: ignore[attr-defined]


def _operacao(rel: str) -> OperacaoCalculadoraInput:
    op = operacao_from_json(_load_json(rel))
    _shim_seletivo(op)
    return op


@pytest.fixture(scope="module")
def svc() -> CalculadoraService:
    """Espelha ``application-testes.yml`` → ``application.ibs.enabled: true``."""
    return CalculadoraService(calculo_ibs_habilitado=True)


def _roc(svc: CalculadoraService, rel: str) -> ROCDomain:
    return svc.calcularTributos(_operacao(rel))


def _item0(roc: ROCDomain):
    assert roc.objetos
    return roc.objetos[0]


def _assert_cbs(item, *, p: str, v: str) -> None:
    cbs = item.get_g_cbs()
    assert cbs is not None
    _cmp(cbs.p_cbs, p)
    _cmp(cbs.v_cbs, v)


def _assert_ibs_uf(item, *, p: str, v: str) -> None:
    uf = item.get_g_ibs_uf()
    assert uf is not None
    _cmp(uf.p_ibs_uf, p)
    _cmp(uf.v_ibs_uf, v)


def _assert_ibs_mun(item, *, p: str, v: str) -> None:
    mun = item.get_g_ibs_mun()
    assert mun is not None
    _cmp(mun.p_ibs_mun, p)
    _cmp(mun.v_ibs_mun, v)


def _assert_is(item, **kwargs: str) -> None:
    is_ = item.get_imposto_seletivo()
    assert is_ is not None
    mapping = {
        "vBCIS": "v_bcis",
        "pIS": "p_is",
        "pISEspec": "p_is_espec",
        "qTrib": "q_trib",
        "vIS": "v_is",
    }
    for jk, py in mapping.items():
        if jk in kwargs:
            val = kwargs[jk]
            if val == "__NULL__":
                assert getattr(is_, py, None) is None
            else:
                _cmp(getattr(is_, py), val)


def _assert_trib_reg(
    item,
    *,
    cbs_p: str,
    cbs_v: str,
    uf_p: str,
    uf_v: str,
    mun_p: str,
    mun_v: str,
) -> None:
    assert item.possui_tributacao_regular()
    tr = item.get_tributacao_regular()
    assert tr is not None
    _cmp(tr.p_aliq_efet_reg_cbs, cbs_p)
    _cmp(tr.v_trib_reg_cbs, cbs_v)
    _cmp(tr.p_aliq_efet_reg_ibs_uf, uf_p)
    _cmp(tr.v_trib_reg_ibs_uf, uf_v)
    _cmp(tr.p_aliq_efet_reg_ibs_mun, mun_p)
    _cmp(tr.v_trib_reg_ibs_mun, mun_v)


def _assert_red(grp, *, p_red: str, p_efet: str) -> None:
    assert grp is not None
    _cmp(grp.p_red_aliq, p_red)
    _cmp(grp.p_aliq_efet, p_efet)


def _assert_suspensao_grupo(item) -> None:
    cbs = item.get_g_cbs()
    uf = item.get_g_ibs_uf()
    mun = item.get_g_ibs_mun()
    assert cbs is not None and uf is not None and mun is not None
    _cmp(cbs.p_cbs, "0.00")
    _cmp(cbs.v_cbs, "0")
    assert cbs.g_red is None
    _cmp(uf.p_ibs_uf, "0.00")
    _cmp(uf.v_ibs_uf, "0")
    assert uf.g_red is None
    _cmp(mun.p_ibs_mun, "0.00")
    _cmp(mun.v_ibs_mun, "0")
    assert mun.g_red is None


# ─── Regressão JSON (gabarito Java) ───────────────────────────────────────────

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
            if isinstance(val, Decimal) and val == 0 and f.name.startswith(("v_", "p_")):
                pass
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


def _get_by_java_path(root: Any, path: str) -> Any:
    cur = root
    rest = path[2:] if path.startswith("$.") else path
    for part in re.split(r"\.(?![^\[]*\])", rest):
        if not part:
            continue
        m = re.match(r"([^[]+)(?:\[(\d+)\])?", part)
        if not m:
            raise KeyError(path)
        name, idx = m.group(1), m.group(2)
        py = None
        for f in fields(cur) if is_dataclass(cur) else []:
            if _py_seg_java(f.name) == name or f.name == name:
                py = f.name
                break
        if py is None:
            if name in ("IS", "IBSCBS") and is_dataclass(cur):
                py = name
            elif hasattr(cur, name):
                py = name
            else:
                rev = {v: k for k, v in _PY_JAVA_SEG.items()}
                py = rev.get(name)
        if py is None:
            raise KeyError(f"{path} ({name})")
        cur = getattr(cur, py)
        if idx is not None:
            cur = cur[int(idx)]
    return cur


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


# ─── cclasstrib_000001 ───────────────────────────────────────────────────────

_FQCN_000001 = "br.gov.serpro.rtc.testesintegracao.calculoscorretos.cbsibs.cclasstrib_000001"


def test_000001_1_testCalcularTributos(record_xml_attribute, svc: CalculadoraService) -> None:
    _java(record_xml_attribute, f"{_FQCN_000001}.Teste_000001_1", "testCalcularTributos")
    item = _item0(_roc(svc, "entradas/calculoscorretos/Teste_000001_1.json"))
    _cmp(item.get_valor_base_calculo_ibscbs(), "200.00")
    _assert_cbs(item, p="0.90", v="1.80")
    _assert_ibs_uf(item, p="0.10", v="0.20")
    _assert_ibs_mun(item, p="0", v="0")


def test_000001_2_testCalcularTributos(record_xml_attribute, svc: CalculadoraService) -> None:
    _java(record_xml_attribute, f"{_FQCN_000001}.Teste_000001_2", "testCalcularTributos")
    item = _item0(_roc(svc, "entradas/calculoscorretos/Teste_000001_2.json"))
    _cmp(item.get_valor_base_calculo_ibscbs(), "247.30")
    _assert_cbs(item, p="8.40", v="20.77")
    _assert_ibs_uf(item, p="0.05", v="0.12")
    _assert_ibs_mun(item, p="0.05", v="0.12")
    _assert_is(item, vBCIS="200.00", pIS="13.00", pISEspec="21.30", vIS="47.30")


def test_000001_3_testCalcularTributos(record_xml_attribute, svc: CalculadoraService) -> None:
    _java(record_xml_attribute, f"{_FQCN_000001}.Teste_000001_3", "testCalcularTributos")
    item = _item0(_roc(svc, "entradas/calculoscorretos/Teste_000001_3.json"))
    _cmp(item.get_valor_base_calculo_ibscbs(), "200.00")
    _assert_suspensao_grupo(item)
    _assert_trib_reg(item, cbs_p="0.90", cbs_v="1.80", uf_p="0.10", uf_v="0.20", mun_p="0.00", mun_v="0.00")


def test_000001_4_testCalcularTributos(record_xml_attribute, svc: CalculadoraService) -> None:
    _java(record_xml_attribute, f"{_FQCN_000001}.Teste_000001_4", "testCalcularTributos")
    item = _item0(_roc(svc, "entradas/calculoscorretos/Teste_000001_4.json"))
    _cmp(item.get_valor_base_calculo_ibscbs(), "247.30")
    _assert_suspensao_grupo(item)
    _assert_is(item, vBCIS="200.00", pIS="13.00", pISEspec="21.30", vIS="47.30")
    _assert_trib_reg(item, cbs_p="8.40", cbs_v="20.77", uf_p="0.05", uf_v="0.12", mun_p="0.05", mun_v="0.12")


def test_000001_5_testCalcularTributos(record_xml_attribute, svc: CalculadoraService) -> None:
    _java(record_xml_attribute, f"{_FQCN_000001}.Teste_000001_5", "testCalcularTributos")
    item = _item0(_roc(svc, "entradas/calculoscorretos/Teste_000001_5.json"))
    _cmp(item.get_valor_base_calculo_ibscbs(), "200.00")
    _assert_cbs(item, p="8.40", v="16.80")
    _assert_ibs_uf(item, p="0.05", v="0.10")
    _assert_ibs_mun(item, p="0.05", v="0.10")


def test_000001_6_testCalcularTributos(record_xml_attribute, svc: CalculadoraService) -> None:
    _java(record_xml_attribute, f"{_FQCN_000001}.Teste_000001_6", "testCalcularTributos")
    item = _item0(_roc(svc, "entradas/calculoscorretos/Teste_000001_6.json"))
    _cmp(item.get_valor_base_calculo_ibscbs(), "210.54")
    _assert_cbs(item, p="8.40", v="17.69")
    _assert_ibs_uf(item, p="0.05", v="0.11")
    _assert_ibs_mun(item, p="0.05", v="0.11")
    _assert_is(item, vBCIS="200.00", pIS="5.27", pISEspec="__NULL__", vIS="10.54")


def test_000001_7_testCalcularTributos(record_xml_attribute, svc: CalculadoraService) -> None:
    _java(record_xml_attribute, f"{_FQCN_000001}.Teste_000001_7", "testCalcularTributos")
    item = _item0(_roc(svc, "entradas/calculoscorretos/Teste_000001_7.json"))
    _cmp(item.get_valor_base_calculo_ibscbs(), "200.00")
    _assert_suspensao_grupo(item)
    _assert_trib_reg(item, cbs_p="8.40", cbs_v="16.80", uf_p="0.05", uf_v="0.10", mun_p="0.05", mun_v="0.10")
    assert item.get_imposto_seletivo() is None


def test_000001_8_testCalcularTributos(record_xml_attribute, svc: CalculadoraService) -> None:
    _java(record_xml_attribute, f"{_FQCN_000001}.Teste_000001_8", "testCalcularTributos")
    item = _item0(_roc(svc, "entradas/calculoscorretos/Teste_000001_8.json"))
    _cmp(item.get_valor_base_calculo_ibscbs(), "210.54")
    _assert_suspensao_grupo(item)
    _assert_trib_reg(item, cbs_p="8.40", cbs_v="17.69", uf_p="0.05", uf_v="0.11", mun_p="0.05", mun_v="0.11")
    _assert_is(item, vBCIS="200.00", pIS="5.27", pISEspec="__NULL__", vIS="10.54")


@pytest.fixture(scope="module")
def operacao_000001_2(svc: CalculadoraService) -> OperacaoCalculadoraInput:
    return _operacao("entradas/calculoscorretos/Teste_000001_2.json")


def _base_ibs_cbs(svc: CalculadoraService, op: OperacaoCalculadoraInput) -> Decimal:
    roc = svc.calcularTributos(op)
    return _item0(roc).get_valor_base_calculo_ibscbs()


def test_000001_9_testEntradaConsistente(record_xml_attribute, svc, operacao_000001_2) -> None:
    _java(record_xml_attribute, f"{_FQCN_000001}.Teste_000001_9", "testEntradaConsistente")
    item = operacao_000001_2.itens[0]
    item.base_calculo = Decimal("200")
    item.imposto_seletivo.base_calculo = Decimal("188")
    item.imposto_seletivo.imposto_informado = Decimal("12")
    _cmp(_base_ibs_cbs(svc, operacao_000001_2), "233.74")


def test_000001_9_testBaseCalculoDerivadaComImpostoInformado(record_xml_attribute, svc, operacao_000001_2) -> None:
    _java(record_xml_attribute, f"{_FQCN_000001}.Teste_000001_9", "testBaseCalculoDerivadaComImpostoInformado")
    item = operacao_000001_2.itens[0]
    item.base_calculo = None
    item.imposto_seletivo.base_calculo = Decimal("188")
    item.imposto_seletivo.imposto_informado = Decimal("12")
    _cmp(_base_ibs_cbs(svc, operacao_000001_2), "233.74")


def test_000001_9_testBaseCalculoDerivadaSemImpostoInformado(record_xml_attribute, svc, operacao_000001_2) -> None:
    _java(record_xml_attribute, f"{_FQCN_000001}.Teste_000001_9", "testBaseCalculoDerivadaSemImpostoInformado")
    item = operacao_000001_2.itens[0]
    item.base_calculo = None
    item.imposto_seletivo.base_calculo = Decimal("188")
    item.imposto_seletivo.imposto_informado = None
    _cmp(_base_ibs_cbs(svc, operacao_000001_2), "233.74")


def test_000001_9_testBaseCalculoMaiorSemImpostoInformado(record_xml_attribute, svc, operacao_000001_2) -> None:
    _java(record_xml_attribute, f"{_FQCN_000001}.Teste_000001_9", "testBaseCalculoMaiorSemImpostoInformado")
    item = operacao_000001_2.itens[0]
    item.base_calculo = Decimal("200")
    item.imposto_seletivo.base_calculo = Decimal("188")
    item.imposto_seletivo.imposto_informado = None
    _cmp(_base_ibs_cbs(svc, operacao_000001_2), "245.74")


def test_000001_9_testBaseCalculoIgualBaseCalculoIsSemImpostoInformado(record_xml_attribute, svc, operacao_000001_2) -> None:
    _java(record_xml_attribute, f"{_FQCN_000001}.Teste_000001_9", "testBaseCalculoIgualBaseCalculoIsSemImpostoInformado")
    item = operacao_000001_2.itens[0]
    item.base_calculo = Decimal("188")
    item.imposto_seletivo.base_calculo = Decimal("188")
    item.imposto_seletivo.imposto_informado = None
    _cmp(_base_ibs_cbs(svc, operacao_000001_2), "233.74")


def test_000001_9_testImpostoInformadoZero(record_xml_attribute, svc, operacao_000001_2) -> None:
    _java(record_xml_attribute, f"{_FQCN_000001}.Teste_000001_9", "testImpostoInformadoZero")
    item = operacao_000001_2.itens[0]
    item.base_calculo = Decimal("188")
    item.imposto_seletivo.base_calculo = Decimal("188")
    item.imposto_seletivo.imposto_informado = Decimal("0")
    _cmp(_base_ibs_cbs(svc, operacao_000001_2), "233.74")


def test_000001_9_testValoresComCasasDecimais(record_xml_attribute, svc, operacao_000001_2) -> None:
    _java(record_xml_attribute, f"{_FQCN_000001}.Teste_000001_9", "testValoresComCasasDecimais")
    item = operacao_000001_2.itens[0]
    item.base_calculo = Decimal("200.50")
    item.imposto_seletivo.base_calculo = Decimal("188.25")
    item.imposto_seletivo.imposto_informado = Decimal("12.25")
    _cmp(_base_ibs_cbs(svc, operacao_000001_2), "234.02")


def test_000001_9_testItemSemImpostoSeletivoComBaseCalculo(record_xml_attribute, svc) -> None:
    _java(record_xml_attribute, f"{_FQCN_000001}.Teste_000001_9", "testItemSemImpostoSeletivoComBaseCalculo")
    op = _operacao("entradas/calculoscorretos/Teste_000001_1.json")
    _cmp(_base_ibs_cbs(svc, op), "200.00")


def test_000001_Equivalencia_deveCalcularComAliquotasNominaisInformadasEm2027(
    record_xml_attribute, svc: CalculadoraService
) -> None:
    _java(
        record_xml_attribute,
        f"{_FQCN_000001}.Teste_000001_EquivalenciaAliquotasNominais",
        "deveCalcularComAliquotasNominaisInformadasEm2027",
    )
    roc = _roc(svc, "entradas/calculoscorretos/Teste_000001_2.json")
    assert roc is not None


def test_000001_Equivalencia_deveCriticarAusenciaDeAliquotasNominaisEm2027(record_xml_attribute, svc) -> None:
    _java(
        record_xml_attribute,
        f"{_FQCN_000001}.Teste_000001_EquivalenciaAliquotasNominais",
        "deveCriticarAusenciaDeAliquotasNominaisEm2027",
    )
    op = _operacao("entradas/calculoscorretos/Teste_000001_2.json")
    op.itens[0] = replace(op.itens[0], aliquotas_nominais=None)
    with pytest.raises(AliquotasNominaisNaoInformadasException):
        svc.calcularTributos(op)


def test_000001_Equivalencia_deveCriticarPreenchimentoParcialDeAliquotasNominaisEm2027(record_xml_attribute, svc) -> None:
    _java(
        record_xml_attribute,
        f"{_FQCN_000001}.Teste_000001_EquivalenciaAliquotasNominais",
        "deveCriticarPreenchimentoParcialDeAliquotasNominaisEm2027",
    )
    op = _operacao("entradas/calculoscorretos/Teste_000001_2.json")
    an = op.itens[0].aliquotas_nominais
    assert an is not None
    op.itens[0] = replace(op.itens[0], aliquotas_nominais=replace(an, ibs_estadual=None, ibs_municipal=None))
    with pytest.raises(AliquotasNominaisNaoInformadasException):
        svc.calcularTributos(op)


# ─── cclasstrib_011002 / 200002 / 200032 / 510002 / 620001 ───────────────────


def test_011002_1_testCalcularTributos(record_xml_attribute, svc) -> None:
    fqcn = "br.gov.serpro.rtc.testesintegracao.calculoscorretos.cbsibs.cclasstrib_011002.Teste_011002_1"
    _java(record_xml_attribute, fqcn, "testCalcularTributos")
    item = _item0(_roc(svc, "entradas/calculoscorretos/Teste_011002_1.json"))
    _cmp(item.get_valor_base_calculo_ibscbs(), "200.00")
    _assert_cbs(item, p="0.90", v="0.72")
    _assert_red(item.get_g_cbs().g_red, p_red="60", p_efet="0.36")
    _assert_ibs_uf(item, p="0.10", v="0.08")
    _assert_red(item.get_g_ibs_uf().g_red, p_red="60", p_efet="0.04")
    _assert_ibs_mun(item, p="0", v="0")
    _assert_red(item.get_g_ibs_mun().g_red, p_red="60", p_efet="0.00")
    assert item.get_tributacao_regular() is None
    assert item.get_imposto_seletivo() is None


_FQCN_200002 = "br.gov.serpro.rtc.testesintegracao.calculoscorretos.cbsibs.cclasstrib_200002"


def test_200002_1_testCalcularTributos(record_xml_attribute, svc) -> None:
    _java(record_xml_attribute, f"{_FQCN_200002}.Teste_200002_1", "testCalcularTributos")
    item = _item0(_roc(svc, "entradas/calculoscorretos/Teste_200002_1.json"))
    _cmp(item.get_valor_base_calculo_ibscbs(), "200.00")
    _assert_cbs(item, p="0.90", v="0")
    _assert_ibs_uf(item, p="0.10", v="0")
    _assert_ibs_mun(item, p="0", v="0")
    assert item.get_imposto_seletivo() is None
    assert item.get_tributacao_regular() is None


def test_200002_2_testCalcularTributos(record_xml_attribute, svc) -> None:
    _java(record_xml_attribute, f"{_FQCN_200002}.Teste_200002_2", "testCalcularTributos")
    item = _item0(_roc(svc, "entradas/calculoscorretos/Teste_200002_2.json"))
    _cmp(item.get_valor_base_calculo_ibscbs(), "247.30")
    _assert_cbs(item, p="8.40", v="0")
    _assert_ibs_uf(item, p="0.05", v="0")
    _assert_ibs_mun(item, p="0.05", v="0")
    _assert_is(item, vBCIS="200.00", pIS="13.00", pISEspec="21.30", vIS="47.30")
    assert item.get_tributacao_regular() is None


def test_200002_3_testCalcularTributos(record_xml_attribute, svc) -> None:
    _java(record_xml_attribute, f"{_FQCN_200002}.Teste_200002_3", "testCalcularTributos")
    item = _item0(_roc(svc, "entradas/calculoscorretos/Teste_200002_3.json"))
    _cmp(item.get_valor_base_calculo_ibscbs(), "200.00")
    _assert_suspensao_grupo(item)
    _assert_trib_reg(item, cbs_p="0", cbs_v="0", uf_p="0", uf_v="0", mun_p="0", mun_v="0")
    assert item.get_imposto_seletivo() is None


def test_200002_4_testCalcularTributos(record_xml_attribute, svc) -> None:
    _java(record_xml_attribute, f"{_FQCN_200002}.Teste_200002_4", "testCalcularTributos")
    item = _item0(_roc(svc, "entradas/calculoscorretos/Teste_200002_4.json"))
    _cmp(item.get_valor_base_calculo_ibscbs(), "247.30")
    _assert_suspensao_grupo(item)
    _assert_trib_reg(item, cbs_p="0", cbs_v="0", uf_p="0", uf_v="0", mun_p="0", mun_v="0")
    _assert_is(item, vBCIS="200.00", pIS="13.00", pISEspec="21.30", vIS="47.30")


_FQCN_200032 = "br.gov.serpro.rtc.testesintegracao.calculoscorretos.cbsibs.cclasstrib_200032"


def test_200032_1_testCalcularTributos(record_xml_attribute, svc) -> None:
    _java(record_xml_attribute, f"{_FQCN_200032}.Teste_200032_1", "testCalcularTributos")
    item = _item0(_roc(svc, "entradas/calculoscorretos/Teste_200032_1.json"))
    _cmp(item.get_valor_base_calculo_ibscbs(), "200.00")
    _assert_cbs(item, p="0.90", v="0.72")
    _assert_red(item.get_g_cbs().g_red, p_red="60", p_efet="0.36")
    _assert_ibs_uf(item, p="0.10", v="0.08")
    _assert_red(item.get_g_ibs_uf().g_red, p_red="60", p_efet="0.04")
    _assert_ibs_mun(item, p="0", v="0")
    _assert_red(item.get_g_ibs_mun().g_red, p_red="60", p_efet="0.00")
    assert item.get_imposto_seletivo() is None
    assert item.get_tributacao_regular() is None


def test_200032_2_testCalcularTributos(record_xml_attribute, svc) -> None:
    _java(record_xml_attribute, f"{_FQCN_200032}.Teste_200032_2", "testCalcularTributos")
    item = _item0(_roc(svc, "entradas/calculoscorretos/Teste_200032_2.json"))
    _cmp(item.get_valor_base_calculo_ibscbs(), "247.30")
    _assert_cbs(item, p="8.40", v="8.31")
    _assert_red(item.get_g_cbs().g_red, p_red="60", p_efet="3.36")
    _assert_ibs_uf(item, p="0.05", v="0.05")
    _assert_red(item.get_g_ibs_uf().g_red, p_red="60", p_efet="0.02")
    _assert_ibs_mun(item, p="0.05", v="0.05")
    _assert_red(item.get_g_ibs_mun().g_red, p_red="60", p_efet="0.02")
    _assert_is(item, vBCIS="200", pIS="13.00", pISEspec="21.30", vIS="47.30")
    assert item.get_tributacao_regular() is None


def test_200032_3_testCalcularTributos(record_xml_attribute, svc) -> None:
    _java(record_xml_attribute, f"{_FQCN_200032}.Teste_200032_3", "testCalcularTributos")
    item = _item0(_roc(svc, "entradas/calculoscorretos/Teste_200032_3.json"))
    _cmp(item.get_valor_base_calculo_ibscbs(), "200.00")
    _assert_suspensao_grupo(item)
    _assert_trib_reg(item, cbs_p="0.36", cbs_v="0.72", uf_p="0.04", uf_v="0.08", mun_p="0.00", mun_v="0.00")
    assert item.get_imposto_seletivo() is None


def test_200032_4_testCalcularTributos(record_xml_attribute, svc) -> None:
    _java(record_xml_attribute, f"{_FQCN_200032}.Teste_200032_4", "testCalcularTributos")
    item = _item0(_roc(svc, "entradas/calculoscorretos/Teste_200032_4.json"))
    _cmp(item.get_valor_base_calculo_ibscbs(), "247.30")
    _assert_suspensao_grupo(item)
    _assert_trib_reg(item, cbs_p="3.36", cbs_v="8.31", uf_p="0.02", uf_v="0.05", mun_p="0.02", mun_v="0.05")
    _assert_is(item, vBCIS="200.00", pIS="13.00", pISEspec="21.30", vIS="47.30")


def test_510002_1_testCalcularTributos(record_xml_attribute, svc) -> None:
    pytest.skip("CLTR 510002 ausente no calculadora-pro.db (Java @Disabled)")
    fqcn = "br.gov.serpro.rtc.testesintegracao.calculoscorretos.cbsibs.cclasstrib_510002.Teste_510002_1"
    _java(record_xml_attribute, fqcn, "testCalcularTributos(Resource)")
    item = _item0(_roc(svc, "entradas/calculoscorretos/Teste_510002_1.json"))
    _cmp(item.get_valor_base_calculo_ibscbs(), "200.00")
    cbs = item.get_g_cbs()
    _cmp(cbs.p_cbs, "0.9")
    _cmp(cbs.v_cbs, "0")
    _assert_red(cbs.g_red, p_red="60", p_efet="0.36")
    uf = item.get_g_ibs_uf()
    _cmp(uf.p_ibs_uf, "0.10")
    _cmp(uf.v_ibs_uf, "0")
    _assert_red(uf.g_red, p_red="60", p_efet="0.04")
    mun = item.get_g_ibs_mun()
    _cmp(mun.p_ibs_mun, "0")
    _cmp(mun.v_ibs_mun, "0")
    _assert_red(mun.g_red, p_red="60", p_efet="0.00")
    assert item.get_tributacao_regular() is None
    assert item.get_imposto_seletivo() is None


def test_620001_1_testCalcularTributos(record_xml_attribute, svc) -> None:
    pytest.skip("620001 exige tratamento com ajuste — Java @Disabled")
    fqcn = "br.gov.serpro.rtc.testesintegracao.calculoscorretos.cbsibs.cclasstrib_620001.Teste_620001_1"
    _java(record_xml_attribute, fqcn, "testCalcularTributos(Resource)")
    item = _item0(_roc(svc, "entradas/calculoscorretos/Teste_620001_1.json"))
    assert not item.possui_base_calculo_ibscbs()
    assert not item.possui_imposto_seletivo()
    assert not item.possui_cbs()
    assert not item.possui_ibs_uf()
    assert not item.possui_ibs_mun()
    assert not item.possui_tributacao_regular()
    assert item.possui_monofasia()
    mono = item.get_g_ibscbs_mono()
    assert mono is not None
    pad = mono.g_mono_padrao
    assert pad is not None
    _cmp(pad.q_bc_mono, "10")
    _cmp(pad.ad_rem_cbs, "1.47")
    _cmp(pad.v_cbs_mono, "14.70")
    _cmp(mono.get_v_ibs_mono(), "14.7")
    assert mono.g_mono_reten is None
    assert mono.g_mono_ret is None
    assert mono.g_mono_dif is None


def test_totais_1_testCalcularTributos(record_xml_attribute, svc) -> None:
    pytest.skip("Teste_totais_1 @Disabled no Java (cClassTrib 000000)")
    fqcn = "br.gov.serpro.rtc.testesintegracao.calculoscorretos.totais.Teste_totais_1"
    _java(record_xml_attribute, fqcn, "testCalcularTributos(Resource)")
    roc = _roc(svc, "entradas/calculoscorretos/totais/Teste_totais_1.json")
    tot = roc.total.trib_calc
    assert tot is not None
    _cmp(tot.is_tot.v_is, "47.30")
    ibs = tot.ibscbs_tot
    _cmp(ibs.v_bc_ibscbs, "647.30")
    _cmp(ibs.g_cbs.v_dev_trib, "0.00")
    _cmp(ibs.g_cbs.v_dif, "6.72")
    _cmp(ibs.g_cbs.v_cbs, "37.57")
    _cmp(ibs.g_cbs.v_cred_pres, "0.00")
    _cmp(ibs.g_cbs.v_cred_pres_cond_sus, "0.00")
    gibs = ibs.g_ibs
    _cmp(gibs.g_ibs_uf.v_dif, "0.04")
    _cmp(gibs.g_ibs_uf.v_dev_trib, "0.00")
    _cmp(gibs.g_ibs_uf.v_ibs_uf, "0.22")
    _cmp(gibs.g_ibs_mun.v_dif, "0.04")
    _cmp(gibs.g_ibs_mun.v_dev_trib, "0.00")
    _cmp(gibs.g_ibs_mun.v_ibs_mun, "0.22")
    _cmp(gibs.v_ibs, "0.44")
    _cmp(gibs.v_cred_pres, "0.00")
    _cmp(gibs.v_cred_pres_cond_sus, "0.00")
    mono = ibs.g_mono
    _cmp(mono.v_cbs_mono, "14.70")
    _cmp(mono.v_ibs_mono, "14.71")
    _cmp(mono.v_cbs_mono_ret, "0.00")
    _cmp(mono.v_ibs_mono_ret, "0.00")
    _cmp(mono.v_cbs_mono_reten, "0.00")
    _cmp(mono.v_ibs_mono_reten, "0.00")


def test_memoria_deveGerarMemoriaCalculoNoGrupoIBSCBSInclusiveSemGIBSCBS(
    record_xml_attribute, svc: CalculadoraService
) -> None:
    fqcn = "br.gov.serpro.rtc.testesintegracao.calculoscorretos.memoriacalculo.MemoriaCalculoTest"
    _java(record_xml_attribute, fqcn, "deveGerarMemoriaCalculoNoGrupoIBSCBSInclusiveSemGIBSCBS")
    roc = _roc(svc, "entradas/calculoscorretos/memoria-calculo/entrada.json")
    ibs1 = roc.objetos[0].trib_calc.IBSCBS
    assert ibs1.g_ibscbs is not None
    mem = ibs1.memoria_calculo
    assert mem is not None and mem.cbs is not None
    assert "R$ 200,00" in mem.cbs and "8,40%" in mem.cbs
    assert mem.ibs_uf is not None and mem.ibs_mun is not None
    ibs2 = roc.objetos[1].trib_calc.IBSCBS
    assert ibs2.g_ibscbs is None
    assert ibs2.memoria_calculo is not None
    assert ibs2.memoria_calculo.cbs is not None
    assert ibs2.memoria_calculo.ibs_uf is not None
    assert ibs2.memoria_calculo.ibs_mun is not None


_FQCN_COMPRA_OBS = (
    "br.gov.serpro.rtc.testesintegracao.calculoscorretos.comprasgovernamentais."
    "CompraGovServiceComObservabilidadeTest"
)


def test_compra_gov_obs_deveCalcularTributosCompraGov(record_xml_attribute) -> None:
    _java(record_xml_attribute, _FQCN_COMPRA_OBS, "deveCalcularTributosCompraGov")
    entrada = _load_json("entradas/calculoscorretos/compras-governamentais/entrada.json")
    operacao = operacao_from_json(entrada)
    _shim_seletivo(operacao)
    roc = ObservabilidadeService().processarOperacao(operacao, _BASE_URL)
    cg = roc.oper.g_compra_gov
    assert cg is not None
    _cmp(cg.p_redutor, "0.00")
    g = roc.objetos[0].trib_calc.IBSCBS.g_ibscbs
    _cmp(g.v_bc, "249.30")
    _cmp(roc.objetos[0].trib_calc.IS.v_is, "49.30")
    _cmp(roc.total.trib_calc.is_tot.v_is, "49.30")
    _cmp(roc.total.trib_calc.ibscbs_tot.v_bc_ibscbs, "249.30")


_FQCN_REG = "br.gov.serpro.rtc.testesintegracao.calculoscorretos.regressao.TesteRegressaoVariosItens"
_FQCN_REG_OBS = (
    "br.gov.serpro.rtc.testesintegracao.calculoscorretos.regressao."
    "TesteRegressaoVariosItensComObservabilidade"
)


def test_regressao_varios_itens(record_xml_attribute, svc) -> None:
    _java(record_xml_attribute, _FQCN_REG, "testRegressaoCalculoVariosItens")
    roc = _roc(svc, "entradas/calculoscorretos/varios_itens/Teste_Varios_Itens.json")
    _assert_gabarito(roc, "saidas/Teste_Varios_Itens.json")


def test_regressao_varios_itens_observabilidade(record_xml_attribute) -> None:
    _java(record_xml_attribute, _FQCN_REG_OBS, "testRegressaoCalculoVariosItens")
    from calculadora_rtc_regime_regular.roc import ObjetoDomain

    op = _operacao("entradas/calculoscorretos/varios_itens/Teste_Varios_Itens.json")
    roc_obs = ObservabilidadeService().processarOperacao(op, _BASE_URL)
    adapter = ROCDomain(
        oper=roc_obs.oper,
        objetos=[ObjetoDomain(n_obj=o.n_obj, trib_calc=o.trib_calc) for o in roc_obs.objetos],
        total=roc_obs.total,
    )
    _assert_gabarito(adapter, "saidas/Teste_Varios_Itens.json")