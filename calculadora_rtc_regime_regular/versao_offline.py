"""Comparador de versão local vs remota (perfil offline)."""

from __future__ import annotations

import http.client
import json
import logging
import re
import urllib.parse
from dataclasses import dataclass
from datetime import date, timedelta
from decimal import Decimal
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from calculadora_rtc_regime_regular.consultas import VersaoBaseDadosService

logger = logging.getLogger(__name__)

SEMVER_PATTERN = re.compile(r"^(0|[1-9]\d*)\.(0|[1-9]\d*)\.(0|[1-9]\d*)")


class RestClientException(Exception):
    """Equivalente a ``org.springframework.web.client.RestClientException``."""


def _texto_json(valor: object) -> str | None:
    if valor is None:
        return None
    if isinstance(valor, str):
        return valor
    if isinstance(valor, Decimal):
        return format(valor, "f")
    return str(valor)


@dataclass(frozen=True)
class VersaoOutput:
    versao_app: str | None = None
    descricao_versao_app: str | None = None
    versao_db: str | None = None
    descricao_versao_db: str | None = None
    data_versao_db: str | None = None
    ambiente: str | None = None

    @classmethod
    def from_json(cls, payload: object) -> VersaoOutput:
        if not isinstance(payload, dict):
            raise RestClientException(
                "Error while extracting response for type VersaoOutput"
            )
        return cls(
            versao_app=_texto_json(payload.get("versaoApp")),
            descricao_versao_app=_texto_json(payload.get("descricaoVersaoApp")),
            versao_db=_texto_json(payload.get("versaoDb")),
            descricao_versao_db=_texto_json(payload.get("descricaoVersaoDb")),
            data_versao_db=_texto_json(payload.get("dataVersaoDb")),
            ambiente=_texto_json(payload.get("ambiente")),
        )


def _extrair_semver(versao: str | None) -> str | None:
    if versao is None:
        return None
    match = SEMVER_PATTERN.search(versao)
    return match.group() if match else None


class VersaoOfflineOutput:
    def __init__(self, local: VersaoOutput, remota: VersaoOutput | None) -> None:
        self.versao_aplicacao_local = local.versao_app
        self.versao_db_local = local.versao_db
        self.data_db_local = local.data_versao_db

        self.versao_aplicacao_remota = remota.versao_app if remota is not None else None
        self.versao_db_remota = remota.versao_db if remota is not None else None
        self.data_db_remota = remota.data_versao_db if remota is not None else None

        semver_local = _extrair_semver(self.versao_aplicacao_local)
        semver_remota = _extrair_semver(self.versao_aplicacao_remota)
        self.aplicacao_atualizada = semver_local is not None and semver_local == semver_remota
        self.db_atualizada = (
            self.versao_db_local is not None and self.versao_db_local == self.versao_db_remota
        )
        self.data_db_atualizada = (
            self.data_db_local is not None and self.data_db_local == self.data_db_remota
        )


class VersaoOfflineService:
    def __init__(
        self,
        versao_base_dados_service: VersaoBaseDadosService,
        connect_timeout: timedelta = timedelta(seconds=5),
        read_timeout: timedelta = timedelta(seconds=10),
        *,
        url_versao_remota: str = "",
        versao_aplicacao_local: str = "unknown",
    ) -> None:
        self._versao_base_dados_service = versao_base_dados_service
        self._connect_timeout = connect_timeout
        self._read_timeout = read_timeout
        self._url_versao_remota = url_versao_remota
        self._versao_aplicacao_local = versao_aplicacao_local

    def verificar_versao(self) -> VersaoOfflineOutput:
        try:
            remota = self._consultar_versao_remota()
        except RestClientException as exc:
            logger.warning(
                "Consulta da versão remota indisponível em [%s]: %s",
                self._url_versao_remota,
                exc,
            )
            remota = None
        return VersaoOfflineOutput(self._versao_local(), remota)

    def verificar_versao_na_inicializacao(self) -> None:
        status = VersaoOfflineOutput(self._versao_local(), self._consultar_versao_remota())
        self._exibir_status_versao(status)

    def _versao_local(self) -> VersaoOutput:
        ultima = self._versao_base_dados_service.get_ultima_versao()
        return VersaoOutput(
            versao_app=self._versao_aplicacao_local,
            descricao_versao_app=self._versao_aplicacao_local,
            versao_db=ultima.numero_versao,
            data_versao_db=ultima.data.isoformat(),
        )

    def _consultar_versao_remota(self) -> VersaoOutput:
        parsed = urllib.parse.urlparse(self._url_versao_remota)
        if parsed.scheme not in ("http", "https"):
            raise RestClientException(f"unsupported url scheme: {parsed.scheme}")
        host = parsed.hostname or "localhost"
        port = parsed.port or (443 if parsed.scheme == "https" else 80)
        path = parsed.path or "/"
        if parsed.query:
            path = f"{path}?{parsed.query}"
        conn: http.client.HTTPConnection | http.client.HTTPSConnection
        if parsed.scheme == "https":
            conn = http.client.HTTPSConnection(
                host,
                port,
                timeout=self._connect_timeout.total_seconds(),
            )
        else:
            conn = http.client.HTTPConnection(
                host,
                port,
                timeout=self._connect_timeout.total_seconds(),
            )
        try:
            conn.request("GET", path)
            if conn.sock is not None:
                conn.sock.settimeout(self._read_timeout.total_seconds())
            resp = conn.getresponse()
            raw = resp.read()
            content_type = resp.getheader("Content-Type", "")
            if resp.status >= 400:
                body = raw.decode(errors="replace") if raw else ""
                detail = body if body else "[no body]"
                raise RestClientException(
                    f"{resp.status} {resp.reason} on GET request for "
                    f'"{self._url_versao_remota}": {detail}'
                )
            if content_type and "json" not in content_type.lower():
                raise RestClientException(
                    "Could not extract response: no suitable HttpMessageConverter "
                    "found for response type VersaoOutput "
                    f"and content type [{content_type.split(';')[0]}]"
                )
            try:
                payload = json.loads(raw.decode(), parse_float=Decimal)
            except json.JSONDecodeError as err:
                raise RestClientException(
                    "Error while extracting response for type VersaoOutput "
                    "and content type [application/json]"
                ) from err
            return VersaoOutput.from_json(payload)
        except TimeoutError as err:
            raise RestClientException(
                f'I/O error on GET request for "{self._url_versao_remota}": Read timed out'
            ) from err
        except ConnectionRefusedError as err:
            raise RestClientException(
                f'I/O error on GET request for "{self._url_versao_remota}": '
                "Connection refused (connect failed)"
            ) from err
        except OSError as err:
            raise RestClientException(
                f'I/O error on GET request for "{self._url_versao_remota}": {err}'
            ) from err
        finally:
            conn.close()

    def _exibir_status_versao(self, status: VersaoOfflineOutput) -> None:
        atualizados: list[str] = []
        desatualizados: list[str] = []

        if status.aplicacao_atualizada:
            atualizados.append(f"Aplicação (LOCAL):  {status.versao_aplicacao_local}")
            atualizados.append(f"Aplicação (ONLINE): {status.versao_aplicacao_remota}")
        else:
            desatualizados.append(f"Aplicação (LOCAL):  {status.versao_aplicacao_local}")
            desatualizados.append(f"Aplicação (ONLINE): {status.versao_aplicacao_remota}")

        if status.db_atualizada:
            atualizados.append(f"Banco de Dados (LOCAL):  {status.versao_db_local}")
            atualizados.append(f"Banco de Dados (ONLINE): {status.versao_db_remota}")
        else:
            desatualizados.append(f"Banco de Dados (LOCAL):  {status.versao_db_local}")
            desatualizados.append(f"Banco de Dados (ONLINE): {status.versao_db_remota}")

        if status.data_db_atualizada:
            atualizados.append(f"Data do Banco (LOCAL):  {status.data_db_local}")
            atualizados.append(f"Data do Banco (ONLINE): {status.data_db_remota}")
        else:
            desatualizados.append(f"Data do Banco (LOCAL):  {status.data_db_local}")
            desatualizados.append(f"Data do Banco (ONLINE): {status.data_db_remota}")

        if atualizados:
            logger.info("= VERSÃO ATUALIZADA " + "=" * 30)
            for linha in atualizados:
                logger.info(linha)
        if desatualizados:
            logger.info("= VERSÃO DESATUALIZADA " + "=" * 27)
            for linha in desatualizados:
                logger.info(linha)