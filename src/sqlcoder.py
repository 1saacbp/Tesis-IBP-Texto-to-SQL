# ===============================
# Imports
# ===============================

from llama_cpp import Llama


from llama_cpp import Llama
import multiprocessing


n_threads = multiprocessing.cpu_count()

llm = Llama(
    model_path="models/sqlcoder-7b-2.Q4_K_M.gguf",
    n_threads=n_threads,
    n_ctx=4096, #funciona bien
    verbose=False
)
prompt = """
### Instruction:
Write a SQL query to answer the following question.

### Question:
cual es el tipo de entidad con mas creditos sin garantia y un rango de monto desembolsado mayor a 1 smlmv menor o igual a 3 smlmv

### Schema:
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
### Response:
"""

output = llm(
    prompt,
    max_tokens=200,
    temperature=0.1,
    stop=["###"]
)
print(output["choices"][0]["text"])



