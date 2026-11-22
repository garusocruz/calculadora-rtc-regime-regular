"""Geração e validação de XML fiscal (transcrição de XmlUtil, XmlService e *XmlService).

Pin ``f1eebd7ce3157423b1a6aaca7dc1d6c3395452c4``. Sem Spring/JAXB; montagem via lxml.
"""

from __future__ import annotations

from collections.abc import Mapping
from decimal import Decimal
from enum import Enum
from functools import lru_cache
from io import BytesIO
from pathlib import Path
from typing import Any
from lxml import etree

from calculadora_rtc_regime_regular.arredondamento import formatar_aliquota

_RECURSOS_XML = (
    Path(__file__).resolve().parent.parent
    / ".cache"
    / "oficial"
    / "java"
    / "src"
    / "main"
    / "resources"
)


class TipoDocumento(Enum):
    NFE = ("nfe", True, True)
    NFCE = ("nfce", True, True)
    NFSE = ("nfse", False, True)
    CTE = ("cte", True, True)
    CTE_SIMPLIFICADO = ("cte-simplificado", True, True)
    BPE = ("bpe", True, True)
    BPE_TM = ("bpe-tm", True, True)
    NF3E = ("nf3e", True, True)

    def __init__(self, mnemonico: str, geracao: bool, validacao: bool) -> None:
        self.mnemonico = mnemonico
        self.geracao = geracao
        self.validacao = validacao

    @classmethod
    def from_mnemonico(cls, mnemonico: str) -> TipoDocumento:
        if mnemonico is None or not str(mnemonico).strip():
            raise ValueError("Mnemonico não pode ser nulo ou vazio")
        for tipo in cls:
            if tipo.mnemonico.lower() == mnemonico.strip().lower():
                return tipo
        raise ValueError(f"Tipo de documento inválido: {mnemonico}")


class TipoXml(Enum):
    GRUPO = "grupo.xsd"
    NOTA = "nota.xsd"

    def __init__(self, mnemonico: str) -> None:
        self.mnemonico = mnemonico

    @classmethod
    def from_mnemonico(cls, mnemonico: str) -> TipoXml:
        if mnemonico is None or not str(mnemonico).strip():
            raise ValueError("Mnemonico não pode ser nulo ou vazio")
        for tipo in cls:
            if tipo.mnemonico.lower() == mnemonico.strip().lower() or tipo.name.lower() == mnemonico.strip().lower():
                return tipo
        raise ValueError(f"Tipo de XML inválido: {mnemonico}")


class ErroXmlException(Exception):
    """Erro de estrutura, parsing ou validação em documentos XML."""

    def __init__(self, erro: str) -> None:
        super().__init__(f"Erro na validação do XML: {erro}")


_NS_POR_DOCUMENTO: dict[TipoDocumento, str] = {
    TipoDocumento.NFE: "http://www.portalfiscal.inf.br/nfe",
    TipoDocumento.NFCE: "http://www.portalfiscal.inf.br/nfe",
    TipoDocumento.NFSE: "http://www.portalfiscal.inf.br/nfse",
    TipoDocumento.CTE: "http://www.portalfiscal.inf.br/cte",
    TipoDocumento.CTE_SIMPLIFICADO: "http://www.portalfiscal.inf.br/cte",
    TipoDocumento.BPE: "http://www.portalfiscal.inf.br/bpe",
    TipoDocumento.BPE_TM: "http://www.portalfiscal.inf.br/bpe",
    TipoDocumento.NF3E: "http://www.portalfiscal.inf.br/nf3e",
}


def _sem_memoria_calculo(valor: Any) -> Any:
    if isinstance(valor, Mapping):
        return {chave: _sem_memoria_calculo(item) for chave, item in valor.items() if chave != "memoriaCalculo"}
    if isinstance(valor, list):
        return [_sem_memoria_calculo(item) for item in valor]
    return valor


def _formatar_p_redutor(valor: Any) -> str:
    if valor is None:
        return None  # type: ignore[return-value]
    if isinstance(valor, str):
        return valor
    return formatar_aliquota(Decimal(str(valor)))


def _ibscbs_tot_layout_nf3e_bpe_tm(tot: Mapping[str, Any]) -> dict[str, Any]:
    """Campos compatíveis com TIBSCBSTot de NF3e e BPe TM (sem gMono nem crédito presumido)."""
    tot = _sem_memoria_calculo(tot)
    g_ibs = tot["gIBS"]
    g_cbs = tot["gCBS"]
    return {
        "vBCIBSCBS": tot["vBCIBSCBS"],
        "gIBS": {
            "gIBSUF": {chave: g_ibs["gIBSUF"][chave] for chave in ("vDif", "vDevTrib", "vIBSUF")},
            "gIBSMun": {chave: g_ibs["gIBSMun"][chave] for chave in ("vDif", "vDevTrib", "vIBSMun")},
            "vIBS": g_ibs["vIBS"],
        },
        "gCBS": {chave: g_cbs[chave] for chave in ("vDif", "vDevTrib", "vCBS")},
    }


def _compra_gov_para_xml(grupo: Mapping[str, Any]) -> dict[str, str]:
    return {
        "tpEnteGov": str(grupo["tpEnteGov"]),
        "pRedutor": _formatar_p_redutor(grupo.get("pRedutor")),
        "tpOperGov": str(grupo["tpOperGov"]),
    }


def _ide_compra_gov(roc: Mapping[str, Any]) -> dict[str, Any] | None:
    oper = roc.get("oper")
    if not oper:
        return None
    compra = oper.get("gCompraGov")
    if not compra:
        return None
    return {"gCompraGov": _compra_gov_para_xml(compra)}


def _exigir(condicao: bool, mensagem: str) -> None:
    if not condicao:
        raise ValueError(mensagem)


def _dict_para_elemento(
    pai: etree._Element,
    tag: str,
    dados: Mapping[str, Any],
    namespace: str,
) -> None:
    elemento = etree.SubElement(pai, f"{{{namespace}}}{tag}")
    for chave, valor in dados.items():
        if valor is None:
            continue
        if isinstance(valor, Mapping):
            _dict_para_elemento(elemento, chave, valor, namespace)
        else:
            filho = etree.SubElement(elemento, f"{{{namespace}}}{chave}")
            filho.text = str(valor)


def _elemento_raiz(nome: str, namespace: str) -> etree._Element:
    return etree.Element(f"{{{namespace}}}{nome}", nsmap={None: namespace})


def _serializar_xml(raiz: etree._Element) -> str:
    corpo = etree.tostring(
        raiz,
        xml_declaration=False,
        encoding="UTF-8",
        pretty_print=True,
    ).decode("utf-8")
    return '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>\n' + corpo


class XmlUtil:
    def get_schema(self, tipo: TipoDocumento, subtipo: TipoXml) -> etree.XMLSchema:
        if tipo is None:
            raise TypeError("tipo não pode ser nulo")
        if subtipo is None:
            raise TypeError("subtipo não pode ser nulo")
        return _schema_compilado(tipo, subtipo)


@lru_cache(maxsize=None)
def _schema_compilado(tipo: TipoDocumento, subtipo: TipoXml) -> etree.XMLSchema:
    relativo = f"xml/{tipo.mnemonico}/{subtipo.mnemonico}"
    xsd_path = _RECURSOS_XML / relativo
    if not xsd_path.is_file():
        raise OSError("XSD file not found in classpath")
    documento = etree.parse(str(xsd_path))
    return etree.XMLSchema(documento)


class NfeXmlService:
    def to_xml(self, roc: Mapping[str, Any]) -> str:
        namespace = _NS_POR_DOCUMENTO[TipoDocumento.NFE]
        _exigir(roc is not None, "ROC não pode ser nulo")
        objetos = roc.get("objetos")
        _exigir(objetos, "ROC deve conter ao menos um objeto")
        trib_total = (roc.get("total") or {}).get("tribCalc")
        _exigir(trib_total is not None, "Total do ROC não informado")

        raiz = _elemento_raiz("infNFe", namespace)
        ide = _ide_compra_gov(roc)
        if ide:
            _dict_para_elemento(raiz, "ide", ide, namespace)

        for objeto in objetos:
            det = etree.SubElement(raiz, f"{{{namespace}}}det", nItem=str(objeto["nObj"]))
            _dict_para_elemento(det, "imposto", _sem_memoria_calculo(objeto["tribCalc"]), namespace)

        _dict_para_elemento(raiz, "total", _sem_memoria_calculo(trib_total), namespace)
        return _serializar_xml(raiz)


class NfceXmlService:
    def to_xml(self, roc: Mapping[str, Any]) -> str:
        namespace = _NS_POR_DOCUMENTO[TipoDocumento.NFCE]
        _exigir(roc is not None, "ROC não pode ser nulo")
        objetos = roc.get("objetos")
        _exigir(objetos, "ROC deve conter ao menos um objeto")
        trib_total = (roc.get("total") or {}).get("tribCalc")
        _exigir(trib_total is not None, "Total do ROC não informado")

        raiz = _elemento_raiz("infNFe", namespace)
        for objeto in objetos:
            det = etree.SubElement(raiz, f"{{{namespace}}}det", nItem=str(objeto["nObj"]))
            _dict_para_elemento(det, "imposto", _sem_memoria_calculo(objeto["tribCalc"]), namespace)

        _dict_para_elemento(raiz, "total", _sem_memoria_calculo(trib_total), namespace)
        return _serializar_xml(raiz)


class _DocumentoItemUnicoService:
    """CTe, CTe simplificado e BPe normal: um objeto, imp.IBSCBS."""

    tag_raiz: str
    tipo: TipoDocumento

    def to_xml(self, roc: Mapping[str, Any]) -> str:
        namespace = _NS_POR_DOCUMENTO[self.tipo]
        _exigir(roc is not None, "ROC não pode ser nulo")
        objetos = roc.get("objetos") or []
        _exigir(len(objetos) == 1, "ROC deve conter um item")

        raiz = _elemento_raiz(self.tag_raiz, namespace)
        ide = _ide_compra_gov(roc)
        if ide:
            _dict_para_elemento(raiz, "ide", ide, namespace)

        imposto = etree.SubElement(raiz, f"{{{namespace}}}imp")
        _dict_para_elemento(
            imposto,
            "IBSCBS",
            _sem_memoria_calculo(objetos[0]["tribCalc"]["IBSCBS"]),
            namespace,
        )
        return _serializar_xml(raiz)


class CteXmlService(_DocumentoItemUnicoService):
    tag_raiz = "infCte"
    tipo = TipoDocumento.CTE


class CteSimplificadoXmlService(_DocumentoItemUnicoService):
    tag_raiz = "infCte"
    tipo = TipoDocumento.CTE_SIMPLIFICADO


class BpeXmlService(_DocumentoItemUnicoService):
    tag_raiz = "infBPe"
    tipo = TipoDocumento.BPE


class BpeTMXmlService:
    def to_xml(self, roc: Mapping[str, Any]) -> str:
        namespace = _NS_POR_DOCUMENTO[TipoDocumento.BPE_TM]
        _exigir(roc is not None, "ROC não pode ser nulo")
        objetos = roc.get("objetos") or []
        _exigir(len(objetos) == 1, "ROC deve conter um item")
        trib_total = (roc.get("total") or {}).get("tribCalc")
        _exigir(trib_total is not None, "Total do ROC não informado")

        raiz = _elemento_raiz("infBPe", namespace)
        ide = _ide_compra_gov(roc)
        if ide:
            _dict_para_elemento(raiz, "ide", ide, namespace)

        det_bpe_tm = etree.SubElement(raiz, f"{{{namespace}}}detBPeTM")
        objeto = objetos[0]
        det = etree.SubElement(det_bpe_tm, f"{{{namespace}}}det", nViagem=str(objeto["nObj"]))
        imp = etree.SubElement(det, f"{{{namespace}}}imp")
        _dict_para_elemento(
            imp,
            "IBSCBS",
            _sem_memoria_calculo(objeto["tribCalc"]["IBSCBS"]),
            namespace,
        )

        total = {"IBSCBSTot": _ibscbs_tot_layout_nf3e_bpe_tm(trib_total["IBSCBSTot"])}
        _dict_para_elemento(raiz, "total", total, namespace)
        return _serializar_xml(raiz)


class Nf3eXmlService:
    def to_xml(self, roc: Mapping[str, Any]) -> str:
        namespace = _NS_POR_DOCUMENTO[TipoDocumento.NF3E]
        _exigir(roc is not None, "ROC não pode ser nulo")
        objetos = roc.get("objetos")
        _exigir(objetos, "ROC deve conter ao menos um item")
        trib_total = (roc.get("total") or {}).get("tribCalc")
        _exigir(trib_total is not None, "Total do ROC não informado")

        raiz = _elemento_raiz("infNF3e", namespace)
        ide = _ide_compra_gov(roc)
        if ide:
            _dict_para_elemento(raiz, "ide", ide, namespace)

        nf_det = etree.SubElement(raiz, f"{{{namespace}}}NFdet")
        for objeto in objetos:
            det = etree.SubElement(nf_det, f"{{{namespace}}}det", nItem=str(objeto["nObj"]))
            det_item = etree.SubElement(det, f"{{{namespace}}}detItem")
            _dict_para_elemento(
                det_item,
                "imposto",
                {"IBSCBS": _sem_memoria_calculo(objeto["tribCalc"]["IBSCBS"])},
                namespace,
            )

        total = {"IBSCBSTot": _ibscbs_tot_layout_nf3e_bpe_tm(trib_total["IBSCBSTot"])}
        _dict_para_elemento(raiz, "total", total, namespace)
        return _serializar_xml(raiz)


class XmlService:
    def __init__(self, xml_util: XmlUtil | None = None) -> None:
        self._xml_util = xml_util or XmlUtil()
        self._nfe = NfeXmlService()
        self._nfce = NfceXmlService()
        self._cte = CteXmlService()
        self._cte_simp = CteSimplificadoXmlService()
        self._bpe = BpeXmlService()
        self._bpe_tm = BpeTMXmlService()
        self._nf3e = Nf3eXmlService()

    def validar_xml(self, xml: str, tipo: TipoDocumento, subtipo: TipoXml) -> bool:
        try:
            schema = self._xml_util.get_schema(tipo, subtipo)
            documento = etree.parse(BytesIO(xml.encode("utf-8")))
            schema.assertValid(documento)
            return True
        except etree.DocumentInvalid as erro:
            log = erro.error_log
            if log:
                primeiro = log[0]
                mensagem = (
                    f"Erro na linha {primeiro.line}, coluna {primeiro.column}: {primeiro.message}"
                )
            else:
                mensagem = str(erro)
            raise ErroXmlException(mensagem) from erro
        except etree.XMLSyntaxError as erro:
            raise ErroXmlException(str(erro)) from erro
        except OSError as erro:
            raise ErroXmlException(f"Erro de IO na validação de XML: {erro}") from erro

    def gerar_xml(self, roc: Mapping[str, Any], tipo: TipoDocumento) -> str:
        if tipo == TipoDocumento.NFE:
            return self._nfe.to_xml(roc)
        if tipo == TipoDocumento.NFCE:
            return self._nfce.to_xml(roc)
        if tipo == TipoDocumento.CTE:
            return self._cte.to_xml(roc)
        if tipo == TipoDocumento.CTE_SIMPLIFICADO:
            return self._cte_simp.to_xml(roc)
        if tipo == TipoDocumento.BPE:
            return self._bpe.to_xml(roc)
        if tipo == TipoDocumento.BPE_TM:
            return self._bpe_tm.to_xml(roc)
        if tipo == TipoDocumento.NF3E:
            return self._nf3e.to_xml(roc)
        raise ValueError(f"Tipo de documento não suportado: {tipo}")


def substituir_primeira_ocorrencia(xml: str, inicio: str, fim: str, novo_valor: str) -> str:
    indice_inicio = xml.index(inicio)
    indice_fim = xml.index(fim, indice_inicio)
    return xml[: indice_inicio + len(inicio)] + novo_valor + xml[indice_fim:]


def remover_primeira_tag_completa(xml: str, nome_tag: str) -> str:
    inicio = f"<{nome_tag}"
    fim = f"</{nome_tag}>"
    indice_inicio = xml.index(inicio)
    indice_fim_abertura = xml.index(">", indice_inicio)
    indice_fim = xml.index(fim, indice_fim_abertura)
    return xml[:indice_inicio] + xml[indice_fim + len(fim) :]


def tag_obrigatoria_do_grupo(tipo: TipoDocumento) -> str:
    if tipo in (TipoDocumento.NFE, TipoDocumento.NFCE):
        return "det"
    if tipo == TipoDocumento.NFSE:
        return "IBSCBS"
    if tipo in (TipoDocumento.CTE, TipoDocumento.CTE_SIMPLIFICADO, TipoDocumento.BPE):
        return "imp"
    if tipo == TipoDocumento.BPE_TM:
        return "detBPeTM"
    if tipo == TipoDocumento.NF3E:
        return "NFdet"
    raise ValueError(f"Tipo de documento não suportado: {tipo}")


def gerar_xml_invalido(xml_valido: str, tipo: TipoDocumento, tipo_xml: TipoXml) -> str:
    if tipo_xml == TipoXml.NOTA:
        return substituir_primeira_ocorrencia(xml_valido, "<tpAmb>", "</tpAmb>", "9")
    return remover_primeira_tag_completa(xml_valido, tag_obrigatoria_do_grupo(tipo))


def canonicalizar_xml(xml: str) -> bytes:
    raiz = etree.fromstring(xml.encode("utf-8"))
    return etree.tostring(raiz, method="c14n")