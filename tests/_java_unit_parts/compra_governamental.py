"""Identidade JUnit para TributacaoCompraGovernamentalDomainTest (surefire)."""

from __future__ import annotations

_FQCN = "br.gov.serpro.rtc.api.model.roc.TributacaoCompraGovernamentalDomainTest"
_MOD = "test_compra_governamental_java"
_PARAM_TYPES = (
    "(int, BigDecimal, BigDecimal, BigDecimal, BigDecimal, BigDecimal, BigDecimal, BigDecimal)"
)

_PARAM_METHODS = (
    "deveConcentrarTudoNaCbsQuandoUniaoCompraAPartirDe2027",
    "deveTransferirParaUfQuandoEstadoCompraAPartirDe2027",
    "deveTransferirParaMunicipioQuandoMunicipioCompraAPartirDe2027",
    "deveTransferirParaMunicipioQuandoDistritoFederalCompraAPartirDe2027",
    "deveTransferirParaMunicipioQuandoConsorcioPublicoCompraAPartirDe2027",
    "deveTransferirParaMunicipioQuandoComiteGestorIbsCompraAPartirDe2027",
)

_STANDALONE: tuple[tuple[str, str], ...] = (
    ("compraDaUniao_valorPelaAliquotaPublicada_naoPelaSomaDoDetalhe", "compraDaUniao_valorPelaAliquotaPublicada_naoPelaSomaDoDetalhe"),
    ("transferenciaDaCbs_quemCedeArredonda_quemRecebeFechaPelaDiferenca", "transferenciaDaCbs_quemCedeArredonda_quemRecebeFechaPelaDiferenca"),
    ("transferenciaDaCbs_estadoRecebeTambemOIbsDoMunicipio", "transferenciaDaCbs_estadoRecebeTambemOIbsDoMunicipio"),
    ("deveRetornarNuloQuandoTipoEnteForNulo", "deveRetornarNuloQuandoTipoEnteForNulo"),
    ("deveLancarExcecaoQuandoDataFatoGeradorForNula", "deveLancarExcecaoQuandoDataFatoGeradorForNula"),
    ("deveLancarExcecaoQuandoPercentualTransferenciaForNulo", "deveLancarExcecaoQuandoPercentualTransferenciaForNulo"),
    ("deveRetornarMesmaInstanciaAntesDe2027", "deveRetornarMesmaInstanciaAntesDe2027"),
)


def _build_identity() -> dict[str, tuple[str, str]]:
    out: dict[str, tuple[str, str]] = {}
    for py_name, java_name in _STANDALONE:
        out[f"{_MOD}::test_{py_name}"] = (_FQCN, java_name)
    for method in _PARAM_METHODS:
        for i in range(1, 8):
            out[f"{_MOD}::test_{method}[{i}]"] = (
                _FQCN,
                f"{method}{_PARAM_TYPES}[{i}]",
            )
    return out


JAVA_UNIT_IDENTITY = _build_identity()