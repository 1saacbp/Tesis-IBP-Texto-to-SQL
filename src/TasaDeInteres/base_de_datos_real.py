
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import sqlite3
datos=pd.read_csv('C:/Users/isaac/Downloads/proyecto_tesis/data/TasaDeInteres/Tasas_activas_por_credito_Historico_20250807.csv')

import unicodedata

def remove_accents(input_str):
    if isinstance(input_str, str):
        nfkd_form = unicodedata.normalize('NFKD', input_str)
        return ''.join([c for c in nfkd_form if not unicodedata.combining(c)])
    return input_str

text_columns = datos.select_dtypes(include='object').columns

for col in text_columns:
    datos[col] = datos[col].apply(lambda x: remove_accents(str(x).lower()) if pd.notna(x) else x)

columnas_deudor = [
    'Tipo_de_persona','Sexo','Clase_deudor',
    'Codigo_Municipio','Codigo_CIIU',
    'Grupo_Etnico','Antiguedad_de_la_empresa',
    'Tamaño_de_empresa'
]

datos= datos.dropna(subset=columnas_deudor)

Entidades = datos[['Tipo_Entidad', 'Nombre_Tipo_Entidad','Codigo_Entidad','Nombre_Entidad']].drop_duplicates().reset_index(drop=True)
Entidades['id_entidad'] = Entidades.index + 1
Deudor = datos[['Tipo_de_persona','Sexo','Clase_deudor','Codigo_Municipio','Codigo_CIIU','Grupo_Etnico','Antiguedad_de_la_empresa','Tamaño_de_empresa']].drop_duplicates().reset_index(drop=True)
Deudor['id_deudor'] = Deudor.index + 1

Credito = datos.merge(
    Entidades,
    on=['Codigo_Entidad','Tipo_Entidad'],
    how='left'
)

Credito=Credito.merge(
    Deudor,
    on=['Tipo_de_persona','Sexo','Clase_deudor','Codigo_Municipio','Codigo_CIIU','Grupo_Etnico','Antiguedad_de_la_empresa','Tamaño_de_empresa'],
    how='left'
)

Credito = Credito.drop(columns=['Tipo_Entidad', 'Nombre_Tipo_Entidad_x','Codigo_Entidad','Nombre_Entidad_x','Nombre_Tipo_Entidad_y','Nombre_Entidad_y',
                              'Tipo_de_persona','Sexo','Clase_deudor','Codigo_Municipio','Codigo_CIIU','Grupo_Etnico','Antiguedad_de_la_empresa','Tamaño_de_empresa',
                              ])

xls = pd.ExcelFile('C:/Users/isaac/Downloads/proyecto_tesis/data/TasaDeInteres/Tablas_extra_Tesis_IBP.xlsx')
df_ciiu = pd.read_excel(xls, sheet_name='Codigos_CIIU')
df_municipios = pd.read_excel(xls, sheet_name='Codigos_Municipios')

text_columns = df_ciiu.select_dtypes(include='object').columns
text_columnss = df_municipios.select_dtypes(include='object').columns
for col in text_columns:
    df_ciiu[col] = df_ciiu[col].apply(lambda x: remove_accents(str(x).lower()) if pd.notna(x) else x)
for col in text_columnss:
    df_municipios[col] = df_municipios[col].apply(lambda x: remove_accents(str(x).lower()) if pd.notna(x) else x)

df_ciiu = df_ciiu.drop_duplicates(subset=['codigo_ciiu'], keep='last')

Credito = Credito.rename(columns={'Tipo_de_crédito': 'tipo_credito'})
Credito = Credito.rename(columns={'Tipo_de_garantía': 'tipo_garantia'})
Credito = Credito.rename(columns={'Producto de crédito': 'producto_credito'})
Credito = Credito.rename(columns={'Plazo de crédito': 'plazo_credito'})
Credito = Credito.rename(columns={'Tasa_efectiva_promedio_ponderada': 'tasa_efectiva_promedio_ponderada'})
Credito = Credito.rename(columns={'margen_adicional': 'margen_adicional'})
Credito = Credito.rename(columns={'Rango_monto_desembolsado': 'rango_monto_desembolsado'})
Credito = Credito.rename(columns={'Tipo_de_Tasa': 'tipo_tasa'})
Credito = Credito.rename(columns={'Numero_de_creditos_desembolsados': 'numero_creditos_desembolsados'})
Credito = Credito.rename(columns={'Fecha_Corte': 'fecha_corte'})
Credito = Credito.rename(columns={'Montos_desembolsados': 'monto_desembolsado'})
#--------------------------------------------------------------------
Deudor=Deudor.rename(columns={'Codigo_Municipio':'codigo_municipio'})
Deudor=Deudor.rename(columns={'Codigo_CIIU':'codigo_ciiu'})
Deudor=Deudor.rename(columns={'Tipo_de_persona':'tipo_persona'})
Deudor=Deudor.rename(columns={'Sexo':'sexo'})
Deudor=Deudor.rename(columns={'Clase_deudor':'clase_deudor'})
Deudor=Deudor.rename(columns={'Grupo_Etnico':'grupo_etnico'})
Deudor=Deudor.rename(columns={'Antiguedad_de_la_empresa':'antiguedad_empresa'})
Deudor=Deudor.rename(columns={'Tamaño_de_empresa':'tamano_empresa'})
Deudor=Deudor.dropna(subset=["codigo_ciiu"])
#--------------------------------------------------------------------
Entidades=Entidades.rename(columns={'Tipo_Entidad':'tipo_entidad'})
Entidades=Entidades.rename(columns={'Nombre_Tipo_Entidad':'nombre_tipo_entidad'})
Entidades=Entidades.rename(columns={'Codigo_Entidad':'codigo_entidad'})
Entidades=Entidades.rename(columns={'Nombre_Entidad':'nombre_entidad'})

Entidades['nombre_tipo_entidad'] = Entidades['nombre_tipo_entidad'].str.replace('bc-establecimiento bancario', 'establecimiento bancario', regex=False)
Entidades['nombre_tipo_entidad'] = Entidades['nombre_tipo_entidad'].str.replace('cf-compania de financiamiento', 'compania de financiamiento', regex=False)

Credito['producto_credito'] = Credito['producto_credito'].str.replace('credito productivo rural  (con recursos de redescuento)', 'productivo rural redescuento', regex=False)
Credito['producto_credito'] = Credito['producto_credito'].str.replace('credito productivo urbano  (con recursos de redescuento)', 'productivo urbano redescuento', regex=False)
Credito['producto_credito'] = Credito['producto_credito'].str.replace('libranza otros', 'libranza', regex=False)


Credito['tipo_garantia'] = Credito['tipo_garantia'].str.replace('garantia del fondo agropecuario de garantias (fag)', 'fag', regex=False)
Credito['tipo_garantia'] = Credito['tipo_garantia'].str.replace('garantia  fondo nacional de garantias (fng) o fondo de garantias de antioquia (fga)', 'fng o fga', regex=False)


Credito['fecha_corte'] = pd.to_datetime(Credito['fecha_corte'], format='%d/%m/%Y')

df_municipios['departamento'] = df_municipios['departamento'].str.replace('bogota, d.c.', 'bogota', regex=False)
df_municipios['departamento'] = df_municipios['departamento'].str.replace('archipielago de san andres, providencia y santa catalina', 'islas san andres', regex=False)
df_ciiu["actividad_economica"] = df_ciiu["actividad_economica"].str.replace(".", "", regex=False)

"""
CREATE TABLE Entidades (
    id_entidad INTEGER PRIMARY KEY,
    tipo_entidad INTEGER,
    nombre_tipo_entidad TEXT,
    codigo_entidad INTEGER,
    nombre_entidad TEXT
);

CREATE TABLE Municipio (
    codigo_municipio INTEGER PRIMARY KEY,
    municipio TEXT,
    departamento TEXT
);

CREATE TABLE Ciiu (
    codigo_ciiu TEXT PRIMARY KEY,
    actividad_economica TEXT
);

CREATE TABLE Deudor (
    id_deudor INTEGER PRIMARY KEY,
    tipo_persona TEXT,
    sexo TEXT,
    clase_deudor TEXT,
    codigo_municipio INTEGER,
    codigo_ciiu TEXT,
    grupo_etnico TEXT ,
    antiguedad_empresa TEXT,
    tamano_empresa TEXT,

    FOREIGN KEY (codigo_municipio)
        REFERENCES Municipio(codigo_municipio),

    FOREIGN KEY (codigo_ciiu)
        REFERENCES Ciiu(codigo_ciiu)
);

CREATE TABLE Credito (
    id_credito INTEGER PRIMARY KEY,
    fecha_corte TEXT,
    tipo_credito TEXT ,
    tipo_garantia TEXT,
    producto_credito TEXT ,
    plazo_credito TEXT,
    tasa_efectiva_promedio_ponderada REAL,
    margen_adicional REAL,
    monto_desembolsado INTEGER,
    numero_creditos_desembolsados INTEGER,
    tipo_tasa TEXT,
    rango_monto_desembolsado TEXT,
    id_deudor INTEGER,
    id_entidad INTEGER,

    FOREIGN KEY (id_deudor)
        REFERENCES Deudor(id_deudor),

    FOREIGN KEY (id_entidad)
        REFERENCES Entidades(id_entidad)
);
"""

# Base de datos SQLite



# =========================
# Conexión
# =========================
conn = sqlite3.connect("mi_base.db")
cursor = conn.cursor()

# Activar claves foráneas
cursor.execute("PRAGMA foreign_keys = ON;")
cursor.executescript("""
DROP TABLE IF EXISTS Credito;
DROP TABLE IF EXISTS Deudor;
DROP TABLE IF EXISTS Municipio;
DROP TABLE IF EXISTS Ciiu;
DROP TABLE IF EXISTS Entidades;
""")

# =========================
# Crear estructura
# =========================

cursor.executescript("""
CREATE TABLE Entidades (
    id_entidad INTEGER PRIMARY KEY,
    tipo_entidad INTEGER,
    nombre_tipo_entidad TEXT,
    codigo_entidad INTEGER,
    nombre_entidad TEXT
);

CREATE TABLE Municipio (
    codigo_municipio INTEGER PRIMARY KEY,
    municipio TEXT,
    departamento TEXT
);

CREATE TABLE Ciiu (
    codigo_ciiu INTEGER PRIMARY KEY,
    actividad_economica TEXT
);

CREATE TABLE Deudor (
    id_deudor INTEGER PRIMARY KEY,
    tipo_persona TEXT,
    sexo TEXT,
    clase_deudor TEXT,
    codigo_municipio INTEGER,
    codigo_ciiu INTEGER,
    grupo_etnico TEXT ,
    antiguedad_empresa TEXT,
    tamano_empresa TEXT,

    FOREIGN KEY (codigo_municipio)
        REFERENCES Municipio(codigo_municipio),

    FOREIGN KEY (codigo_ciiu)
        REFERENCES Ciiu(codigo_ciiu)
);

CREATE TABLE Credito (
    id_credito INTEGER PRIMARY KEY,
    fecha_corte TEXT,
    tipo_credito TEXT ,
    tipo_garantia TEXT,
    producto_credito TEXT ,
    plazo_credito TEXT,
    tasa_efectiva_promedio_ponderada REAL,
    margen_adicional REAL,
    monto_desembolsado INTEGER,
    numero_creditos_desembolsados INTEGER,
    tipo_tasa TEXT,
    rango_monto_desembolsado TEXT,
    id_deudor INTEGER,
    id_entidad INTEGER,

    FOREIGN KEY (id_deudor)
        REFERENCES Deudor(id_deudor),

    FOREIGN KEY (id_entidad)
        REFERENCES Entidades(id_entidad)
);
""")

conn.commit()

Entidades.to_sql("Entidades", conn, if_exists="append", index=False, chunksize=10000)
df_municipios.to_sql("Municipio", conn, if_exists="append", index=False, chunksize=10000)
df_ciiu.to_sql("Ciiu", conn, if_exists="append", index=False, chunksize=10000)
Deudor.to_sql("Deudor", conn, if_exists="append", index=False, chunksize=10000)

# =========================
# Cargar datos
# =========================
Credito.to_sql("Credito", conn, if_exists="append", index=False, chunksize=10000)

conn.commit()

print("✅ Tablas creadas y datos cargados correctamente.")

# =========================
# Verificar
# =========================
for tabla in ["Entidades", "Municipio", "Ciiu", "Deudor", "Credito"]:
    count = pd.read_sql(f"SELECT COUNT(*) as total FROM {tabla}", conn)
    print(tabla, count["total"][0])

conn.close()