"""Paridade — VersaoOfflineOutputTest e Teste_VersaoOfflineService."""

from __future__ import annotations

import json
import logging
import re
import socket
import threading
import time
from contextlib import contextmanager
from dataclasses import dataclass
from datetime import date, timedelta
from http.server import BaseHTTPRequestHandler, HTTPServer
from typing import Iterator
from unittest.mock import Mock

import pytest

from calculadora_rtc_regime_regular.consultas import VersaoBaseDados
from calculadora_rtc_regime_regular.versao_offline import (
    RestClientException,
    VersaoOfflineOutput,
    VersaoOfflineService,
    VersaoOutput,
)

_CORPO_REMOTO = (
    '{"ambiente":"apr","dataVersaoDb":"2026-11-09","descricaoVersaoApp":"1.7.0-753903df",'
    '"descricaoVersaoDb":"Nova tabela de Classificações Tributárias (IT 2025.002 v.1.71), '
    'publicada em 30/10/2026.",'
    '"versaoApp":"1.7.0-753903df","versaoDb":"V0073"}'
)

_VERSOES_SUFIXO = (
    "1.2.3-SNAPSHOT",
    "1.2.3-prerelease+meta",
    "1.2.3+meta",
    "1.2.3+meta-valid",
    "1.2.3-beta",
    "1.2.3-SNAPSHOT-123",
    "1.2.3----RC-SNAPSHOT.12.9.1--.12+788",
    "1.2.3----R-S.12.9.1--.12+meta",
    "1.2.3----RC-SNAPSHOT.12.9.1--.12",
)

_VERSOES_SIMPLES = ("0.0.4", "1.2.3", "10.20.30", "1.0.0", "2.0.0", "1.1.7")

_VERSOES_COMPLEXAS = (
    "1.0.0-alpha",
    "1.0.0-beta",
    "1.0.0-alpha.beta",
    "1.0.0-alpha.beta.1",
    "1.0.0-alpha.1",
    "1.0.0-alpha0.valid",
    "1.0.0-alpha.0valid",
    "1.0.0-alpha-a.b-c-somethinglong+build.1-aef.1-its-okay",
    "1.0.0-rc.1+build.1",
    "2.0.0-rc.1+build.123",
    "10.2.3-DEV-SNAPSHOT",
    "2.0.0+build.1848",
    "2.0.1-alpha.1227",
    "1.0.0-alpha+beta",
    "1.0.0+0.build.1-rc.10000aaa-kk-0.1",
    "1.0.0-0A.is.legal",
    "1.1.2-prerelease+meta",
    "1.1.2+meta",
    "1.1.2+meta-valid",
)

_VERSOES_ZEROS = ("01.1.1", "1.01.1", "1.1.01")

_VERSOES_INVALIDAS = (
    "1",
    "1.2",
    "alpha",
    "alpha.beta",
    "alpha.beta.1",
    "alpha.1",
    "alpha+beta",
    "alpha_beta",
    "alpha.",
    "alpha..",
    "beta",
    "+invalid",
    "-invalid",
    "-invalid+invalid",
    "-invalid.01",
    "1.2-SNAPSHOT",
    "1.2-RC-SNAPSHOT",
    "-1.0.3-gamma+b7718",
    "+justmeta",
    "-alpha.",
)


def _versao(app: str | None, db: str, data_db: str) -> VersaoOutput:
    return VersaoOutput(versao_app=app, versao_db=db, data_versao_db=data_db)


def _prefixo_esperado(versao_completa: str) -> str:
    prefixo = re.split(r"[-+]", versao_completa, maxsplit=1)[0]
    if re.fullmatch(r"\d+\.\d+\.\d+", prefixo):
        return prefixo
    match = re.match(r"^(\d+\.\d+\.\d+)", versao_completa)
    return match.group(1) if match else prefixo


# --- VersaoOfflineOutputTest ---


def test_deveRetornarTudoAtualizadoQuandoVersoesIguais() -> None:
    local = _versao("1.2.3", "1.0.0", "2026-01-01")
    remota = _versao("1.2.3", "1.0.0", "2026-01-01")
    output = VersaoOfflineOutput(local, remota)
    assert output.aplicacao_atualizada
    assert output.db_atualizada
    assert output.data_db_atualizada


def test_deveRetornarDesatualizadoQuandoVersoesDiferentes() -> None:
    local = _versao("1.0.0", "1.0.0", "2026-01-01")
    remota = _versao("2.0.0", "2.0.0", "2026-06-01")
    output = VersaoOfflineOutput(local, remota)
    assert not output.aplicacao_atualizada
    assert not output.db_atualizada
    assert not output.data_db_atualizada


def test_deveRetornarTudoDesatualizadoQuandoRemotaNula() -> None:
    local = _versao("1.0.0", "1.0.0", "2026-01-01")
    output = VersaoOfflineOutput(local, None)
    assert not output.aplicacao_atualizada
    assert not output.db_atualizada
    assert not output.data_db_atualizada
    assert output.versao_aplicacao_remota is None
    assert output.versao_db_remota is None
    assert output.data_db_remota is None


def test_deveRetornarNaoAtualizadaQuandoVersaoAppLocalNull() -> None:
    local = _versao(None, "1.0.0", "2026-01-01")
    remota = _versao("1.0.0", "1.0.0", "2026-01-01")
    output = VersaoOfflineOutput(local, remota)
    assert not output.aplicacao_atualizada


def test_naoDeveGerarFalsePositiveQuandoSemverNullEmAmbosLados() -> None:
    local = _versao("abc", "1.0.0", "2026-01-01")
    remota = _versao("xyz", "1.0.0", "2026-01-01")
    output = VersaoOfflineOutput(local, remota)
    assert not output.aplicacao_atualizada


@pytest.mark.parametrize(
    "versao_com_sufixo",
    _VERSOES_SUFIXO,
    ids=[str(i) for i in range(1, len(_VERSOES_SUFIXO) + 1)],
)
def test_deveExtrairPrefixoIgnorandoSufixo(versao_com_sufixo: str) -> None:
    local = _versao(versao_com_sufixo, "1.0.0", "2026-01-01")
    remota = _versao("1.2.3", "1.0.0", "2026-01-01")
    output = VersaoOfflineOutput(local, remota)
    assert output.aplicacao_atualizada


@pytest.mark.parametrize(
    "versao",
    _VERSOES_SIMPLES,
    ids=[str(i) for i in range(1, len(_VERSOES_SIMPLES) + 1)],
)
def test_deveReconhecerVersoesValidasSimples(versao: str) -> None:
    local = _versao(versao, "1.0.0", "2026-01-01")
    remota = _versao(versao, "1.0.0", "2026-01-01")
    output = VersaoOfflineOutput(local, remota)
    assert output.aplicacao_atualizada


@pytest.mark.parametrize(
    "versao_completa",
    _VERSOES_COMPLEXAS,
    ids=[str(i) for i in range(1, len(_VERSOES_COMPLEXAS) + 1)],
)
def test_deveReconhecerVersoesValidasComplexas(versao_completa: str) -> None:
    prefixo = _prefixo_esperado(versao_completa)
    local = _versao(versao_completa, "1.0.0", "2026-01-01")
    remota = _versao(prefixo, "1.0.0", "2026-01-01")
    output = VersaoOfflineOutput(local, remota)
    assert output.aplicacao_atualizada


def test_deveReconhecerNumerosGrandes() -> None:
    grande = "99999999999999999999999.999999999999999999.99999999999999999"
    local = _versao(grande, "1.0.0", "2026-01-01")
    remota = _versao(grande, "1.0.0", "2026-01-01")
    output = VersaoOfflineOutput(local, remota)
    assert output.aplicacao_atualizada


@pytest.mark.parametrize(
    "versao_invalida",
    _VERSOES_ZEROS,
    ids=[str(i) for i in range(1, len(_VERSOES_ZEROS) + 1)],
)
def test_deveRejeitarZerosAEsquerda(versao_invalida: str) -> None:
    local = _versao(versao_invalida, "1.0.0", "2026-01-01")
    remota = _versao("1.2.3", "1.0.0", "2026-01-01")
    output = VersaoOfflineOutput(local, remota)
    assert not output.aplicacao_atualizada


@pytest.mark.parametrize(
    "versao_invalida",
    _VERSOES_INVALIDAS,
    ids=[str(i) for i in range(1, len(_VERSOES_INVALIDAS) + 1)],
)
def test_deveRejeitarStringsSemFormatoSemver(versao_invalida: str) -> None:
    local = _versao(versao_invalida, "1.0.0", "2026-01-01")
    remota = _versao("1.0.0", "1.0.0", "2026-01-01")
    output = VersaoOfflineOutput(local, remota)
    assert not output.aplicacao_atualizada


# --- Teste_VersaoOfflineService ---


@dataclass
class _HttpConfig:
    status: int = 200
    body: bytes = b""
    content_type: str = "application/json"
    stall: bool = False


class _StubHandler(BaseHTTPRequestHandler):
    config = _HttpConfig()

    def log_message(self, _format: str, *_args: object) -> None:
        return

    def do_GET(self) -> None:
        if self.config.stall:
            return
        self.send_response(self.config.status)
        self.send_header("Content-Type", self.config.content_type)
        self.send_header("Content-Length", str(len(self.config.body)))
        self.end_headers()
        if self.config.body:
            self.wfile.write(self.config.body)


class _MuteAcceptServer:
    def __init__(self) -> None:
        self._sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self._sock.bind(("127.0.0.1", 0))
        self._sock.listen(1)
        self.port = self._sock.getsockname()[1]
        self._stop = threading.Event()
        self._thread = threading.Thread(target=self._loop, daemon=True)
        self._thread.start()

    def _loop(self) -> None:
        self._sock.settimeout(0.5)
        while not self._stop.is_set():
            try:
                conn, _ = self._sock.accept()
                conn.settimeout(120)
            except TimeoutError:
                continue

    def close(self) -> None:
        self._stop.set()
        self._sock.close()


@contextmanager
def _http_stub(config: _HttpConfig) -> Iterator[str]:
    _StubHandler.config = config
    server = HTTPServer(("127.0.0.1", 0), _StubHandler)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    host, port = server.server_address
    url = f"http://{host}:{port}/versao"
    try:
        yield url
    finally:
        server.shutdown()
        server.server_close()


def _closed_port() -> int:
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    sock.bind(("127.0.0.1", 0))
    port = sock.getsockname()[1]
    sock.close()
    return port


@pytest.fixture
def versao_base_mock() -> Mock:
    mock = Mock()
    versao = VersaoBaseDados(
        id=1,
        data=date(2026, 11, 9),
        descricao="",
        numero_versao="V0073",
    )
    mock.get_ultima_versao.return_value = versao
    return mock


def _novo_servico(
    versao_base_mock: Mock,
    url: str,
    connect: timedelta,
    read: timedelta,
) -> VersaoOfflineService:
    return VersaoOfflineService(
        versao_base_mock,
        connect,
        read,
        url_versao_remota=url,
        versao_aplicacao_local="1.7.2-c7512f9a",
    )


def _assert_sem_versao_remota(status: VersaoOfflineOutput) -> None:
    assert status.versao_aplicacao_remota is None
    assert status.versao_db_remota is None
    assert status.data_db_remota is None
    assert not status.aplicacao_atualizada
    assert not status.db_atualizada
    assert not status.data_db_atualizada
    assert status.versao_aplicacao_local == "1.7.2-c7512f9a"
    assert status.versao_db_local == "V0073"
    assert status.data_db_local == "2026-11-09"


def test_leAVersaoPublicadaPelaInstalacaoOnlineECompara(versao_base_mock: Mock) -> None:
    with _http_stub(_HttpConfig(body=_CORPO_REMOTO.encode())) as url:
        servico = _novo_servico(
            versao_base_mock, url, timedelta(seconds=5), timedelta(seconds=10)
        )
        status = servico.verificar_versao()
    assert status.versao_aplicacao_remota == "1.7.0-753903df"
    assert status.versao_db_remota == "V0073"
    assert status.data_db_remota == "2026-11-09"
    assert status.versao_aplicacao_local == "1.7.2-c7512f9a"
    assert status.versao_db_local == "V0073"
    assert status.data_db_local == "2026-11-09"
    assert not status.aplicacao_atualizada
    assert status.db_atualizada
    assert status.data_db_atualizada


def test_campoDesconhecidoNaRespostaRemotaNaoImpedeALeitura(versao_base_mock: Mock) -> None:
    corpo = json.dumps(
        {
            "versaoApp": "1.8.0-abcdef12",
            "versaoDb": "V0074",
            "dataVersaoDb": "2026-12-01",
            "arquivoDb": "calculadora-pro.db",
            "campoFuturo": {"a": 1},
        }
    )
    with _http_stub(_HttpConfig(body=corpo.encode())) as url:
        servico = _novo_servico(
            versao_base_mock, url, timedelta(seconds=5), timedelta(seconds=10)
        )
        status = servico.verificar_versao()
    assert status.versao_aplicacao_remota == "1.8.0-abcdef12"
    assert status.versao_db_remota == "V0074"
    assert status.data_db_remota == "2026-12-01"
    assert not status.aplicacao_atualizada
    assert not status.db_atualizada
    assert not status.data_db_atualizada


_FALHAS_REMOTA = (
    pytest.param(
        "conexao_recusada",
        None,
        id="1",
    ),
    pytest.param(
        "timeout",
        _HttpConfig(stall=True),
        id="2",
    ),
    pytest.param(
        "erro_500",
        _HttpConfig(status=500, body=b"", content_type="text/plain"),
        id="3",
    ),
    pytest.param(
        "erro_404",
        _HttpConfig(status=404, body=b"", content_type="text/plain"),
        id="4",
    ),
    pytest.param(
        "html",
        _HttpConfig(
            body="<html><body>Portal de acesso à rede</body></html>".encode(),
            content_type="text/html",
        ),
        id="5",
    ),
    pytest.param(
        "json_incompleto",
        _HttpConfig(body=b'{"versaoApp":'),
        id="6",
    ),
    pytest.param(
        "json_array",
        _HttpConfig(body=b"[1,2,3]"),
        id="7",
    ),
)


@pytest.mark.parametrize("modo,config", _FALHAS_REMOTA)
def test_falhaDaConsultaRemotaDevolveComparacaoSemVersaoRemota(
    versao_base_mock: Mock,
    caplog: pytest.LogCaptureFixture,
    modo: str,
    config: _HttpConfig | None,
) -> None:
    caplog.set_level(logging.WARNING, logger="calculadora_rtc_regime_regular.versao_offline")
    if modo == "conexao_recusada":
        url = f"http://127.0.0.1:{_closed_port()}/versao"
        servico = _novo_servico(
            versao_base_mock, url, timedelta(seconds=2), timedelta(seconds=2)
        )
        status = servico.verificar_versao()
    elif modo == "timeout":
        with _http_stub(config) as url:
            servico = _novo_servico(
                versao_base_mock, url, timedelta(seconds=2), timedelta(seconds=1)
            )
            status = servico.verificar_versao()
    else:
        with _http_stub(config) as url:
            servico = _novo_servico(
                versao_base_mock, url, timedelta(seconds=5), timedelta(seconds=10)
            )
            status = servico.verificar_versao()
    _assert_sem_versao_remota(status)
    avisos = [r for r in caplog.records if r.levelno == logging.WARNING]
    assert len(avisos) == 1
    assert url in avisos[0].getMessage()


def test_naSubidaAFalhaDaConsultaRemotaAcionaNovaTentativa(
    versao_base_mock: Mock,
    caplog: pytest.LogCaptureFixture,
) -> None:
    caplog.set_level(logging.DEBUG, logger="calculadora_rtc_regime_regular.versao_offline")
    with _http_stub(_HttpConfig(status=500, body=b"", content_type="text/plain")) as url:
        servico = _novo_servico(
            versao_base_mock, url, timedelta(seconds=5), timedelta(seconds=10)
        )
        with pytest.raises(RestClientException):
            servico.verificar_versao_na_inicializacao()
    assert caplog.records == []


def test_naSubidaAComparacaoERegistradaQuandoAConsultaResponde(
    versao_base_mock: Mock,
    caplog: pytest.LogCaptureFixture,
) -> None:
    caplog.set_level(logging.INFO, logger="calculadora_rtc_regime_regular.versao_offline")
    with _http_stub(_HttpConfig(body=_CORPO_REMOTO.encode())) as url:
        servico = _novo_servico(
            versao_base_mock, url, timedelta(seconds=5), timedelta(seconds=10)
        )
        servico.verificar_versao_na_inicializacao()
    mensagens = [r.getMessage() for r in caplog.records]
    assert "Aplicação (LOCAL):  1.7.2-c7512f9a" in mensagens
    assert "Aplicação (ONLINE): 1.7.0-753903df" in mensagens
    assert "Banco de Dados (LOCAL):  V0073" in mensagens
    assert "Banco de Dados (ONLINE): V0073" in mensagens
    assert not any(r.levelno == logging.WARNING for r in caplog.records)


def test_instalacaoOnlineQueNaoRespondeEsgotaOTempoLimiteDeLeitura(
    versao_base_mock: Mock,
    caplog: pytest.LogCaptureFixture,
) -> None:
    caplog.set_level(logging.WARNING, logger="calculadora_rtc_regime_regular.versao_offline")
    mudo = _MuteAcceptServer()
    try:
        url = f"http://127.0.0.1:{mudo.port}/versao"
        servico = _novo_servico(
            versao_base_mock, url, timedelta(seconds=2), timedelta(milliseconds=300)
        )
        inicio = time.monotonic()
        status = servico.verificar_versao()
        espera = time.monotonic() - inicio
    finally:
        mudo.close()
    _assert_sem_versao_remota(status)
    assert status.versao_aplicacao_remota is None
    assert 0.25 <= espera <= 5.0
    avisos = [r for r in caplog.records if r.levelno == logging.WARNING]
    assert len(avisos) == 1


def test_conexaoRecusadaDevolveComparacaoSemVersaoRemota(
    versao_base_mock: Mock,
    caplog: pytest.LogCaptureFixture,
) -> None:
    caplog.set_level(logging.WARNING, logger="calculadora_rtc_regime_regular.versao_offline")
    url = f"http://127.0.0.1:{_closed_port()}/versao"
    servico = _novo_servico(
        versao_base_mock, url, timedelta(seconds=2), timedelta(seconds=2)
    )
    status = servico.verificar_versao()
    _assert_sem_versao_remota(status)
    avisos = [r for r in caplog.records if r.levelno == logging.WARNING]
    assert len(avisos) == 1