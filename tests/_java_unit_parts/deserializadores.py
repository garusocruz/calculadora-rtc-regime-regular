"""Identidade JUnit — deserializadores customizados (config.serializer)."""

from __future__ import annotations

_MOD = "test_deserializadores_java"

_FQCN_OFFSET = "br.gov.serpro.rtc.config.serializer.OffsetDateTimeCustomDeserializerTest"
_FQCN_OFFSET_API = (
    "br.gov.serpro.rtc.config.serializer.OffsetDateTimeCustomDeserializerApiIntegrationTest"
)
_FQCN_OFFSET_JACKSON = (
    "br.gov.serpro.rtc.config.serializer.OffsetDateTimeCustomDeserializerJacksonConfigTest"
)
_FQCN_LOCAL_DATE = "br.gov.serpro.rtc.config.serializer.LocalDateCustomDeserializerTest"
_FQCN_TDEC = "br.gov.serpro.rtc.config.serializer.BigDecimalTDec1104OpRTCSerializerTest"

JAVA_UNIT_IDENTITY: dict[str, tuple[str, str]] = {}

for i in range(1, 3):
    JAVA_UNIT_IDENTITY[f"{_MOD}::test_shouldDeserializeValidOffsetDateTime[{i}]"] = (
        _FQCN_OFFSET,
        f"shouldDeserializeValidOffsetDateTime(String)[{i}]",
    )
for i in range(1, 14):
    JAVA_UNIT_IDENTITY[f"{_MOD}::test_shouldThrowExceptionForInvalidOffsetDateTime[{i}]"] = (
        _FQCN_OFFSET,
        f"shouldThrowExceptionForInvalidOffsetDateTime(String)[{i}]",
    )

for i in range(1, 3):
    JAVA_UNIT_IDENTITY[
        f"{_MOD}::test_shouldUseApplicationJacksonDeserializerForValidDateTime[{i}]"
    ] = (
        _FQCN_OFFSET_API,
        f"shouldUseApplicationJacksonDeserializerForValidDateTime(String)[{i}]",
    )
for i in range(1, 14):
    JAVA_UNIT_IDENTITY[f"{_MOD}::test_shouldRejectInvalidDateTimeByCustomRule[{i}]"] = (
        _FQCN_OFFSET_API,
        f"shouldRejectInvalidDateTimeByCustomRule(String)[{i}]",
    )

for i in range(1, 3):
    JAVA_UNIT_IDENTITY[f"{_MOD}::test_shouldDeserializeValidOffsetDateTimeJackson[{i}]"] = (
        _FQCN_OFFSET_JACKSON,
        f"shouldDeserializeValidOffsetDateTime(String)[{i}]",
    )
for i in range(1, 14):
    JAVA_UNIT_IDENTITY[
        f"{_MOD}::test_shouldRejectInvalidOffsetDateTimeWithCustomMessage[{i}]"
    ] = (
        _FQCN_OFFSET_JACKSON,
        f"shouldRejectInvalidOffsetDateTimeWithCustomMessage(String)[{i}]",
    )

JAVA_UNIT_IDENTITY[f"{_MOD}::test_shouldDeserializeValidDate"] = (
    _FQCN_LOCAL_DATE,
    "shouldDeserializeValidDate",
)
for i in range(1, 11):
    JAVA_UNIT_IDENTITY[f"{_MOD}::test_shouldThrowExceptionForInvalidDate[{i}]"] = (
        _FQCN_LOCAL_DATE,
        f"shouldThrowExceptionForInvalidDate(String)[{i}]",
    )

for i in range(1, 10):
    JAVA_UNIT_IDENTITY[f"{_MOD}::test_deveSerializarQuantidadeConformePadrao[{i}]"] = (
        _FQCN_TDEC,
        f"deveSerializarQuantidadeConformePadrao(String, String)[{i}]",
    )