"""Mapa explícito nodeid → (fqcn Java, método @Test)."""

from __future__ import annotations

JAVA_STRIP_TESTE_PREFIX: frozenset[str] = frozenset({"test_arredondamento_java"})

JAVA_MODULE_CLASS: dict[str, str] = {
    "test_expressao_aritmetica": "br.gov.serpro.rtc.testesunitarios.service.Teste_AvaliadorExpressaoAritmetica",
    "test_arredondamento_java": "br.gov.serpro.rtc.testesunitarios.shared.Teste_ArredondamentoUtils",
    "test_aliquota_resultado_java": "br.gov.serpro.rtc.testesunitarios.dto.Teste_AliquotaResultadoDTO",
    "test_cibs_java": "br.gov.serpro.rtc.testesunitarios.service.Teste_BaseCalculoService_CalcularCibs",
    "test_is_mercadorias_java": "br.gov.serpro.rtc.testesunitarios.service.Teste_BaseCalculoService_CalcularISMercadorias",
}

JAVA_UNIT_IDENTITY: dict[str, tuple[str, str]] = {
    "test_base_calculo_service::test_cibs_antes_de_2026_rejeita": ('br.gov.serpro.rtc.testesunitarios.service.Teste_BaseCalculoService_CalcularCibs', 'teste_anoAnterior2026_LancaExcecao'),
    "test_base_calculo_service::test_cibs_cada_campo_que_integra": ('br.gov.serpro.rtc.testesunitarios.service.Teste_BaseCalculoService_CalcularCibs', 'teste_camposIndividuaisIntegram'),
    "test_base_calculo_service::test_cibs_cada_campo_que_nao_integra": ('br.gov.serpro.rtc.testesunitarios.service.Teste_BaseCalculoService_CalcularCibs', 'teste_camposIndividuaisNaoIntegram'),
    "test_base_calculo_service::test_cibs_deduz_todos_os_campos_de_2026": ('br.gov.serpro.rtc.testesunitarios.service.Teste_BaseCalculoService_CalcularCibs', 'teste_pisCofinsDeducaoSimultanea2026'),
    "test_base_calculo_service::test_cibs_em_2026_deduz_pis_e_cofins": ('br.gov.serpro.rtc.testesunitarios.service.Teste_BaseCalculoService_CalcularCibs', 'teste_ano2026_PisCofinsDeduzidos'),
    "test_base_calculo_service::test_cibs_em_2027_rejeita_pis_e_cofins[cofins]": ('br.gov.serpro.rtc.testesunitarios.service.Teste_BaseCalculoService_CalcularCibs', 'teste_ano2027_CofinsLancaExcecao'),
    "test_base_calculo_service::test_cibs_em_2027_rejeita_pis_e_cofins[cofins_importacao]": ('br.gov.serpro.rtc.testesunitarios.service.Teste_BaseCalculoService_CalcularCibs', 'teste_ano2027_CofinsImportacaoLancaExcecao'),
    "test_base_calculo_service::test_cibs_em_2027_rejeita_pis_e_cofins[pis]": ('br.gov.serpro.rtc.testesunitarios.service.Teste_BaseCalculoService_CalcularCibs', 'teste_ano2027_PisLancaExcecao'),
    "test_base_calculo_service::test_cibs_em_2027_rejeita_pis_e_cofins[pis_importacao]": ('br.gov.serpro.rtc.testesunitarios.service.Teste_BaseCalculoService_CalcularCibs', 'teste_ano2027_PisImportacaoLancaExcecao'),
    "test_base_calculo_service::test_cibs_mensagem_lista_os_campos_em_ordem": ('br.gov.serpro.rtc.testesunitarios.service.Teste_BaseCalculoService_CalcularCibs', 'teste_mensagemErroOrdenadaAlfabeticamente_PisCofins'),
    "test_base_calculo_service::test_cibs_negativa_rejeita": ('br.gov.serpro.rtc.testesunitarios.service.Teste_BaseCalculoService_CalcularCibs', 'teste_baseNegativaLancaExcecao'),
    "test_base_calculo_service::test_cibs_soma_o_que_integra_e_deduz_icms_e_iss": ('br.gov.serpro.rtc.testesunitarios.service.Teste_BaseCalculoService_CalcularCibs', 'teste_logicaCalculoCorreta'),
    "test_base_calculo_service::test_cibs_valida_o_pis_antes_da_soma_e_antes_do_icms": ('br.gov.serpro.rtc.testesunitarios.service.Teste_BaseCalculoService_CalcularCibs', 'teste_validacaoAntesDaSoma'),
    "test_base_calculo_service::test_cibs_zerada": ('br.gov.serpro.rtc.testesunitarios.service.Teste_BaseCalculoService_CalcularCibs', 'teste_todosCamposZeroRetornaZero'),
    "test_coletor::test_add_erro_global_marca_has_erros_true": ('br.gov.serpro.rtc.testesunitarios.collector.Teste_GlobalCollector', 'addErroGlobalMarcaHasErrosTrue'),
    "test_coletor::test_add_item_collector_funciona": ('br.gov.serpro.rtc.testesunitarios.collector.Teste_GlobalCollector', 'addItemCollectorFunciona'),
    "test_coletor::test_add_multiplos_item_collectors": ('br.gov.serpro.rtc.testesunitarios.collector.Teste_GlobalCollector', 'addMultiplosItemCollectors'),
    "test_coletor::test_collector_com_itens_e_erros_globais_simultaneos": ('br.gov.serpro.rtc.testesunitarios.collector.Teste_GlobalCollector', 'collectorComItensEErrosGlobaisSimultaneos'),
    "test_coletor::test_erros_globais_preservam_ordem": ('br.gov.serpro.rtc.testesunitarios.collector.Teste_GlobalCollector', 'errosGlobaisPreservamOrdem'),
    "test_coletor::test_get_erros_globais_retorna_lista_imutavel": ('br.gov.serpro.rtc.testesunitarios.collector.Teste_GlobalCollector', 'getErrosGlobaisRetornaListaImutavel'),
    "test_coletor::test_get_item_collectors_retorna_lista_imutavel": ('br.gov.serpro.rtc.testesunitarios.collector.Teste_GlobalCollector', 'getItemCollectorsRetornaListaImutavel'),
    "test_coletor::test_multiplos_erros_globais": ('br.gov.serpro.rtc.testesunitarios.collector.Teste_GlobalCollector', 'multiplosErrosGlobais'),
    "test_coletor::test_novo_collector_nao_tem_erros": ('br.gov.serpro.rtc.testesunitarios.collector.Teste_GlobalCollector', 'novoCollectorNaoTemErros'),
    "test_dados_abertos::test_demais_tipos_preservam_valor": ('br.gov.serpro.rtc.testesunitarios.service.Teste_DadosAbertosService_ConversaoDecimal', 'demaisTiposPreservamOValor'),
    "test_dados_abertos::test_float_convertido_pelo_texto_do_numero": ('br.gov.serpro.rtc.testesunitarios.service.Teste_DadosAbertosService_ConversaoDecimal', 'floatEConvertidoPeloTextoDoNumero'),
    "test_nfse_base::test_nfse_cada_deducao_e_transicao": ('br.gov.serpro.rtc.testesunitarios.service.Teste_NfseService_CalcularBaseCalculo', 'teste_cadaCampoNaoIntegraCorretamente'),
    "test_nfse_base::test_nfse_em_2026_deduz_pis_cofins_e_iss": ('br.gov.serpro.rtc.testesunitarios.service.Teste_NfseService_CalcularBaseCalculo', 'teste_calculoCorretoEm2026_PisCofinsnaoIntegram'),
    "test_nfse_base::test_nfse_em_2027_deduz_iss_sem_pis": ('br.gov.serpro.rtc.testesunitarios.service.Teste_NfseService_CalcularBaseCalculo', 'teste_calculoCorretoEm2027_SemPisCofinsSemIss'),
    "test_nfse_base::test_nfse_em_2033_sem_iss": ('br.gov.serpro.rtc.testesunitarios.service.Teste_NfseService_CalcularBaseCalculo', 'teste_dataAPartirDe2033SemIss'),
    "test_nfse_base::test_nfse_extincao_de_pis_e_de_iss": ('br.gov.serpro.rtc.testesunitarios.service.Teste_NfseService_CalcularBaseCalculo', 'teste_transicao2026Para2027_PisCofinsLancaExcecaoEm2027'),
    "test_nfse_base::test_nfse_mensagem_ordena_cofins_antes_de_pis": ('br.gov.serpro.rtc.testesunitarios.service.Teste_NfseService_CalcularBaseCalculo', 'teste_mensagemOrdenadaAlfabeticamente'),
    "test_nfse_base::test_nfse_negativa_e_ano_minimo": ('br.gov.serpro.rtc.testesunitarios.service.Teste_NfseService_CalcularBaseCalculo', 'teste_baseNegativaLancaExcecao'),
    "test_nfse_base::test_nfse_todos_os_campos_em_2026_e_2032": ('br.gov.serpro.rtc.testesunitarios.service.Teste_NfseService_CalcularBaseCalculo', 'teste_todosOsCamposSempreDeduzidos2026'),
    "test_nomenclatura::test_nbs_com_anexo_exige_completa": ('br.gov.serpro.rtc.testesunitarios.service.Teste_NcmNbsAplicavelService_TabelaVerdade', 'teste_nbs_comAnexoExigeCompleta'),
    "test_nomenclatura::test_nbs_sem_anexo_aceita": ('br.gov.serpro.rtc.testesunitarios.service.Teste_NcmNbsAplicavelService_TabelaVerdade', 'teste_nbs_semAnexoAceita'),
    "test_nomenclatura::test_nbs_tabela_verdade": ('br.gov.serpro.rtc.testesunitarios.service.Teste_NcmNbsAplicavelService_TabelaVerdade', 'teste_nbs_tabelaVerdade'),
    "test_nomenclatura::test_ncm_com_anexo_exige_completo": ('br.gov.serpro.rtc.testesunitarios.service.Teste_NcmNbsAplicavelService_TabelaVerdade', 'teste_ncm_comAnexoExigeCompleto'),
    "test_nomenclatura::test_ncm_excepcionado_com_vinculo_livre_aceita": ('br.gov.serpro.rtc.testesunitarios.service.Teste_NcmNbsAplicavelService_TabelaVerdade', 'teste_ncm_excepcionadoComVinculoLivreAceita'),
    "test_nomenclatura::test_ncm_excepcionado_rejeita": ('br.gov.serpro.rtc.testesunitarios.service.Teste_NcmNbsAplicavelService_TabelaVerdade', 'teste_ncm_excepcionadoRejeita'),
    "test_nomenclatura::test_ncm_fora_do_anexo_rejeita": ('br.gov.serpro.rtc.testesunitarios.service.Teste_NcmNbsAplicavelService_TabelaVerdade', 'teste_ncm_foraDoAnexoRejeita'),
    "test_nomenclatura::test_ncm_sem_anexo_aceita": ('br.gov.serpro.rtc.testesunitarios.service.Teste_NcmNbsAplicavelService_TabelaVerdade', 'teste_ncm_semAnexoAceita'),
    "test_nomenclatura::test_ncm_sem_excecao_cobrindo_aceita": ('br.gov.serpro.rtc.testesunitarios.service.Teste_NcmNbsAplicavelService_TabelaVerdade', 'teste_ncm_semExcecaoCobrindoAceita'),
    "test_nomenclatura::test_ncm_service_consultar_vigentes": ('br.gov.serpro.rtc.testesunitarios.service.NcmServiceTest', 'deveRetornarListaDeNcmsVigentes'),
    "test_nomenclatura::test_ncm_service_existe_quando_repositorio_false": ('br.gov.serpro.rtc.testesunitarios.service.NcmServiceTest', 'deveRetornarFalseQuandoNcmNaoExistirNaData'),
    "test_nomenclatura::test_ncm_service_existe_quando_repositorio_true": ('br.gov.serpro.rtc.testesunitarios.service.NcmServiceTest', 'deveRetornarTrueQuandoNcmExistirNaData'),
    "test_nomenclatura::test_ncm_service_lista_vazia": ('br.gov.serpro.rtc.testesunitarios.service.NcmServiceTest', 'deveRetornarListaVaziaQuandoNaoExistiremNcmsVigentes'),
    "test_nomenclatura::test_ncm_service_repassa_lista_do_repositorio": ('br.gov.serpro.rtc.testesunitarios.service.NcmServiceTest', 'deveRetornarListaConformeDadosDoRepositorio'),
    "test_nomenclatura::test_ncm_vinculo_fora_de_vigencia_com_excecao_rejeita": ('br.gov.serpro.rtc.testesunitarios.service.Teste_NcmNbsAplicavelService_TabelaVerdade', 'teste_ncm_vinculoForaDeVigenciaComExcecaoRejeita'),
    "test_pedagio::test_buscar_aliquota_padrao_aliquota_zero": ('br.gov.serpro.rtc.testesunitarios.service.Teste_PedagioService_BuscarAliquotaPadrao', 'teste_BuscarAliquotaPadrao_AliquotaZero'),
    "test_pedagio::test_buscar_aliquota_padrao_aliquota_zero[data_operacao0]": ('br.gov.serpro.rtc.testesunitarios.service.Teste_PedagioService_BuscarAliquotaPadrao', 'teste_BuscarAliquotaPadrao_AliquotaZero'),
    "test_pedagio::test_buscar_aliquota_padrao_cbs_aliquota_normal": ('br.gov.serpro.rtc.testesunitarios.service.Teste_PedagioService_BuscarAliquotaPadrao', 'teste_BuscarAliquotaPadrao_CBS_AliquotaNormal'),
    "test_pedagio::test_buscar_aliquota_padrao_cbs_aliquota_normal[data_operacao0]": ('br.gov.serpro.rtc.testesunitarios.service.Teste_PedagioService_BuscarAliquotaPadrao', 'teste_BuscarAliquotaPadrao_CBS_AliquotaNormal'),
    "test_pedagio::test_buscar_aliquota_padrao_com_acrescimo": ('br.gov.serpro.rtc.testesunitarios.service.Teste_PedagioService_BuscarAliquotaPadrao', 'teste_BuscarAliquotaPadrao_ComAcrescimo'),
    "test_pedagio::test_buscar_aliquota_padrao_com_acrescimo[data_operacao0]": ('br.gov.serpro.rtc.testesunitarios.service.Teste_PedagioService_BuscarAliquotaPadrao', 'teste_BuscarAliquotaPadrao_ComAcrescimo'),
    "test_pedagio::test_buscar_aliquota_padrao_com_decrescimo": ('br.gov.serpro.rtc.testesunitarios.service.Teste_PedagioService_BuscarAliquotaPadrao', 'teste_BuscarAliquotaPadrao_ComDecrescimo'),
    "test_pedagio::test_buscar_aliquota_padrao_com_decrescimo[data_operacao0]": ('br.gov.serpro.rtc.testesunitarios.service.Teste_PedagioService_BuscarAliquotaPadrao', 'teste_BuscarAliquotaPadrao_ComDecrescimo'),
    "test_pedagio::test_buscar_aliquota_padrao_conversao_exata_sem_arredondamento": ('br.gov.serpro.rtc.testesunitarios.service.Teste_PedagioService_BuscarAliquotaPadrao', 'teste_BuscarAliquotaPadrao_ConversaoExataSemArredondamento'),
    "test_pedagio::test_buscar_aliquota_padrao_conversao_exata_sem_arredondamento[data_operacao0]": ('br.gov.serpro.rtc.testesunitarios.service.Teste_PedagioService_BuscarAliquotaPadrao', 'teste_BuscarAliquotaPadrao_ConversaoExataSemArredondamento'),
    "test_pedagio::test_buscar_aliquota_padrao_datas_diferentes": ('br.gov.serpro.rtc.testesunitarios.service.Teste_PedagioService_BuscarAliquotaPadrao', 'teste_BuscarAliquotaPadrao_DatasDiferentes'),
    "test_pedagio::test_buscar_aliquota_padrao_datas_diferentes[data_operacao0]": ('br.gov.serpro.rtc.testesunitarios.service.Teste_PedagioService_BuscarAliquotaPadrao', 'teste_BuscarAliquotaPadrao_DatasDiferentes'),
    "test_pedagio::test_buscar_aliquota_padrao_ibs_estadual_com_codigo_uf": ('br.gov.serpro.rtc.testesunitarios.service.Teste_PedagioService_BuscarAliquotaPadrao', 'teste_BuscarAliquotaPadrao_IBSEstadual_ComCodigoUF'),
    "test_pedagio::test_buscar_aliquota_padrao_ibs_estadual_com_codigo_uf[data_operacao0]": ('br.gov.serpro.rtc.testesunitarios.service.Teste_PedagioService_BuscarAliquotaPadrao', 'teste_BuscarAliquotaPadrao_IBSEstadual_ComCodigoUF'),
    "test_pedagio::test_buscar_aliquota_padrao_ibs_municipal_com_codigo_municipio": ('br.gov.serpro.rtc.testesunitarios.service.Teste_PedagioService_BuscarAliquotaPadrao', 'teste_BuscarAliquotaPadrao_IBSMunicipal_ComCodigoMunicipio'),
    "test_pedagio::test_buscar_aliquota_padrao_ibs_municipal_com_codigo_municipio[data_operacao0]": ('br.gov.serpro.rtc.testesunitarios.service.Teste_PedagioService_BuscarAliquotaPadrao', 'teste_BuscarAliquotaPadrao_IBSMunicipal_ComCodigoMunicipio'),
    "test_pedagio::test_buscar_aliquota_padrao_tres_tributos_diferentes": ('br.gov.serpro.rtc.testesunitarios.service.Teste_PedagioService_BuscarAliquotaPadrao', 'teste_BuscarAliquotaPadrao_TresTributosDiferentes'),
    "test_pedagio::test_buscar_aliquota_padrao_tres_tributos_diferentes[data_operacao0]": ('br.gov.serpro.rtc.testesunitarios.service.Teste_PedagioService_BuscarAliquotaPadrao', 'teste_BuscarAliquotaPadrao_TresTributosDiferentes'),
    "test_pedagio::test_buscar_aliquota_padrao_valor_com_muitas_decimais": ('br.gov.serpro.rtc.testesunitarios.service.Teste_PedagioService_BuscarAliquotaPadrao', 'teste_BuscarAliquotaPadrao_ValorComMuitasDecimais'),
    "test_pedagio::test_buscar_aliquota_padrao_valor_com_muitas_decimais[data_operacao0]": ('br.gov.serpro.rtc.testesunitarios.service.Teste_PedagioService_BuscarAliquotaPadrao', 'teste_BuscarAliquotaPadrao_ValorComMuitasDecimais'),
    "test_pedagio::test_totaliza_cbs_retorna_tributo_trechos": ('br.gov.serpro.rtc.testesunitarios.domain.Teste_TributoTotalPedagioOutput', 'teste_totalizaCbs_retornaTributoTrechos'),
    "test_pedagio::test_totaliza_cbs_retorna_valores_apurado_e_devido": ('br.gov.serpro.rtc.testesunitarios.domain.Teste_TributoTotalPedagioOutput', 'teste_totalizaCbs_retornaValoresApuradoEDevido'),
    "test_pedagio::test_totaliza_ibs_estadual_retorna_soma_tributo_trechos": ('br.gov.serpro.rtc.testesunitarios.domain.Teste_TributoTotalPedagioOutput', 'teste_totalizaIbsEstadual_retornaSomaTributoTrechos'),
    "test_pedagio::test_totaliza_ibs_municipal_retorna_soma_tributo_trechos": ('br.gov.serpro.rtc.testesunitarios.domain.Teste_TributoTotalPedagioOutput', 'teste_totalizaIbsMunicipal_retornaSomaTributoTrechos'),
    "test_componentes_base_calculo_input_java::test_getValor_deveRetornarVProd": (
        "br.gov.serpro.rtc.api.model.input.basecalculo.ComponentesBaseCalculoInputTest",
        "getValor_deveRetornarVProd",
    ),
    "test_componentes_base_calculo_input_java::test_getValor_deveRetornarVFrete": (
        "br.gov.serpro.rtc.api.model.input.basecalculo.ComponentesBaseCalculoInputTest",
        "getValor_deveRetornarVFrete",
    ),
    "test_componentes_base_calculo_input_java::test_getValor_deveRetornarVSeg": (
        "br.gov.serpro.rtc.api.model.input.basecalculo.ComponentesBaseCalculoInputTest",
        "getValor_deveRetornarVSeg",
    ),
    "test_componentes_base_calculo_input_java::test_getValor_deveRetornarVOutro": (
        "br.gov.serpro.rtc.api.model.input.basecalculo.ComponentesBaseCalculoInputTest",
        "getValor_deveRetornarVOutro",
    ),
    "test_componentes_base_calculo_input_java::test_getValor_deveRetornarVII": (
        "br.gov.serpro.rtc.api.model.input.basecalculo.ComponentesBaseCalculoInputTest",
        "getValor_deveRetornarVII",
    ),
    "test_componentes_base_calculo_input_java::test_getValor_deveRetornarVIS": (
        "br.gov.serpro.rtc.api.model.input.basecalculo.ComponentesBaseCalculoInputTest",
        "getValor_deveRetornarVIS",
    ),
    "test_componentes_base_calculo_input_java::test_getValor_deveRetornarVDesc": (
        "br.gov.serpro.rtc.api.model.input.basecalculo.ComponentesBaseCalculoInputTest",
        "getValor_deveRetornarVDesc",
    ),
    "test_componentes_base_calculo_input_java::test_getValor_deveRetornarVPIS": (
        "br.gov.serpro.rtc.api.model.input.basecalculo.ComponentesBaseCalculoInputTest",
        "getValor_deveRetornarVPIS",
    ),
    "test_componentes_base_calculo_input_java::test_getValor_deveRetornarVCOFINS": (
        "br.gov.serpro.rtc.api.model.input.basecalculo.ComponentesBaseCalculoInputTest",
        "getValor_deveRetornarVCOFINS",
    ),
    "test_componentes_base_calculo_input_java::test_getValor_deveRetornarVICMS": (
        "br.gov.serpro.rtc.api.model.input.basecalculo.ComponentesBaseCalculoInputTest",
        "getValor_deveRetornarVICMS",
    ),
    "test_componentes_base_calculo_input_java::test_getValor_deveRetornarVICMSUFDest": (
        "br.gov.serpro.rtc.api.model.input.basecalculo.ComponentesBaseCalculoInputTest",
        "getValor_deveRetornarVICMSUFDest",
    ),
    "test_componentes_base_calculo_input_java::test_getValor_deveRetornarVFCP": (
        "br.gov.serpro.rtc.api.model.input.basecalculo.ComponentesBaseCalculoInputTest",
        "getValor_deveRetornarVFCP",
    ),
    "test_componentes_base_calculo_input_java::test_getValor_deveRetornarVFCPUFDest": (
        "br.gov.serpro.rtc.api.model.input.basecalculo.ComponentesBaseCalculoInputTest",
        "getValor_deveRetornarVFCPUFDest",
    ),
    "test_componentes_base_calculo_input_java::test_getValor_deveRetornarVICMSMono": (
        "br.gov.serpro.rtc.api.model.input.basecalculo.ComponentesBaseCalculoInputTest",
        "getValor_deveRetornarVICMSMono",
    ),
    "test_componentes_base_calculo_input_java::test_getValor_deveRetornarVISSQN": (
        "br.gov.serpro.rtc.api.model.input.basecalculo.ComponentesBaseCalculoInputTest",
        "getValor_deveRetornarVISSQN",
    ),
    "test_componentes_base_calculo_input_java::test_getValor_deveRetornarNullQuandoCampoNaoInformado[1]": (
        "br.gov.serpro.rtc.api.model.input.basecalculo.ComponentesBaseCalculoInputTest",
        "getValor_deveRetornarNullQuandoCampoNaoInformado(ElementoBaseCalculo)[1]",
    ),
    "test_componentes_base_calculo_input_java::test_getValor_deveRetornarNullQuandoCampoNaoInformado[2]": (
        "br.gov.serpro.rtc.api.model.input.basecalculo.ComponentesBaseCalculoInputTest",
        "getValor_deveRetornarNullQuandoCampoNaoInformado(ElementoBaseCalculo)[2]",
    ),
    "test_componentes_base_calculo_input_java::test_getValor_deveRetornarNullQuandoCampoNaoInformado[3]": (
        "br.gov.serpro.rtc.api.model.input.basecalculo.ComponentesBaseCalculoInputTest",
        "getValor_deveRetornarNullQuandoCampoNaoInformado(ElementoBaseCalculo)[3]",
    ),
    "test_componentes_base_calculo_input_java::test_getValor_deveRetornarNullQuandoCampoNaoInformado[4]": (
        "br.gov.serpro.rtc.api.model.input.basecalculo.ComponentesBaseCalculoInputTest",
        "getValor_deveRetornarNullQuandoCampoNaoInformado(ElementoBaseCalculo)[4]",
    ),
    "test_componentes_base_calculo_input_java::test_getValor_deveRetornarNullQuandoCampoNaoInformado[5]": (
        "br.gov.serpro.rtc.api.model.input.basecalculo.ComponentesBaseCalculoInputTest",
        "getValor_deveRetornarNullQuandoCampoNaoInformado(ElementoBaseCalculo)[5]",
    ),
    "test_componentes_base_calculo_input_java::test_getValor_deveRetornarNullQuandoCampoNaoInformado[6]": (
        "br.gov.serpro.rtc.api.model.input.basecalculo.ComponentesBaseCalculoInputTest",
        "getValor_deveRetornarNullQuandoCampoNaoInformado(ElementoBaseCalculo)[6]",
    ),
    "test_componentes_base_calculo_input_java::test_getValor_deveRetornarNullQuandoCampoNaoInformado[7]": (
        "br.gov.serpro.rtc.api.model.input.basecalculo.ComponentesBaseCalculoInputTest",
        "getValor_deveRetornarNullQuandoCampoNaoInformado(ElementoBaseCalculo)[7]",
    ),
    "test_componentes_base_calculo_input_java::test_getValor_deveRetornarNullQuandoCampoNaoInformado[8]": (
        "br.gov.serpro.rtc.api.model.input.basecalculo.ComponentesBaseCalculoInputTest",
        "getValor_deveRetornarNullQuandoCampoNaoInformado(ElementoBaseCalculo)[8]",
    ),
    "test_componentes_base_calculo_input_java::test_getValor_deveRetornarNullQuandoCampoNaoInformado[9]": (
        "br.gov.serpro.rtc.api.model.input.basecalculo.ComponentesBaseCalculoInputTest",
        "getValor_deveRetornarNullQuandoCampoNaoInformado(ElementoBaseCalculo)[9]",
    ),
    "test_componentes_base_calculo_input_java::test_getValor_deveRetornarNullQuandoCampoNaoInformado[10]": (
        "br.gov.serpro.rtc.api.model.input.basecalculo.ComponentesBaseCalculoInputTest",
        "getValor_deveRetornarNullQuandoCampoNaoInformado(ElementoBaseCalculo)[10]",
    ),
    "test_componentes_base_calculo_input_java::test_getValor_deveRetornarNullQuandoCampoNaoInformado[11]": (
        "br.gov.serpro.rtc.api.model.input.basecalculo.ComponentesBaseCalculoInputTest",
        "getValor_deveRetornarNullQuandoCampoNaoInformado(ElementoBaseCalculo)[11]",
    ),
    "test_componentes_base_calculo_input_java::test_getValor_deveRetornarNullQuandoCampoNaoInformado[12]": (
        "br.gov.serpro.rtc.api.model.input.basecalculo.ComponentesBaseCalculoInputTest",
        "getValor_deveRetornarNullQuandoCampoNaoInformado(ElementoBaseCalculo)[12]",
    ),
    "test_componentes_base_calculo_input_java::test_getValor_deveRetornarNullQuandoCampoNaoInformado[13]": (
        "br.gov.serpro.rtc.api.model.input.basecalculo.ComponentesBaseCalculoInputTest",
        "getValor_deveRetornarNullQuandoCampoNaoInformado(ElementoBaseCalculo)[13]",
    ),
    "test_componentes_base_calculo_input_java::test_getValor_deveRetornarNullQuandoCampoNaoInformado[14]": (
        "br.gov.serpro.rtc.api.model.input.basecalculo.ComponentesBaseCalculoInputTest",
        "getValor_deveRetornarNullQuandoCampoNaoInformado(ElementoBaseCalculo)[14]",
    ),
    "test_componentes_base_calculo_input_java::test_getValor_deveRetornarNullQuandoCampoNaoInformado[15]": (
        "br.gov.serpro.rtc.api.model.input.basecalculo.ComponentesBaseCalculoInputTest",
        "getValor_deveRetornarNullQuandoCampoNaoInformado(ElementoBaseCalculo)[15]",
    ),
}
