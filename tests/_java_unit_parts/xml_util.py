"""Identidade JUnit Surefire: ``br.gov.serpro.rtc.core.util.XmlUtilTest`` (50 casos)."""

from __future__ import annotations

_FQCN = "br.gov.serpro.rtc.core.util.XmlUtilTest"
_MOD = "test_xml_util_java"

_VALIDAR = "deveValidarDemaisCenariosDeXmlDeExemplo(String, TipoDocumento, TipoXml)"
_RESOLVER = "deveResolverSchemaParaTodasAsCombinacoesDeDocumentoETipoXml(TipoDocumento, TipoXml)"
_REJEITAR = "deveRejeitarCenariosInvalidosDerivadosDosExemplos(String, TipoDocumento, TipoXml)"


def _build_identity() -> dict[str, tuple[str, str]]:
    out: dict[str, tuple[str, str]] = {}
    for i in range(1, 18):
        out[f"{_MOD}::test_deve_validar_demais_cenarios_de_xml_de_exemplo[{i}]"] = (
            _FQCN,
            f"{_VALIDAR}[{i}]",
        )
    for i in range(1, 17):
        out[f"{_MOD}::test_deve_resolver_schema_para_todas_combinacoes[{i}]"] = (
            _FQCN,
            f"{_RESOLVER}[{i}]",
        )
    for i in range(1, 18):
        out[f"{_MOD}::test_deve_rejeitar_cenarios_invalidos_derivados_dos_exemplos[{i}]"] = (
            _FQCN,
            f"{_REJEITAR}[{i}]",
        )
    return out


JAVA_UNIT_IDENTITY = _build_identity()