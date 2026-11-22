"""Espelha testes unitários Java de nomenclatura (pin f1eebd7)."""

from __future__ import annotations

from datetime import date
from unittest.mock import MagicMock

import pytest

from calculadora_rtc_regime_regular.nomenclatura import (
    NbsAplicavelService,
    NbsCompletoNaoInformadoException,
    NbsNaoVinculadaException,
    NcmAplicavelService,
    NcmCompletoNaoInformadoException,
    NcmNaoVinculadaException,
    NcmService,
    NcmVigencia,
)

DATA = date(2026, 1, 1)
ID_CLASSIFICACAO = 1
CODIGO = "200003"
TRIBUTOS = "CBS e IBS"


@pytest.fixture
def ncm_aplicavel() -> tuple[MagicMock, NcmAplicavelService]:
    repo = MagicMock()
    return repo, NcmAplicavelService(repo)


@pytest.fixture
def nbs_aplicavel() -> tuple[MagicMock, NbsAplicavelService]:
    repo = MagicMock()
    return repo, NbsAplicavelService(repo)


def test_ncm_sem_anexo_aceita(ncm_aplicavel: tuple[MagicMock, NcmAplicavelService]) -> None:
    repo, servico = ncm_aplicavel
    repo.tem.return_value = False
    servico.validar_ncm_aplicavel(None, ID_CLASSIFICACAO, CODIGO, DATA, TRIBUTOS)
    servico.validar_ncm_aplicavel("24021000", ID_CLASSIFICACAO, CODIGO, DATA, TRIBUTOS)


def test_ncm_com_anexo_exige_completo(ncm_aplicavel: tuple[MagicMock, NcmAplicavelService]) -> None:
    repo, servico = ncm_aplicavel
    repo.tem.return_value = True
    with pytest.raises(NcmCompletoNaoInformadoException):
        servico.validar_ncm_aplicavel(None, ID_CLASSIFICACAO, CODIGO, DATA, TRIBUTOS)
    with pytest.raises(NcmCompletoNaoInformadoException):
        servico.validar_ncm_aplicavel("2402", ID_CLASSIFICACAO, CODIGO, DATA, TRIBUTOS)


def test_ncm_fora_do_anexo_rejeita(ncm_aplicavel: tuple[MagicMock, NcmAplicavelService]) -> None:
    repo, servico = ncm_aplicavel
    repo.tem.return_value = True
    repo.tem_ncm_aplicavel.return_value = False
    repo.tem_excecao_ncm_aplicavel.return_value = False
    with pytest.raises(NcmNaoVinculadaException):
        servico.validar_ncm_aplicavel("24021000", ID_CLASSIFICACAO, CODIGO, DATA, TRIBUTOS)


def test_ncm_vinculo_fora_de_vigencia_com_excecao_rejeita(
    ncm_aplicavel: tuple[MagicMock, NcmAplicavelService],
) -> None:
    repo, servico = ncm_aplicavel
    repo.tem.return_value = True
    repo.tem_ncm_aplicavel.return_value = False
    repo.tem_excecao_ncm_aplicavel.return_value = True
    with pytest.raises(NcmNaoVinculadaException):
        servico.validar_ncm_aplicavel("24021000", ID_CLASSIFICACAO, CODIGO, DATA, TRIBUTOS)


def test_ncm_sem_excecao_cobrindo_aceita(ncm_aplicavel: tuple[MagicMock, NcmAplicavelService]) -> None:
    repo, servico = ncm_aplicavel
    repo.tem.return_value = True
    repo.tem_ncm_aplicavel.return_value = True
    repo.tem_excecao_ncm_aplicavel.return_value = False
    repo.tem_ncm_aplicavel_sem_excecao.return_value = False
    servico.validar_ncm_aplicavel("24021000", ID_CLASSIFICACAO, CODIGO, DATA, TRIBUTOS)


def test_ncm_excepcionado_rejeita(ncm_aplicavel: tuple[MagicMock, NcmAplicavelService]) -> None:
    repo, servico = ncm_aplicavel
    repo.tem.return_value = True
    repo.tem_ncm_aplicavel.return_value = True
    repo.tem_excecao_ncm_aplicavel.return_value = True
    repo.tem_ncm_aplicavel_sem_excecao.return_value = False
    with pytest.raises(NcmNaoVinculadaException):
        servico.validar_ncm_aplicavel("24021000", ID_CLASSIFICACAO, CODIGO, DATA, TRIBUTOS)


def test_ncm_excepcionado_com_vinculo_livre_aceita(ncm_aplicavel: tuple[MagicMock, NcmAplicavelService]) -> None:
    repo, servico = ncm_aplicavel
    repo.tem.return_value = True
    repo.tem_ncm_aplicavel.return_value = True
    repo.tem_excecao_ncm_aplicavel.return_value = True
    repo.tem_ncm_aplicavel_sem_excecao.return_value = True
    servico.validar_ncm_aplicavel("24021000", ID_CLASSIFICACAO, CODIGO, DATA, TRIBUTOS)


def test_nbs_sem_anexo_aceita(nbs_aplicavel: tuple[MagicMock, NbsAplicavelService]) -> None:
    repo, servico = nbs_aplicavel
    repo.tem.return_value = False
    servico.validar_nbs_aplicavel(None, ID_CLASSIFICACAO, CODIGO, DATA, TRIBUTOS)
    servico.validar_nbs_aplicavel("115012000", ID_CLASSIFICACAO, CODIGO, DATA, TRIBUTOS)


def test_nbs_com_anexo_exige_completa(nbs_aplicavel: tuple[MagicMock, NbsAplicavelService]) -> None:
    repo, servico = nbs_aplicavel
    repo.tem.return_value = True
    with pytest.raises(NbsCompletoNaoInformadoException):
        servico.validar_nbs_aplicavel(None, ID_CLASSIFICACAO, CODIGO, DATA, TRIBUTOS)


def test_nbs_tabela_verdade(nbs_aplicavel: tuple[MagicMock, NbsAplicavelService]) -> None:
    repo, servico = nbs_aplicavel
    repo.tem.return_value = True

    repo.tem_nbs_aplicavel.return_value = True
    repo.tem_excecao_nbs_aplicavel.return_value = False
    servico.validar_nbs_aplicavel("115012000", ID_CLASSIFICACAO, CODIGO, DATA, TRIBUTOS)

    repo.tem_excecao_nbs_aplicavel.return_value = True
    repo.tem_nbs_aplicavel_sem_excecao.return_value = False
    with pytest.raises(NbsNaoVinculadaException):
        servico.validar_nbs_aplicavel("115012000", ID_CLASSIFICACAO, CODIGO, DATA, TRIBUTOS)

    repo.tem_nbs_aplicavel.return_value = False
    with pytest.raises(NbsNaoVinculadaException):
        servico.validar_nbs_aplicavel("115012000", ID_CLASSIFICACAO, CODIGO, DATA, TRIBUTOS)


@pytest.fixture
def ncm_service() -> tuple[MagicMock, NcmService]:
    repo = MagicMock()
    return repo, NcmService(repo)


def test_ncm_service_existe_quando_repositorio_true(ncm_service: tuple[MagicMock, NcmService]) -> None:
    repo, servico = ncm_service
    ncm = "23099070"
    repo.existe_ncm.return_value = True
    assert servico.existe_ncm(ncm, DATA) is True
    repo.existe_ncm.assert_called_once_with(ncm, DATA)


def test_ncm_service_existe_quando_repositorio_false(ncm_service: tuple[MagicMock, NcmService]) -> None:
    repo, servico = ncm_service
    ncm = "99999999"
    repo.existe_ncm.return_value = False
    assert servico.existe_ncm(ncm, DATA) is False
    repo.existe_ncm.assert_called_once_with(ncm, DATA)


def test_ncm_service_consultar_vigentes(ncm_service: tuple[MagicMock, NcmService]) -> None:
    repo, servico = ncm_service
    esperado = [
        NcmVigencia("01012100", "ANIMAIS VIVOS"),
        NcmVigencia("01012900", "CAVALOS"),
    ]
    repo.buscar_todos_ncms_vigentes.return_value = esperado
    assert servico.consultar_ncms_vigentes(DATA) == esperado
    repo.buscar_todos_ncms_vigentes.assert_called_once_with(DATA)


def test_ncm_service_lista_vazia(ncm_service: tuple[MagicMock, NcmService]) -> None:
    repo, servico = ncm_service
    repo.buscar_todos_ncms_vigentes.return_value = []
    assert servico.consultar_ncms_vigentes(DATA) == []
    repo.buscar_todos_ncms_vigentes.assert_called_once_with(DATA)


def test_ncm_service_repassa_lista_do_repositorio(ncm_service: tuple[MagicMock, NcmService]) -> None:
    repo, servico = ncm_service
    esperado = [
        NcmVigencia("01012100", "A"),
        NcmVigencia("ABC12100", "B"),
        NcmVigencia("01012", "C"),
        NcmVigencia("0101210X", "D"),
        NcmVigencia("01012900", "E"),
    ]
    repo.buscar_todos_ncms_vigentes.return_value = esperado
    assert servico.consultar_ncms_vigentes(DATA) == esperado
    repo.buscar_todos_ncms_vigentes.assert_called_once_with(DATA)