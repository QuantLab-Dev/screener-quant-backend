"""
Pruebas Unitarias para el módulo de Ingesta (app/data/fetcherpy).
"""

from unittest.mock import patch, MagicMock
import pandas as pd
import pytest

from app.data.fetcher import extraer_estados_financieros

@pytest.fixture
def mock_datos_financieros_validos():
    """Crea DataFrames de prueba pequeños para simular la respuesta de yfinance."""
    df_income = pd.DataFrame(
        {"Total Revenue": [1000.0], "Net Income": [150.0]},
        index=["2023-12-31"]
        ).T

    df_balance = pd.DataFrame(
        {"Total Stockholder Equity": [500.0], "Total Debt": [200.0]},
        index=["2023-12-31"]
        ).T

    df_cashflow = pd.DataFrame(
        {"Operating Cash Flow": [200.0], "Capital Expenditures": [-50.0]},
        index=["2023-12-31"]
        ).T

    return df_income, df_balance, df_cashflow

def test_extraer_estados_financieros_exito(mock_datos_financieros_validos):
    """
    Verifica que la función procese y transponga correctamente los DataFrames cuando la API responde con datos válidos.
    """
    income_mock, balance_mock, cashflow_mock = mock_datos_financieros_validos

    # Interceptamos yfinance.Ticker para que devuelva nuestros datos simulados
    with patch("yfinance.Ticker") as mock_ticker_class:
        instancia_mock = MagicMock()
        instancia_mock.financials = income_mock
        instancia_mock.balance_sheet = balance_mock
        instancia_mock.cashflow = cashflow_mock

        mock_ticker_class.return_value = instancia_mock

        # Ejecutamos nuestra función
        resultado = extraer_estados_financieros("YPF")

        # verificaciones paso a paso
        assert "income_statement" in resultado
        assert "balance_sheet" in resultado
        assert "cash_flow" in resultado

        # Verificar que se realizó la transposición (Fechas quedan en las filas/index)

        df_income_resultado = resultado["income_statement"]
        assert "2023-12-31" in df_income_resultado.index
        assert "Total Revenue" in df_income_resultado.columns

