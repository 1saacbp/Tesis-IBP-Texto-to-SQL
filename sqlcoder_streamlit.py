# ===============================
# Imports
# ===============================
import streamlit as st
import matplotlib.pyplot as plt
from llama_cpp import Llama
import multiprocessing

st.title("SQLCoder - GENERADOR DE CONSULTAS SQL")
st.write("""
SQLCoder es un modelo de lenguaje especializado diseñado para generar consultas SQL basadas en preguntas en lenguaje natural y esquemas de bases de datos.
""")

n_threads = multiprocessing.cpu_count()

@st.cache_resource
def cargar_llm():
    n_threads = multiprocessing.cpu_count()
    return Llama(
        model_path="models/sqlcoder-7b-2.Q4_K_M.gguf",
        n_threads=n_threads,
        n_ctx=4096,
        verbose=False
    )

llm = cargar_llm()

prompt = st.text_area(
    "Pregunta en lenguaje natural",
    value=""
)

if st.button("Generar SQL"):
    with st.spinner("Generando consulta SQL..."):
        output = llm(
            f"""
### Instruction:
Write a SQL query to answer the following question.

### Question:
{prompt}

### Schema:
CREATE TABLE clientes (
   cliente_id INTEGER PRIMARY KEY,
   nombre VARCHAR(50),
   direccion VARCHAR(100),
   edad INTEGER
);
CREATE TABLE producto (
    producto_id INTEGER PRIMARY KEY,
    nombre_producto VARCHAR(50),
    precio DECIMAL(10, 2)
);
CREATE TABLE productos_ordenes (
    orden_id INTEGER PRIMARY KEY,
    cliente_id INTEGER,
    producto_id INTEGER,
    cantidad INTEGER,
    fecha_orden DATE,
    FOREIGN KEY (cliente_id) REFERENCES clientes(cliente_id),
    FOREIGN KEY (producto_id) REFERENCES producto(producto_id)
);

### Response:
""",
            max_tokens=256,
            temperature=0.1,
            stop=["###"]
        )

        respuesta = output["choices"][0]["text"]

    st.subheader("SQL generado")
    st.code(respuesta, language="sql")
