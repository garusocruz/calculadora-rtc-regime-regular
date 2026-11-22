from decimal import Decimal

import pytest

from calculadora_rtc_regime_regular.base_calculo import (
    Componentes,
    DocumentoInvalido,
    Natureza,
    calcular,
    calcular_publicado,
)


def _comp(**valores: str | None) -> Componentes:
    return Componentes(**{nome: None if valor is None else Decimal(valor) for nome, valor in valores.items()})


def test_base_da_nfe_em_2026() -> None:
    resultado = calcular(
        _comp(vProd="1000", vFrete="50", vSeg="20", vDesc="40", vICMS="180"),
        2026,
        Natureza.BEM,
        55,
    )
    assert resultado.base_rg == Decimal("850")


def test_base_da_nfce_ignora_campo_so_da_nfe() -> None:
    resultado = calcular(
        _comp(vProd="1000", vFrete="50", vII="150", vDesc="40", vICMS="180", vICMSUFDest="20"),
        2026,
        Natureza.BEM,
        65,
    )
    assert resultado.base_rg == Decimal("830")


def test_issqn_so_entra_em_servico() -> None:
    componentes = _comp(vProd="1000", vISSQN="20")
    bem = calcular(componentes, 2026, Natureza.BEM, 55).base_rg
    servico = calcular(componentes, 2026, Natureza.SERVICO, 55).base_rg
    assert bem == Decimal("1000")
    assert servico == Decimal("980")


def test_nulos_viram_zero_e_desconto_maior_que_o_produto_fica_negativo() -> None:
    assert calcular(Componentes(), 2026, Natureza.BEM, 55).base_rg == Decimal(0)
    assert calcular(_comp(vProd="100", vDesc="200"), 2026, Natureza.BEM, 55).base_rg == Decimal("-100")


def test_publicacao_arredonda_uma_vez() -> None:
    resultado = calcular_publicado(_comp(vProd="1000", vDesc="40", vICMS="180"), 2026, Natureza.BEM, 55)
    assert resultado.base_rg == Decimal("780.00")


def test_documento_invalido() -> None:
    with pytest.raises(DocumentoInvalido, match="55"):
        calcular_publicado(_comp(vProd="1000"), 2026, Natureza.BEM, 57)
    with pytest.raises(DocumentoInvalido):
        calcular(_comp(vProd="1000"), 2026, Natureza.BEM, None)


def test_aviso_quando_o_campo_nao_compoe() -> None:
    resultado = calcular(_comp(vProd="1000", vISSQN="20"), 2026, Natureza.BEM, 55)
    assert resultado.avisos
    assert "vISSQN" in resultado.avisos[0]


def test_t10_oficial_base_unificada_com_vfrete_com_tres_decimais() -> None:
    """Pedido T10_base_unificada.json — empate em 954,505 arredonda para o par."""
    resultado = calcular_publicado(
        _comp(vProd="1000", vFrete="10.005", vDesc="0", vPIS="9.25", vCOFINS="46.25"),
        2026,
        Natureza.BEM,
        55,
    )
    assert resultado.base_rg == Decimal("954.50")
    assert resultado.base_is == Decimal("954.50")
    assert resultado.base_sn == Decimal("1010.00")


def test_n1_oficial_base_unificada_com_duas_casas() -> None:
    """Pedido N1_base_unificada.json."""
    resultado = calcular_publicado(
        _comp(vProd="1000", vFrete="10", vDesc="0", vPIS="9.25", vCOFINS="46.25"),
        2026,
        Natureza.BEM,
        55,
    )
    assert resultado.base_rg == Decimal("954.50")
    assert resultado.base_is == Decimal("954.50")
    assert resultado.base_sn == Decimal("1010.00")
