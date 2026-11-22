"""Identidade JUnit — ``ItemOperacaoInputTest``."""

from __future__ import annotations

_FQCN = "br.gov.serpro.rtc.api.model.input.ItemOperacaoInputTest"
_MOD = "test_item_operacao_input_java"

_JAVA_AJUSTA_NCM = "ajustaNcm_DeveRespeitarPermiteNcmZero(boolean, String, String)"

JAVA_UNIT_IDENTITY: dict[str, tuple[str, str]] = {
    f"{_MOD}::test_ajustaNcm_DeveRespeitarPermiteNcmZero[permite-zero-curto]": (
        _FQCN,
        f"{_JAVA_AJUSTA_NCM}[1]",
    ),
    f"{_MOD}::test_ajustaNcm_DeveRespeitarPermiteNcmZero[permite-zero-longo]": (
        _FQCN,
        f"{_JAVA_AJUSTA_NCM}[2]",
    ),
    f"{_MOD}::test_ajustaNcm_DeveRespeitarPermiteNcmZero[permite-valido]": (
        _FQCN,
        f"{_JAVA_AJUSTA_NCM}[3]",
    ),
    f"{_MOD}::test_ajustaNcm_DeveRespeitarPermiteNcmZero[nao-permite-zero-curto]": (
        _FQCN,
        f"{_JAVA_AJUSTA_NCM}[4]",
    ),
    f"{_MOD}::test_ajustaNcm_DeveRespeitarPermiteNcmZero[nao-permite-zero-longo]": (
        _FQCN,
        f"{_JAVA_AJUSTA_NCM}[5]",
    ),
    f"{_MOD}::test_ajustaNcm_DeveRespeitarPermiteNcmZero[nao-permite-valido]": (
        _FQCN,
        f"{_JAVA_AJUSTA_NCM}[6]",
    ),
    f"{_MOD}::test_ajustaNcm_DeveRespeitarPermiteNcmZero[permite-null]": (
        _FQCN,
        f"{_JAVA_AJUSTA_NCM}[7]",
    ),
    f"{_MOD}::test_ajustaNcm_DeveRespeitarPermiteNcmZero[nao-permite-null]": (
        _FQCN,
        f"{_JAVA_AJUSTA_NCM}[8]",
    ),
    f"{_MOD}::test_naoDeveLimparNcmQuandoTipoDfeEhNull": (
        _FQCN,
        "naoDeveLimparNcmQuandoTipoDfeEhNull",
    ),
}