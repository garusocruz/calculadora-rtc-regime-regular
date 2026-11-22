"""Casos fixos de pedágio e bases unificadas — espelho Teste_CasosFixosPedagioBasesArredondamento."""

from __future__ import annotations

import json
import os
from datetime import datetime
from decimal import Decimal
from pathlib import Path

import pytest

os.environ.setdefault(
    "CALC_DB",
    "/home/garusotec/projects/lynko/libs/calculadora-rtc-regime-regular/.cache/oficial/java/calculadora/db/calculadora-pro.db",
)

from calculadora_rtc_regime_regular.arredondamento import formatar_aliquota, formatar_moeda
from calculadora_rtc_regime_regular.banco import conectar
from calculadora_rtc_regime_regular.base_calculo import (
    BaseCalculoUnificadaInput,
    BaseCalculoUnificadaService,
    Componentes,
    Natureza,
)
from calculadora_rtc_regime_regular.nfse_unificada import (
    EntradaUnificada,
    Locacao,
    OpcaoSimples,
    Situacao,
    calcular_unificada,
)
from calculadora_rtc_regime_regular.pedagio import (
    PedagioEntrada,
    PedagioService,
    TrechoPedagioEntrada,
    pedagio_com_banco,
)

_BANCO_OFICIAL = Path(
    "/home/garusotec/projects/lynko/libs/calculadora-rtc-regime-regular/.cache/oficial/java/calculadora/db/calculadora-pro.db"
)
_CACHE = Path(__file__).resolve().parents[1] / ".cache/oficial/java/src/test/resources"
SEMENTE_ARREDONDAMENTO = 20261117
MUNICIPIOS_ARREDONDAMENTO = [
    (3550308, "SP"),
    (3509502, "SP"),
    (3304557, "RJ"),
    (4313409, "RS"),
    (1200013, "AC"),
]

pytestmark = pytest.mark.skipif(not os.environ.get("CALC_DB"), reason="CALC_DB ausente")

_BASE_SERVICE = BaseCalculoUnificadaService()


class _GeradorJavaRandom:
    """Mesma LCG que ``java.util.Random`` (semente GeradorLoteArredondamento.SEMENTE_PADRAO)."""

    def __init__(self, semente: int) -> None:
        self._seed = (semente ^ 0x5DEECE66D) & ((1 << 48) - 1)

    def _next(self, bits: int) -> int:
        self._seed = (self._seed * 0x5DEECE66D + 0xB) & ((1 << 48) - 1)
        return self._seed >> (48 - bits)

    def next_int(self, bound: int) -> int:
        if bound <= 0:
            raise ValueError(bound)
        candidate = self._next(31)
        limite = bound - 1
        if (bound & limite) == 0:
            return int((bound * candidate) >> 31)
        while True:
            resto = candidate % bound
            if candidate - resto + limite >= 0:
                return resto
            candidate = self._next(31)


def _load_json(nome: str) -> dict:
    return json.loads((_CACHE / "entradas/arredondamento" / f"{nome}.json").read_text(encoding="utf-8"))


def _moeda(valor: Decimal | None) -> str:
    assert valor is not None
    return formatar_moeda(valor)


def _aliq(valor: Decimal | None) -> str:
    assert valor is not None
    return formatar_aliquota(valor)


def _dec(valor) -> Decimal:
    return Decimal(str(valor))


def _pedagio_from_json(payload: dict) -> PedagioEntrada:
    texto = str(payload["dataHoraEmissao"])
    if texto.endswith("Z"):
        texto = texto[:-1] + "+00:00"
    trechos = [
        TrechoPedagioEntrada(int(t["numero"]), int(t["municipio"]), str(t["uf"]), _dec(t["extensao"]))
        for t in payload["trechos"]
    ]
    return PedagioEntrada(
        datetime.fromisoformat(texto),
        int(payload["codigoMunicipioOrigem"]),
        str(payload["ufMunicipioOrigem"]),
        str(payload["cst"]),
        str(payload["cClassTrib"]),
        _dec(payload["baseCalculo"]),
        trechos,
    )


def _base_unificada_from_json(payload: dict):
    meta = {"anoFatoGerador", "tipoDocumento", "natureza"}
    comp = Componentes(**{chave: _dec(valor) for chave, valor in payload.items() if chave not in meta})
    entrada = BaseCalculoUnificadaInput(
        anoFatoGerador=int(payload["anoFatoGerador"]),
        tipoDocumento=int(payload["tipoDocumento"]),
        natureza=Natureza[payload["natureza"]],
        componentes=comp,
    )
    return _BASE_SERVICE.calcular(entrada)


def _nfse_unificada_from_json(payload: dict) -> EntradaUnificada:
    bloco = payload.get("locacao")
    locacao = None
    if bloco is not None:
        locacao = Locacao(
            _dec(bloco["pCopropriedade"]),
            _dec(bloco["vTotOper"]),
            _dec(bloco["vDescIncondTot"]),
            _dec(bloco["somaAjustesLocImoveis"]),
        )
    return EntradaUnificada(
        int(payload["anoFatoGerador"]),
        OpcaoSimples(int(payload["opSimpNac"])),
        Situacao(payload["situacao"]),
        _dec(payload["vServ"]),
        _dec(payload["vDescIncond"]),
        _dec(payload["vISSQN"]),
        _dec(payload["vPIS"]),
        _dec(payload["vCOFINS"]),
        locacao=locacao,
    )


@pytest.fixture(scope="module")
def svc_pedagio() -> PedagioService:
    if not _BANCO_OFICIAL.is_file():
        pytest.skip("calculadora-pro.db oficial ausente no cache")
    with conectar() as conexao:
        yield pedagio_com_banco(conexao)


def test_t6PedagioParcelasSomamOTotal(svc_pedagio: PedagioService) -> None:
    saida = svc_pedagio.calcular_cibs(_pedagio_from_json(_load_json("T6_pedagio")))
    trechos = sorted(saida.trechos, key=lambda t: t.numero)
    assert saida.total is not None
    total = saida.total
    assert total.cbs_total is not None and total.ibs_estadual_total is not None
    assert total.ibs_municipal_total is not None

    assert _moeda(total.cbs_total.valor_tributo) == "1.80"
    assert trechos[0].cbs is not None and _moeda(trechos[0].cbs.tributo_calculado) == "0.55"
    assert trechos[1].cbs is not None and _moeda(trechos[1].cbs.tributo_calculado) == "0.71"
    assert trechos[2].cbs is not None and _moeda(trechos[2].cbs.tributo_calculado) == "0.54"

    assert _moeda(total.ibs_estadual_total.valor_tributo) == "0.20"
    assert trechos[0].ibs_estadual is not None and _moeda(trechos[0].ibs_estadual.tributo_calculado) == "0.06"
    assert trechos[1].ibs_estadual is not None and _moeda(trechos[1].ibs_estadual.tributo_calculado) == "0.08"
    assert trechos[2].ibs_estadual is not None and _moeda(trechos[2].ibs_estadual.tributo_calculado) == "0.06"

    assert _moeda(total.ibs_municipal_total.valor_tributo) == "0.00"
    for trecho in trechos:
        assert trecho.ibs_municipal is not None
        assert _moeda(trecho.ibs_municipal.tributo_calculado) == "0.00"

    assert trechos[0].cbs is not None and _aliq(trechos[0].cbs.aliquota_efetiva) == "0.2727"
    assert trechos[1].cbs is not None and _aliq(trechos[1].cbs.aliquota_efetiva) == "0.3545"
    assert trechos[2].cbs is not None and _aliq(trechos[2].cbs.aliquota_efetiva) == "0.2727"
    assert trechos[0].cbs.aliquota == Decimal("0.9")
    assert trechos[0].ibs_estadual is not None and trechos[0].ibs_estadual.aliquota == Decimal("0.1")


def test_pedagioParcelasSomamOTotalEmPedidosSorteados(svc_pedagio: PedagioService) -> None:
    gerador = _GeradorJavaRandom(SEMENTE_ARREDONDAMENTO)
    pares = (
        ("cbs", "cbs_total"),
        ("ibs_estadual", "ibs_estadual_total"),
        ("ibs_municipal", "ibs_municipal_total"),
    )
    for _ in range(300):
        quantidade = 1 + gerador.next_int(8)
        base = Decimal(1 + gerador.next_int(50_000_000)).scaleb(-2)
        trechos: list[TrechoPedagioEntrada] = []
        for numero in range(1, quantidade + 1):
            municipio, uf = MUNICIPIOS_ARREDONDAMENTO[gerador.next_int(len(MUNICIPIOS_ARREDONDAMENTO))]
            extensao = Decimal(1 + gerador.next_int(500_000)).scaleb(-gerador.next_int(4))
            trechos.append(TrechoPedagioEntrada(numero, municipio, uf, extensao))
        entrada = PedagioEntrada(
            datetime(2026, 10, 20, 10, 0),
            3550308,
            "SP",
            "000",
            "000001",
            base,
            trechos,
        )
        saida = svc_pedagio.calcular_cibs(entrada)
        assert saida.total is not None
        for campo, total_campo in pares:
            soma = Decimal(0)
            for trecho in saida.trechos:
                detalhe = getattr(trecho, campo)
                assert detalhe is not None and detalhe.tributo_calculado is not None
                assert detalhe.tributo_calculado.as_tuple().exponent == -2
                assert detalhe.aliquota_efetiva is not None
                assert detalhe.aliquota_efetiva.as_tuple().exponent == -4
                soma += detalhe.tributo_calculado
            bloco = getattr(saida.total, total_campo)
            assert bloco is not None and bloco.valor_tributo is not None
            assert soma == bloco.valor_tributo


def test_t10BaseUnificadaComDuasCasas() -> None:
    saida = _base_unificada_from_json(_load_json("T10_base_unificada"))
    assert _moeda(saida.getBaseRG()) == "954.50"
    assert _moeda(saida.getBaseIS()) == "954.50"
    assert _moeda(saida.getBaseSN()) == "1010.00"


def test_n1BaseUnificadaComDuasCasas() -> None:
    saida = _base_unificada_from_json(_load_json("N1_base_unificada"))
    assert _moeda(saida.getBaseRG()) == "954.50"
    assert _moeda(saida.getBaseIS()) == "954.50"
    assert _moeda(saida.getBaseSN()) == "1010.00"


def test_rg12BaseUnificadaNfse() -> None:
    resultado = calcular_unificada(_nfse_unificada_from_json(_load_json("RG12_base_unificada_nfse")))
    assert _moeda(resultado.base_rg) == "333.32"
    assert resultado.base_sn is None