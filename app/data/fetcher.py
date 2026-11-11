"""
Módulo de Ingesta y Limpieza de datos financieros.

Este módulo se encarga de conectar con Yahoo Finance mediante la librería yfinance, descargar los 3 estados contables principales de un ticker, limpiar valores nulos y estructurar los DataFrames para el motor de métricas.
"""

from typing import Dict, Any
import pandas as pd
import yfinance as yf

def extraer_estados_financieros(ticker_simbolo: str) -> Dict[str, pd.DataFrame]:
    # PASO 1: Limpia espacios en blancos tanto al principio como al final del string y lo convierte a mayúsculas
    simbolo_procesado: str = ticker_simbolo.strip().upper()

    # PASO 2: Instanciar la entidad Ticker de yfinance
    # --------------------------------------------------------------------------------------------------
    # Crear un objeto conector que contiene los métodos de descarga para la empresa
    objeto_ticker: yf.Ticker = yf.Ticker(simbolo_procesado)

    # PASO 3: Extracción de datos crudos (Raw DataFrame)
    raw_income_statement: pd.DataFrame = objeto_ticker.financials
    raw_balance_sheet: pd.DataFrame = objeto_ticker.balance_sheet
    raw_cash_flow: pd.DataFrame = objeto_ticker.cashflow

    # PASO 4: Valicación de la existencia de datos
    is_income_empty: bool = raw_income_statement.empty
    is_balance_empty: bool = raw_balance_sheet.empty
    is_cashflow_empty: bool = raw_cash_flow.empty

    if is_income_empty or is_balance_empty or is_cashflow_empty:
        raise ValueError(f"Datos no disponibles para el ticker '{simbolo_procesado}'")

    # PASO 5: Reestructuración
    income_transpuesto: pd.DataFrame = raw_income_statement.T
    balance_transpuesto: pd.DataFrame = raw_balance_sheet.T
    cashflow_transpuesto: pd.DataFrame = raw_cash_flow.T

    # Paso 6: Limpieza de valores nulos
    income_limpio: pd.DataFrame = income_transpuesto.fillna(0.0)
    balance_limpio: pd.DataFrame = balance_transpuesto.fillna(0.0)
    cashflow_limpio: pd.DataFrame = cashflow_transpuesto.fillna(0.0)

    # Paso 7: Estructuración de los DataFrames
    resultado_estados: Dict[str, pd.DataFrame] = {
        "income_statement": income_limpio,
        "balance_sheet": balance_limpio,
        "cash_flow": cashflow_limpio
    }

    return resultado_estados