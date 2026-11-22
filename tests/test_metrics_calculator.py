"""
Pruebas unitarias para el Motor de Métricas (app/metrics/calculator.py).
"""

from unittest.mock import patch, MagicMock
from typing import Dict, List
import pandas as pd
import pytest

from app.metrics.calculator import (_obtener_ultimo_dato, 
                                    calcular_pilar_rentabilidad, 
                                    calcular_pilar_salud,
                                    calcular_pilar_flujo_caja)

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

def test_calcular_pilar_salud_exito():
    """
    Verifica el cálculo exacto de Deuda/EBITDA y Liquidez Corriente bajo condiciones financiera esaludables.
    """
    df_income: pd.DataFrame = pd.DataFrame(
        {
            "EBITDA": [400.0, 300.0]
        },
        index=["2023-21-31", "2022-12-31"]
    )

    df_balance: pd.DataFrame = pd.DataFrame(
        {
            "Total Debt": [600.0, 210.0],
            "Current Assets": [300.0, 230.0],
            "Current Liabilities": [200.0, 120.0]
        },
        index=["2023-12-31","2022-12-31"]
    )

    estados_simulados: Dict[str, pd.DataFrame] = {
       "income_statement": df_income,
       "balance_sheet": df_balance,
       "cash_flow": pd.DataFrame()
    }

    resultado_metricas: Dict[str, float] = calcular_pilar_salud(estados_financieros=estados_simulados)

    assert resultado_metricas["deuda_ebitda"] == pytest.approx(1.5)
    assert resultado_metricas["liquidez_corriente"] == pytest.approx(1.5)

def test_calcular_pilar_salud_casos_bordes():
    """
    Verificamos la penalización máxima cuando hay deuda con EBITDA negativo y la protección contra división por cero en pasivos corrientes.
    """
    df_income: pd.DataFrame = pd.DataFrame(
        {
            "EBITDA": [-50.0]
        },
        index=["2023-12-31"]
    )

    df_balance: pd.DataFrame = pd.DataFrame(
        {
            "Total Debt": [500.0],
            "Current Assets": [100.0],
            "Current Liabilities": [0.0]
        },
        index=["2023-12-31"]
    )

    estados_simulados: Dict[str, pd.DataFrame] = {
        "income_statement": df_income,
        "balance_sheet": df_balance,
        "cash_flow": pd.DataFrame()
    }

    resultado_metricas: Dict[str, float] = calcular_pilar_salud(estados_financieros= estados_simulados)

    assert resultado_metricas["deuda_ebitda"] == pytest.approx(10.0)
    assert resultado_metricas["liquidez_corriente"] == pytest.approx(0.0)

def test_calcular_pilar_flujo_caja_exito():
    """"
    Verifica el cálculo de Margen FCF y Conversión de Caja cuando el CAPEX viene con signo negativo.
    """
    df_cashflow: pd.DataFrame = pd.DataFrame(
        {
            "Operating Cash Flow": [300.0],
            "Capital Expenditure": [-60.0]
        },
        index=["2023-12-31"]
    )

    df_income: pd.DataFrame = pd.DataFrame(
        {
            "Total Revenue": [1000.0],
            "Net Income": [250.0]
        },
        index=["2023-12-31"]
    )

    estados_simulados: Dict[str, pd.DataFrame] = {
        "income_statement": df_income,
        "balance_sheet": pd.DataFrame(),
        "cash_flow": df_cashflow
    }

    resultado = calcular_pilar_flujo_caja(estados_financieros=estados_simulados)

    assert resultado["fcf_margin"] == pytest.approx(0.24)
    assert resultado["conversion_caja"] == pytest.approx(1.20)

def test_calcular_pilar_flujo_caja_casos_borde():
    """
    Verifica la protección contra división por cero cuando no hay ventas
    y cuando la ganancia neta es negativa.
    """
    df_cashflow = pd.DataFrame(
        {
            "Operating Cash Flow": [-20.0],
            "Capital Expenditure": [10.0],
        },
        index=["2023-12-31"]
    )
    df_income = pd.DataFrame(
        {
            "Total Revenue": [0.0],
            "Net Income": [-50.0],
        },
        index=["2023-12-31"]
    )

    estados_borde = {
        "income_statement": df_income,
        "balance_sheet": pd.DataFrame(),
        "cash_flow": df_cashflow,
    }

    resultado = calcular_pilar_flujo_caja(estados_borde)

    assert resultado["fcf_margin"] == 0.0
    assert resultado["conversion_caja"] == 0.0