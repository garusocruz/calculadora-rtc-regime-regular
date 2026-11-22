from datetime import date
from types import SimpleNamespace

from calculadora_rtc_regime_regular.aviso import TipoWarningDadosSimulados, aviso_dados_simulados


def _item(cst: str = "000", seletivo: bool = False) -> SimpleNamespace:
    return SimpleNamespace(cst=cst, imposto_seletivo=object() if seletivo else None)


def test_depois_de_2026_e_calculo_simulado() -> None:
    aviso = aviso_dados_simulados(date(2027, 1, 1), [_item(seletivo=True)])
    assert aviso is TipoWarningDadosSimulados.CASO_CALCULOS_SIMULADOS


def test_cst_ficticio_em_2026() -> None:
    aviso = aviso_dados_simulados(date(2026, 6, 1), [_item("220")])
    assert aviso is TipoWarningDadosSimulados.CASO_ALIQUOTAS_FICTICIAS


def test_2026_sem_cst_ficticio_nao_avisa() -> None:
    assert aviso_dados_simulados(date(2026, 1, 15), [_item("000", seletivo=True)]) is None


def test_antes_de_2026_nao_avisa() -> None:
    assert aviso_dados_simulados(date(2025, 12, 31), [_item("010")]) is None
