"""Paridade com ``ItemOperacaoInputTest`` (``ajustarNcm``)."""

from __future__ import annotations

import pytest

from calculadora_rtc_regime_regular.processamento_item import ItemOperacaoInput, TipoDfe

NCM_ZERO_CURTO = "00"
NCM_ZERO_LONGO = "00000000"
NCM_VALIDO = "24021000"


def _tipo_dfe(permite_ncm_zero: bool) -> TipoDfe:
    return TipoDfe(tipo=55, sigla="NFE", permite_ncm_zero=permite_ncm_zero)


@pytest.mark.parametrize(
    ("permite_ncm_zero", "ncm", "ncm_esperado"),
    [
        (True, NCM_ZERO_CURTO, None),
        (True, NCM_ZERO_LONGO, None),
        (True, NCM_VALIDO, NCM_VALIDO),
        (False, NCM_ZERO_CURTO, NCM_ZERO_CURTO),
        (False, NCM_ZERO_LONGO, NCM_ZERO_LONGO),
        (False, NCM_VALIDO, NCM_VALIDO),
        (True, None, None),
        (False, None, None),
    ],
    ids=[
        "permite-zero-curto",
        "permite-zero-longo",
        "permite-valido",
        "nao-permite-zero-curto",
        "nao-permite-zero-longo",
        "nao-permite-valido",
        "permite-null",
        "nao-permite-null",
    ],
)
def test_ajustaNcm_DeveRespeitarPermiteNcmZero(
    permite_ncm_zero: bool, ncm: str | None, ncm_esperado: str | None
) -> None:
    item = ItemOperacaoInput(ncm=ncm)
    item.ajustar_ncm(_tipo_dfe(permite_ncm_zero))
    assert item.ncm == ncm_esperado


def test_naoDeveLimparNcmQuandoTipoDfeEhNull() -> None:
    item = ItemOperacaoInput(ncm=NCM_ZERO_CURTO)
    item.ajustar_ncm(None)
    assert item.ncm == NCM_ZERO_CURTO