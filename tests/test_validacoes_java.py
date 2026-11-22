"""Testes de validação espelhando integração Java (pin f1eebd7)."""

from __future__ import annotations

import json
import os
import re
from copy import deepcopy
from dataclasses import replace
from datetime import date, datetime
from decimal import Decimal
from pathlib import Path
from typing import Any, Callable

import pytest

os.environ.setdefault("CALC_DB", "/home/garusotec/projects/lynko/libs/calculadora-rtc-regime-regular/.cache/oficial/java/calculadora/db/calculadora-pro.db")

from calculadora_rtc_regime_regular.base_calculo_service import CampoInvalido
from calculadora_rtc_regime_regular.banco import conectar
from calculadora_rtc_regime_regular.calculadora import (
    CalculadoraService,
    ClassificacaoTributariaNaoVinculadaTipoDfeException,
)
from calculadora_rtc_regime_regular.coletor import ErrosCalculoException, EstadoItemEnum
from calculadora_rtc_regime_regular.consultas import (
    MunicipioNaoEncontradoException,
    MunicipioNaoPertencenteException,
    SituacaoTributariaNaoEncontradaException,
    TipoDfeNaoEncontradoException,
    TipoDfeNaoTratadoException,
    UfNaoEncontradaException,
)
from calculadora_rtc_regime_regular.nomenclatura import (
    ClassificacaoTributariaService,
    ClassificacaoTributariaNaoEncontradaException,
    NbsCompletoNaoInformadoException,
    NbsNaoVinculadaException,
    NcmCompletoNaoInformadoException,
    NcmNaoVinculadaException,
    NcmAplicavelService,
    NomenclaturaIncompativelTipoDfeException,
    NomenclaturaNaoPermitidaTipoDfeException,
    NomenclaturaObrigatoriaNaoInformadaException,
    montar_nomenclatura_sqlite,
)
from calculadora_rtc_regime_regular.observabilidade import (
    ErroFaltaImplementacaoException,
    ObservabilidadeService,
    operacao_from_json,
)
from calculadora_rtc_regime_regular.pedagio import (
    MunicipioNaoEncontrado as PedagioMunicipioNaoEncontrado,
    MunicipioNaoPertencente as PedagioMunicipioNaoPertencente,
    PedagioEntrada,
    PedagioService,
    TrechoPedagioEntrada,
    pedagio_com_banco,
)
from calculadora_rtc_regime_regular.processamento_item import (
    AliquotaImpostoSeletivoNaoInformadaException,
    AliquotasNominaisImpostoSeletivo,
    AliquotasNominaisInformadasIndevidamenteException,
    AliquotasNominaisInput,
    AliquotasNominaisNaoInformadasException,
    BaseCalculoInconsistenteException,
    BaseCalculoMenorBaseCalculoImpostoSeletivoException,
    BaseCalculoNaoInformadaException,
    ClassificacaoTributariaNaoVinculadaSituacaoTributariaException,
    DataFatoGeradorNaoInformadaException,
    ImpostoSeletivoInput,
    ImpostoSeletivoNaoAdmitidoTipoDfeException,
    ImpostoSeletivoNaoInformadoException,
    IncompatibilidadeSuspensaoException,
    NbsNaoEncontradaException,
    NcmNaoEncontradaException,
    NcmNbsSimultaneasException,
    TributacaoRegularInput,
    TributacaoRegularNaoInformadaException,
)

_RES = Path(__file__).resolve().parents[1] / ".cache/oficial/java/src/test/resources"
_BASE_URL = "http://localhost:8080"
_CALC = CalculadoraService()
_OBS = ObservabilidadeService()
_DFE_TRATADOS = (55, 57, 62, 63, 65, 66, 67, 75, 76, 83, 91)
_DFE_NAO_TRATADOS = (77, 94, 95, 96)

JAVA_EXCEPTIONS = {
    "AliquotaImpostoSeletivoNaoInformadaException": AliquotaImpostoSeletivoNaoInformadaException,
    "AliquotasNominaisInformadasIndevidamenteException": AliquotasNominaisInformadasIndevidamenteException,
    "AliquotasNominaisNaoInformadasException": AliquotasNominaisNaoInformadasException,
    "BaseCalculoInconsistenteException": BaseCalculoInconsistenteException,
    "BaseCalculoMenorBaseCalculoImpostoSeletivoException": BaseCalculoMenorBaseCalculoImpostoSeletivoException,
    "BaseCalculoNaoInformadaException": BaseCalculoNaoInformadaException,
    "CampoInvalidoException": CampoInvalido,
    "ClassificacaoTributariaNaoEncontradaException": ClassificacaoTributariaNaoEncontradaException,
    "ClassificacaoTributariaNaoVinculadaSituacaoTributariaException": ClassificacaoTributariaNaoVinculadaSituacaoTributariaException,
    "ClassificacaoTributariaNaoVinculadaTipoDfeException": ClassificacaoTributariaNaoVinculadaTipoDfeException,
    "DataFatoGeradorNaoInformadaException": DataFatoGeradorNaoInformadaException,
    "ErroFaltaImplementacaoException": ErroFaltaImplementacaoException,
    "ErrosCalculoException": ErrosCalculoException,
    "ImpostoSeletivoNaoAdmitidoTipoDfeException": ImpostoSeletivoNaoAdmitidoTipoDfeException,
    "ImpostoSeletivoNaoInformadoException": ImpostoSeletivoNaoInformadoException,
    "IncompatibilidadeSuspensaoException": IncompatibilidadeSuspensaoException,
    "MunicipioNaoEncontradoException": MunicipioNaoEncontradoException,
    "MunicipioNaoPertencenteException": MunicipioNaoPertencenteException,
    "NbsCompletoNaoInformadoException": NbsCompletoNaoInformadoException,
    "NbsNaoEncontradaException": NbsNaoEncontradaException,
    "NbsNaoVinculadaException": NbsNaoVinculadaException,
    "NcmCompletoNaoInformadoException": NcmCompletoNaoInformadoException,
    "NcmNaoEncontradaException": NcmNaoEncontradaException,
    "NcmNaoVinculadaException": NcmNaoVinculadaException,
    "NcmNbsSimultaneasException": NcmNbsSimultaneasException,
    "NomenclaturaIncompativelTipoDfeException": NomenclaturaIncompativelTipoDfeException,
    "NomenclaturaNaoPermitidaTipoDfeException": NomenclaturaNaoPermitidaTipoDfeException,
    "NomenclaturaObrigatoriaNaoInformadaException": NomenclaturaObrigatoriaNaoInformadaException,
    "SituacaoTributariaNaoEncontradaException": SituacaoTributariaNaoEncontradaException,
    "TipoDfeNaoEncontradoException": TipoDfeNaoEncontradoException,
    "TipoDfeNaoTratadoException": TipoDfeNaoTratadoException,
    "TributacaoRegularNaoInformadaException": TributacaoRegularNaoInformadaException,
    "UfNaoEncontradaException": UfNaoEncontradaException,
}


def _java_attrs(record_xml_attribute, classname: str, name: str) -> None:
    record_xml_attribute("classname", classname)
    record_xml_attribute("name", name)


def _load_json(path: str) -> dict[str, Any]:
    return json.loads((_RES / path).read_text(encoding="utf-8"))


def _load_operacao(path: str):
    return operacao_from_json(_load_json(path))


def _load_pedagio(path: str) -> PedagioEntrada:
    raw = _load_json(path)
    trechos = [
        TrechoPedagioEntrada(
            numero=int(t["numero"]),
            municipio=int(t["municipio"]),
            uf=str(t["uf"]),
            extensao=Decimal(str(t["extensao"])),
        )
        for t in raw["trechos"]
    ]
    texto_data = str(raw["dataHoraEmissao"])
    if texto_data.endswith("Z"):
        texto_data = texto_data[:-1] + "+00:00"
    return PedagioEntrada(
        data_hora_emissao=datetime.fromisoformat(texto_data),
        codigo_municipio_origem=int(raw["codigoMunicipioOrigem"]),
        uf_municipio_origem=str(raw["ufMunicipioOrigem"]),
        cst=str(raw["cst"]),
        c_class_trib=str(raw["cClassTrib"]),
        base_calculo=Decimal(str(raw["baseCalculo"])),
        trechos=trechos,
    )


@pytest.fixture(scope="module")
def pedagio_svc() -> PedagioService:
    if not Path(os.environ["CALC_DB"]).is_file():
        pytest.skip("calculadora-pro.db ausente")
    with conectar() as conexao:
        yield pedagio_com_banco(conexao)


def _param_index(name: str) -> int | None:
    m = re.search(r"\[(\d+)]", name)
    return int(m.group(1)) if m else None


def _base_name(name: str) -> str:
    return re.sub(r"\(.*", "", name)


def _expect_raises(exc_name: str | None):
    if exc_name is None:
        return pytest.raises(Exception) if False else nullcontext()
    return pytest.raises(JAVA_EXCEPTIONS[exc_name])


from contextlib import nullcontext


def _informar_is(op):
    op.itens[0] = replace(
        op.itens[0],
        imposto_seletivo=ImpostoSeletivoInput(
            cst="000",
            c_class_trib="000001",
            base_calculo=Decimal("100"),
            quantidade=Decimal("1"),
            unidade="UN",
            imposto_informado=None,
        ),
    )
    return op


def _mudar_2026(op):
    op.data_fato_gerador = date(2026, 8, 30)
    return op


def _mutate(classname: str, base: str, op, index: int | None):
    item = op.itens[0]
    if classname.endswith("Teste_tpdoc_1_NfeNomenclaturaNcm"):
        if base == "teste_ncmForaDoAnexoErro":
            op.itens[0] = replace(item, ncm="24021000")
        elif base == "teste_nbsInformadaErro":
            op.itens[0] = replace(item, ncm=None, nbs="115012000")
        elif base == "teste_ncmAusenteErro":
            op.itens[0] = replace(item, ncm=None)
    elif classname.endswith("Teste_tpdoc_2_NfseNomenclaturaMisto"):
        if base == "teste_ncmValidoDoAnexoPassa":
            op.itens[0] = replace(item, nbs=None, ncm="87100000")
        elif base == "teste_nenhumaNomenclaturaErro":
            op.itens[0] = replace(item, ncm=None, nbs=None)
        elif base == "teste_nbsForaDoAnexoErro":
            op.itens[0] = replace(item, nbs="109052100")
    elif classname.endswith("Teste_tpdoc_3_NfcomPermissivoRigido"):
        if base == "teste_permissivo_ncmInvalidoErro":
            op.itens[0] = replace(item, ncm="24021000")
        elif base == "teste_permissivo_nbsInvalidaErro":
            op.itens[0] = replace(item, nbs="109052100")
        elif base == "teste_permissivo_ncmValidoPassa":
            op.itens[0] = replace(item, nbs=None, ncm="87100000")
        elif base == "teste_permissivo_nbsValidaPassa":
            op.itens[0] = replace(item, ncm=None, nbs="115012000")
    elif classname.endswith("Teste_tpdoc_4_ClassificacaoSemAnexo"):
        if base == "teste_comTpDoc_nbsEmNfeErro":
            op.itens[0] = replace(item, ncm=None, nbs="115012000")
        elif base == "teste_comTpDocNfse_nbsAceita":
            op.tp_doc = 91
            op.itens[0] = replace(item, ncm=None, nbs="115062100")
        elif base == "teste_semTpDoc_ncmAceito":
            op.tp_doc = None
            op.itens[0] = replace(item, nbs=None, ncm="24021000")
        elif base == "teste_semTpDoc_semNomenclaturaPassa":
            op.tp_doc = None
            op.itens[0] = replace(item, ncm=None, nbs=None)
    elif classname.endswith("Teste_tpdoc_5_TpDocInvalido"):
        if base == "teste_service_tpDocInexistente":
            op.tp_doc = 99
        elif base == "teste_service_tpDocForaDeVigencia":
            op.data_fato_gerador = date(2024, 6, 1)
        elif base == "teste_observabilidade_tpDocInexistente":
            op.tp_doc = 99999
    elif classname.endswith("Teste_tpdoc_7_TributacaoRegular"):
        if base == "teste_tributacaoRegularSemVinculoErro" and item.tributacao_regular:
            op.itens[0] = replace(
                item,
                tributacao_regular=replace(item.tributacao_regular, c_class_trib="200044"),
            )
        elif base == "teste_tributacaoRegularNcmForaDoAnexoErro":
            op.itens[0] = replace(item, ncm="24021000")
        elif base == "teste_tributacaoRegularNaoExigidaSemVinculoErro" and item.tributacao_regular:
            op.itens[0] = replace(
                item,
                cst="000",
                c_class_trib="000001",
                ncm="24021000",
                tributacao_regular=replace(item.tributacao_regular, cst="200", c_class_trib="200044"),
            )
    elif classname.endswith("Teste_tpdoc_8_ImpostoSeletivo"):
        if base == "teste_tpDoc65_impostoSeletivoAceito":
            op.tp_doc = 65
        elif base == "teste_tpDocForaWhitelist_ncmExigeIsErro":
            op.tp_doc = 62
        elif base == "teste_tpDocForaWhitelist_grupoSemIncidenciaValidaCst":
            return _load_operacao("entradas/tpdoc/tpdoc_imposto_seletivo_superfluo_2026.json")
        elif base == "teste_semTpDoc_comportamentoAtual":
            op.tp_doc = None
    elif classname.endswith("Teste_tpdoc_10_NfseAnexoIxSemNcm"):
        if base in {"teste_ncmDoAnexoBloqueado", "teste_ncmDoAnexoBloqueado200038"}:
            op.itens[0] = replace(item, nbs=None, ncm="31010000")
            if base.endswith("200038"):
                op.itens[0] = replace(op.itens[0], cst="200", c_class_trib="200038")
        elif base == "teste_semNomenclaturaErro":
            op.itens[0] = replace(item, nbs=None)
        elif base == "teste_nbsForaDoAnexoErro":
            op.itens[0] = replace(item, nbs="115012000")
    elif classname.endswith("Teste_validacao_26_TipoDfeNaoTratadoException"):
        if index is None:
            return op
        if base.startswith("servicoDeveCalcularTributosComSucessoParaDFeTratado"):
            op.tp_doc = _DFE_TRATADOS[index - 1]
        elif base.startswith("servicoDeveLancarExcecaoParaDFeNaoTratado"):
            op.tp_doc = _DFE_NAO_TRATADOS[index - 1]
        elif base.startswith("observabilidadeServicoDeveProcessarComSucessoParaDFeTratado"):
            op.tp_doc = _DFE_TRATADOS[index - 1]
        elif base.startswith("observabilidadeServicoDeveLancarExcecaoParaDFeNaoTratado"):
            op.tp_doc = _DFE_NAO_TRATADOS[index - 1]
    elif classname.endswith("Teste_validacao_AliquotasNominaisPorAnoFatoGerador"):
        op = _load_operacao("entradas/validacoes/Teste_validacao_15_ImpostoSeletivoNaoInformadoException.json")
        if base == "deveCriticarAliquotasNominaisInformadasAte2026":
            op = _mudar_2026(op)
        elif base == "deveCriticarQualquerCampoDoGrupoAliquotasNominaisAte2026":
            op = _mudar_2026(op)
            an = AliquotasNominaisInput(cbs=None, ibs_estadual=None, ibs_municipal=None, imposto_seletivo=AliquotasNominaisImpostoSeletivo(ad_valorem=Decimal("10.0"), ad_rem=None))
            op.itens[0] = replace(op.itens[0], aliquotas_nominais=an)
        elif base == "deveCalcularNormalmenteEm2026SemAliquotasNominais":
            op = _mudar_2026(op)
            op.itens[0] = replace(op.itens[0], aliquotas_nominais=None, imposto_seletivo=None)
        elif base == "deveValidarCstDoGrupoImpostoSeletivoEm2026AntesDaBuscaDeAliquota":
            op = _mudar_2026(op)
            op.itens[0] = replace(op.itens[0], aliquotas_nominais=None)
            op = _informar_is(op)
        elif base == "deveCriticarAusenciaDeAliquotasNominaisAPartirDe2027":
            op.itens[0] = replace(op.itens[0], aliquotas_nominais=None)
        elif base == "deveCriticarPreenchimentoParcialDasAliquotasNominaisAPartirDe2027":
            an = op.itens[0].aliquotas_nominais
            assert an is not None
            op.itens[0] = replace(op.itens[0], aliquotas_nominais=replace(an, ibs_estadual=None, ibs_municipal=None))
        elif base == "deveCriticarAliquotaImpostoSeletivoNaoResolvivelAPartirDe2027":
            op = _informar_is(op)
        elif base == "deveValidarCstImpostoSeletivoAntesDaAusenciaDeAliquotaEm2027":
            op = _informar_is(op)
            isg = op.itens[0].imposto_seletivo
            assert isg
            op.itens[0] = replace(op.itens[0], imposto_seletivo=replace(isg, cst="999"))
        elif base == "deveValidarClassificacaoImpostoSeletivoAntesDaAusenciaDeAliquotaEm2027":
            op = _informar_is(op)
            isg = op.itens[0].imposto_seletivo
            assert isg
            op.itens[0] = replace(op.itens[0], imposto_seletivo=replace(isg, c_class_trib="999999"))
        elif base == "deveValidarVinculoCstDaClassificacaoIsAntesDaAusenciaDeAliquotaEm2027":
            op = _informar_is(op)
            isg = op.itens[0].imposto_seletivo
            assert isg
            op.itens[0] = replace(op.itens[0], imposto_seletivo=replace(isg, c_class_trib="100001"))
        elif base == "deveCalcularComAliquotaImpostoSeletivoInformadaAPartirDe2027":
            op = _informar_is(op)
            an = op.itens[0].aliquotas_nominais
            assert an is not None
            op.itens[0] = replace(
                op.itens[0],
                aliquotas_nominais=replace(an, imposto_seletivo=AliquotasNominaisImpostoSeletivo(ad_valorem=Decimal("13.0"), ad_rem=None)),
            )
    return op


def _run_nfcom_rigido(base: str, exc_name: str | None) -> None:
    from calculadora_rtc_regime_regular.nomenclatura import (
        ClassificacaoTributariaRepositorioSqlite,
        ModoValidacaoNomenclatura,
        SiglaDFe,
    )

    data = date(2026, 1, 15)
    with conectar() as conexao:
        stack = montar_nomenclatura_sqlite(conexao)
        clas = ClassificacaoTributariaService(
            ClassificacaoTributariaRepositorioSqlite(conexao)
        ).buscar_classificacao_tributaria_cbs_ibs("200044", data)
        ncm = "87100000" if base == "teste_rigido_ncmInformadoErro" else None
        nbs = "115012000" if base == "teste_rigido_nbsInformadaErro" else None
        ctx = (
            pytest.raises(NomenclaturaNaoPermitidaTipoDfeException)
            if exc_name
            else nullcontext()
        )
        with ctx:
            stack.validar(
                SiglaDFe.NFCOM,
                clas.id,
                clas.codigo,
                ncm,
                nbs,
                data,
                "CBS e IBS",
                ModoValidacaoNomenclatura.RIGIDO,
            )


def _run_repo_case(classname: str, base: str, index: int | None, exc_name: str | None) -> None:
    from calculadora_rtc_regime_regular.nomenclatura import (
        ClassificacaoTributariaRepositorioSqlite,
        NbsAplicavelRepositorioSqlite,
        NcmAplicavelRepositorioSqlite,
    )

    with conectar() as conexao:
        nomenclatura = montar_nomenclatura_sqlite(conexao)
        ncm_svc = nomenclatura._ncm_aplicavel_service
        ncm_repo = NcmAplicavelRepositorioSqlite(conexao)
        nbs_repo = NbsAplicavelRepositorioSqlite(conexao)
        clas_svc = ClassificacaoTributariaService(ClassificacaoTributariaRepositorioSqlite(conexao))
        if base == "teste_temNcm_filtraVigencia":
            assert ncm_repo.tem(139, date(2026, 6, 1)) is False
            assert ncm_repo.tem(139, date(2027, 6, 1)) is True
            return
        if base == "teste_temNbs_filtraVigencia":
            assert nbs_repo.tem(139, date(2026, 6, 1)) is False
            assert nbs_repo.tem(139, date(2027, 6, 1)) is True
            return
        if base == "teste_ncmExcepcionadoRejeitado":
            clas = clas_svc.buscar_classificacao_tributaria_cbs_ibs("200003", date(2026, 6, 1))
            with pytest.raises(NcmNaoVinculadaException):
                ncm_svc.criticar_ncm_contra_anexo("02074300", clas.id, clas.codigo, date(2026, 6, 1), "CBS e IBS")
            return
        if base == "teste_ncmNaoExcepcionadoAceito":
            clas = clas_svc.buscar_classificacao_tributaria_cbs_ibs("200003", date(2026, 6, 1))
            ncm_svc.criticar_ncm_contra_anexo("02071100", clas.id, clas.codigo, date(2026, 6, 1), "CBS e IBS")
            return
        if base == "teste_anexoXv_07108000Aceito":
            datas = ("2026-01-01", "2026-06-01")
            assert index is not None
            data_v = date.fromisoformat(datas[index - 1])
            clas = clas_svc.buscar_classificacao_tributaria_cbs_ibs("200014", data_v)
            ncm_svc.criticar_ncm_contra_anexo("07108000", clas.id, clas.codigo, data_v, "CBS e IBS")
            return
        if base == "teste_anexoXv_07095Rejeitado":
            datas = ("2026-01-01", "2026-06-01")
            assert index is not None
            data_v = date.fromisoformat(datas[index - 1])
            clas = clas_svc.buscar_classificacao_tributaria_cbs_ibs("200014", data_v)
            with pytest.raises(NcmNaoVinculadaException):
                ncm_svc.criticar_ncm_contra_anexo("07095100", clas.id, clas.codigo, data_v, "CBS e IBS")
            return
        if base == "teste_ncmForaDoAnexoRejeitado":
            clas = clas_svc.buscar_classificacao_tributaria_cbs_ibs("200003", date(2026, 6, 1))
            with pytest.raises(NcmNaoVinculadaException):
                ncm_svc.criticar_ncm_contra_anexo("24021000", clas.id, clas.codigo, date(2026, 6, 1), "CBS e IBS")
            return
    raise AssertionError(f"caso repo não implementado: {base}")


def _run_case(classname: str, name: str, svc: str, exc_name: str | None, json_path: str | None, pedagio_svc: PedagioService | None):
    base = _base_name(name)
    index = _param_index(name)
    if classname.endswith("Teste_tpdoc_3_NfcomPermissivoRigido") and base.startswith("teste_rigido_"):
        _run_nfcom_rigido(base, exc_name)
        return
    if svc == "repo":
        _run_repo_case(classname, base, index, exc_name)
        return
    if svc == "ped":
        assert json_path and pedagio_svc
        entrada = _load_pedagio(json_path)
        if exc_name == "MunicipioNaoEncontradoException":
            ctx = pytest.raises(PedagioMunicipioNaoEncontrado)
        elif exc_name == "MunicipioNaoPertencenteException":
            ctx = pytest.raises(PedagioMunicipioNaoPertencente)
        elif exc_name:
            ctx = pytest.raises(JAVA_EXCEPTIONS[exc_name])
        else:
            ctx = nullcontext()
        with ctx:
            out = pedagio_svc.calcular_cibs(entrada)
        if not exc_name and base == "deveCalcularTributoPedagio":
            assert out is not None and len(out.trechos) == 4
        return
    op = _load_operacao(json_path) if json_path else None
    if op is not None and classname.endswith("Teste_validacao_AliquotasNominaisPorAnoFatoGerador"):
        op = _mutate(classname, base, op, index)
    elif op is not None and not (classname.endswith("Teste_tpdoc_8_ImpostoSeletivo") and base == "teste_tpDocForaWhitelist_grupoSemIncidenciaValidaCst"):
        op = deepcopy(op)
        op = _mutate(classname, base, op, index)
    if classname.endswith("Teste_tpdoc_8_ImpostoSeletivo") and base == "teste_tpDocForaWhitelist_grupoSemIncidenciaValidaCst":
        op = _load_operacao("entradas/tpdoc/tpdoc_imposto_seletivo_superfluo_2026.json")
    if classname.endswith("Teste_validacao_99") or classname.endswith("Teste_validacao_11_NomenclaturaException"):
        assert op is not None
        out = _CALC.calcular_tributos(op)
        assert out is not None
        return
    if base == "deveProcessarOperacaoComObservabilidade":
        roc = _OBS.processar_operacao(op, _BASE_URL)
        assert roc.objetos and len(roc.objetos) == 6
        return
    if base == "deveLancarExcecaoQuandoErroGlobal4xx":
        path = "entradas/calculoscorretos/observabilidade/entrada_com_erro_global.json"
        op = _load_operacao(path)
        with pytest.raises(ErrosCalculoException):
            _OBS.processar_operacao(op, _BASE_URL)
        return
    if base == "deveLancarExcecaoQuandoErroGlobal5xx":
        op = _load_operacao("entradas/calculoscorretos/observabilidade/entrada_com_erro_422.json")
        with pytest.raises(ErrosCalculoException):
            _OBS.processar_operacao(op, _BASE_URL)
        return
    if base == "deveLancarErroFaltaImplementacaoNoServico":
        with pytest.raises(ErroFaltaImplementacaoException):
            _CALC.calcular_tributos(op)
        return
    if base == "deveProcessarComEstadoNaoImplementadoNoServicoObservabilidade":
        roc = _OBS.processar_operacao(op, _BASE_URL)
        assert roc.objetos[0].estado_item == EstadoItemEnum.NAO_IMPLEMENTADO
        return
    if base == "teste_observabilidade_apenasItemAfetadoFalha":
        roc = _OBS.processar_operacao(op, _BASE_URL)
        assert roc.objetos[0].estado_item == EstadoItemEnum.CALCULADO
        assert roc.objetos[1].estado_item == EstadoItemEnum.INCONSISTENCIA_ENTRADA
        assert roc.objetos[1].erros and roc.objetos[1].erros[0].code == "REG-029"
        return
    if base.startswith("observabilidadeServicoDeveLancarExcecaoParaDFeNaoTratado"):
        with pytest.raises(ErrosCalculoException) as excinfo:
            _OBS.processar_operacao(op, _BASE_URL)
        erros = excinfo.value.get_erros()
        assert any(e.title == "Tipo de documento fiscal não tratado" for e in erros)
        return
    ctx = pytest.raises(JAVA_EXCEPTIONS[exc_name]) if exc_name else nullcontext()
    with ctx:
        if svc == "obs":
            _OBS.processar_operacao(op, _BASE_URL)
        else:
            _CALC.calcular_tributos(op)



JAVA_CASES = [
    ('br.gov.serpro.rtc.testesintegracao.observabilidade.ObservabilidadeErroGlobalServiceTest', 'deveLancarExcecaoQuandoErroGlobal4xx(Resource)', 'obs', 'ErrosCalculoException', 'entradas/calculoscorretos/observabilidade/entrada_com_erro_global.json', False),
    ('br.gov.serpro.rtc.testesintegracao.observabilidade.ObservabilidadeErroGlobalServiceTest', 'deveLancarExcecaoQuandoErroGlobal5xx(Resource)', 'obs', 'ErrosCalculoException', 'entradas/calculoscorretos/observabilidade/entrada_com_erro_global.json', False),
    ('br.gov.serpro.rtc.testesintegracao.observabilidade.ObservabilidadeServiceTest', 'deveProcessarOperacaoComObservabilidade(Resource)', 'obs', None, 'entradas/calculoscorretos/observabilidade/entrada.json', False),
    ('br.gov.serpro.rtc.testesintegracao.pedagio.PedagioServiceTest', 'deveCalcularTributoPedagio(Resource)', 'ped', None, 'entradas/pedagio/entrada.json', False),
    ('br.gov.serpro.rtc.testesintegracao.tpdoc.Teste_tpdoc_10_NfseAnexoIxSemNcm', 'teste_ncmDoAnexoBloqueado200038', 'calc', 'NomenclaturaIncompativelTipoDfeException', 'entradas/tpdoc/tpdoc_nfse_515001.json', False),
    ('br.gov.serpro.rtc.testesintegracao.tpdoc.Teste_tpdoc_10_NfseAnexoIxSemNcm', 'teste_semNomenclaturaErro', 'calc', 'NbsCompletoNaoInformadoException', 'entradas/tpdoc/tpdoc_nfse_515001.json', False),
    ('br.gov.serpro.rtc.testesintegracao.tpdoc.Teste_tpdoc_10_NfseAnexoIxSemNcm', 'teste_nbsValidaDoAnexoPassa', 'calc', None, 'entradas/tpdoc/tpdoc_nfse_515001.json', False),
    ('br.gov.serpro.rtc.testesintegracao.tpdoc.Teste_tpdoc_10_NfseAnexoIxSemNcm', 'teste_nbsForaDoAnexoErro', 'calc', 'NbsNaoVinculadaException', 'entradas/tpdoc/tpdoc_nfse_515001.json', False),
    ('br.gov.serpro.rtc.testesintegracao.tpdoc.Teste_tpdoc_10_NfseAnexoIxSemNcm', 'teste_ncmDoAnexoBloqueado', 'calc', 'NomenclaturaIncompativelTipoDfeException', 'entradas/tpdoc/tpdoc_nfse_515001.json', False),
    ('br.gov.serpro.rtc.testesintegracao.tpdoc.Teste_tpdoc_1_NfeNomenclaturaNcm', 'teste_nbsInformadaErro', 'calc', 'NomenclaturaIncompativelTipoDfeException', 'entradas/tpdoc/tpdoc_nfe_200043.json', False),
    ('br.gov.serpro.rtc.testesintegracao.tpdoc.Teste_tpdoc_1_NfeNomenclaturaNcm', 'teste_ncmForaDoAnexoErro', 'calc', 'NcmNaoVinculadaException', 'entradas/tpdoc/tpdoc_nfe_200043.json', False),
    ('br.gov.serpro.rtc.testesintegracao.tpdoc.Teste_tpdoc_1_NfeNomenclaturaNcm', 'teste_ncmValidoDoAnexoPassa', 'calc', None, 'entradas/tpdoc/tpdoc_nfe_200043.json', False),
    ('br.gov.serpro.rtc.testesintegracao.tpdoc.Teste_tpdoc_1_NfeNomenclaturaNcm', 'teste_ncmAusenteErro', 'calc', 'NcmCompletoNaoInformadoException', 'entradas/tpdoc/tpdoc_nfe_200043.json', False),
    ('br.gov.serpro.rtc.testesintegracao.tpdoc.Teste_tpdoc_2_NfseNomenclaturaMisto', 'teste_nenhumaNomenclaturaErro', 'calc', 'NomenclaturaObrigatoriaNaoInformadaException', 'entradas/tpdoc/tpdoc_nfse_200043.json', False),
    ('br.gov.serpro.rtc.testesintegracao.tpdoc.Teste_tpdoc_2_NfseNomenclaturaMisto', 'teste_nbsValidaDoAnexoPassa', 'calc', None, 'entradas/tpdoc/tpdoc_nfse_200043.json', False),
    ('br.gov.serpro.rtc.testesintegracao.tpdoc.Teste_tpdoc_2_NfseNomenclaturaMisto', 'teste_nbsForaDoAnexoErro', 'calc', 'NbsNaoVinculadaException', 'entradas/tpdoc/tpdoc_nfse_200043.json', False),
    ('br.gov.serpro.rtc.testesintegracao.tpdoc.Teste_tpdoc_2_NfseNomenclaturaMisto', 'teste_ncmValidoDoAnexoPassa', 'calc', None, 'entradas/tpdoc/tpdoc_nfse_200043.json', False),
    ('br.gov.serpro.rtc.testesintegracao.tpdoc.Teste_tpdoc_3_NfcomPermissivoRigido', 'teste_permissivo_ncmValidoPassa', 'calc', None, 'entradas/tpdoc/tpdoc_nfcom_200044.json', False),
    ('br.gov.serpro.rtc.testesintegracao.tpdoc.Teste_tpdoc_3_NfcomPermissivoRigido', 'teste_permissivo_nbsValidaPassa', 'calc', None, 'entradas/tpdoc/tpdoc_nfcom_200044.json', False),
    ('br.gov.serpro.rtc.testesintegracao.tpdoc.Teste_tpdoc_3_NfcomPermissivoRigido', 'teste_semNomenclaturaPassa', 'calc', None, 'entradas/tpdoc/tpdoc_nfcom_200044.json', False),
    ('br.gov.serpro.rtc.testesintegracao.tpdoc.Teste_tpdoc_3_NfcomPermissivoRigido', 'teste_permissivo_nbsInvalidaErro', 'calc', 'NbsNaoVinculadaException', 'entradas/tpdoc/tpdoc_nfcom_200044.json', False),
    ('br.gov.serpro.rtc.testesintegracao.tpdoc.Teste_tpdoc_3_NfcomPermissivoRigido', 'teste_rigido_nbsInformadaErro', 'calc', 'NomenclaturaNaoPermitidaTipoDfeException', 'entradas/tpdoc/tpdoc_nfcom_200044.json', False),
    ('br.gov.serpro.rtc.testesintegracao.tpdoc.Teste_tpdoc_3_NfcomPermissivoRigido', 'teste_rigido_ncmInformadoErro', 'calc', 'NomenclaturaNaoPermitidaTipoDfeException', 'entradas/tpdoc/tpdoc_nfcom_200044.json', False),
    ('br.gov.serpro.rtc.testesintegracao.tpdoc.Teste_tpdoc_3_NfcomPermissivoRigido', 'teste_permissivo_ncmInvalidoErro', 'calc', 'NcmNaoVinculadaException', 'entradas/tpdoc/tpdoc_nfcom_200044.json', False),
    ('br.gov.serpro.rtc.testesintegracao.tpdoc.Teste_tpdoc_3_NfcomPermissivoRigido', 'teste_rigido_semNomenclaturaPassa', 'calc', None, 'entradas/tpdoc/tpdoc_nfcom_200044.json', False),
    ('br.gov.serpro.rtc.testesintegracao.tpdoc.Teste_tpdoc_4_ClassificacaoSemAnexo', 'teste_semTpDoc_ncmAceito', 'calc', None, 'entradas/tpdoc/tpdoc_sem_anexo_000001.json', False),
    ('br.gov.serpro.rtc.testesintegracao.tpdoc.Teste_tpdoc_4_ClassificacaoSemAnexo', 'teste_comTpDoc_semNomenclaturaPassa', 'calc', None, 'entradas/tpdoc/tpdoc_sem_anexo_000001.json', False),
    ('br.gov.serpro.rtc.testesintegracao.tpdoc.Teste_tpdoc_4_ClassificacaoSemAnexo', 'teste_comTpDoc_nbsEmNfeErro', 'calc', 'NomenclaturaIncompativelTipoDfeException', 'entradas/tpdoc/tpdoc_sem_anexo_000001.json', False),
    ('br.gov.serpro.rtc.testesintegracao.tpdoc.Teste_tpdoc_4_ClassificacaoSemAnexo', 'teste_semTpDoc_semNomenclaturaPassa', 'calc', None, 'entradas/tpdoc/tpdoc_sem_anexo_000001.json', False),
    ('br.gov.serpro.rtc.testesintegracao.tpdoc.Teste_tpdoc_4_ClassificacaoSemAnexo', 'teste_comTpDoc_ncmAceitoSemCritica', 'calc', None, 'entradas/tpdoc/tpdoc_sem_anexo_000001.json', False),
    ('br.gov.serpro.rtc.testesintegracao.tpdoc.Teste_tpdoc_4_ClassificacaoSemAnexo', 'teste_comTpDocNfse_nbsAceita', 'calc', None, 'entradas/tpdoc/tpdoc_sem_anexo_000001.json', False),
    ('br.gov.serpro.rtc.testesintegracao.tpdoc.Teste_tpdoc_5_TpDocInvalido', 'teste_service_tpDocInexistente', 'calc', 'TipoDfeNaoEncontradoException', 'entradas/tpdoc/tpdoc_sem_anexo_000001.json', False),
    ('br.gov.serpro.rtc.testesintegracao.tpdoc.Teste_tpdoc_5_TpDocInvalido', 'teste_service_tpDocForaDeVigencia', 'calc', 'TipoDfeNaoEncontradoException', 'entradas/tpdoc/tpdoc_sem_anexo_000001.json', False),
    ('br.gov.serpro.rtc.testesintegracao.tpdoc.Teste_tpdoc_5_TpDocInvalido', 'teste_observabilidade_tpDocInexistente', 'obs', 'ErrosCalculoException', 'entradas/tpdoc/tpdoc_sem_anexo_000001.json', False),
    ('br.gov.serpro.rtc.testesintegracao.tpdoc.Teste_tpdoc_6_ClassificacaoSemVinculoTipoDfe', 'teste_observabilidade_apenasItemAfetadoFalha', 'obs', None, 'entradas/tpdoc/tpdoc_observabilidade_vinculo.json', False),
    ('br.gov.serpro.rtc.testesintegracao.tpdoc.Teste_tpdoc_6_ClassificacaoSemVinculoTipoDfe', 'teste_service_classificacaoSemVinculoErro', 'calc', 'ClassificacaoTributariaNaoVinculadaTipoDfeException', 'entradas/tpdoc/tpdoc_observabilidade_vinculo.json', False),
    ('br.gov.serpro.rtc.testesintegracao.tpdoc.Teste_tpdoc_7_TributacaoRegular', 'teste_tributacaoRegularVinculadaPassa', 'calc', None, 'entradas/tpdoc/tpdoc_tributacao_regular.json', False),
    ('br.gov.serpro.rtc.testesintegracao.tpdoc.Teste_tpdoc_7_TributacaoRegular', 'teste_tributacaoRegularSemVinculoErro', 'calc', 'ClassificacaoTributariaNaoVinculadaTipoDfeException', 'entradas/tpdoc/tpdoc_tributacao_regular.json', False),
    ('br.gov.serpro.rtc.testesintegracao.tpdoc.Teste_tpdoc_7_TributacaoRegular', 'teste_tributacaoRegularNcmForaDoAnexoErro', 'calc', 'NcmNaoVinculadaException', 'entradas/tpdoc/tpdoc_tributacao_regular.json', False),
    ('br.gov.serpro.rtc.testesintegracao.tpdoc.Teste_tpdoc_7_TributacaoRegular', 'teste_tributacaoRegularNaoExigidaSemVinculoErro', 'calc', 'ClassificacaoTributariaNaoVinculadaTipoDfeException', 'entradas/tpdoc/tpdoc_tributacao_regular.json', False),
    ('br.gov.serpro.rtc.testesintegracao.tpdoc.Teste_tpdoc_8_ImpostoSeletivo', 'teste_tpDocForaWhitelist_grupoSemIncidenciaValidaCst', 'calc', 'SituacaoTributariaNaoEncontradaException', 'entradas/tpdoc/tpdoc_imposto_seletivo_2027.json', False),
    ('br.gov.serpro.rtc.testesintegracao.tpdoc.Teste_tpdoc_8_ImpostoSeletivo', 'teste_tpDoc65_impostoSeletivoAceito', 'calc', None, 'entradas/tpdoc/tpdoc_imposto_seletivo_2027.json', False),
    ('br.gov.serpro.rtc.testesintegracao.tpdoc.Teste_tpdoc_8_ImpostoSeletivo', 'teste_tpDoc55_impostoSeletivoAceito', 'calc', None, 'entradas/tpdoc/tpdoc_imposto_seletivo_2027.json', False),
    ('br.gov.serpro.rtc.testesintegracao.tpdoc.Teste_tpdoc_8_ImpostoSeletivo', 'teste_tpDocForaWhitelist_ncmExigeIsErro', 'calc', 'ImpostoSeletivoNaoAdmitidoTipoDfeException', 'entradas/tpdoc/tpdoc_imposto_seletivo_2027.json', False),
    ('br.gov.serpro.rtc.testesintegracao.tpdoc.Teste_tpdoc_8_ImpostoSeletivo', 'teste_semTpDoc_comportamentoAtual', 'calc', None, 'entradas/tpdoc/tpdoc_imposto_seletivo_2027.json', False),
    ('br.gov.serpro.rtc.testesintegracao.tpdoc.Teste_tpdoc_9_RegressaoAnexoVigenciaExcecao', 'teste_anexoXv_07095Rejeitado(String)[1]', 'repo', 'NcmNaoVinculadaException', None, False),
    ('br.gov.serpro.rtc.testesintegracao.tpdoc.Teste_tpdoc_9_RegressaoAnexoVigenciaExcecao', 'teste_anexoXv_07095Rejeitado(String)[2]', 'repo', 'NcmNaoVinculadaException', None, False),
    ('br.gov.serpro.rtc.testesintegracao.tpdoc.Teste_tpdoc_9_RegressaoAnexoVigenciaExcecao', 'teste_ncmExcepcionadoRejeitado', 'repo', 'NcmNaoVinculadaException', None, False),
    ('br.gov.serpro.rtc.testesintegracao.tpdoc.Teste_tpdoc_9_RegressaoAnexoVigenciaExcecao', 'teste_ncmNaoExcepcionadoAceito', 'repo', None, None, False),
    ('br.gov.serpro.rtc.testesintegracao.tpdoc.Teste_tpdoc_9_RegressaoAnexoVigenciaExcecao', 'teste_anexoXv_07108000Aceito(String)[1]', 'repo', None, None, False),
    ('br.gov.serpro.rtc.testesintegracao.tpdoc.Teste_tpdoc_9_RegressaoAnexoVigenciaExcecao', 'teste_anexoXv_07108000Aceito(String)[2]', 'repo', None, None, False),
    ('br.gov.serpro.rtc.testesintegracao.tpdoc.Teste_tpdoc_9_RegressaoAnexoVigenciaExcecao', 'teste_temNbs_filtraVigencia', 'repo', None, None, False),
    ('br.gov.serpro.rtc.testesintegracao.tpdoc.Teste_tpdoc_9_RegressaoAnexoVigenciaExcecao', 'teste_ncmForaDoAnexoRejeitado', 'repo', 'NcmNaoVinculadaException', None, False),
    ('br.gov.serpro.rtc.testesintegracao.tpdoc.Teste_tpdoc_9_RegressaoAnexoVigenciaExcecao', 'teste_temNcm_filtraVigencia', 'repo', None, None, False),
    ('br.gov.serpro.rtc.testesintegracao.validacoes.negocio.Teste_validacao_10_SituacaoTributariaNaoEncontradaException', 'teste_service_CalcularTributos', 'calc', 'SituacaoTributariaNaoEncontradaException', 'entradas/validacoes/Teste_validacao_10_SituacaoTributariaNaoEncontradaException.json', False),
    ('br.gov.serpro.rtc.testesintegracao.validacoes.negocio.Teste_validacao_11_NomenclaturaException', 'teste_service_CalcularTributos', 'calc', None, 'entradas/validacoes/Teste_validacao_11_NomenclaturaException.json', False),
    ('br.gov.serpro.rtc.testesintegracao.validacoes.negocio.Teste_validacao_12_IncompatibilidadeSuspensaoException', 'teste_service_CalcularTributos', 'calc', 'IncompatibilidadeSuspensaoException', 'entradas/validacoes/Teste_validacao_12_IncompatibilidadeSuspensaoException.json', False),
    ('br.gov.serpro.rtc.testesintegracao.validacoes.negocio.Teste_validacao_13_TributacaoRegularNaoInformadaException', 'teste_service_CalcularTributos', 'calc', 'TributacaoRegularNaoInformadaException', 'entradas/validacoes/Teste_validacao_13_TributacaoRegularNaoInformadaException.json', False),
    ('br.gov.serpro.rtc.testesintegracao.validacoes.negocio.Teste_validacao_14_TributacaoRegularInformadaIndevidamenteException', 'teste_service_CalcularTributos', 'calc', 'TributacaoRegularInformadaIndevidamenteException', 'entradas/validacoes/Teste_validacao_14_TributacaoRegularInformadaIndevidamenteException.json', True),
    ('br.gov.serpro.rtc.testesintegracao.validacoes.negocio.Teste_validacao_15_ImpostoSeletivoNaoInformadoException', 'teste_service_CalcularTributos', 'calc', 'ImpostoSeletivoNaoInformadoException', 'entradas/validacoes/Teste_validacao_15_ImpostoSeletivoNaoInformadoException.json', False),
    ('br.gov.serpro.rtc.testesintegracao.validacoes.negocio.Teste_validacao_16_ImpostoSeletivoInformadoIndevidamenteException', 'teste_service_CalcularTributos', 'calc', 'ImpostoSeletivoInformadoIndevidamenteException', 'entradas/validacoes/Teste_validacao_16_ImpostoSeletivoInformadoIndevidamenteException.json', True),
    ('br.gov.serpro.rtc.testesintegracao.validacoes.negocio.Teste_validacao_17_MunicipioNaoEncontradoException', 'teste_service_CalcularTributos', 'calc', 'MunicipioNaoEncontradoException', 'entradas/validacoes/Teste_validacao_17_MunicipioNaoEncontradoException.json', False),
    ('br.gov.serpro.rtc.testesintegracao.validacoes.negocio.Teste_validacao_18_UfNaoEncontradaException', 'teste_service_CalcularTributos', 'calc', 'UfNaoEncontradaException', 'entradas/validacoes/Teste_validacao_18_UfNaoEncontradaException.json', False),
    ('br.gov.serpro.rtc.testesintegracao.validacoes.negocio.Teste_validacao_19_MunicipioNaoPertencenteException', 'teste_service_CalcularTributos', 'calc', 'MunicipioNaoPertencenteException', 'entradas/validacoes/Teste_validacao_19_MunicipioNaoPertencenteException.json', False),
    ('br.gov.serpro.rtc.testesintegracao.validacoes.negocio.Teste_validacao_1_NcmNaoEncontradaException', 'teste_service_CalcularTributos', 'calc', 'NcmNaoEncontradaException', 'entradas/validacoes/Teste_validacao_1_NcmNaoEncontradaException.json', False),
    ('br.gov.serpro.rtc.testesintegracao.validacoes.negocio.Teste_validacao_21_DataFatoGeradorNaoInformadaException', 'teste_service_CalcularTributos', 'calc', 'DataFatoGeradorNaoInformadaException', 'entradas/validacoes/Teste_validacao_21_DataFatoGeradorNaoInformadaException.json', False),
    ('br.gov.serpro.rtc.testesintegracao.validacoes.negocio.Teste_validacao_22_ErroFaltaImplementacaoException', 'deveLancarErroFaltaImplementacaoNoServico', 'calc', None, 'entradas/validacoes/Teste_validacao_22_ErroFaltaImplementacaoException.json', False),
    ('br.gov.serpro.rtc.testesintegracao.validacoes.negocio.Teste_validacao_22_ErroFaltaImplementacaoException', 'deveProcessarComEstadoNaoImplementadoNoServicoObservabilidade', 'obs', None, 'entradas/validacoes/Teste_validacao_22_ErroFaltaImplementacaoException.json', False),
    ('br.gov.serpro.rtc.testesintegracao.validacoes.negocio.Teste_validacao_23_BaseCalculoNaoInformadaException', 'teste_service_CalcularTributos', 'calc', 'BaseCalculoNaoInformadaException', 'entradas/validacoes/Teste_validacao_23_BaseCalculoNaoInformadaException.json', False),
    ('br.gov.serpro.rtc.testesintegracao.validacoes.negocio.Teste_validacao_24_BaseCalculoInconsistenteException', 'teste_service_CalcularTributos', 'calc', 'BaseCalculoInconsistenteException', 'entradas/validacoes/Teste_validacao_24_BaseCalculoInconsistenteException.json', False),
    ('br.gov.serpro.rtc.testesintegracao.validacoes.negocio.Teste_validacao_25_BaseCalculoMenorBaseCalculoImpostoSeletivoException', 'teste_service_CalcularTributos', 'calc', 'BaseCalculoMenorBaseCalculoImpostoSeletivoException', 'entradas/validacoes/Teste_validacao_25_BaseCalculoMenorBaseCalculoImpostoSeletivoException.json', False),
    ('br.gov.serpro.rtc.testesintegracao.validacoes.negocio.Teste_validacao_26_TipoDfeNaoTratadoException', 'servicoDeveCalcularTributosComSucessoParaDFeTratado(int)[1]', 'calc', None, 'entradas/validacoes/Teste_validacao_26_TipoDfeNaoTratadoException.json', False),
    ('br.gov.serpro.rtc.testesintegracao.validacoes.negocio.Teste_validacao_26_TipoDfeNaoTratadoException', 'servicoDeveCalcularTributosComSucessoParaDFeTratado(int)[2]', 'calc', None, 'entradas/validacoes/Teste_validacao_26_TipoDfeNaoTratadoException.json', False),
    ('br.gov.serpro.rtc.testesintegracao.validacoes.negocio.Teste_validacao_26_TipoDfeNaoTratadoException', 'servicoDeveCalcularTributosComSucessoParaDFeTratado(int)[3]', 'calc', None, 'entradas/validacoes/Teste_validacao_26_TipoDfeNaoTratadoException.json', False),
    ('br.gov.serpro.rtc.testesintegracao.validacoes.negocio.Teste_validacao_26_TipoDfeNaoTratadoException', 'servicoDeveCalcularTributosComSucessoParaDFeTratado(int)[4]', 'calc', None, 'entradas/validacoes/Teste_validacao_26_TipoDfeNaoTratadoException.json', False),
    ('br.gov.serpro.rtc.testesintegracao.validacoes.negocio.Teste_validacao_26_TipoDfeNaoTratadoException', 'servicoDeveCalcularTributosComSucessoParaDFeTratado(int)[5]', 'calc', None, 'entradas/validacoes/Teste_validacao_26_TipoDfeNaoTratadoException.json', False),
    ('br.gov.serpro.rtc.testesintegracao.validacoes.negocio.Teste_validacao_26_TipoDfeNaoTratadoException', 'servicoDeveCalcularTributosComSucessoParaDFeTratado(int)[6]', 'calc', None, 'entradas/validacoes/Teste_validacao_26_TipoDfeNaoTratadoException.json', False),
    ('br.gov.serpro.rtc.testesintegracao.validacoes.negocio.Teste_validacao_26_TipoDfeNaoTratadoException', 'servicoDeveCalcularTributosComSucessoParaDFeTratado(int)[7]', 'calc', None, 'entradas/validacoes/Teste_validacao_26_TipoDfeNaoTratadoException.json', False),
    ('br.gov.serpro.rtc.testesintegracao.validacoes.negocio.Teste_validacao_26_TipoDfeNaoTratadoException', 'servicoDeveCalcularTributosComSucessoParaDFeTratado(int)[8]', 'calc', None, 'entradas/validacoes/Teste_validacao_26_TipoDfeNaoTratadoException.json', False),
    ('br.gov.serpro.rtc.testesintegracao.validacoes.negocio.Teste_validacao_26_TipoDfeNaoTratadoException', 'servicoDeveCalcularTributosComSucessoParaDFeTratado(int)[9]', 'calc', None, 'entradas/validacoes/Teste_validacao_26_TipoDfeNaoTratadoException.json', False),
    ('br.gov.serpro.rtc.testesintegracao.validacoes.negocio.Teste_validacao_26_TipoDfeNaoTratadoException', 'servicoDeveCalcularTributosComSucessoParaDFeTratado(int)[10]', 'calc', None, 'entradas/validacoes/Teste_validacao_26_TipoDfeNaoTratadoException.json', False),
    ('br.gov.serpro.rtc.testesintegracao.validacoes.negocio.Teste_validacao_26_TipoDfeNaoTratadoException', 'servicoDeveCalcularTributosComSucessoParaDFeTratado(int)[11]', 'calc', None, 'entradas/validacoes/Teste_validacao_26_TipoDfeNaoTratadoException.json', False),
    ('br.gov.serpro.rtc.testesintegracao.validacoes.negocio.Teste_validacao_26_TipoDfeNaoTratadoException', 'servicoDeveLancarExcecaoParaDFeNaoTratado(int)[1]', 'calc', 'TipoDfeNaoTratadoException', 'entradas/validacoes/Teste_validacao_26_TipoDfeNaoTratadoException.json', False),
    ('br.gov.serpro.rtc.testesintegracao.validacoes.negocio.Teste_validacao_26_TipoDfeNaoTratadoException', 'servicoDeveLancarExcecaoParaDFeNaoTratado(int)[2]', 'calc', 'TipoDfeNaoTratadoException', 'entradas/validacoes/Teste_validacao_26_TipoDfeNaoTratadoException.json', False),
    ('br.gov.serpro.rtc.testesintegracao.validacoes.negocio.Teste_validacao_26_TipoDfeNaoTratadoException', 'servicoDeveLancarExcecaoParaDFeNaoTratado(int)[3]', 'calc', 'TipoDfeNaoTratadoException', 'entradas/validacoes/Teste_validacao_26_TipoDfeNaoTratadoException.json', False),
    ('br.gov.serpro.rtc.testesintegracao.validacoes.negocio.Teste_validacao_26_TipoDfeNaoTratadoException', 'servicoDeveLancarExcecaoParaDFeNaoTratado(int)[4]', 'calc', 'TipoDfeNaoTratadoException', 'entradas/validacoes/Teste_validacao_26_TipoDfeNaoTratadoException.json', False),
    ('br.gov.serpro.rtc.testesintegracao.validacoes.negocio.Teste_validacao_26_TipoDfeNaoTratadoException', 'observabilidadeServicoDeveLancarExcecaoParaDFeNaoTratado(int)[1]', 'obs', 'ErrosCalculoException', 'entradas/validacoes/Teste_validacao_26_TipoDfeNaoTratadoException.json', False),
    ('br.gov.serpro.rtc.testesintegracao.validacoes.negocio.Teste_validacao_26_TipoDfeNaoTratadoException', 'observabilidadeServicoDeveLancarExcecaoParaDFeNaoTratado(int)[2]', 'obs', 'ErrosCalculoException', 'entradas/validacoes/Teste_validacao_26_TipoDfeNaoTratadoException.json', False),
    ('br.gov.serpro.rtc.testesintegracao.validacoes.negocio.Teste_validacao_26_TipoDfeNaoTratadoException', 'observabilidadeServicoDeveLancarExcecaoParaDFeNaoTratado(int)[3]', 'obs', 'ErrosCalculoException', 'entradas/validacoes/Teste_validacao_26_TipoDfeNaoTratadoException.json', False),
    ('br.gov.serpro.rtc.testesintegracao.validacoes.negocio.Teste_validacao_26_TipoDfeNaoTratadoException', 'observabilidadeServicoDeveLancarExcecaoParaDFeNaoTratado(int)[4]', 'obs', 'ErrosCalculoException', 'entradas/validacoes/Teste_validacao_26_TipoDfeNaoTratadoException.json', False),
    ('br.gov.serpro.rtc.testesintegracao.validacoes.negocio.Teste_validacao_26_TipoDfeNaoTratadoException', 'observabilidadeServicoDeveProcessarComSucessoParaDFeTratado(int)[1]', 'obs', None, 'entradas/validacoes/Teste_validacao_26_TipoDfeNaoTratadoException.json', False),
    ('br.gov.serpro.rtc.testesintegracao.validacoes.negocio.Teste_validacao_26_TipoDfeNaoTratadoException', 'observabilidadeServicoDeveProcessarComSucessoParaDFeTratado(int)[2]', 'obs', None, 'entradas/validacoes/Teste_validacao_26_TipoDfeNaoTratadoException.json', False),
    ('br.gov.serpro.rtc.testesintegracao.validacoes.negocio.Teste_validacao_26_TipoDfeNaoTratadoException', 'observabilidadeServicoDeveProcessarComSucessoParaDFeTratado(int)[3]', 'obs', None, 'entradas/validacoes/Teste_validacao_26_TipoDfeNaoTratadoException.json', False),
    ('br.gov.serpro.rtc.testesintegracao.validacoes.negocio.Teste_validacao_26_TipoDfeNaoTratadoException', 'observabilidadeServicoDeveProcessarComSucessoParaDFeTratado(int)[4]', 'obs', None, 'entradas/validacoes/Teste_validacao_26_TipoDfeNaoTratadoException.json', False),
    ('br.gov.serpro.rtc.testesintegracao.validacoes.negocio.Teste_validacao_26_TipoDfeNaoTratadoException', 'observabilidadeServicoDeveProcessarComSucessoParaDFeTratado(int)[5]', 'obs', None, 'entradas/validacoes/Teste_validacao_26_TipoDfeNaoTratadoException.json', False),
    ('br.gov.serpro.rtc.testesintegracao.validacoes.negocio.Teste_validacao_26_TipoDfeNaoTratadoException', 'observabilidadeServicoDeveProcessarComSucessoParaDFeTratado(int)[6]', 'obs', None, 'entradas/validacoes/Teste_validacao_26_TipoDfeNaoTratadoException.json', False),
    ('br.gov.serpro.rtc.testesintegracao.validacoes.negocio.Teste_validacao_26_TipoDfeNaoTratadoException', 'observabilidadeServicoDeveProcessarComSucessoParaDFeTratado(int)[7]', 'obs', None, 'entradas/validacoes/Teste_validacao_26_TipoDfeNaoTratadoException.json', False),
    ('br.gov.serpro.rtc.testesintegracao.validacoes.negocio.Teste_validacao_26_TipoDfeNaoTratadoException', 'observabilidadeServicoDeveProcessarComSucessoParaDFeTratado(int)[8]', 'obs', None, 'entradas/validacoes/Teste_validacao_26_TipoDfeNaoTratadoException.json', False),
    ('br.gov.serpro.rtc.testesintegracao.validacoes.negocio.Teste_validacao_26_TipoDfeNaoTratadoException', 'observabilidadeServicoDeveProcessarComSucessoParaDFeTratado(int)[9]', 'obs', None, 'entradas/validacoes/Teste_validacao_26_TipoDfeNaoTratadoException.json', False),
    ('br.gov.serpro.rtc.testesintegracao.validacoes.negocio.Teste_validacao_26_TipoDfeNaoTratadoException', 'observabilidadeServicoDeveProcessarComSucessoParaDFeTratado(int)[10]', 'obs', None, 'entradas/validacoes/Teste_validacao_26_TipoDfeNaoTratadoException.json', False),
    ('br.gov.serpro.rtc.testesintegracao.validacoes.negocio.Teste_validacao_26_TipoDfeNaoTratadoException', 'observabilidadeServicoDeveProcessarComSucessoParaDFeTratado(int)[11]', 'obs', None, 'entradas/validacoes/Teste_validacao_26_TipoDfeNaoTratadoException.json', False),
    ('br.gov.serpro.rtc.testesintegracao.validacoes.negocio.Teste_validacao_2_NcmNaoVinculadaException', 'teste_service_CalcularTributos', 'calc', 'NcmNaoVinculadaException', 'entradas/validacoes/Teste_validacao_2_NcmNaoVinculadaException.json', False),
    ('br.gov.serpro.rtc.testesintegracao.validacoes.negocio.Teste_validacao_3_NbsNaoEncontradaException', 'teste_service_CalcularTributos', 'calc', 'NbsNaoEncontradaException', 'entradas/validacoes/Teste_validacao_3_NbsNaoEncontradaException.json', False),
    ('br.gov.serpro.rtc.testesintegracao.validacoes.negocio.Teste_validacao_4_NbsNaoVinculadaException', 'teste_service_CalcularTributos', 'calc', 'NbsNaoVinculadaException', 'entradas/validacoes/Teste_validacao_4_NbsNaoVinculadaException.json', False),
    ('br.gov.serpro.rtc.testesintegracao.validacoes.negocio.Teste_validacao_6_NcmNbsSimultaneasException', 'teste_service_CalcularTributos', 'calc', 'NcmNbsSimultaneasException', 'entradas/validacoes/Teste_validacao_6_NcmNbsSimultaneasException.json', False),
    ('br.gov.serpro.rtc.testesintegracao.validacoes.negocio.Teste_validacao_7_ClassificacaoTributariaNaoEncontradaException', 'teste_service_CalcularTributos', 'calc', 'ClassificacaoTributariaNaoEncontradaException', 'entradas/validacoes/Teste_validacao_7_ClassificacaoTributariaNaoEncontradaException.json', False),
    ('br.gov.serpro.rtc.testesintegracao.validacoes.negocio.Teste_validacao_8_ClassificacaoTributariaNaoVinculadaException', 'teste_service_CalcularTributos', 'calc', 'ClassificacaoTributariaNaoVinculadaSituacaoTributariaException', 'entradas/validacoes/Teste_validacao_8_ClassificacaoTributariaNaoVinculadaException.json', False),
    ('br.gov.serpro.rtc.testesintegracao.validacoes.negocio.Teste_validacao_99', 'teste_service_CalcularTributos', 'calc', None, 'entradas/validacoes/Teste_validacao_99.json', False),
    ('br.gov.serpro.rtc.testesintegracao.validacoes.negocio.Teste_validacao_9_AliquotaAdRemNaoEncontradaException', 'teste_service_CalcularTributos', 'calc', 'AliquotaAdRemNaoEncontradaException', 'entradas/validacoes/Teste_validacao_9_AliquotaAdRemNaoEncontradaException.json', True),
    ('br.gov.serpro.rtc.testesintegracao.validacoes.negocio.Teste_validacao_AliquotasNominaisPorAnoFatoGerador', 'deveCriticarQualquerCampoDoGrupoAliquotasNominaisAte2026', 'calc', 'AliquotasNominaisInformadasIndevidamenteException', 'entradas/validacoes/Teste_validacao_15_ImpostoSeletivoNaoInformadoException.json', False),
    ('br.gov.serpro.rtc.testesintegracao.validacoes.negocio.Teste_validacao_AliquotasNominaisPorAnoFatoGerador', 'deveValidarCstImpostoSeletivoAntesDaAusenciaDeAliquotaEm2027', 'calc', 'SituacaoTributariaNaoEncontradaException', 'entradas/validacoes/Teste_validacao_15_ImpostoSeletivoNaoInformadoException.json', False),
    ('br.gov.serpro.rtc.testesintegracao.validacoes.negocio.Teste_validacao_AliquotasNominaisPorAnoFatoGerador', 'deveValidarCstDoGrupoImpostoSeletivoEm2026AntesDaBuscaDeAliquota', 'calc', 'SituacaoTributariaNaoEncontradaException', 'entradas/validacoes/Teste_validacao_15_ImpostoSeletivoNaoInformadoException.json', False),
    ('br.gov.serpro.rtc.testesintegracao.validacoes.negocio.Teste_validacao_AliquotasNominaisPorAnoFatoGerador', 'deveCalcularNormalmenteEm2026SemAliquotasNominais', 'calc', None, 'entradas/validacoes/Teste_validacao_15_ImpostoSeletivoNaoInformadoException.json', False),
    ('br.gov.serpro.rtc.testesintegracao.validacoes.negocio.Teste_validacao_AliquotasNominaisPorAnoFatoGerador', 'deveValidarClassificacaoImpostoSeletivoAntesDaAusenciaDeAliquotaEm2027', 'calc', 'ClassificacaoTributariaNaoEncontradaException', 'entradas/validacoes/Teste_validacao_15_ImpostoSeletivoNaoInformadoException.json', False),
    ('br.gov.serpro.rtc.testesintegracao.validacoes.negocio.Teste_validacao_AliquotasNominaisPorAnoFatoGerador', 'deveCriticarPreenchimentoParcialDasAliquotasNominaisAPartirDe2027', 'calc', 'AliquotasNominaisNaoInformadasException', 'entradas/validacoes/Teste_validacao_15_ImpostoSeletivoNaoInformadoException.json', False),
    ('br.gov.serpro.rtc.testesintegracao.validacoes.negocio.Teste_validacao_AliquotasNominaisPorAnoFatoGerador', 'deveValidarVinculoCstDaClassificacaoIsAntesDaAusenciaDeAliquotaEm2027', 'calc', 'ClassificacaoTributariaNaoVinculadaSituacaoTributariaException', 'entradas/validacoes/Teste_validacao_15_ImpostoSeletivoNaoInformadoException.json', False),
    ('br.gov.serpro.rtc.testesintegracao.validacoes.negocio.Teste_validacao_AliquotasNominaisPorAnoFatoGerador', 'deveCriticarAusenciaDeAliquotasNominaisAPartirDe2027', 'calc', 'AliquotasNominaisNaoInformadasException', 'entradas/validacoes/Teste_validacao_15_ImpostoSeletivoNaoInformadoException.json', False),
    ('br.gov.serpro.rtc.testesintegracao.validacoes.negocio.Teste_validacao_AliquotasNominaisPorAnoFatoGerador', 'deveCalcularComAliquotaImpostoSeletivoInformadaAPartirDe2027', 'calc', None, 'entradas/validacoes/Teste_validacao_15_ImpostoSeletivoNaoInformadoException.json', False),
    ('br.gov.serpro.rtc.testesintegracao.validacoes.negocio.Teste_validacao_AliquotasNominaisPorAnoFatoGerador', 'deveCriticarAliquotasNominaisInformadasAte2026', 'calc', 'AliquotasNominaisInformadasIndevidamenteException', 'entradas/validacoes/Teste_validacao_15_ImpostoSeletivoNaoInformadoException.json', False),
    ('br.gov.serpro.rtc.testesintegracao.validacoes.negocio.Teste_validacao_AliquotasNominaisPorAnoFatoGerador', 'deveCriticarAliquotaImpostoSeletivoNaoResolvivelAPartirDe2027', 'calc', 'AliquotaImpostoSeletivoNaoInformadaException', 'entradas/validacoes/Teste_validacao_15_ImpostoSeletivoNaoInformadoException.json', False),
    ('br.gov.serpro.rtc.testesintegracao.validacoes.pedagio.Teste_pedagio_validacao_1_NumeroDuplicado', 'teste_service_NumeroDuplicado', 'ped', 'CampoInvalidoException', 'entradas/validacoes/pedagio/Teste_pedagio_validacao_1_NumeroDuplicado.json', False),
    ('br.gov.serpro.rtc.testesintegracao.validacoes.pedagio.Teste_pedagio_validacao_4_OrigemUfMunicipioDivergentes', 'teste_service_OrigemUfMunicipioDivergentes', 'ped', 'MunicipioNaoPertencenteException', 'entradas/validacoes/pedagio/Teste_pedagio_validacao_4_OrigemUfMunicipioDivergentes.json', False),
    ('br.gov.serpro.rtc.testesintegracao.validacoes.pedagio.Teste_pedagio_validacao_5_TrechoUfMunicipioDivergentes', 'teste_service_TrechoUfMunicipioDivergentes', 'ped', 'MunicipioNaoPertencenteException', 'entradas/validacoes/pedagio/Teste_pedagio_validacao_5_TrechoUfMunicipioDivergentes.json', False),
    ('br.gov.serpro.rtc.testesintegracao.validacoes.pedagio.Teste_pedagio_validacao_6_OrigemMunicipioInvalido', 'teste_service_OrigemMunicipioInvalido', 'ped', 'MunicipioNaoEncontradoException', 'entradas/validacoes/pedagio/Teste_pedagio_validacao_6_OrigemMunicipioInvalido.json', False),
    ('br.gov.serpro.rtc.testesintegracao.validacoes.pedagio.Teste_pedagio_validacao_7_TrechoMunicipioInvalido', 'teste_service_TrechoMunicipioInvalido', 'ped', 'MunicipioNaoEncontradoException', 'entradas/validacoes/pedagio/Teste_pedagio_validacao_7_TrechoMunicipioInvalido.json', False),
]

@pytest.mark.parametrize('classname,name,svc,exc_name,json_path,skipped', JAVA_CASES)
def test_java_validacao(record_xml_attribute, classname, name, svc, exc_name, json_path, skipped, pedagio_svc):
    _java_attrs(record_xml_attribute, classname, name)
    if skipped:
        pytest.skip('@Disabled no Java')
    if exc_name and exc_name not in JAVA_EXCEPTIONS and not (
        svc == 'ped' and exc_name in {'MunicipioNaoEncontradoException', 'MunicipioNaoPertencenteException'}
    ):
        pytest.fail(f'Exceção Java sem mapeamento Python: {exc_name}')
    if pedagio_svc is None and svc == 'ped':
        pytest.skip('pedagio indisponível')
    _run_case(classname, name, svc, exc_name, json_path, pedagio_svc)
