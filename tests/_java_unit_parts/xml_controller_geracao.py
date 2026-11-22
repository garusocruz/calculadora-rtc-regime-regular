"""Identidade JUnit: XmlControllerGeracaoTest (surefire)."""

from __future__ import annotations

_FQCN = "br.gov.serpro.rtc.testesintegracao.xml.XmlControllerGeracaoTest"
_MOD = "test_xml_controller_geracao_java"

JAVA_UNIT_IDENTITY: dict[str, tuple[str, str]] = {
    **{
        f"{_MOD}::test_deveGerarXmlViaEndpoint[deveGerarXmlViaEndpoint(TipoDocumento)[{i}]]": (
            _FQCN,
            f"deveGerarXmlViaEndpoint(TipoDocumento)[{i}]",
        )
        for i in range(1, 8)
    },
}