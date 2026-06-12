import json
import re
from datetime import datetime, timedelta

import pandas as pd
from config.columns import COLUMNS
from config.dictionary import SECTORES


def json_to_dataframe(json_str: str) -> pd.DataFrame:
    """
    Convierte una cadena JSON en un DataFrame de pandas.
    Maneja respuestas HTTP con estructura {statusCode, body} y JSON directo.

    Args:
        json_str (str): Cadena JSON a convertir.

    Returns:
        pd.DataFrame: DataFrame resultante.

    Raises:
        ValueError: Si el JSON no es válido o no se puede convertir.
    """
    if json_str is None or not str(json_str).strip():
        return pd.DataFrame()

    if isinstance(json_str, bytes):
        json_str = json_str.decode("utf-8")

    try:
        data = json.loads(json_str)
        
        # Manejo de respuesta HTTP con statusCode y body
        if isinstance(data, dict) and 'statusCode' in data and 'body' in data:
            data = data['body']
        
        if isinstance(data, list):
            return pd.DataFrame(data)
        elif isinstance(data, dict):
            if 'results' in data:
                return pd.DataFrame(data['results'])
            return pd.DataFrame([data])
        raise ValueError("El JSON debe ser una lista de objetos o un objeto con clave 'results'.")
    except json.JSONDecodeError as e:
        raise ValueError(f"Error al decodificar JSON: {e}")




def process_dataframe(df: pd.DataFrame, columns_map: dict = None) -> pd.DataFrame:
    """
    Procesa el DataFrame para seleccionar y renombrar columnas según el mapeo proporcionado.

    Args:
        df (pd.DataFrame): DataFrame original.
        columns_map (dict): Diccionario con el mapeo de columnas {nombre_destino: nombre_origen}.
                           Si es None, usa el mapeo predeterminado de COLUMNS.

    Returns:
        pd.DataFrame: DataFrame procesado.
    """
    if columns_map is None:
        columns_map = COLUMNS
    
    if df.empty:
        columns = list(columns_map.keys())
        return pd.DataFrame(columns=columns)

    # Seleccionar solo las columnas que existen en el DataFrame
    existing_columns = [col for col in columns_map.values() if col in df.columns]
    if not existing_columns:
        return pd.DataFrame()
    
    df_processed = df[existing_columns].rename(columns={v: k for k, v in columns_map.items() if v in df.columns})
    
    # Agregar TOP_SECTORIAL si la columna original existe
    if "account.iav_target" in df.columns:
        df_processed["TOP_SECTORIAL"] = df["account.iav_target"].apply(lambda x: "No" if pd.isna(x) or x is None else "Si")
    
    return df_processed


def get_week_range(weeks_ago: int) -> tuple[datetime.date, datetime.date]:
    """
    Obtiene el rango de fechas de la semana X semanas atrás.

    Args:
        weeks_ago (int): Número de semanas atrás.

    Returns:
        tuple[datetime.date, datetime.date]: Inicio y fin de la semana.
    """
    target_date = datetime.now().date() - timedelta(weeks=weeks_ago)
    start_of_week = target_date - timedelta(days=target_date.weekday())
    end_of_week = start_of_week + timedelta(days=6)
    return start_of_week, end_of_week


def chunk_array(array, chunk_size: int):
    """
    Divide un arreglo en varios subarreglos de tamaño máximo `chunk_size`.

    Args:
        array: Lista, arreglo numpy, Series o cualquier objeto indexable.
        chunk_size (int): Tamaño máximo de cada subarreglo.

    Returns:
        list: Lista de subarreglos.
    """
    if chunk_size <= 0:
        raise ValueError("chunk_size debe ser un entero positivo")

    try:
        length = len(array)
    except TypeError:
        raise TypeError("El objeto proporcionado debe ser indexable y tener longitud")

    return [array[i:i + chunk_size] for i in range(0, length, chunk_size)]


def join_tagged_values(values, tag: str = "value") -> str:
    """
    Une los datos de un arreglo en una cadena donde cada valor queda envuelto en etiquetas XML.

    Args:
        values: Lista, arreglo numpy, Series o cualquier colección iterable.
        tag (str): Nombre de la etiqueta. Por defecto "value".

    Returns:
        str: Cadena con los valores envueltos en etiquetas.
    """
    if not isinstance(tag, str) or not tag.strip():
        raise ValueError("tag debe ser una cadena no vacía")

    return "".join(f"<{tag}>{value}</{tag}>" for value in values)


def join_sql_values(values) -> str:
    """
    Une los valores de un arreglo en una cadena con formato SQL IN: 'val1', 'val2', ...

    Args:
        values: Lista, arreglo numpy, Series o cualquier colección iterable.

    Returns:
        str: Cadena con los valores entre comillas simples separados por coma.
    """
    return ", ".join(f"'{str(value).replace(chr(39), chr(39) * 2)}'" for value in values)


_ILLEGAL_XML_CHARS_RE = re.compile(
    r"[\x00-\x08\x0b\x0c\x0e-\x1f\x7f-\x84\x86-\x9f"
    r"\ud800-\udfff\ufffe\uffff]"
)


def _sanitize_value(val):
    if isinstance(val, str):
        return _ILLEGAL_XML_CHARS_RE.sub("", val)
    return val


def export_to_excel(dfs: dict, file_path: str) -> None:
    """
    Exporta múltiples DataFrames a Excel en hojas diferentes.

    Args:
        dfs (dict): Diccionario con {nombre_hoja: DataFrame}
        file_path (str): Ruta del archivo Excel.
    """
    with pd.ExcelWriter(file_path, engine="openpyxl") as writer:
        for sheet_name, df in dfs.items():
            df = df.apply(lambda col: col.apply(_sanitize_value))
            df.to_excel(writer, sheet_name=sheet_name, index=False)


def map_sector_grants(df: pd.DataFrame, crm_column: str, target_column: str = "SECTOR_GRANTS") -> pd.DataFrame:
    """
    Mapea los valores de una columna del CRM a su sector equivalente en GRANTS.

    Args:
        df (pd.DataFrame): DataFrame de entrada.
        crm_column (str): Nombre de la columna que contiene los sectores del CRM.
        target_column (str): Nombre de la columna de salida con los sectores GRANTS.
                             Por defecto "SECTOR_GRANTS".

    Returns:
        pd.DataFrame: Copia del DataFrame con la columna de sectores GRANTS añadida.
                      Los valores sin correspondencia quedan como NaN.
    """
    crm_to_grants = {item["CRM"]: item["GRANTS"] for item in SECTORES}
    df = df.copy()
    df[target_column] = df[crm_column].map(crm_to_grants)
    return df