"""Memória de cálculo e tokenização de templates (pin f1eebd7ce3157423b1a6aaca7dc1d6c3395452c4).

Transcrição de ``MemoriaCalculoService`` e ``domain.service.token`` sem Spring.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from decimal import Decimal
from typing import Any, Mapping

from calculadora_rtc_regime_regular.arredondamento import (
    arredondar_aliquota_publicada,
    arredondar_valor_fiscal,
)
from calculadora_rtc_regime_regular.consultas import (
    FundamentacaoClassificacaoService,
    TratamentoClassificacaoDTO,
    TratamentoTributarioService,
)
from calculadora_rtc_regime_regular.roc import (
    CBSDomain,
    DiferimentoDomain,
    GrupoMonofasiaOutput,
    IBSCBSDomain,
    IBSMunDomain,
    IBSUFDomain,
    ImpostoSeletivoDomain,
    MemoriaCalculoDomain,
)

_TEXTO_MEMORIA_AUSENTE = "Texto de memória de cálculo não encontrado"


@dataclass(frozen=True, slots=True)
class TextToken:
    text: str | None
    key: str | None


def tokenize(template: str) -> tuple[TextToken, ...]:
    tokens: list[TextToken] = []
    last = 0
    length = len(template)
    while last < length:
        open_bracket = template.find("[", last)
        if open_bracket < 0:
            tokens.append(TextToken(template[last:], None))
            break
        close_bracket = template.find("]", open_bracket + 1)
        if close_bracket < 0:
            tokens.append(TextToken(template[last:], None))
            break
        if open_bracket > last:
            tokens.append(TextToken(template[last:open_bracket], None))
        key = template[open_bracket + 1 : close_bracket]
        tokens.append(TextToken(None, key))
        last = close_bracket + 1
    return tuple(tokens)


class TokenizerService:
    def substituir_placeholders(
        self, template: str, values: Mapping[str, str]
    ) -> str:
        if "[" not in template:
            return template
        parts: list[str] = []
        for token in tokenize(template):
            if token.key is None:
                parts.append(token.text or "")
            else:
                parts.append(values.get(token.key, ""))
        return "".join(parts)


def _agrupar_milhares(inteiro: str) -> str:
    if len(inteiro) <= 3:
        return inteiro
    grupos: list[str] = []
    restante = inteiro
    while restante:
        grupos.append(restante[-3:])
        restante = restante[:-3]
    return ".".join(reversed(grupos))


def formatar_moeda(valor: Decimal | None) -> str:
    v = arredondar_valor_fiscal(Decimal(0) if valor is None else valor)
    assert v is not None
    negativo = v < 0
    v = abs(v)
    inteiro, fracao = f"{v:.2f}".split(".")
    prefixo = "-" if negativo else ""
    return f"{prefixo}{_agrupar_milhares(inteiro)},{fracao}"


def formatar_percentual(valor: Decimal | None) -> str:
    v = arredondar_aliquota_publicada(Decimal(0) if valor is None else valor)
    assert v is not None
    negativo = v < 0
    v = abs(v)
    inteiro, fracao = f"{v:.4f}".split(".")
    fracao = fracao.rstrip("0")
    if len(fracao) < 2:
        fracao = fracao.ljust(2, "0")
    prefixo = "-" if negativo else ""
    return f"{prefixo}{_agrupar_milhares(inteiro)},{fracao}"


def _default_string(texto: str | None) -> str:
    return texto if texto is not None else ""


def _ler_base_calculo(tributo: Any) -> Decimal | None:
    if tributo is None:
        return None
    if (valor := getattr(tributo, "base_calculo", None)) is not None:
        return valor
    return getattr(tributo, "baseCalculo", None)


def _ler_aliquota(tributo: Any) -> Decimal | None:
    if tributo is None:
        return None
    return getattr(tributo, "aliquota", None)


def _ler_grupo_reducao(tributo: Any) -> Any | None:
    if tributo is None:
        return None
    return getattr(tributo, "grupo_reducao", None) or getattr(
        tributo, "grupoReducao", None
    )


def _ler_grupo_diferimento(tributo: Any) -> Any | None:
    if tributo is None:
        return None
    return getattr(tributo, "grupo_diferimento", None) or getattr(
        tributo, "grupoDiferimento", None
    )


def _ler_grupo_monofasia(tributo: Any) -> GrupoMonofasiaOutput | None:
    if tributo is None:
        return None
    return getattr(tributo, "grupo_monofasia", None) or getattr(
        tributo, "grupoMonofasia", None
    )


def _percentual_reducao(grupo: Any) -> Decimal | None:
    if grupo is None:
        return None
    return getattr(grupo, "p_red_aliq", None) or getattr(grupo, "pRedAliq", None)


def _diferimento(grupo: Any) -> tuple[Decimal | None, Decimal | None]:
    if grupo is None:
        return None, None
    p_dif = getattr(grupo, "p_dif", None) or getattr(grupo, "pDif", None)
    v_dif = getattr(grupo, "v_dif", None) or getattr(grupo, "vDif", None)
    return p_dif, v_dif


def _aliquota_ad_rem_monofasia(grupo: GrupoMonofasiaOutput | None) -> Decimal | None:
    if grupo is None:
        return None
    mono = getattr(grupo, "tributo_monofasico", None) or getattr(
        grupo, "tributoMonofasico", None
    )
    if mono is None:
        return None
    return getattr(mono, "aliquota_ad_rem", None) or getattr(mono, "aliquotaAdRem", None)


@dataclass
class TributoCbsIbsMemoria:
    base_calculo: Decimal | None = None
    aliquota: Decimal | None = None
    grupo_reducao: Any | None = None
    grupo_diferimento: DiferimentoDomain | None = None
    grupo_monofasia: GrupoMonofasiaOutput | None = None


class MemoriaCalculoService:
    def __init__(
        self,
        tokenizer_service: TokenizerService | None = None,
        fundamentacao_classificacao_service: FundamentacaoClassificacaoService
        | None = None,
        tratamento_service: TratamentoTributarioService | None = None,
        *,
        memoria_calculo_habilitada: bool = True,
    ) -> None:
        self._tokenizer = tokenizer_service or TokenizerService()
        self._fundamentacao = (
            fundamentacao_classificacao_service or FundamentacaoClassificacaoService()
        )
        self._tratamento = tratamento_service or TratamentoTributarioService()
        self._memoria_habilitada = memoria_calculo_habilitada

    @staticmethod
    def formatarMoeda(valor: Decimal | None) -> str:
        """Espelho do ``MemoriaCalculoService.formatarMoeda`` Java (pt-BR)."""
        return formatar_moeda(valor)

    @staticmethod
    def formatarPercentual(valor: Decimal | None) -> str:
        """Espelho do ``MemoriaCalculoService.formatarPercentual`` Java (pt-BR)."""
        return formatar_percentual(valor)

    def gerar_memoria_calculo_cbs_ibs(
        self,
        tratamento_classificacao: TratamentoClassificacaoDTO,
        tributo: TributoCbsIbsMemoria | Any | None,
        base_calculo_informada: Decimal | None,
        quantidade: Decimal | None,
        unidade: str | None,
        data: date,
    ) -> str | None:
        if not self._memoria_habilitada:
            return None
        if tributo is None:
            tributo = TributoCbsIbsMemoria(base_calculo=base_calculo_informada)

        fundamentacao = self._fundamentacao.buscar(
            tratamento_classificacao.id_classificacao_tributaria, data
        )
        tt = self._tratamento.buscar(tratamento_classificacao.id_tratamento_tributario)

        base = _ler_base_calculo(tributo) or base_calculo_informada
        grupo_red = _ler_grupo_reducao(tributo)
        grupo_dif = _ler_grupo_diferimento(tributo)
        p_dif, v_dif = _diferimento(grupo_dif)

        valores = {
            "norma": _default_string(fundamentacao.texto_curto),
            "tratamento": _default_string(tt.descricao),
            "base_calculo": _default_string(formatar_moeda(base)),
            "aliquota_ad_valorem": _default_string(
                formatar_percentual(_ler_aliquota(tributo))
            ),
            "aliquota_ad_rem": _default_string(
                formatar_percentual(
                    _aliquota_ad_rem_monofasia(_ler_grupo_monofasia(tributo))
                )
            ),
            "quantidade": str(quantidade) if quantidade is not None else "0",
            "unidade": _default_string(unidade),
            "percentual_reducao": _default_string(
                formatar_percentual(_percentual_reducao(grupo_red))
            ),
            "percentual_diferimento": _default_string(formatar_percentual(p_dif))
            if p_dif is not None and v_dif is not None
            else _default_string(formatar_percentual(None)),
            "valor_diferimento": _default_string(formatar_moeda(v_dif))
            if p_dif is not None and v_dif is not None
            else _default_string(formatar_moeda(None)),
            "aliquota_desoneracao": _default_string(formatar_percentual(None)),
            "montante_desoneracao": _default_string(formatar_moeda(None)),
        }

        texto = fundamentacao.memoria_calculo
        if not (texto or "").strip():
            return _TEXTO_MEMORIA_AUSENTE
        return self._tokenizer.substituir_placeholders(texto, valores)

    def gerar_memoria_calculo_imposto_seletivo(
        self,
        tratamento_classificacao: TratamentoClassificacaoDTO,
        tributo: ImpostoSeletivoDomain,
        quantidade: Decimal | None,
        unidade: str | None,
        data: date,
    ) -> None:
        if not self._memoria_habilitada:
            return
        fundamentacao = self._fundamentacao.buscar(
            tratamento_classificacao.id_classificacao_tributaria, data
        )
        tt = self._tratamento.buscar(tratamento_classificacao.id_tratamento_tributario)
        valores = {
            "norma": _default_string(fundamentacao.texto_curto),
            "tratamento": _default_string(tt.descricao),
            "base_calculo": _default_string(formatar_moeda(tributo.v_bcis)),
            "aliquota_ad_valorem": _default_string(formatar_percentual(tributo.p_is)),
            "aliquota_ad_rem": _default_string(formatar_percentual(tributo.p_is_espec)),
            "quantidade": "" if quantidade is None else str(quantidade),
            "unidade": _default_string(unidade),
        }
        texto = fundamentacao.memoria_calculo
        if not (texto or "").strip():
            tributo.memoria_calculo = _TEXTO_MEMORIA_AUSENTE
        else:
            tributo.memoria_calculo = self._tokenizer.substituir_placeholders(
                texto, valores
            )

    def anexar_memoria_ibscbs(
        self,
        tratamento: TratamentoClassificacaoDTO,
        ibscbs: IBSCBSDomain,
        base_calculo: Decimal | None,
        quantidade: Decimal | None,
        unidade: str | None,
        data: date,
        *,
        calcular_ibs_estadual: bool,
        calcular_ibs_municipal: bool,
    ) -> None:
        """Preenche ``IBSCBSDomain.memoria_calculo`` como ``CalculoTributoService``."""
        grupo = ibscbs.g_ibscbs
        ibscbs.memoria_calculo = MemoriaCalculoDomain(
            cbs=self.gerar_memoria_calculo_cbs_ibs(
                tratamento,
                _tributo_memoria(grupo.g_cbs if grupo else None, base_calculo),
                base_calculo,
                quantidade,
                unidade,
                data,
            ),
            ibs_uf=(
                self.gerar_memoria_calculo_cbs_ibs(
                    tratamento,
                    _tributo_memoria(grupo.g_ibs_uf if grupo else None, base_calculo),
                    base_calculo,
                    quantidade,
                    unidade,
                    data,
                )
                if calcular_ibs_estadual
                else None
            ),
            ibs_mun=(
                self.gerar_memoria_calculo_cbs_ibs(
                    tratamento,
                    _tributo_memoria(grupo.g_ibs_mun if grupo else None, base_calculo),
                    base_calculo,
                    quantidade,
                    unidade,
                    data,
                )
                if calcular_ibs_municipal
                else None
            ),
        )


def _aliquota_publicada(grupo: CBSDomain | IBSUFDomain | IBSMunDomain | None) -> Decimal | None:
    if grupo is None:
        return None
    for nome in ("p_cbs", "p_ibs_uf", "p_ibs_mun", "aliquota"):
        valor = getattr(grupo, nome, None)
        if valor is not None:
            return valor
    return None


def _tributo_memoria(
    grupo: CBSDomain | IBSUFDomain | IBSMunDomain | None,
    base_calculo: Decimal | None,
) -> TributoCbsIbsMemoria | None:
    if grupo is None:
        return None
    return TributoCbsIbsMemoria(
        base_calculo=base_calculo,
        aliquota=_aliquota_publicada(grupo),
        grupo_reducao=getattr(grupo, "g_red", None),
        grupo_diferimento=getattr(grupo, "g_dif", None),
    )