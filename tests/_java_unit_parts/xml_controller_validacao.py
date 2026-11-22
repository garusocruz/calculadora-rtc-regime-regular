"""Identidade JUnit: XmlControllerValidacaoTest (surefire)."""

from __future__ import annotations

_FQCN = "br.gov.serpro.rtc.testesintegracao.xml.XmlControllerValidacaoTest"
_MOD = "test_xml_controller_validacao_java"

JAVA_UNIT_IDENTITY: dict[str, tuple[str, str]] = {
    **{
        f"{_MOD}::test_deveValidarXmlViaEndpoint[deveValidarXmlViaEndpoint(String, TipoDocumento, TipoXml)[{i}]]": (
            _FQCN,
            f"deveValidarXmlViaEndpoint(String, TipoDocumento, TipoXml)[{i}]",
        )
        for i in range(1, 8)
    },
}