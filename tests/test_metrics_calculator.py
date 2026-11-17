"""
Pruebas unitarias para el Motor de Métricas (app/metrics/calculator.py).
"""

from unittest.mock import patch, MagicMock
from typing import Dict, List
import pandas as pd
import pytest

from app.metrics.calculator import _obtener_ultimo_dato, calcular_pilar_rentabilidad

def test_obtener_ultimo_dato_exito():
    """
    Verifica que la función _obtener_ultimo_dato devuelve correctamente el valor del período fiscal más reciente cuando se encuentra la métrica contable.
    """
    df_prueba: pd.DataFrame = pd.DataFrame(
        {
            "Total Revenue": [1000.0, 950.0, 900.0],
            "Net Income": [150.0, 120.0, 100.0]
        },
        index=["2023-12-31", "2022-12-31", "2021-12-31"]
    )

    nombres_columnas_posibles: list[str] = ["Total Revenue", "Revenue", "Sales"]

    nombres_columnas_no_posibles: list[str] = ["Revenue", "Sales"]

    # Caso de éxito: la métrica contable se encuentra en el DataFrame
    ultimo_dato_exito: float = _obtener_ultimo_dato(df_prueba,nombres_columnas_posibles)
    assert ultimo_dato_exito == 1000.0

    # Caso de fallo: la métrica contable no se encuentra en el DataFrame
    ultimo_dato_fallo: float = _obtener_ultimo_dato(df_prueba,nombres_columnas_no_posibles)
    assert ultimo_dato_fallo == 0.0

def test_calcular_pilar_rentabilidad_exito():
    """
    Verifica el cálculo exacto de ROE, Margen Operativo y Margen Neto con datos contables positivos y conocidos.
    """

    df_income: pd.DataFrame = pd.DataFrame(
        {
            "Total Revenue": [1000.0, 950.0, 900.0],
            "Operating Income": [300.0, 285.0, 270.0],
            "Net Income": [250.0, 200.1, 100.7]
        },
        index=["2023-12-31","2022-12-31","2021-12-31"]
    )

    df_balance: pd.DataFrame = pd.DataFrame(
        {
            "Stockholders Equity": [500.0, 450.0, 400.0],
        },
        index=["2023-12-31","2022-12-31","2021-12-31"]
    )

    df_cashflow: pd.DataFrame = pd.DataFrame(
        {
            "Operating Cash Flow": [200.0, 180.0, 160.0],
        },
        index=["2023-12-31","2022-12-31","2021-12-31"]
    )

    estados_simulados: Dict[str, pd.DataFrame] = {
        "income_statement": df_income,
        "balance_sheet": df_balance,
        "cash_flow": df_cashflow
    }

    resultados: Dict[str, float] = calcular_pilar_rentabilidad(estados_simulados)

    # Verificación de los resultados esperados
    assert resultados["roe"] == pytest.approx(0.5)
    assert resultados["margen_operativo"] == pytest.approx(0.3)
    assert resultados["margen_neto"] == pytest.approx(0.25)

def test_calcular_pilar_rentabilidad_division_por_cero():
    """"
    Verifica que el sistema no falle por división por cero ni genere ROE falsamente positivo cuando el patrimonio neto es negativo.
    """
    df_income: pd.DataFrame = pd.DataFrame(
        {
            "Net Income": [100.0],
        },
        index=["2023-12-31"]
    )

    df_balance: pd.DataFrame = pd.DataFrame(
        {
            "Stockholders Equity": [-50.0],
        },
        index=["2023-12-31"]
    )

    df_cashflow: pd.DataFrame = pd.DataFrame()

    estados_simulados: Dict[str, pd.DataFrame] = {
        "income_statement": df_income,
        "balance_sheet": df_balance,
        "cash_flow": df_cashflow
    }

    resultados: Dict[str, float] = calcular_pilar_rentabilidad(estados_simulados)

    assert resultados["roe"] == 0.0
    assert resultados["margen_operativo"] == 0.0
    assert resultados["margen_neto"] == 0.0