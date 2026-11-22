"""Consumo Python ↔ testes de serviço Java (integração, sem HTTP)."""

from __future__ import annotations

import json
import os
from datetime import date, datetime
from decimal import Decimal
from pathlib import Path

import pytest

os.environ.setdefault(
    "CALC_DB",
    "/home/garusotec/projects/lynko/libs/calculadora-rtc-regime-regular/.cache/oficial/java/calculadora/db/calculadora-pro.db",
)

from calculadora_rtc_regime_regular.consumo import (
    CalculadoraService,
    DadosAbertosService,
    ObservabilidadeService,
    PedagioService,
)
from calculadora_rtc_regime_regular.coletor import ErrosCalculoException, EstadoItemEnum
from calculadora_rtc_regime_regular.dados_abertos import AliquotaNaoEncontradaException
from calculadora_rtc_regime_regular.observabilidade import operacao_from_json
from calculadora_rtc_regime_regular.pedagio import PedagioEntrada, TrechoPedagioEntrada

_CACHE = Path(__file__).resolve().parents[1] / ".cache/oficial/java/src/test/resources"
_BASE_URL = "http://localhost:8080"

_FQCN_DADOS = "br.gov.serpro.rtc.testesintegracao.dadosabertos.controller.DadosAbertosServiceTest"
_FQCN_OBS = "br.gov.serpro.rtc.testesintegracao.observabilidade.ObservabilidadeServiceTest"
_FQCN_OBS_ERR = "br.gov.serpro.rtc.testesintegracao.observabilidade.ObservabilidadeErroGlobalServiceTest"
_FQCN_PED = "br.gov.serpro.rtc.testesintegracao.pedagio.PedagioServiceTest"
_FQCN_COMPRA = (
    "br.gov.serpro.rtc.testesintegracao.calculoscorretos.comprasgovernamentais.CompraGovServiceTest"
)

DATA = date(2027, 1, 1)
DATA_COM_ALIQUOTAS = date(2026, 1, 1)
NCM = "09024000"
NBS = "102020000"
SIGLA_UF = "AC"
CODIGO_UF = 12
CODIGO_MUNICIPIO = 1200013
CST = "000"
C_CLASS_TRIB = "000001"
ID_SITUACAO_TRIBUTARIA = 1
SIGLA_DFE = "NFE"
ID_ST_CBS_IBS = 2
ID_ST_IS = 1

pytestmark = pytest.mark.skipif(not os.environ.get("CALC_DB"), reason="CALC_DB ausente")


def _java(record_xml_attribute, fqcn: str, method: str) -> None:
    record_xml_attribute("classname", fqcn)
    record_xml_attribute("name", method)


def _dec(value: object) -> Decimal:
    return Decimal(str(value))


def _compat_itens_seletivo(operacao) -> None:
    """Mesmo shim que ``ObservabilidadeService`` aplica antes do cálculo."""
    for item in operacao.itens:
        seletivo = item.imposto_seletivo
        if seletivo is not None and not hasattr(seletivo, "valor_informado"):
            seletivo.valor_informado = seletivo.imposto_informado  # type: ignore[attr-defined]


def _pedagio_from_json(payload: dict) -> PedagioEntrada:
    texto = str(payload["dataHoraEmissao"])
    if texto.endswith("Z"):
        texto = texto[:-1] + "+00:00"
    trechos = [
        TrechoPedagioEntrada(
            int(t["numero"]),
            int(t["municipio"]),
            str(t["uf"]),
            _dec(t["extensao"]),
        )
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


@pytest.fixture(scope="module")
def dados() -> DadosAbertosService:
    return DadosAbertosService()


# ─── DadosAbertosServiceTest ───────────────────────────────────────────────────


def test_consultarUfs(record_xml_attribute, dados: DadosAbertosService) -> None:
    _java(record_xml_attribute, _FQCN_DADOS, "consultarUfs")
    assert dados.consultarUfs() is not None


def test_consultarMunicipiosPorSiglaUf(record_xml_attribute, dados: DadosAbertosService) -> None:
    _java(record_xml_attribute, _FQCN_DADOS, "consultarMunicipiosPorSiglaUf")
    assert dados.consultarMunicipiosPorSiglaUf(SIGLA_UF) is not None


def test_consultarSituacoesTributariasCbsIbs(record_xml_attribute, dados: DadosAbertosService) -> None:
    _java(record_xml_attribute, _FQCN_DADOS, "consultarSituacoesTributariasCbsIbs")
    assert dados.consultarSituacoesTributarias(ID_ST_CBS_IBS, DATA) is not None


def test_consultarClassificacoesTributariasPorIdSituacaoTributaria(
    record_xml_attribute, dados: DadosAbertosService
) -> None:
    _java(record_xml_attribute, _FQCN_DADOS, "consultarClassificacoesTributariasPorIdSituacaoTributaria")
    assert dados.consultarClassificacoesTributariasPorIdSituacaoTributaria(
        ID_SITUACAO_TRIBUTARIA, DATA
    ) is not None


def test_listarPorCstImpostoSeletivo(record_xml_attribute, dados: DadosAbertosService) -> None:
    _java(record_xml_attribute, _FQCN_DADOS, "listarPorCstImpostoSeletivo")
    assert dados.consultarClassificacoesTributariasPorCstETributoTipo(CST, ["IS"], DATA) is not None


def test_listarPorCstCbsIbs(record_xml_attribute, dados: DadosAbertosService) -> None:
    _java(record_xml_attribute, _FQCN_DADOS, "listarPorCstCbsIbs")
    assert dados.consultarClassificacoesTributariasPorCstETributoTipo(
        CST, ["CBS", "IBSUF", "IBSMun"], DATA
    ) is not None


def test_consultarClassificacoesTributariasCbsIbs(record_xml_attribute, dados: DadosAbertosService) -> None:
    _java(record_xml_attribute, _FQCN_DADOS, "consultarClassificacoesTributariasCbsIbs")
    assert dados.consultarClassificacoesTributariasCbsIbs(DATA) is not None


def test_consultarClassificacoesTributariasImpostoSeletivo(
    record_xml_attribute, dados: DadosAbertosService
) -> None:
    _java(record_xml_attribute, _FQCN_DADOS, "consultarClassificacoesTributariasImpostoSeletivo")
    assert dados.consultarClassificacoesTributariasImpostoSeletivo(DATA) is not None


def test_listarClassificacaoAplicavelPorNbs(record_xml_attribute, dados: DadosAbertosService) -> None:
    _java(record_xml_attribute, _FQCN_DADOS, "listarClassificacaoAplicavelPorNbs")
    assert dados.listarClassificacaoAplicavelPorNbs(NBS, DATA) is not None


def test_consultarSituacoesTributariasImpostoSeletivo(
    record_xml_attribute, dados: DadosAbertosService
) -> None:
    _java(record_xml_attribute, _FQCN_DADOS, "consultarSituacoesTributariasImpostoSeletivo")
    assert dados.consultarSituacoesTributarias(ID_ST_IS, DATA) is not None


def test_consultarNcm(record_xml_attribute, dados: DadosAbertosService) -> None:
    _java(record_xml_attribute, _FQCN_DADOS, "consultarNcm")
    assert dados.consultarNcm(NCM, DATA) is not None


def test_consultarNcmTributadaPeloImpostoSeletivoSemValorDefinidoEmLei(
    record_xml_attribute, dados: DadosAbertosService
) -> None:
    _java(record_xml_attribute, _FQCN_DADOS, "consultarNcmTributadaPeloImpostoSeletivoSemValorDefinidoEmLei")
    ncm = dados.consultarNcm("24021000", DATA)
    assert ncm.tributado_pelo_imposto_seletivo is True
    assert ncm.tem_aliquota_ad_valorem is True
    assert ncm.tem_aliquota_ad_rem is True
    assert ncm.aliquota_ad_valorem is None
    assert ncm.aliquota_ad_rem is None


def test_consultarNcmNaoTributadaPeloImpostoSeletivo(
    record_xml_attribute, dados: DadosAbertosService
) -> None:
    _java(record_xml_attribute, _FQCN_DADOS, "consultarNcmNaoTributadaPeloImpostoSeletivo")
    ncm = dados.consultarNcm(NCM, DATA)
    assert ncm.tributado_pelo_imposto_seletivo is False
    assert ncm.tem_aliquota_ad_valorem is False
    assert ncm.tem_aliquota_ad_rem is False


def test_consultarNbs(record_xml_attribute, dados: DadosAbertosService) -> None:
    _java(record_xml_attribute, _FQCN_DADOS, "consultarNbs")
    assert dados.consultarNbs(NBS, DATA) is not None


def test_consultarNbsNaoTributadaPeloImpostoSeletivo(record_xml_attribute, dados: DadosAbertosService) -> None:
    _java(record_xml_attribute, _FQCN_DADOS, "consultarNbsNaoTributadaPeloImpostoSeletivo")
    nbs = dados.consultarNbs(NBS, DATA)
    assert nbs.tributado_pelo_imposto_seletivo is False
    assert nbs.tem_aliquota_ad_valorem is False


def test_listarNbs(record_xml_attribute, dados: DadosAbertosService) -> None:
    _java(record_xml_attribute, _FQCN_DADOS, "listarNbs")
    assert dados.listarNbs(DATA) is not None


def test_listarNbsAplicaveisPorClassificacao(record_xml_attribute, dados: DadosAbertosService) -> None:
    _java(record_xml_attribute, _FQCN_DADOS, "listarNbsAplicaveisPorClassificacao")
    assert dados.listarNbsAplicaveisPorClassificacao(C_CLASS_TRIB, DATA) is not None


def test_consultarFundamentacoesLegais(record_xml_attribute, dados: DadosAbertosService) -> None:
    _java(record_xml_attribute, _FQCN_DADOS, "consultarFundamentacoesLegais")
    assert dados.consultarFundamentacoesLegais(DATA) is not None


def test_consultarAliquotaUniao(record_xml_attribute, dados: DadosAbertosService) -> None:
    _java(record_xml_attribute, _FQCN_DADOS, "consultarAliquotaUniao")
    assert dados.consultarAliquota(2, None, None, DATA_COM_ALIQUOTAS) is not None


def test_consultarAliquotaUf(record_xml_attribute, dados: DadosAbertosService) -> None:
    _java(record_xml_attribute, _FQCN_DADOS, "consultarAliquotaUf")
    assert dados.consultarAliquota(3, CODIGO_UF, None, DATA_COM_ALIQUOTAS) is not None


def test_consultarAliquotaMunicipio(record_xml_attribute, dados: DadosAbertosService) -> None:
    _java(record_xml_attribute, _FQCN_DADOS, "consultarAliquotaMunicipio")
    assert dados.consultarAliquota(4, None, CODIGO_MUNICIPIO, DATA_COM_ALIQUOTAS) is not None


def test_consultarAliquotaUniaoSemAliquotaDefinidaEmLei(
    record_xml_attribute, dados: DadosAbertosService
) -> None:
    _java(record_xml_attribute, _FQCN_DADOS, "consultarAliquotaUniaoSemAliquotaDefinidaEmLei")
    with pytest.raises(AliquotaNaoEncontradaException):
        dados.consultarAliquota(2, None, None, DATA)


def test_consultarAliquotaUfSemAliquotaDefinidaEmLei(
    record_xml_attribute, dados: DadosAbertosService
) -> None:
    _java(record_xml_attribute, _FQCN_DADOS, "consultarAliquotaUfSemAliquotaDefinidaEmLei")
    with pytest.raises(AliquotaNaoEncontradaException):
        dados.consultarAliquota(3, CODIGO_UF, None, DATA)


def test_consultarAliquotaMunicipioSemAliquotaDefinidaEmLei(
    record_xml_attribute, dados: DadosAbertosService
) -> None:
    _java(record_xml_attribute, _FQCN_DADOS, "consultarAliquotaMunicipioSemAliquotaDefinidaEmLei")
    with pytest.raises(AliquotaNaoEncontradaException):
        dados.consultarAliquota(4, None, CODIGO_MUNICIPIO, DATA)


def test_consultarNomenclatura(record_xml_attribute, dados: DadosAbertosService) -> None:
    _java(record_xml_attribute, _FQCN_DADOS, "consultarNomenclatura")
    result = dados.consultarNomenclatura(SIGLA_DFE, C_CLASS_TRIB, DATA)
    assert result.sigla_dfe == SIGLA_DFE
    assert result.c_class_trib == C_CLASS_TRIB
    assert result.data == DATA
    assert result.nomenclatura == "SEM"


def test_consultarClassificacaoTributariaIsPorCodigo(record_xml_attribute, dados: DadosAbertosService) -> None:
    _java(record_xml_attribute, _FQCN_DADOS, "consultarClassificacaoTributariaIsPorCodigo")
    assert dados.consultarClassificacaoTributariaIsPorCodigo(C_CLASS_TRIB, DATA) is not None


_VALIDADE_EXIGE_GRUPO = [
    ("000001", True),
    ("010001", True),
    ("011001", True),
    ("200001", True),
    ("221001", True),
    ("222001", True),
    ("400001", False),
    ("410001", False),
    ("510001", True),
    ("515001", True),
    ("550001", True),
    ("620001", False),
    ("800001", False),
    ("810001", False),
    ("811001", False),
    ("820001", False),
    ("830001", True),
]


@pytest.mark.parametrize(
    "codigo, esperado",
    _VALIDADE_EXIGE_GRUPO,
    ids=[str(i + 1) for i in range(len(_VALIDADE_EXIGE_GRUPO))],
)
def test_quando_consultarValidadeDfeClassificacaoTributariaExigirGrupoIbcCbs(
    record_xml_attribute,
    dados: DadosAbertosService,
    codigo: str,
    esperado: bool,
    request: pytest.FixtureRequest,
) -> None:
    indice = request.node.callspec.id if request.node.callspec else "1"
    _java(
        record_xml_attribute,
        _FQCN_DADOS,
        f"quando_consultarValidadeDfeClassificacaoTributariaExigirGrupoIbcCbs(String, boolean)[{indice}]",
    )
    resultado = dados.consultarValidadeDfeClassificacaoTributaria(SIGLA_DFE, codigo, DATA)
    assert resultado is not None
    assert resultado.exige_grupo_ibs_cbs is esperado


def test_consultarCstsComClassificacoesCbsIbsPorSiglaDfe(
    record_xml_attribute, dados: DadosAbertosService
) -> None:
    _java(record_xml_attribute, _FQCN_DADOS, "consultarCstsComClassificacoesCbsIbsPorSiglaDfe")
    resultado = dados.consultarCstsComClassificacoesCbsIbs(SIGLA_DFE, DATA)
    assert resultado is not None
    assert len(resultado) > 0


def test_consultarCstsComClassificacoesCbsIbsSemSiglaDfe(
    record_xml_attribute, dados: DadosAbertosService
) -> None:
    _java(record_xml_attribute, _FQCN_DADOS, "consultarCstsComClassificacoesCbsIbsSemSiglaDfe")
    resultado = dados.consultarCstsComClassificacoesCbsIbs(None, DATA)
    assert resultado is not None
    assert len(resultado) > 0


def test_consultarCstsComClassificacoesIsPorSiglaDfe(
    record_xml_attribute, dados: DadosAbertosService
) -> None:
    _java(record_xml_attribute, _FQCN_DADOS, "consultarCstsComClassificacoesIsPorSiglaDfe")
    assert dados.consultarCstsComClassificacoesIs(SIGLA_DFE, DATA) is not None


def test_consultarCstsComClassificacoesIsSemSiglaDfe(
    record_xml_attribute, dados: DadosAbertosService
) -> None:
    _java(record_xml_attribute, _FQCN_DADOS, "consultarCstsComClassificacoesIsSemSiglaDfe")
    assert dados.consultarCstsComClassificacoesIs(None, DATA) is not None


def test_consultarTiposDfeAgrupados(record_xml_attribute, dados: DadosAbertosService) -> None:
    _java(record_xml_attribute, _FQCN_DADOS, "consultarTiposDfeAgrupados")
    grupos = dados.consultarTiposDfeAgrupados(DATA)
    assert grupos
    for grupo in grupos:
        assert grupo.tipos
        assert grupo.ordem > 0
    assert grupos[0].ordem == 1
    assert grupos[0].tipos[0].codigo == SIGLA_DFE
    tipos = [tipo for grupo in grupos for tipo in grupo.tipos]
    for tipo in tipos:
        assert tipo.suportado is not None
        assert tipo.permite_ncm_zero is not None
    nfe = next(t for t in tipos if t.codigo == "NFE")
    assert nfe.suportado is True
    assert nfe.permite_ncm_zero is True
    cte = next(t for t in tipos if t.codigo == "CTE")
    assert cte.suportado is True
    assert cte.permite_ncm_zero is False
    nao_suportados = [t for t in tipos if t.codigo in ("NFEABI", "DERE", "DIR", "DUIMP")]
    assert len(nao_suportados) == 4
    assert all(not t.suportado for t in nao_suportados)


def test_consultarTiposDfeAgrupados_semData_usaDataAtual(
    record_xml_attribute, dados: DadosAbertosService
) -> None:
    _java(record_xml_attribute, _FQCN_DADOS, "consultarTiposDfeAgrupados_semData_usaDataAtual")
    resultado = dados.consultarTiposDfeAgrupados(None)
    assert resultado is not None
    assert len(resultado) > 0


def test_consultarRedutoresCompraGovernamental(record_xml_attribute, dados: DadosAbertosService) -> None:
    _java(record_xml_attribute, _FQCN_DADOS, "consultarRedutoresCompraGovernamental")
    assert dados.consultarRedutoresCompraGovernamental() is not None


def test_consultarTransferenciasCBS(record_xml_attribute, dados: DadosAbertosService) -> None:
    _java(record_xml_attribute, _FQCN_DADOS, "consultarTransferenciasCBS")
    assert dados.consultarTransferenciasCBS() is not None


def test_consultarTransferenciasIBS(record_xml_attribute, dados: DadosAbertosService) -> None:
    _java(record_xml_attribute, _FQCN_DADOS, "consultarTransferenciasIBS")
    assert dados.consultarTransferenciasIBS() is not None


# ─── Observabilidade / Calculadora / Pedágio ───────────────────────────────────


def test_deveProcessarOperacaoComObservabilidade(record_xml_attribute) -> None:
    _java(record_xml_attribute, _FQCN_OBS, "deveProcessarOperacaoComObservabilidade")
    entrada = json.loads(
        (_CACHE / "entradas/calculoscorretos/observabilidade/entrada.json").read_text(encoding="utf-8")
    )
    roc = ObservabilidadeService().processarOperacao(operacao_from_json(entrada), _BASE_URL)
    assert roc is not None
    assert roc.objetos is not None
    assert len(roc.objetos) == 6
    estados = [o.estado_item for o in roc.objetos]
    assert estados == [
        EstadoItemEnum.INCONSISTENCIA_ENTRADA,
        EstadoItemEnum.NAO_IMPLEMENTADO,
        EstadoItemEnum.INCONSISTENCIA_ENTRADA,
        EstadoItemEnum.INCONSISTENCIA_ENTRADA,
        EstadoItemEnum.CALCULADO,
        EstadoItemEnum.CALCULO_SIMULADO,
    ]


def test_deveLancarExcecaoQuandoErroGlobal4xx(record_xml_attribute) -> None:
    _java(record_xml_attribute, _FQCN_OBS_ERR, "deveLancarExcecaoQuandoErroGlobal4xx")
    entrada = json.loads(
        (_CACHE / "entradas/calculoscorretos/observabilidade/entrada_com_erro_global.json").read_text(
            encoding="utf-8"
        )
    )
    with pytest.raises(Exception):
        ObservabilidadeService().processarOperacao(operacao_from_json(entrada), _BASE_URL)


def test_deveLancarExcecaoQuandoErroGlobal5xx(record_xml_attribute) -> None:
    _java(record_xml_attribute, _FQCN_OBS_ERR, "deveLancarExcecaoQuandoErroGlobal5xx")
    entrada = json.loads(
        (_CACHE / "entradas/calculoscorretos/observabilidade/entrada_com_erro_422.json").read_text(
            encoding="utf-8"
        )
    )
    with pytest.raises(ErrosCalculoException):
        ObservabilidadeService().processarOperacao(operacao_from_json(entrada), _BASE_URL)


def test_deveCalcularTributoPedagio(record_xml_attribute) -> None:
    _java(record_xml_attribute, _FQCN_PED, "deveCalcularTributoPedagio")
    payload = json.loads((_CACHE / "entradas/pedagio/entrada.json").read_text(encoding="utf-8"))
    out = PedagioService().calcularCIBS(_pedagio_from_json(payload))
    assert out is not None
    assert out.municipio_origem == 1200013
    assert _dec(out.base_calculo) == _dec("200")
    assert _dec(out.extensao_total) == _dec("100")
    trechos = out.trechos
    assert trechos is not None and len(trechos) == 4
    t1 = trechos[0]
    assert t1.numero == 1
    assert t1.municipio == 1200013
    assert _dec(t1.base_calculo) == _dec("200")
    assert t1.cbs is not None and _dec(t1.cbs.aliquota) == _dec("0.900000")
    assert _dec(t1.cbs.tributo_calculado) == _dec("0.18000000")
    total = out.total
    assert total is not None and total.cbs_total is not None
    assert _dec(total.cbs_total.valor_tributo) == _dec("1.80")


def test_deveCalcularTributosCompraGov(record_xml_attribute) -> None:
    _java(record_xml_attribute, _FQCN_COMPRA, "deveCalcularTributosCompraGov")
    entrada = json.loads(
        (_CACHE / "entradas/calculoscorretos/compras-governamentais/entrada.json").read_text(encoding="utf-8")
    )
    operacao = operacao_from_json(entrada)
    _compat_itens_seletivo(operacao)
    roc = CalculadoraService().calcularTributos(operacao)
    assert roc is not None

    compra_gov = roc.oper.g_compra_gov
    assert compra_gov is not None
    assert compra_gov.tp_ente_gov is not None
    assert compra_gov.tp_oper_gov is not None
    assert _dec(compra_gov.p_redutor) == _dec("0.00")

    assert roc.objetos is not None and len(roc.objetos) == 1
    obj = roc.objetos[0]
    assert obj.n_obj == 1
    trib = obj.trib_calc
    assert trib is not None

    is_calc = trib.IS
    assert is_calc is not None
    assert _dec(is_calc.v_bcis) == _dec("200.00")
    assert _dec(is_calc.p_is) == _dec("14.00")
    assert _dec(is_calc.p_is_espec) == _dec("21.30")
    assert _dec(is_calc.q_trib) == _dec("1")
    assert _dec(is_calc.v_is) == _dec("49.30")

    assert trib.IBSCBS is not None
    g = trib.IBSCBS.g_ibscbs
    assert g is not None
    assert _dec(g.v_bc) == _dec("249.30")

    ibs_uf = g.g_ibs_uf
    assert ibs_uf is not None
    assert _dec(ibs_uf.p_ibs_uf) == _dec("0.00")
    assert ibs_uf.g_red is not None
    assert _dec(ibs_uf.g_red.p_red_aliq) == _dec("0.00")
    assert _dec(ibs_uf.g_red.p_aliq_efet) == _dec("0.00")
    assert _dec(ibs_uf.v_ibs_uf) == _dec("0.00")

    ibs_mun = g.g_ibs_mun
    assert ibs_mun is not None
    assert _dec(ibs_mun.p_ibs_mun) == _dec("0.00")
    assert ibs_mun.g_red is not None
    assert _dec(ibs_mun.g_red.p_red_aliq) == _dec("0.00")
    assert _dec(ibs_mun.g_red.p_aliq_efet) == _dec("0.00")
    assert _dec(ibs_mun.v_ibs_mun) == _dec("0.00")
    assert _dec(g.v_ibs) == _dec("0.00")

    cbs = g.g_cbs
    assert cbs is not None
    assert _dec(cbs.p_cbs) == _dec("0.00")
    assert cbs.g_red is not None
    assert _dec(cbs.g_red.p_red_aliq) == _dec("0.00")
    assert _dec(cbs.g_red.p_aliq_efet) == _dec("0.00")
    assert _dec(cbs.v_cbs) == _dec("0.00")

    reg = g.g_trib_regular
    assert reg is not None
    assert _dec(reg.p_aliq_efet_reg_ibs_uf) == _dec("1.08")
    assert _dec(reg.v_trib_reg_ibs_uf) == _dec("2.69")
    assert _dec(reg.p_aliq_efet_reg_ibs_mun) == _dec("0.00")
    assert _dec(reg.v_trib_reg_ibs_mun) == _dec("0.00")
    assert _dec(reg.p_aliq_efet_reg_cbs) == _dec("3.06")
    assert _dec(reg.v_trib_reg_cbs) == _dec("7.63")

    tcg = g.g_trib_compra_gov
    assert tcg is not None
    assert _dec(tcg.p_aliq_ibs_uf) == _dec("0.00")
    assert _dec(tcg.v_trib_ibs_uf) == _dec("0.00")
    assert _dec(tcg.p_aliq_ibs_mun) == _dec("0.00")
    assert _dec(tcg.v_trib_ibs_mun) == _dec("0.00")
    assert _dec(tcg.p_aliq_cbs) == _dec("0.00")
    assert _dec(tcg.v_trib_cbs) == _dec("0.00")

    tot = roc.total.trib_calc
    assert tot is not None and tot.is_tot is not None
    assert _dec(tot.is_tot.v_is) == _dec("49.30")
    assert tot.ibscbs_tot is not None
    assert _dec(tot.ibscbs_tot.v_bc_ibscbs) == _dec("249.30")
    tot_ibs = tot.ibscbs_tot.g_ibs
    assert tot_ibs is not None
    assert _dec(tot_ibs.g_ibs_uf.v_dif) == _dec("0.00")
    assert _dec(tot_ibs.g_ibs_uf.v_dev_trib) == _dec("0.00")
    assert _dec(tot_ibs.g_ibs_uf.v_ibs_uf) == _dec("0.00")
    assert _dec(tot_ibs.g_ibs_mun.v_dif) == _dec("0.00")
    assert _dec(tot_ibs.g_ibs_mun.v_dev_trib) == _dec("0.00")
    assert _dec(tot_ibs.g_ibs_mun.v_ibs_mun) == _dec("0.00")
    assert _dec(tot_ibs.v_ibs) == _dec("0.00")
    assert _dec(tot_ibs.v_cred_pres) == _dec("0.00")
    assert _dec(tot_ibs.v_cred_pres_cond_sus) == _dec("0.00")

    tot_cbs = tot.ibscbs_tot.g_cbs
    assert tot_cbs is not None
    assert _dec(tot_cbs.v_dif) == _dec("0.00")
    assert _dec(tot_cbs.v_dev_trib) == _dec("0.00")
    assert _dec(tot_cbs.v_cbs) == _dec("0.00")
    assert _dec(tot_cbs.v_cred_pres) == _dec("0.00")
    assert _dec(tot_cbs.v_cred_pres_cond_sus) == _dec("0.00")

    mono = tot.ibscbs_tot.g_mono
    assert mono is not None
    assert _dec(mono.v_ibs_mono) == _dec("0.00")
    assert _dec(mono.v_cbs_mono) == _dec("0.00")
    assert _dec(mono.v_ibs_mono_reten) == _dec("0.00")
    assert _dec(mono.v_cbs_mono_reten) == _dec("0.00")
    assert _dec(mono.v_ibs_mono_ret) == _dec("0.00")
    assert _dec(mono.v_cbs_mono_ret) == _dec("0.00")