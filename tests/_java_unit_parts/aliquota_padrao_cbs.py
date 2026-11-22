"""Identidade JUnit: CalculoCbsIbsService.buscarAliquotaPadrao (14 casos)."""

from __future__ import annotations

_FQCN = (
    "br.gov.serpro.rtc.domain.service.calculotributo."
    "Teste_CalculoCbsIbsService_BuscarAliquotaPadrao"
)
_MOD = "test_aliquota_padrao_cbs_java"

JAVA_UNIT_IDENTITY: dict[str, tuple[str, str]] = {
    f"{_MOD}::teste_BuscarAliquotaPadrao_SemValorPadrao": (_FQCN, "teste_BuscarAliquotaPadrao_SemValorPadrao"),
    f"{_MOD}::teste_BuscarAliquotaPadrao_ComAcrescimo": (_FQCN, "teste_BuscarAliquotaPadrao_ComAcrescimo"),
    f"{_MOD}::teste_BuscarAliquotaPadrao_ComDecrescimo": (_FQCN, "teste_BuscarAliquotaPadrao_ComDecrescimo"),
    f"{_MOD}::teste_BuscarAliquotaPadrao_ComSubstituicao": (_FQCN, "teste_BuscarAliquotaPadrao_ComSubstituicao"),
    f"{_MOD}::teste_BuscarAliquotaPadrao_ValorZero": (_FQCN, "teste_BuscarAliquotaPadrao_ValorZero"),
    f"{_MOD}::teste_BuscarAliquotaPadrao_PrecisaoDecimal": (_FQCN, "teste_BuscarAliquotaPadrao_PrecisaoDecimal"),
    f"{_MOD}::teste_BuscarAliquotaPadrao_TributoIBS": (_FQCN, "teste_BuscarAliquotaPadrao_TributoIBS"),
    f"{_MOD}::teste_BuscarAliquotaPadrao_UFDiferente": (_FQCN, "teste_BuscarAliquotaPadrao_UFDiferente"),
    f"{_MOD}::teste_BuscarAliquotaPadrao_DataDiferente": (_FQCN, "teste_BuscarAliquotaPadrao_DataDiferente"),
    f"{_MOD}::teste_BuscarAliquotaPadrao_SubstituicaoPorZero": (_FQCN, "teste_BuscarAliquotaPadrao_SubstituicaoPorZero"),
    f"{_MOD}::teste_BuscarAliquotaPadrao_AcrescimoComPrecisao": (_FQCN, "teste_BuscarAliquotaPadrao_AcrescimoComPrecisao"),
    f"{_MOD}::teste_BuscarAliquotaPadrao_DecrescimoComPrecisao": (_FQCN, "teste_BuscarAliquotaPadrao_DecrescimoComPrecisao"),
    f"{_MOD}::teste_BuscarAliquotaPadrao_VerificaDivisaoPor100": (_FQCN, "teste_BuscarAliquotaPadrao_VerificaDivisaoPor100"),
    f"{_MOD}::teste_BuscarAliquotaPadrao_VerificaChamadaAoService": (
        _FQCN,
        "teste_BuscarAliquotaPadrao_VerificaChamadaAoService",
    ),
}