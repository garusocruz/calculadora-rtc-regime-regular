"""Fachada de consumo (espelho dos serviços Java, sem Spring/HTTP)."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from decimal import Decimal
from typing import Any

from calculadora_rtc_regime_regular import (
    calculadora,
    dados_abertos,
    nfse_servico,
    observabilidade,
    pedagio,
)
from calculadora_rtc_regime_regular.banco import conectar
from calculadora_rtc_regime_regular.dados_abertos import BuscarAliquota, PapelAtor
from calculadora_rtc_regime_regular.base_calculo import Componentes, ElementoBaseCalculo
from calculadora_rtc_regime_regular.nfse_base import EntradaNfse, calcular_base_nfse


class ComponentesBaseCalculoInput:
    """``br.gov.serpro.rtc.api.model.input.basecalculo.ComponentesBaseCalculoInput``."""

    def __init__(self) -> None:
        self._componentes = Componentes()

    def setVProd(self, valor: Decimal | None) -> None:
        self._componentes.vProd = valor

    def setVFrete(self, valor: Decimal | None) -> None:
        self._componentes.vFrete = valor

    def setVSeg(self, valor: Decimal | None) -> None:
        self._componentes.vSeg = valor

    def setVOutro(self, valor: Decimal | None) -> None:
        self._componentes.vOutro = valor

    def setVII(self, valor: Decimal | None) -> None:
        self._componentes.vII = valor

    def setVIS(self, valor: Decimal | None) -> None:
        self._componentes.vIS = valor

    def setVDesc(self, valor: Decimal | None) -> None:
        self._componentes.vDesc = valor

    def setVPIS(self, valor: Decimal | None) -> None:
        self._componentes.vPIS = valor

    def setVCOFINS(self, valor: Decimal | None) -> None:
        self._componentes.vCOFINS = valor

    def setVICMS(self, valor: Decimal | None) -> None:
        self._componentes.vICMS = valor

    def setVICMSUFDest(self, valor: Decimal | None) -> None:
        self._componentes.vICMSUFDest = valor

    def setVFCP(self, valor: Decimal | None) -> None:
        self._componentes.vFCP = valor

    def setVFCPUFDest(self, valor: Decimal | None) -> None:
        self._componentes.vFCPUFDest = valor

    def setVICMSMono(self, valor: Decimal | None) -> None:
        self._componentes.vICMSMono = valor

    def setVISSQN(self, valor: Decimal | None) -> None:
        self._componentes.vISSQN = valor

    def getValor(self, elemento: ElementoBaseCalculo) -> Decimal | None:
        return self._componentes.get_valor(elemento)


class CalculadoraService:
    """``br.gov.serpro.rtc.domain.service.CalculadoraService``."""

    def __init__(
        self,
        conexao: Any | None = None,
        *,
        calculo_ibs_habilitado: bool = False,
    ) -> None:
        self._inner = calculadora.CalculadoraService(
            conexao, calculo_ibs_habilitado=calculo_ibs_habilitado
        )

    def calcularTributos(self, operacao: calculadora.OperacaoCalculadoraInput) -> Any:
        return self._inner.calcular_tributos(operacao)


class ObservabilidadeService:
    """``br.gov.serpro.rtc.domain.service.ObservabilidadeService``."""

    def __init__(self, conexao: Any | None = None) -> None:
        self._inner = observabilidade.ObservabilidadeService(conexao)

    def processarOperacao(
        self,
        operacao: calculadora.OperacaoCalculadoraInput,
        base_url: str,
    ) -> Any:
        return self._inner.processar_operacao(operacao, base_url)


class DadosAbertosService:
    """``br.gov.serpro.rtc.domain.service.dadosabertos.DadosAbertosService``."""

    def __init__(self, aliquota_padrao: BuscarAliquota | None = None) -> None:
        self._inner = dados_abertos.DadosAbertosService(aliquota_padrao=aliquota_padrao)

    def consultarUfs(self) -> list[dados_abertos.UfDadosAbertos]:
        return self._inner.consultar_ufs()

    def consultarMunicipiosPorSiglaUf(self, sigla_uf: str) -> list[dados_abertos.MunicipioDadosAbertos]:
        return self._inner.consultar_municipios_por_sigla_uf(sigla_uf)

    def consultarSituacoesTributarias(
        self, id_tributo: int, data: date
    ) -> list[dados_abertos.SituacaoTributariaDadosAbertos]:
        return self._inner.consultar_situacoes_tributarias(id_tributo, data)

    def consultarClassificacoesTributariasPorIdSituacaoTributaria(
        self, id_situacao_tributaria: int, data: date
    ) -> list[dados_abertos.ClassificacaoTributariaDadosAbertos]:
        return self._inner.consultar_classificacoes_tributarias_por_id_situacao_tributaria(
            id_situacao_tributaria, data
        )

    def consultarClassificacoesTributariasPorCstETributoTipo(
        self, cst: str, tributos: list[str], data: date
    ) -> list[dados_abertos.ClassificacaoTributariaDadosAbertos]:
        return self._inner.consultar_classificacoes_tributarias_por_cst_e_tributo_tipo(
            cst, tributos, data
        )

    def consultarNcm(self, ncm: str, data: date) -> dados_abertos.NcmDadosAbertos:
        return self._inner.consultar_ncm(ncm, data)

    def consultarNbs(self, nbs: str, data: date) -> dados_abertos.NbsDadosAbertos:
        return self._inner.consultar_nbs(nbs, data)

    def listarNbs(self, data: date) -> list[dados_abertos.NbsListaDadosAbertos]:
        return self._inner.listar_nbs(data)

    def consultarFundamentacoesLegais(
        self, data: date
    ) -> list[dados_abertos.FundamentacaoClassificacaoDadosAbertos]:
        return self._inner.consultar_fundamentacoes_legais(data)

    def consultarClassificacoesTributariasCbsIbs(
        self, data: date
    ) -> list[dados_abertos.ClassificacaoTributariaDadosAbertos]:
        return self._inner.consultar_classificacoes_tributarias_cbs_ibs(data)

    def consultarClassificacoesTributariasCbsIbsPorAtores(
        self,
        data: date,
        fornecedor: int | None = None,
        adquirente: int | None = None,
        sigla_dfe: str | None = None,
    ) -> list[dados_abertos.ClassificacaoTributariaDadosAbertos]:
        return self._inner.consultar_classificacoes_tributarias_cbs_ibs_por_atores(
            data, fornecedor=fornecedor, adquirente=adquirente, sigla_dfe=sigla_dfe
        )

    def consultarClassificacaoTributariaCbsIbsPorCodigo(
        self, c_class_trib: str, data: date
    ) -> dados_abertos.ClassificacaoTributariaDadosAbertos:
        return self._inner.consultar_classificacao_tributaria_cbs_ibs_por_codigo(
            c_class_trib, data
        )

    def consultarClassificacaoTributariaIsPorCodigo(
        self, c_class_trib: str, data: date
    ) -> dados_abertos.ClassificacaoTributariaDadosAbertos:
        return self._inner.consultar_classificacao_tributaria_is_por_codigo(c_class_trib, data)

    def consultarClassificacoesTributariasImpostoSeletivo(
        self, data: date
    ) -> list[dados_abertos.ClassificacaoTributariaDadosAbertos]:
        return self._inner.consultar_classificacoes_tributarias_imposto_seletivo(data)

    def consultarAliquota(
        self,
        id_tributo: int,
        codigo_uf: int | None,
        codigo_municipio: int | None,
        data: date,
    ) -> dados_abertos.AliquotaDadosAbertos:
        return self._inner.consultar_aliquota(id_tributo, codigo_uf, codigo_municipio, data)

    def consultarValidadeDfeClassificacaoTributaria(
        self, sigla_dfe: str, c_class_trib: str, data: date
    ) -> dados_abertos.ValidadeDfeClassificacaoTributariaDadosAbertos:
        return self._inner.consultar_validade_dfe_classificacao_tributaria(
            sigla_dfe, c_class_trib, data
        )

    def consultarCstsComClassificacoesCbsIbs(
        self, sigla_dfe: str | None, data: date
    ) -> list[dados_abertos.SituacaoClassificacaoAninhado]:
        return self._inner.consultar_csts_com_classificacoes_cbs_ibs(sigla_dfe, data)

    def consultarCstsComClassificacoesIs(
        self, sigla_dfe: str | None, data: date
    ) -> list[dados_abertos.SituacaoClassificacaoAninhado]:
        return self._inner.consultar_csts_com_classificacoes_is(sigla_dfe, data)

    def consultarRedutoresCompraGovernamental(
        self,
    ) -> list[dados_abertos.RedutorCompraGovernamentalDadosAbertos]:
        return self._inner.consultar_redutores_compra_governamental()

    def consultarTransferenciasCBS(self) -> list[dados_abertos.TransferenciaCBSDadosAbertos]:
        return self._inner.consultar_transferencias_cbs()

    def consultarTransferenciasIBS(self) -> list[dados_abertos.TransferenciaIBSDadosAbertos]:
        return self._inner.consultar_transferencias_ibs()

    def listarNbsAplicaveisPorClassificacao(
        self, c_class_trib: str, data: date
    ) -> list[dados_abertos.NbsListaDadosAbertos]:
        return self._inner.listar_nbs_aplicaveis_por_classificacao(c_class_trib, data)

    def listarClassificacaoAplicavelPorNbs(self, nbs: str, data: date) -> list[str]:
        return self._inner.listar_classificacao_aplicavel_por_nbs(nbs, data)

    def getWarningDadosSimuladosPorData(
        self, data: date
    ) -> dados_abertos.TipoWarningDadosSimulados | None:
        return self._inner.get_warning_dados_simulados_por_data(data)

    def validarNbsAplicavel(
        self, c_class_trib: str, nbs: str, data_ocorrencia_fato_gerador: date
    ) -> dados_abertos.NbsAplicavelSaida:
        return self._inner.validar_nbs_aplicavel(c_class_trib, nbs, data_ocorrencia_fato_gerador)

    def validarNcmAplicavel(
        self, c_class_trib: str, ncm: str, data_ocorrencia_fato_gerador: date
    ) -> dados_abertos.NcmAplicavelSaida:
        return self._inner.validar_ncm_aplicavel(c_class_trib, ncm, data_ocorrencia_fato_gerador)

    def consultarTiposDfeAgrupados(
        self, data: date | None = None
    ) -> list[dados_abertos.GrupoDfeDadosAbertos]:
        return self._inner.consultar_tipos_dfe_agrupados(data)

    def consultarNomenclatura(
        self, sigla_dfe: str, c_class_trib: str, data: date
    ) -> dados_abertos.NomenclaturaDadosAbertos:
        return self._inner.consultar_nomenclatura(sigla_dfe, c_class_trib, data)

    def consultarAtoresAgrupados(
        self, data: date, papel: PapelAtor | None = None
    ) -> list[dados_abertos.GrupoAtorDadosAbertos]:
        return self._inner.consultar_atores_agrupados(data, papel)

    def consultarNcmsVigentes(self, data: date) -> list[dados_abertos.NcmVigencia]:
        return self._inner.consultar_ncms_vigentes(data)


class PedagioService:
    """``br.gov.serpro.rtc.domain.service.pedagio.PedagioService``."""

    def __init__(self, inner: pedagio.PedagioService | None = None) -> None:
        self._inner = inner

    def calcularCIBS(self, operacao: pedagio.PedagioEntrada) -> pedagio.PedagioSaida:
        if self._inner is not None:
            return self._inner.calcular_cibs(operacao)
        with conectar() as conexao:
            return pedagio.pedagio_com_banco(conexao).calcular_cibs(operacao)


@dataclass
class NfseBaseCalculoInput:
    ano_fato_gerador: int
    valor_servico: Decimal
    desconto_incondicional: Decimal = Decimal(0)
    v_calc_ree_rep_res: Decimal = Decimal(0)
    v_calc_ded_red_ibscbs: Decimal = Decimal(0)
    iss: Decimal = Decimal(0)
    pis: Decimal = Decimal(0)
    cofins: Decimal = Decimal(0)


@dataclass
class NfseBaseCalculoOutput:
    base_calculo: Decimal


class NfseService:
    """``br.gov.serpro.rtc.domain.service.nfse.NfseService``."""

    def __init__(self, inner: nfse_servico.NfseServico | None = None) -> None:
        self._inner = inner

    def calcularBaseCalculo(self, entrada: NfseBaseCalculoInput) -> NfseBaseCalculoOutput:
        base = calcular_base_nfse(
            EntradaNfse(
                ano=entrada.ano_fato_gerador,
                valor_servico=entrada.valor_servico,
                desconto_incondicional=entrada.desconto_incondicional,
                reembolso=entrada.v_calc_ree_rep_res,
                deducao=entrada.v_calc_ded_red_ibscbs,
                iss=entrada.iss,
                pis=entrada.pis,
                cofins=entrada.cofins,
            )
        )
        return NfseBaseCalculoOutput(base_calculo=base)

    def validarIndicadorOperacao(
        self, entrada: nfse_servico.NfseValidacaoIndicadorOperacaoEntrada
    ) -> nfse_servico.NfseValidacaoIndicadorOperacaoSaida:
        if self._inner is not None:
            return self._inner.validar_indicador_operacao(entrada)
        with conectar() as conexao:
            return nfse_servico.nfse_com_banco(conexao).validar_indicador_operacao(entrada)

    def consultarLocalOperacao(
        self,
        c_ind_op: str | None,
        data_ocorrencia_fato_gerador: date | str | None,
    ) -> nfse_servico.NfseLocalOperacaoSaida:
        if self._inner is not None:
            return self._inner.consultar_local_operacao(c_ind_op, data_ocorrencia_fato_gerador)
        with conectar() as conexao:
            return nfse_servico.nfse_com_banco(conexao).consultar_local_operacao(
                c_ind_op, data_ocorrencia_fato_gerador
            )

    def consultarIndicadorOperacao(
        self, data_ocorrencia_fato_gerador: date, nbs: str | None = None
    ) -> list[nfse_servico.NfseIndicadorOperacaoSaida]:
        if self._inner is not None:
            return self._inner.consultar_indicador_operacao(data_ocorrencia_fato_gerador, nbs)
        with conectar() as conexao:
            return nfse_servico.nfse_com_banco(conexao).consultar_indicador_operacao(
                data_ocorrencia_fato_gerador, nbs
            )

    def consultarSituacoesClassificacoesPorNbs(
        self, nbs: str | None, data: date | str | None
    ) -> list[nfse_servico.NfseSituacaoClassificacaoSaida]:
        if self._inner is not None:
            return self._inner.consultar_situacoes_classificacoes_por_nbs(nbs, data)
        with conectar() as conexao:
            return nfse_servico.nfse_com_banco(conexao).consultar_situacoes_classificacoes_por_nbs(
                nbs, data
            )