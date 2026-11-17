"""
Módulo de Cálculo de Métricas Financieras.

Transforma los DataFrames de estados contables limpios en ratios financieros agrupados por los 4 pilares del modelo cuantitativo.
"""

from typing import Dict, List
import pandas as pd

def _obtener_ultimo_dato(
        dataframe_estado: pd.DataFrame,
        nombres_columnas_posibles: List[str]
) -> float:
    """
    Busca una métrica contable dentro de un DataFrame probando distintos nombres posibles y extrae el valor del período fiscal más reciente.
    """
    columnas_disponibles: List[str] = list(dataframe_estado.columns)

    for nombre_buscado in nombres_columnas_posibles:
        if nombre_buscado  in columnas_disponibles:
            serie_historica: pd.Series = dataframe_estado[nombre_buscado]
            ultimo_dato: float = float(serie_historica.iloc[0])

            return ultimo_dato

    valor_por_defecto: float = 0.0
    return valor_por_defecto

def calcular_pilar_rentabilidad(
    estados_financieros: Dict[str, pd.DataFrame]
) -> Dict[str, float]:
    """
    Calcula las 3 métricas del Pilar (Rentabilidad): ROE, Margen Operativo y Margen Neto.
    """
    #----------------------------------------------------------------------------
    # PASO 1: Desempaquetar los estados contables necesarios para este pilar
    #----------------------------------------------------------------------------
    df_income: pd.DataFrame = estados_financieros["income_statement"]
    df_balance: pd.DataFrame = estados_financieros["balance_sheet"]

    #----------------------------------------------------------------------------
    # PASO 2: Extraer los rubros contables crudos del último año fiscal
    #----------------------------------------------------------------------------
    ventas_totales: float = _obtener_ultimo_dato(dataframe_estado=df_income, nombres_columnas_posibles=["Total Revenue", "Revenue"])
    resultados_operativos: float = _obtener_ultimo_dato(dataframe_estado=df_income, nombres_columnas_posibles=["Operating Income", "EBIT"])
    ganancia_neta: float = _obtener_ultimo_dato(dataframe_estado=df_income, nombres_columnas_posibles=["Net Income", "Net Income Common Stockholders"])
    patrimonio_neto: float = _obtener_ultimo_dato(dataframe_estado=df_balance, nombres_columnas_posibles=["Stockholders Equity", "Total Stockholder Equity", "Common Stock Equity"])

    #----------------------------------------------------------------------------
    # PASO 3: Calculo de ROE con protección contra patrimonio negativo o cero
    #----------------------------------------------------------------------------
    roe: float = 0.0
    if patrimonio_neto > 0:
        roe = ganancia_neta / patrimonio_neto

    #----------------------------------------------------------------------------
    # PASO 4: Calculo de Margenes con protección contra división por cero
    #----------------------------------------------------------------------------
    margen_operativo: float = 0.0
    margen_neto: float = 0.0

    if ventas_totales > 0:
        margen_operativo = resultados_operativos / ventas_totales
        margen_neto = ganancia_neta / ventas_totales

    #----------------------------------------------------------------------------
    # PASO 5: Empaquetado y retorno de métricas
    #----------------------------------------------------------------------------
    metricas_rentabilidad: Dict[str, float] = {
        "roe": roe,
        "margen_operativo": margen_operativo,
        "margen_neto": margen_neto
    }

    return metricas_rentabilidad

    