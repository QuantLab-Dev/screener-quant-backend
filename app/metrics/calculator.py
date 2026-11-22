"""
Módulo de Cálculo de Métricas Financieras.

Transforma los DataFrames de estados contables limpios en ratios financieros agrupados por los 4 pilares del modelo cuantitativo.
"""

from typing import Dict, List, Any
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

def calcular_pilar_valuacion(
    estados_financieros: Dict[str, pd.DataFrame],
    datos_mercado: Dict[str, Any]
) -> Dict[str, float]:
    """
    Calcula las 2 métricas del Pilar 4 (Valuación): Ratio P/E (Price-to-Earnings)
    y Ratio EV/EBITDA.

    Entrada:
        estados_financieros: Diccionario con 'income_statement', 'balance_sheet' y 'cash_flow'.
        datos_mercado: Diccionario con cotizaciones y múltiplos de mercado (ticker.info).
    Salida:
        Dict[str, float]: Diccionario con los múltiplos de valuación.
    """
    # --------------------------------------------------------------------------
    # PASO 1: Desempaquetar los estados contables necesarios para este pilar
    # --------------------------------------------------------------------------
    df_income: pd.DataFrame = estados_financieros["income_statement"]
    df_balance: pd.DataFrame = estados_financieros["balance_sheet"]

    # --------------------------------------------------------------------------
    # PASO 2: Extraer los rubros contables crudos del último año fiscal
    # --------------------------------------------------------------------------
    ganancia_neta: float = _obtener_ultimo_dato(
        dataframe_estado=df_income,
        nombres_columnas_posibles=["Net Income", "Net Income Common Stockholders"]
    )
    ebitda: float = _obtener_ultimo_dato(
        dataframe_estado=df_income,
        nombres_columnas_posibles=["EBITDA", "Normalized EBITDA"]
    )
    deuda_total: float = _obtener_ultimo_dato(
        dataframe_estado=df_balance,
        nombres_columnas_posibles=["Total Debt", "Long Term Debt And Capital Lease Obligation"]
    )
    efectivo_caja: float = _obtener_ultimo_dato(
        dataframe_estado=df_balance,
        nombres_columnas_posibles=[
            "Cash And Cash Equivalents",
            "Cash Cash Equivalents And Short Term Investments"
        ]
    )

    # --------------------------------------------------------------------------
    # PASO 3: Extraer valores de mercado de forma segura (manejando None)
    # --------------------------------------------------------------------------
    market_cap_crudo: Any = datos_mercado.get("marketCap", 0.0)
    market_cap: float = float(market_cap_crudo) if market_cap_crudo is not None else 0.0

    ev_crudo: Any = datos_mercado.get("enterpriseValue", None)
    enterprise_value: float = 0.0

    if ev_crudo is not None:
        enterprise_value = float(ev_crudo)
    elif market_cap > 0.0:
        # Cálculo de respaldo si Yahoo Finance no provee el Enterprise Value directo
        enterprise_value = market_cap + deuda_total - efectivo_caja

    # --------------------------------------------------------------------------
    # PASO 4: Calcular Ratio P/E con penalización si hay pérdidas
    # --------------------------------------------------------------------------
    pe_ratio: float = 100.0

    if market_cap > 0.0 and ganancia_neta > 0.0:
        pe_ratio = market_cap / ganancia_neta

    # --------------------------------------------------------------------------
    # PASO 5: Calcular Ratio EV/EBITDA con penalización si EBITDA <= 0
    # --------------------------------------------------------------------------
    ev_ebitda: float = 50.0

    if enterprise_value > 0.0 and ebitda > 0.0:
        ev_ebitda = enterprise_value / ebitda

    # --------------------------------------------------------------------------
    # PASO 6: Empaquetar y retornar el diccionario de métricas del Pilar 4
    # --------------------------------------------------------------------------
    metricas_valuacion: Dict[str, float] = {
        "pe_ratio": pe_ratio,
        "ev_ebitda": ev_ebitda
    }

    return metricas_valuacion


def calcular_metricas_empresa(
    estados_financieros: Dict[str, pd.DataFrame],
    datos_mercado: Dict[str, Any]
) -> Dict[str, float]:
    """
    Ejecuta los 4 pilares analíticos sobre una empresa y consolida sus 9 ratios financieros en un único diccionario.
    """
    # --------------------------------------------------------------------------
    # PASO 1: Ejecutar cada pilar de forma modular
    # --------------------------------------------------------------------------
    pilar_1: Dict[str, float] = calcular_pilar_rentabilidad(estados_financieros)
    pilar_2: Dict[str, float] = calcular_pilar_salud(estados_financieros)
    pilar_3: Dict[str, float] = calcular_pilar_flujo_caja(estados_financieros)
    pilar_4: Dict[str, float] = calcular_pilar_valuacion(estados_financieros, datos_mercado)

    # --------------------------------------------------------------------------
    # PASO 2: Consolidar todas las métricas en un diccionario plano para la Capa 3
    # --------------------------------------------------------------------------
    perfil_metricas: Dict[str, float] = {}
    perfil_metricas.update(pilar_1)
    perfil_metricas.update(pilar_2)
    perfil_metricas.update(pilar_3)
    perfil_metricas.update(pilar_4)

    return perfil_metricas