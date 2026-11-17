from unittest.mock import patch, MagicMock
from typing import Dict, List
import pandas as pd
import pytest

from app.metrics.calculator import _obtener_ultimo_dato

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
