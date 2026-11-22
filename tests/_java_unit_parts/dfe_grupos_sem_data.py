"""Identidade JUnit: consulta de DFe sem data usa a data de hoje."""

from __future__ import annotations

_FQCN = "br.gov.serpro.rtc.testesintegracao.dadosabertos.Teste_dadosabertos_14_tiposDfeAgrupados"
_MOD = "test_dfe_grupos_sem_data_java"

JAVA_UNIT_IDENTITY: dict[str, tuple[str, str]] = {
    f"{_MOD}::test_dfeGrupos_semData_usaDataAtual": (
        _FQCN,
        "teste_dfeGrupos_semData_usaDataAtual",
    ),
}
