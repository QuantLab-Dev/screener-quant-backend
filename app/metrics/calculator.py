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

def calcular_pilar_salud(
    estados_financieros: Dict[str, pd.DataFrame]
)-> Dict[str, float]:
    """"
    Calcula las 2 métricas del pilar (salud financiera): Ratio Deuda/EBITDA y Liquidez Corriente.
    """
    #----------------------------------------------------------------------------
    # PASO 1: Desempaquetamos los estados contables necesarios
    #----------------------------------------------------------------------------
    df_income: pd.DataFrame = estados_financieros["income_statement"]
    df_balance: pd.DataFrame = estados_financieros["balance_sheet"]

    #----------------------------------------------------------------------------
    # PASO 2: Extraer rubros contables crudos del último año fiscal
    #----------------------------------------------------------------------------
    # EBITDA: Es la ganancia operativa pura del negocio antes de pagar intereses de deuda, impuestos y gastos contables que no implican salida de dinero.
    ebitda: float = _obtener_ultimo_dato(dataframe_estado=df_income, nombres_columnas_posibles=["EBITDA","Normalized EBITDA"])
    # Total Debt: Es la suma de todos los préstamos bancarios y bonos emitidos por la empresa, tanto de corto como de largo plazo.
    deuda_total: float = _obtener_ultimo_dato(dataframe_estado=df_balance, nombres_columnas_posibles=["Total Debt", "Long Term Debt And Capital Lease Obligation"])
    # Current Assets: Todo el dinero en efectivo y los bienes que la empresa espera convertir en efectivo dentro de los próximos 12 meses.
    activo_corriente: float = _obtener_ultimo_dato(dataframe_estado=df_balance, nombres_columnas_posibles=["Current Assets","Total Current Assets"])
    # Current Liabilities: Todas las deudas y obligaciones que la empresa debe pagar obligatoriamente dentro de los próximos 12 meses.
    pasivo_corriente: float = _obtener_ultimo_dato(dataframe_estado=df_balance, nombres_columnas_posibles=["Current Liabilities", "Total Currrent Liabilities"])
    #----------------------------------------------------------------------------
    # PASO 3: Calcular Ratio Deuda / EBITDA con reglas de solvencia
    #----------------------------------------------------------------------------
    # Deuda EBITDA: Indica cuántos años tardaría la empresa en pagar toda su deuda si destinara el 100% de su EBITDA a cancelarla.
    deuda_ebitda: float = 0.0

    if deuda_total > 0.0:
        if ebitda > 0.0:
            deuda_ebitda = deuda_total / ebitda
        else:
            deuda_ebitda = 10.0
    #----------------------------------------------------------------------------
    # PASO 4: Calculamos liquidez corriente evitando division por cero
    #----------------------------------------------------------------------------
    # Liquidez corriente: Mide cuántos dólares liquidos tiene la empresa para cubrir cada dólar que vence este año.
    liquidez_corriente: float = 0.0

    if pasivo_corriente > 0.0:
        liquidez_corriente = activo_corriente / pasivo_corriente
    #----------------------------------------------------------------------------
    # PASO 5: Empaquetamos y retornamos las métricas del pilar
    #----------------------------------------------------------------------------
    metricas_salud: Dict[str, float] = {
        "deuda_ebitda": deuda_ebitda,
        "liquidez_corriente": liquidez_corriente
    }

    return metricas_salud

def calcular_pilar_flujo_caja(
    estados_financieros: Dict[str, pd.DataFrame]
) -> Dict[str, float]:
    """"
    Calcula las 2 métricas del Pilar (Flujo de Caja): Margen de Flujo de
    Caja Libre (FCF Margin) y Ratio de Conversión de Caja.

    Entrada:
        estados_financieros: Diccionario generado por fetcher.py con las claves
                             'income_statement', 'balance_sheet' y 'cash_flow'.
    Salida:
        Dict[str, float]: Diccionario con los ratios de generación de efectivo.
    """
    #---------------------------------------------------------------------------
    # PASO 1: Desempaquetar los estados contables necesarios
    #---------------------------------------------------------------------------
    df_cashflow: pd.DataFrame = estados_financieros["cash_flow"]
    df_income: pd.DataFrame = estados_financieros["income_statement"]
    #---------------------------------------------------------------------------
    # PASO 2: Extrae los rubros contables crudos del último año fiscal.
    #---------------------------------------------------------------------------
    # fcf_margin: Es el dinero efectivo que sobra después de operar el negocio y pagar las inversiones obligatorias en activos físicos o tecnológicos (maquinarias, servidores, plantas) necesarias para mantenerlo funcionando (CAPEX o Capital Expenditures).
    flujo_operativo: float = _obtener_ultimo_dato(dataframe_estado=df_cashflow, nombres_columnas_posibles=["Operating Cash Flow", "Cash Flow From Continuing Operating Activities"])
    capex_crudo: float = _obtener_ultimo_dato(dataframe_estado=df_cashflow, nombres_columnas_posibles=["Capital Expenditure", "Capital Expenditures"])
    ventas_totales: float = _obtener_ultimo_dato(dataframe_estado=df_income, nombres_columnas_posibles=["Total Revenue", "Operating Revenue"])
    ganancia_neta: float = _obtener_ultimo_dato(dataframe_estado=df_income, nombres_columnas_posibles=["Net Income", "Net Income Common Stockholders"])
    #-----------------------------------------------------------------------------
    # PASO 3: Calcular el Flujo de la Caja Libre (FCF) normalizando signo de CAPEX
    #-----------------------------------------------------------------------------
    inversion_capex: float = abs(capex_crudo)
    free_cash_flow: float = flujo_operativo - inversion_capex
    #-----------------------------------------------------------------------------
    # PASO 4: Calcular Margen FCF con protección contra division por cero
    #-----------------------------------------------------------------------------
    fcf_margin: float = 0.0

    if ventas_totales > 0.0:
        fcf_margin: float = free_cash_flow / ventas_totales

    #-----------------------------------------------------------------------------
    # PASO 5: Calcular Conversión de Caja
    #-----------------------------------------------------------------------------
    conversion_caja: float = 0.0

    if ganancia_neta > 0.0:
        conversion_caja: float = flujo_operativo / ganancia_neta

    #-----------------------------------------------------------------------------
    # PASO 6: Empaquetado y retorno del diccionario de métricas
    #-----------------------------------------------------------------------------
    metricass_flujo_caja: Dict[str, float] = {
        "fcf_margin": fcf_margin,
        "conversion_caja": conversion_caja
    }

    return metricass_flujo_caja