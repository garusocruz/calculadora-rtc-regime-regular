"""Processamento de operações em modo observabilidade (pin f1eebd7).

Transcrição de ``ObservabilidadeService.processarOperacao`` sem Spring, Jakarta
Validator, ModelMapper, log, ExecutorService nem virtual threads.
"""

from __future__ import annotations

import re
import sqlite3
from dataclasses import dataclass, field
from datetime import date, datetime
from decimal import Decimal
from typing import Any

from calculadora_rtc_regime_regular.banco import conectar
from calculadora_rtc_regime_regular.calculadora import (
    CalculadoraService,
    OperacaoCalculadoraInput,
    _buscar_aliquota_fixa,
    _buscar_aliquota_setorial,
    _montar_processamento,
    _tributos_item_para_domain,
)
from calculadora_rtc_regime_regular.cbs_ibs import AjusteNaoImplementado
from calculadora_rtc_regime_regular.coletor import (
    ErroDetalhe,
    ErrosCalculoException,
    EstadoItemEnum,
    ItemCollector,
    _titulo_validacao,
)
from calculadora_rtc_regime_regular.consultas import (
    MunicipioService,
    RedutorCompraGovernamentalService,
    SituacaoTributariaService,
    TipoDfeService,
    TributoEnum,
    UfService,
)
from calculadora_rtc_regime_regular.pedagio import buscar_aliquota_sqlite
from calculadora_rtc_regime_regular.processamento_item import (
    AliquotasNominaisImpostoSeletivo,
    AliquotasNominaisInput,
    ImpostoSeletivoInput,
    ItemOperacaoInput,
    OperacaoInput,
    ProcessamentoItemService,
    TipoDfe as TipoDfeItem,
    TributacaoRegularInput,
)
from calculadora_rtc_regime_regular.roc import (
    ObjetoDomain,
    TributosDomain,
    ValoresTotaisDomain,
)

_ARRAY_INDEX = re.compile(r"\[(\d+)]")

_ANNOTATION_CODES: dict[str, str] = {
    "NotNull": "VAL-001",
    "NotBlank": "VAL-002",
    "NotEmpty": "VAL-003",
    "Size": "VAL-004",
    "Min": "VAL-005",
    "Max": "VAL-006",
    "DecimalMin": "VAL-007",
    "DecimalMax": "VAL-008",
    "Pattern": "VAL-009",
    "Digits": "VAL-010",
    "Positive": "VAL-012",
    "PositiveOrZero": "VAL-013",
}

_TITULOS_CODIGO = {
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
    "VAL-012": "Valor deve ser positivo",
    "VAL-013": "Valor deve ser positivo ou zero",
}


class ErroFaltaImplementacaoException(Exception):
    _MESSAGE = (
        "A classificação tributária %s ainda não possui tratamento tributário "
        "implementado na Calculadora. Essa funcionalidade está prevista no "
        "roadmap e será disponibilizada em versão futura."
    )

    def __init__(self, codigo: str) -> None:
        super().__init__(self._MESSAGE % codigo)


@dataclass
class ObservabilidadeItemDomain:
    n_obj: int | None = None
    estado_item: EstadoItemEnum | None = None
    trib_calc: TributosDomain | None = None
    erros: list[ErroDetalhe] | None = None


@dataclass
class ObservabilidadeROCDomain:
    oper: Any = None
    objetos: list[ObservabilidadeItemDomain] = field(default_factory=list)
    total: ValoresTotaisDomain | None = None


class _ObservabilidadeItemCollector(ItemCollector):
    def registrar_falta_implementacao(self, codigo_cltr: str) -> None:
        self._estado = EstadoItemEnum.NAO_IMPLEMENTADO
        exc = ErroFaltaImplementacaoException(codigo_cltr)
        pointer = self._build_pointer("cClassTrib")
        code = "CAL-007"
        type_uri = self._build_type_uri(code)
        self._erros.append(
            ErroDetalhe(
                type_uri,
                "Classificação tributária em desenvolvimento",
                code,
                pointer,
                str(exc),
            )
        )


@dataclass(frozen=True, slots=True)
class _Violacao:
    campo: str
    anotacao: str
    mensagem: str
    valor: object | None


def _code_from(annotation: str) -> str:
    return _ANNOTATION_CODES.get(annotation, "VAL-000")


def _titulo_de_codigo(code: str) -> str:
    return _TITULOS_CODIGO.get(code, _titulo_validacao(code))


def _build_validation_detail(field: str, message: str, rejected: object | None) -> str:
    if rejected is not None:
        return f"Campo '{field}' {message}, recebido: '{rejected}'"
    return f"Campo '{field}' {message}"


def _to_json_pointer(field: str) -> str:
    converted = _ARRAY_INDEX.sub(r"/\1", field)
    converted = converted.replace(".", "/")
    return "#/" + converted


def _msg_not_null() -> str:
    return "não deve ser nulo"


def _msg_size(mn: int, mx: int) -> str:
    return f"tamanho deve ser entre {mn} e {mx}"


def _msg_min(value: int | Decimal) -> str:
    return f"deve ser maior que ou igual a {value}"


def _msg_max(value: int | Decimal) -> str:
    return f"deve ser menor que ou igual a {value}"


def _msg_positive_or_zero() -> str:
    return "deve ser maior que ou igual a 0"


def _msg_digits(integer: int, fraction: int) -> str:
    return (
        f"valor numérico fora dos limites (<{integer} dígitos>.<{fraction} dígitos> esperado)"
    )


def _msg_pattern() -> str:
    return "Informar somente dígitos"


def _digits_ok(value: Decimal, integer: int, fraction: int) -> bool:
    tup = value.as_tuple()
    if tup.sign:
        return False
    digitos = "".join(str(d) for d in tup.digits)
    if tup.exponent >= 0:
        int_part = digitos + "0" * tup.exponent
        frac_part = ""
    else:
        split = len(digitos) + tup.exponent
        if split <= 0:
            int_part = "0"
            frac_part = "0" * (-split) + digitos
        else:
            int_part = digitos[:split]
            frac_part = digitos[split:]
    if len(int_part) > integer:
        return False
    if len(frac_part) > fraction:
        return False
    return True


def _add_violation(
    out: list[_Violacao],
    prefix: str,
    anotacao: str,
    mensagem: str,
    valor: object | None,
) -> None:
    out.append(_Violacao(prefix, anotacao, mensagem, valor))


def _validar_string(
    out: list[_Violacao],
    prefix: str,
    valor: str | None,
    *,
    obrigatorio: bool,
    tamanho: tuple[int, int] | None = None,
    somente_digitos: bool = False,
) -> None:
    if valor is None:
        if obrigatorio:
            _add_violation(out, prefix, "NotNull", _msg_not_null(), None)
        return
    if tamanho is not None:
        mn, mx = tamanho
        if len(valor) < mn or len(valor) > mx:
            _add_violation(out, prefix, "Size", _msg_size(mn, mx), valor)
    if somente_digitos and not re.fullmatch(r"\d+", valor):
        _add_violation(out, prefix, "Pattern", _msg_pattern(), valor)


def _validar_decimal_campo(
    out: list[_Violacao],
    prefix: str,
    valor: Decimal | None,
    *,
    positive_or_zero: bool = False,
    digits: tuple[int, int] | None = None,
    decimal_max: Decimal | None = None,
) -> None:
    if valor is None:
        return
    if positive_or_zero and valor < 0:
        _add_violation(out, prefix, "PositiveOrZero", _msg_positive_or_zero(), valor)
    if digits is not None and not _digits_ok(valor, digits[0], digits[1]):
        _add_violation(out, prefix, "Digits", _msg_digits(digits[0], digits[1]), valor)
    if decimal_max is not None and valor > decimal_max:
        _add_violation(
            out, prefix, "DecimalMax", _msg_max(decimal_max), valor
        )


def _validar_inteiro(
    out: list[_Violacao],
    prefix: str,
    valor: int | None,
    *,
    obrigatorio: bool = False,
    mn: int | None = None,
    mx: int | None = None,
) -> None:
    if valor is None:
        if obrigatorio:
            _add_violation(out, prefix, "NotNull", _msg_not_null(), None)
        return
    if mn is not None and valor < mn:
        _add_violation(out, prefix, "Min", _msg_min(mn), valor)
    if mx is not None and valor > mx:
        _add_violation(out, prefix, "Max", _msg_max(mx), valor)


def _validar_imposto_seletivo(out: list[_Violacao], prefix: str, grupo: ImpostoSeletivoInput | None) -> None:
    if grupo is None:
        return
    _validar_string(out, f"{prefix}.cst", grupo.cst, obrigatorio=True, tamanho=(3, 3), somente_digitos=True)
    _validar_string(
        out,
        f"{prefix}.cClassTrib",
        grupo.c_class_trib,
        obrigatorio=True,
        tamanho=(6, 6),
        somente_digitos=True,
    )
    if grupo.base_calculo is None:
        _add_violation(out, f"{prefix}.baseCalculo", "NotNull", _msg_not_null(), None)
    else:
        _validar_decimal_campo(
            out,
            f"{prefix}.baseCalculo",
            grupo.base_calculo,
            positive_or_zero=True,
            digits=(13, 2),
        )
    _validar_decimal_campo(
        out, f"{prefix}.quantidade", grupo.quantidade, positive_or_zero=True, digits=(11, 4)
    )
    _validar_decimal_campo(
        out,
        f"{prefix}.impostoInformado",
        grupo.imposto_informado,
        positive_or_zero=True,
        digits=(13, 2),
    )


def _validar_tributacao_regular(out: list[_Violacao], prefix: str, grupo: TributacaoRegularInput | None) -> None:
    if grupo is None:
        return
    _validar_string(out, f"{prefix}.cst", grupo.cst, obrigatorio=True, tamanho=(3, 3), somente_digitos=True)
    _validar_string(
        out,
        f"{prefix}.cClassTrib",
        grupo.c_class_trib,
        obrigatorio=True,
        tamanho=(6, 6),
        somente_digitos=True,
    )


def _validar_aliquotas_nominais_is(
    out: list[_Violacao],
    prefix: str,
    grupo: AliquotasNominaisImpostoSeletivo | None,
) -> None:
    if grupo is None:
        return
    _validar_decimal_campo(
        out, f"{prefix}.adValorem", grupo.ad_valorem, positive_or_zero=True, digits=(3, 4), decimal_max=Decimal("100")
    )
    _validar_decimal_campo(
        out, f"{prefix}.adRem", grupo.ad_rem, positive_or_zero=True, digits=(3, 4), decimal_max=Decimal("100")
    )


def _validar_aliquotas_nominais(out: list[_Violacao], prefix: str, grupo: AliquotasNominaisInput | None) -> None:
    if grupo is None:
        return
    _validar_decimal_campo(
        out, f"{prefix}.cbs", grupo.cbs, positive_or_zero=True, digits=(3, 4), decimal_max=Decimal("100")
    )
    _validar_decimal_campo(
        out,
        f"{prefix}.ibsEstadual",
        grupo.ibs_estadual,
        positive_or_zero=True,
        digits=(3, 4),
        decimal_max=Decimal("100"),
    )
    _validar_decimal_campo(
        out,
        f"{prefix}.ibsMunicipal",
        grupo.ibs_municipal,
        positive_or_zero=True,
        digits=(3, 4),
        decimal_max=Decimal("100"),
    )
    _validar_aliquotas_nominais_is(out, f"{prefix}.impostoSeletivo", grupo.imposto_seletivo)


def _validar_item_estrutural(item: ItemOperacaoInput, index: int) -> list[_Violacao]:
    prefix = f"itens[{index}]"
    out: list[_Violacao] = []
    _validar_inteiro(out, f"{prefix}.numero", item.numero, obrigatorio=True, mn=1, mx=9_999_999)
    _validar_string(out, f"{prefix}.cst", item.cst, obrigatorio=True, tamanho=(3, 3), somente_digitos=True)
    _validar_string(
        out,
        f"{prefix}.cClassTrib",
        item.c_class_trib,
        obrigatorio=True,
        tamanho=(6, 6),
        somente_digitos=True,
    )
    _validar_decimal_campo(
        out, f"{prefix}.baseCalculo", item.base_calculo, positive_or_zero=True, digits=(13, 2)
    )
    _validar_decimal_campo(
        out, f"{prefix}.quantidade", item.quantidade, positive_or_zero=True, digits=(11, 4)
    )
    _validar_imposto_seletivo(out, f"{prefix}.impostoSeletivo", item.imposto_seletivo)
    _validar_tributacao_regular(out, f"{prefix}.tributacaoRegular", item.tributacao_regular)
    _validar_aliquotas_nominais(out, f"{prefix}.aliquotasNominais", item.aliquotas_nominais)
    return out


def _validar_operacao_estrutural(operacao: OperacaoCalculadoraInput) -> list[_Violacao]:
    out: list[_Violacao] = []
    if operacao.id is None:
        _add_violation(out, "id", "NotNull", _msg_not_null(), None)
    if operacao.versao is None:
        _add_violation(out, "versao", "NotNull", _msg_not_null(), None)
    _validar_inteiro(out, "municipio", operacao.municipio, obrigatorio=True, mn=0, mx=9_999_999)
    if operacao.uf is not None:
        if len(operacao.uf) < 2 or len(operacao.uf) > 2:
            _add_violation(out, "uf", "Size", _msg_size(2, 2), operacao.uf)
    if operacao.tp_doc is not None:
        _validar_inteiro(out, "tpDoc", operacao.tp_doc, mn=1, mx=999)
    if not operacao.itens:
        _add_violation(out, "itens", "NotEmpty", "não deve estar vazio", operacao.itens)
    return out


def _violacoes_para_erros_globais(
    violacoes: list[_Violacao], base_url: str
) -> list[ErroDetalhe]:
    erros: list[ErroDetalhe] = []
    for v in violacoes:
        code = _code_from(v.anotacao)
        pointer = _to_json_pointer(v.campo)
        detail = _build_validation_detail(v.campo, v.mensagem, v.valor)
        erros.append(
            ErroDetalhe(
                f"{base_url}/api/calculadora/observabilidade/erros?codigo={code}",
                _titulo_de_codigo(code),
                code,
                pointer,
                detail,
            )
        )
    return erros


def _compat_calculadora_runtime() -> None:
    """Ajustes pontuais sem alterar ``calculadora.py`` / ``consultas.py``."""
    if not hasattr(TributoEnum, "IMPOSTO_SELETIVO"):
        TributoEnum.IMPOSTO_SELETIVO = TributoEnum.IS  # type: ignore[attr-defined]


def _compat_item_seletivo(item: ItemOperacaoInput) -> None:
    seletivo = item.imposto_seletivo
    if seletivo is not None and not hasattr(seletivo, "valor_informado"):
        seletivo.valor_informado = seletivo.imposto_informado  # type: ignore[attr-defined]


class ObservabilidadeService:
    """Valida entrada, calcula itens em sequência e consolida erros por item."""

    def __init__(self, conexao: sqlite3.Connection | None = None) -> None:
        _compat_calculadora_runtime()
        self._conexao = conexao
        self._calculadora = CalculadoraService(conexao)
        self._uf = UfService(conexao)
        self._municipio = MunicipioService(conexao)
        self._tipo_dfe = TipoDfeService(conexao)
        self._redutor = RedutorCompraGovernamentalService(conexao)

    def _abrir(self) -> sqlite3.Connection:
        return self._conexao or conectar()

    def processar_operacao(
        self, operacao: OperacaoCalculadoraInput, base_url: str
    ) -> ObservabilidadeROCDomain:
        erros_globais = _violacoes_para_erros_globais(
            _validar_operacao_estrutural(operacao), base_url
        )
        if erros_globais:
            raise ErrosCalculoException(erros_globais)

        data: date
        tipo_dfe_db = None
        try:
            if not operacao.uf:
                operacao.uf = self._municipio.buscar_uf_por_municipio(operacao.municipio or 0)
            self._uf.validar_uf(operacao.uf or "")
            self._municipio.validar_municipio(operacao.municipio or 0, operacao.uf or "")
            data = operacao.fato_gerador_aplicavel()
            if operacao.tp_doc is not None:
                tipo_dfe_db = self._tipo_dfe.buscar_por_tipo(operacao.tp_doc, data)
        except Exception as ex:
            collector = ItemCollector(-1, base_url)
            collector.add_erro(ex)
            raise ErrosCalculoException(collector.get_erros()) from ex

        tipo_dfe_item = None
        if tipo_dfe_db is not None:
            tipo_dfe_item = TipoDfeItem(
                tipo_dfe_db.tipo, tipo_dfe_db.sigla, tipo_dfe_db.permite_ncm_zero
            )

        resultados: list[ObservabilidadeItemDomain] = []
        with self._abrir() as conexao:
            tipo_holder: list = [tipo_dfe_db]
            processamento = _montar_processamento(conexao, tipo_holder)
            codigo_uf = self._uf.buscar(operacao.uf or "")
            p_redutor = self._redutor.buscar_valor_redutor(operacao.tp_ente_gov(), data)
            tp_ente = operacao.tp_ente_gov().name if operacao.tp_ente_gov() is not None else None
            op_proc = OperacaoInput(
                id=operacao.id,
                versao=operacao.versao,
                tp_doc=operacao.tp_doc,
                municipio=operacao.municipio,
                uf=operacao.uf,
                data_fato_gerador=data,
            )
            itens = operacao.itens
            for index in range(len(itens)):
                item_in = itens[index]
                resultados.append(
                    self._processar_item_com_validacao(
                        operacao=operacao,
                        op_proc=op_proc,
                        item=item_in,
                        index=index,
                        data=data,
                        tipo_dfe_item=tipo_dfe_item,
                        processamento=processamento,
                        conexao=conexao,
                        codigo_uf=codigo_uf,
                        tp_ente=tp_ente,
                        p_redutor=p_redutor,
                        base_url=base_url,
                    )
                )

        resultados.sort(key=lambda r: r.n_obj or 0)

        calculados = [
            ObjetoDomain(n_obj=r.n_obj, trib_calc=r.trib_calc)
            for r in resultados
            if r.estado_item in (EstadoItemEnum.CALCULADO, EstadoItemEnum.CALCULO_SIMULADO)
        ]
        total = ValoresTotaisDomain.create(calculados) if calculados else None

        return ObservabilidadeROCDomain(
            oper=self._calculadora._operacao_output(operacao, data),
            objetos=resultados,
            total=total,
        )

    def _processar_item_com_validacao(
        self,
        *,
        operacao: OperacaoCalculadoraInput,
        op_proc: OperacaoInput,
        item: ItemOperacaoInput,
        index: int,
        data: date,
        tipo_dfe_item: TipoDfeItem | None,
        processamento: ProcessamentoItemService,
        conexao: sqlite3.Connection,
        codigo_uf: int,
        tp_ente: str | None,
        p_redutor: Decimal,
        base_url: str,
    ) -> ObservabilidadeItemDomain:
        collector = _ObservabilidadeItemCollector(index, base_url)
        n_obj = item.numero if item.numero is not None else index + 1

        for v in _validar_item_estrutural(item, index):
            campo = v.campo
            if campo.startswith(f"itens[{index}]."):
                campo = campo[len(f"itens[{index}].") :]
            collector.add_erro_validacao(
                _code_from(v.anotacao),
                campo,
                _build_validation_detail(v.campo, v.mensagem, v.valor),
            )

        if collector.has_erros():
            return ObservabilidadeItemDomain(
                n_obj=n_obj,
                estado_item=collector.estado,
                erros=list(collector.get_erros()),
            )

        item_proc = ItemOperacaoInput(
            numero=item.numero,
            ncm=item.ncm,
            nbs=item.nbs,
            cst=item.cst,
            c_class_trib=item.c_class_trib,
            base_calculo=item.base_calculo,
            quantidade=item.quantidade,
            unidade=item.unidade,
            imposto_seletivo=item.imposto_seletivo,
            tributacao_regular=item.tributacao_regular,
            g_componentes_bc=item.g_componentes_bc,
            aliquotas_nominais=item.aliquotas_nominais,
        )

        try:
            _compat_item_seletivo(item_proc)
            from calculadora_rtc_regime_regular.aliquota_resultado import (
                AliquotaReferenciaNaoEncontrada,
            )

            def buscar_padrao(id_tributo: int, uf: int | None, municipio: int | None, d: date):
                resultado = buscar_aliquota_sqlite(id_tributo, uf, municipio, d, conexao)
                if resultado is None:
                    raise AliquotaReferenciaNaoEncontrada()
                return resultado

            sit = SituacaoTributariaService(conexao)
            modelo = processamento.processar_item(op_proc, item_proc, data, tipo_dfe_item)
            tributos_item = self._calculadora._calcular_item(
                conexao,
                op_proc,
                item_proc,
                data,
                modelo,
                codigo_uf,
                tp_ente,
                p_redutor,
                sit=sit,
                buscar_padrao=buscar_padrao,
                buscar_referencia=lambda id_tributo, d: self._calculadora._referencia.buscar(
                    id_tributo, d
                ),
                buscar_setorial=lambda nbs, id_tributo, id_classificacao, d: _buscar_aliquota_setorial(
                    conexao, nbs, id_tributo, id_classificacao, d
                ),
                buscar_fixa=lambda id_tributo, id_classificacao, d: _buscar_aliquota_fixa(
                    conexao, id_tributo, id_classificacao, d
                ),
                buscar_percentual_transferencia=lambda d: self._calculadora._transferencia.get_percentual_transferencia(
                    d
                ),
            )
            trib_domain = _tributos_item_para_domain(tributos_item)
            estado = (
                EstadoItemEnum.CALCULO_SIMULADO
                if item.aliquotas_nominais is not None
                else EstadoItemEnum.CALCULADO
            )
            return ObservabilidadeItemDomain(
                n_obj=n_obj, estado_item=estado, trib_calc=trib_domain
            )
        except AjusteNaoImplementado as ex:
            codigo = str(ex.args[0]) if ex.args else ""
            collector.registrar_falta_implementacao(codigo)
            return ObservabilidadeItemDomain(
                n_obj=n_obj,
                estado_item=collector.estado,
                erros=list(collector.get_erros()),
            )
        except Exception as ex:
            collector.add_erro(ex)
            return ObservabilidadeItemDomain(
                n_obj=n_obj,
                estado_item=collector.estado,
                erros=list(collector.get_erros()),
            )


def operacao_from_json(payload: dict[str, Any]) -> OperacaoCalculadoraInput:
    """Converte JSON de teste (nomes Jackson) em ``OperacaoCalculadoraInput``."""

    def _dec(key: str, src: dict[str, Any]) -> Decimal | None:
        if key not in src or src[key] is None:
            return None
        return Decimal(str(src[key]))

    def _parse_data(raw: dict[str, Any]) -> date | None:
        if "dhFatoGerador" in raw and raw["dhFatoGerador"]:
            text = str(raw["dhFatoGerador"])
            if text.endswith("Z"):
                text = text[:-1] + "+00:00"
            return datetime.fromisoformat(text).date()
        if "dataHoraEmissao" in raw and raw["dataHoraEmissao"]:
            text = str(raw["dataHoraEmissao"])
            if text.endswith("Z"):
                text = text[:-1] + "+00:00"
            return datetime.fromisoformat(text).date()
        if "data_fato_gerador" in raw and raw["data_fato_gerador"]:
            val = raw["data_fato_gerador"]
            if isinstance(val, date):
                return val
            return date.fromisoformat(str(val)[:10])
        return None

    def _is(raw: dict[str, Any] | None) -> ImpostoSeletivoInput | None:
        if not raw:
            return None
        return ImpostoSeletivoInput(
            cst=raw.get("cst"),
            c_class_trib=raw.get("cClassTrib"),
            base_calculo=_dec("baseCalculo", raw),
            quantidade=_dec("quantidade", raw),
            unidade=raw.get("unidade"),
            imposto_informado=_dec("impostoInformado", raw),
        )

    def _an_is(raw: dict[str, Any] | None) -> AliquotasNominaisImpostoSeletivo | None:
        if not raw:
            return None
        return AliquotasNominaisImpostoSeletivo(
            ad_valorem=_dec("adValorem", raw),
            ad_rem=_dec("adRem", raw),
        )

    def _aliquotas(raw: dict[str, Any] | None) -> AliquotasNominaisInput | None:
        if not raw:
            return None
        return AliquotasNominaisInput(
            cbs=_dec("cbs", raw),
            ibs_estadual=_dec("ibsEstadual", raw),
            ibs_municipal=_dec("ibsMunicipal", raw),
            imposto_seletivo=_an_is(raw.get("impostoSeletivo")),
        )

    def _trib_reg(raw: dict[str, Any] | None) -> TributacaoRegularInput | None:
        if not raw:
            return None
        return TributacaoRegularInput(cst=raw["cst"], c_class_trib=raw["cClassTrib"])

    itens: list[ItemOperacaoInput] = []
    for raw_item in payload.get("itens") or []:
        itens.append(
            ItemOperacaoInput(
                numero=raw_item.get("numero"),
                ncm=raw_item.get("ncm"),
                nbs=raw_item.get("nbs"),
                cst=raw_item.get("cst"),
                c_class_trib=raw_item.get("cClassTrib"),
                base_calculo=_dec("baseCalculo", raw_item),
                quantidade=_dec("quantidade", raw_item),
                unidade=raw_item.get("unidade"),
                imposto_seletivo=_is(raw_item.get("impostoSeletivo")),
                tributacao_regular=_trib_reg(raw_item.get("tributacaoRegular")),
                aliquotas_nominais=_aliquotas(raw_item.get("aliquotasNominais")),
            )
        )

    g_compra = payload.get("gCompraGov")
    g_compra_obj = None
    if g_compra:
        from calculadora_rtc_regime_regular.calculadora import CompraGovernamentalInput
        from calculadora_rtc_regime_regular.consultas import TipoEnteGovernamental

        g_compra_obj = CompraGovernamentalInput(
            tp_ente_gov=TipoEnteGovernamental(int(g_compra["tpEnteGov"])),
            tp_oper_gov=g_compra.get("tpOperGov"),
        )

    return OperacaoCalculadoraInput(
        id=payload.get("id"),
        versao=payload.get("versao"),
        municipio=payload.get("municipio"),
        uf=payload.get("uf"),
        tp_doc=payload.get("tpDoc"),
        data_fato_gerador=_parse_data(payload),
        g_compra_gov=g_compra_obj,
        itens=itens,
    )