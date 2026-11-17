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

