"""Coletores de erros de observabilidade (pin f1eebd7ce3157423b1a6aaca7dc1d6c3395452c4).

Transcrição de ``GlobalCollector`` e ``ItemCollector`` sem Spring e sem HTTP.
"""

from __future__ import annotations

from collections.abc import Sequence
from dataclasses import dataclass
from enum import Enum


class EstadoItemEnum(Enum):
    CALCULADO = "CALCULADO"
    NAO_IMPLEMENTADO = "NAO_IMPLEMENTADO"
    INCONSISTENCIA_ENTRADA = "INCONSISTENCIA_ENTRADA"
    FALHA_TECNICA = "FALHA_TECNICA"
    CALCULO_SIMULADO = "CALCULO_SIMULADO"


@dataclass(frozen=True, slots=True)
class ErroDetalhe:
    type: str
    title: str
    code: str
    pointer: str
    detail: str


@dataclass(frozen=True, slots=True)
class CodigoErro:
    codigo: str
    campo_default: str | None
    estado: EstadoItemEnum


@dataclass(frozen=True, slots=True)
class _ProblemType:
    titulo: str
    codigo_erro: CodigoErro | None = None


_TITULOS_VALIDACAO: dict[str, str] = {
    "VAL-001": "Campo obrigatório não informado",
    "VAL-002": "Campo obrigatório em branco",
    "VAL-003": "Lista ou campo não pode estar vazio",
    "VAL-004": "Tamanho fora do intervalo permitido",
    "VAL-005": "Valor abaixo do mínimo permitido",
    "VAL-006": "Valor acima do máximo permitido",
    "VAL-007": "Valor decimal abaixo do mínimo permitido",
    "VAL-008": "Valor decimal acima do máximo permitido",
    "VAL-009": "Formato inválido",
    "VAL-010": "Quantidade de dígitos inválida",
    "VAL-011": "E-mail inválido",
    "VAL-012": "Valor deve ser positivo",
    "VAL-013": "Valor deve ser positivo ou zero",
    "VAL-014": "Condição não atendida",
    "VAL-015": "Condição atendida indevidamente",
    "VAL-000": "Erro de validação não categorizado",
}


def _problem_types() -> dict[type[BaseException], _ProblemType]:
    from calculadora_rtc_regime_regular.base_calculo_service import CampoInvalido
    from calculadora_rtc_regime_regular.consultas import (
        AliquotaReferenciaNaoEncontradaException,
        FundamentacaoClassificacaoNaoEncontradaException,
        MunicipioNaoEncontradoException,
        MunicipioNaoPertencenteException,
        PercentualReducaoNaoEncontradoException,
        SituacaoTributariaNaoEncontradaException as SituacaoConsultas,
        TipoDfeNaoEncontradoException,
        TipoDfeNaoTratadoException,
        TratamentoClassificacaoNaoEncontradoException,
        TratamentoTributarioNaoEncontradoException,
        TributoSituacaoTributariaNaoEncontradoException,
        UfNaoEncontradaException,
        ErroGenericoValidacaoException as ErroGenericoConsultas,
    )
    from calculadora_rtc_regime_regular.nomenclatura import (
        ClassificacaoTributariaNaoEncontradaException,
        NbsCompletoNaoInformadoException,
        NbsNaoVinculadaException,
        NcmCompletoNaoInformadoException,
        NcmNaoVinculadaException,
        NomenclaturaIncompativelTipoDfeException,
        NomenclaturaNaoPermitidaTipoDfeException,
        NomenclaturaObrigatoriaNaoInformadaException,
        SiglaDFeNaoEncontradaException,
    )
    from calculadora_rtc_regime_regular.calculadora import ClassificacaoTributariaNaoVinculadaTipoDfeException
    from calculadora_rtc_regime_regular.processamento_item import (
        AliquotaImpostoSeletivoNaoInformadaException,
        AliquotasNominaisInformadasIndevidamenteException,
        AliquotasNominaisNaoInformadasException,
        BaseCalculoComponentesInconsistenteException,
        BaseCalculoInconsistenteException,
        BaseCalculoMenorBaseCalculoImpostoSeletivoException,
        BaseCalculoNaoInformadaException,
        ClassificacaoTributariaNaoVinculadaSituacaoTributariaException,
        DataFatoGeradorNaoInformadaException,
        ErroGenericoValidacaoException,
        ImpostoSeletivoNaoAdmitidoTipoDfeException,
        ImpostoSeletivoNaoInformadoException,
        IncompatibilidadeSuspensaoException,
        NbsNaoEncontradaException,
        NcmNaoEncontradaException,
        NcmNbsSimultaneasException,
        SituacaoTributariaNaoEncontradaException,
        TributacaoRegularNaoInformadaException,
    )

    inc = EstadoItemEnum.INCONSISTENCIA_ENTRADA
    fat = EstadoItemEnum.FALHA_TECNICA

    return {
        CampoInvalido: _ProblemType(
            "Campo inválido",
            CodigoErro("REG-024", None, inc),
        ),
        NcmNbsSimultaneasException: _ProblemType(
            "NCM e NBS informadas simultaneamente",
            CodigoErro("REG-001", None, inc),
        ),
        NcmNaoEncontradaException: _ProblemType(
            "NCM não encontrada",
            CodigoErro("REG-002", "ncm", inc),
        ),
        NbsNaoEncontradaException: _ProblemType(
            "NBS não encontrada",
            CodigoErro("REG-003", "nbs", inc),
        ),
        SituacaoTributariaNaoEncontradaException: _ProblemType(
            "Situação tributária não encontrada",
            CodigoErro("REG-004", "cst", inc),
        ),
        SituacaoConsultas: _ProblemType(
            "Situação tributária não encontrada",
            CodigoErro("REG-004", "cst", inc),
        ),
        ClassificacaoTributariaNaoEncontradaException: _ProblemType(
            "Classificação tributária não encontrada",
            CodigoErro("REG-005", "cClassTrib", inc),
        ),
        ClassificacaoTributariaNaoVinculadaSituacaoTributariaException: _ProblemType(
            "Classificação tributária não vinculada à situação tributária",
            CodigoErro("REG-006", "cClassTrib", inc),
        ),
        ClassificacaoTributariaNaoVinculadaTipoDfeException: _ProblemType(
            "Classificação tributária não vinculada ao tipo de documento",
            CodigoErro("REG-029", "cClassTrib", inc),
        ),
        TratamentoClassificacaoNaoEncontradoException: _ProblemType(
            "Tratamento de classificação não encontrado",
            CodigoErro("REG-008", "cClassTrib", inc),
        ),
        TributacaoRegularNaoInformadaException: _ProblemType(
            "Grupo de tributação regular não informado",
            CodigoErro("REG-009", "tributacaoRegular", inc),
        ),
        IncompatibilidadeSuspensaoException: _ProblemType(
            "Incompatibilidade com suspensão",
            CodigoErro("REG-010", "tributacaoRegular/cClassTrib", inc),
        ),
        NcmNaoVinculadaException: _ProblemType(
            "NCM não vinculada",
            CodigoErro("REG-011", "ncm", inc),
        ),
        NbsNaoVinculadaException: _ProblemType(
            "NBS não vinculada",
            CodigoErro("REG-012", "nbs", inc),
        ),
        ImpostoSeletivoNaoInformadoException: _ProblemType(
            "Dados do Imposto Seletivo não informados",
            CodigoErro("REG-013", "impostoSeletivo", inc),
        ),
        NcmCompletoNaoInformadoException: _ProblemType(
            "NCM completo não informado",
            CodigoErro("REG-015", "ncm", inc),
        ),
        NbsCompletoNaoInformadoException: _ProblemType(
            "NBS completo não informado",
            CodigoErro("REG-016", "nbs", inc),
        ),
        MunicipioNaoPertencenteException: _ProblemType(
            "Município não pertencente à UF",
            CodigoErro("REG-018", None, inc),
        ),
        MunicipioNaoEncontradoException: _ProblemType(
            "Município não encontrado",
            CodigoErro("REG-019", None, inc),
        ),
        UfNaoEncontradaException: _ProblemType(
            "UF não encontrada",
            CodigoErro("REG-020", None, inc),
        ),
        DataFatoGeradorNaoInformadaException: _ProblemType(
            "Data do fato gerador não informada",
            CodigoErro("REG-021", None, inc),
        ),
        ErroGenericoValidacaoException: _ProblemType(
            "Erro genérico de validação",
            CodigoErro("REG-023", None, inc),
        ),
        ErroGenericoConsultas: _ProblemType(
            "Erro genérico de validação",
            CodigoErro("REG-023", None, inc),
        ),
        BaseCalculoNaoInformadaException: _ProblemType(
            "Base de cálculo não informada",
            CodigoErro("REG-025", "baseCalculo", inc),
        ),
        BaseCalculoInconsistenteException: _ProblemType(
            "Base de cálculo inconsistente",
            CodigoErro("REG-026", "baseCalculo", inc),
        ),
        BaseCalculoMenorBaseCalculoImpostoSeletivoException: _ProblemType(
            "Base de cálculo menor que a base de cálculo do Imposto Seletivo",
            CodigoErro("REG-027", "baseCalculo", inc),
        ),
        TipoDfeNaoEncontradoException: _ProblemType(
            "Tipo de documento fiscal não encontrado",
            CodigoErro("REG-028", "tpDoc", inc),
        ),
        NomenclaturaIncompativelTipoDfeException: _ProblemType(
            "Nomenclatura incompatível com o tipo de documento",
            CodigoErro("REG-030", None, inc),
        ),
        NomenclaturaNaoPermitidaTipoDfeException: _ProblemType(
            "Nomenclatura não permitida para o tipo de documento",
            CodigoErro("REG-031", None, inc),
        ),
        ImpostoSeletivoNaoAdmitidoTipoDfeException: _ProblemType(
            "Imposto Seletivo não admitido pelo tipo de documento",
            CodigoErro("REG-032", "impostoSeletivo", inc),
        ),
        NomenclaturaObrigatoriaNaoInformadaException: _ProblemType(
            "Nomenclatura obrigatória não informada",
            CodigoErro("REG-033", None, inc),
        ),
        BaseCalculoComponentesInconsistenteException: _ProblemType(
            "Base de cálculo inconsistente",
            CodigoErro("REG-034", "baseCalculo", inc),
        ),
        AliquotaImpostoSeletivoNaoInformadaException: _ProblemType(
            "Alíquota do Imposto Seletivo não informada",
            CodigoErro("REG-035", "aliquotasNominais/impostoSeletivo", inc),
        ),
        AliquotasNominaisInformadasIndevidamenteException: _ProblemType(
            "Alíquotas nominais informadas indevidamente",
            CodigoErro("REG-036", "aliquotasNominais", inc),
        ),
        AliquotasNominaisNaoInformadasException: _ProblemType(
            "Alíquotas nominais não informadas",
            CodigoErro("REG-037", "aliquotasNominais", inc),
        ),
        TipoDfeNaoTratadoException: _ProblemType(
            "Tipo de documento fiscal não tratado",
            CodigoErro("REG-038", "tpDoc", inc),
        ),
        AliquotaReferenciaNaoEncontradaException: _ProblemType(
            "Alíquota de referência não encontrada",
            CodigoErro("CAL-003", None, fat),
        ),
        TratamentoTributarioNaoEncontradoException: _ProblemType(
            "Tratamento tributário não encontrado",
            CodigoErro("CAL-009", None, fat),
        ),
        PercentualReducaoNaoEncontradoException: _ProblemType(
            "Percentual de redução não encontrado",
            CodigoErro("CAL-010", None, fat),
        ),
        FundamentacaoClassificacaoNaoEncontradaException: _ProblemType(
            "Fundamentação não encontrada",
            CodigoErro("CAL-011", None, fat),
        ),
        TributoSituacaoTributariaNaoEncontradoException: _ProblemType(
            "Tributo/situação tributária não encontrado",
            CodigoErro("CAL-012", None, fat),
        ),
        SiglaDFeNaoEncontradaException: _ProblemType(
            "Sigla DFe não reconhecida", None,
        ),
    }


_PROBLEM_TYPES: dict[type[BaseException], _ProblemType] | None = None


def _catalogo() -> dict[type[BaseException], _ProblemType]:
    global _PROBLEM_TYPES
    if _PROBLEM_TYPES is None:
        _PROBLEM_TYPES = _problem_types()
    return _PROBLEM_TYPES


def _problem_type_from(exc: BaseException) -> _ProblemType:
    return _catalogo().get(
        type(exc),
        _ProblemType("Erro de sistema não previsto", None),
    )


def _titulo_validacao(codigo: str) -> str:
    return _TITULOS_VALIDACAO.get(codigo, "Erro de validação")


class GlobalCollector:
    def __init__(self) -> None:
        self._erros_globais: list[ErroDetalhe] = []
        self._item_collectors: list[ItemCollector] = []

    def add_erro_global(
        self,
        type_uri: str,
        title: str,
        code: str,
        pointer: str,
        detail: str,
    ) -> None:
        self._erros_globais.append(
            ErroDetalhe(type_uri, title, code, pointer, detail)
        )

    def add_item_collector(self, collector: ItemCollector) -> None:
        self._item_collectors.append(collector)

    def get_erros_globais(self) -> Sequence[ErroDetalhe]:
        return tuple(self._erros_globais)

    def get_item_collectors(self) -> Sequence[ItemCollector]:
        return tuple(self._item_collectors)

    def has_erros_globais(self) -> bool:
        return bool(self._erros_globais)


class ItemCollector:
    def __init__(self, index: int, base_url: str) -> None:
        self._index = index
        self._base_url = base_url
        self._erros: list[ErroDetalhe] = []
        self._estado = EstadoItemEnum.CALCULADO

    def add_erro_validacao(self, code: str, campo: str, detail: str) -> None:
        if self._estado is EstadoItemEnum.CALCULADO:
            self._estado = EstadoItemEnum.INCONSISTENCIA_ENTRADA
        pointer = self._build_pointer(campo)
        type_uri = self._build_type_uri(code)
        title = _titulo_validacao(code)
        self._erros.append(ErroDetalhe(type_uri, title, code, pointer, detail))

    def add_erro(self, exc: BaseException) -> None:
        problema = _problem_type_from(exc)
        codigo = problema.codigo_erro
        if codigo is not None:
            self._estado = codigo.estado
            pointer = self._build_pointer(codigo.campo_default)
            type_uri = self._build_type_uri(codigo.codigo)
            self._erros.append(
                ErroDetalhe(
                    type_uri,
                    problema.titulo,
                    codigo.codigo,
                    pointer,
                    str(exc),
                )
            )
        else:
            self._estado = EstadoItemEnum.FALHA_TECNICA
            pointer = f"#/itens/{self._index}"
            type_uri = self._build_type_uri("CAL-999")
            self._erros.append(
                ErroDetalhe(type_uri, problema.titulo, "CAL-999", pointer, str(exc))
            )

    def _build_type_uri(self, codigo: str) -> str:
        return f"{self._base_url}/api/calculadora/observabilidade/erros?codigo={codigo}"

    def _build_pointer(self, campo: str | None) -> str:
        if campo is None:
            return f"#/itens/{self._index}"
        return f"#/itens/{self._index}/{campo}"

    @property
    def estado(self) -> EstadoItemEnum:
        return self._estado

    def get_erros(self) -> Sequence[ErroDetalhe]:
        return tuple(self._erros)

    def has_erros(self) -> bool:
        return bool(self._erros)


class ErrosCalculoException(RuntimeError):
    def __init__(self, erros: Sequence[ErroDetalhe]) -> None:
        super().__init__("Erros de cálculo encontrados")
        self._erros = tuple(erros)

    def get_erros(self) -> Sequence[ErroDetalhe]:
        return self._erros