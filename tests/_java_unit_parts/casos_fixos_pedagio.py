"""Identidade JUnit — surefire Teste_CasosFixosPedagioBasesArredondamento (@DisplayName na classe)."""

from __future__ import annotations

_CLASSNAME = "Casos fixos de arredondamento do pedágio e das bases unificadas"
_MOD = "test_casos_fixos_pedagio_java"

JAVA_UNIT_IDENTITY: dict[str, tuple[str, str]] = {
    f"{_MOD}::test_t6PedagioParcelasSomamOTotal": (_CLASSNAME, "t6PedagioParcelasSomamOTotal"),
    f"{_MOD}::test_pedagioParcelasSomamOTotalEmPedidosSorteados": (
        _CLASSNAME,
        "pedagioParcelasSomamOTotalEmPedidosSorteados",
    ),
    f"{_MOD}::test_t10BaseUnificadaComDuasCasas": (_CLASSNAME, "t10BaseUnificadaComDuasCasas"),
    f"{_MOD}::test_n1BaseUnificadaComDuasCasas": (_CLASSNAME, "n1BaseUnificadaComDuasCasas"),
    f"{_MOD}::test_rg12BaseUnificadaNfse": (_CLASSNAME, "rg12BaseUnificadaNfse"),
}