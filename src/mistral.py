# ===============================
# Imports
# ===============================
from llama_cpp import Llama
import multiprocessing
import sqlite3

conn = sqlite3.connect("src/bd-prueba-inicial.db")
cursor = conn.cursor()

cursor.executescript("""
CREATE TABLE IF NOT EXISTS customers (
   customer_id INTEGER PRIMARY KEY,
   name TEXT,
   address TEXT,
   age INTEGER
);

CREATE TABLE IF NOT EXISTS products (
   product_id INTEGER PRIMARY KEY,
   name TEXT,
   price REAL
);

CREATE TABLE IF NOT EXISTS products_orders (
   order_id INTEGER PRIMARY KEY,
   customer_id INTEGER,
   product_id INTEGER,
   quantity INTEGER,
   order_date DATE,
   FOREIGN KEY (customer_id) REFERENCES customers(customer_id),
   FOREIGN KEY (product_id) REFERENCES products(product_id)
);
""")

conn.commit()
conn.close()

print("Base de datos creada")

conn = sqlite3.connect("src/bd-prueba-inicial.db")
cursor = conn.cursor()

cursor.execute("INSERT or REPLACE INTO customers VALUES (1,'Ana','Bogota',21)")
cursor.execute("INSERT or REPLACE INTO customers VALUES (2,'Juan','Medellin',63)")
cursor.execute("INSERT or REPLACE INTO customers VALUES (3,'Camilo','Cali',20)")
cursor.execute("INSERT or REPLACE INTO products VALUES (1,'Laptop',1200)")
cursor.execute("INSERT or REPLACE INTO products VALUES (2,'Tablet',800)")
cursor.execute("INSERT or REPLACE INTO products VALUES (3,'Smartphone',600)")
cursor.execute("INSERT or REPLACE INTO products_orders VALUES (1,1,1,1,'2024-01-10')")
cursor.execute("INSERT or REPLACE INTO products_orders VALUES (2,2,3,2,'2025-09-15')")
cursor.execute("INSERT or REPLACE INTO products_orders VALUES (3,3,2,3,'2023-11-23')")
cursor.execute("INSERT or REPLACE INTO products_orders VALUES (4,1,3,1,'2024-07-01')")

conn.commit()
conn.close()

n_threads = multiprocessing.cpu_count()

llm = Llama(
    model_path="models/mistral-7b-v0.1.Q4_K_M.gguf",
    n_threads=n_threads,
    n_ctx=4096,#4096 funciona bien
    verbose=False
)
def generar_sql(pregunta):

    prompt = f"""
### Instruction:
Write just a SQL query to answer the following question.

### Question:
{pregunta}

### Schema:
customers(customer_id, name, address, age)
products(product_id, name, price)
products_orders(order_id, customer_id, product_id, quantity, order_date)

### Response:
"""

    output = llm(
        prompt,
        max_tokens=256,
        temperature=0,
        stop=["###"]
    )

    sql = output["choices"][0]["text"].strip()
    sql = sql.replace("SQL:", "").replace("```sql","").replace("```","")

    return sql.strip()

import json

dataset = []

with open("data/PruebasIniciales/prueba-ejemplo-uno.jsonl", "r", encoding="utf-8") as f:
    for line in f:
        dataset.append(json.loads(line))


exact_match = 0
execution_correct = 0
execution_error = 0
total = len(dataset)

conn = sqlite3.connect("src/bd-prueba-inicial.db")
cursor = conn.cursor()
print(len(dataset))
for row in dataset:

    pregunta = row["question"]
    sql_gold = row["sql"]

    sql_modelo = generar_sql(pregunta)

    print("\nPregunta:", pregunta)
    print("SQL modelo:", sql_modelo)
    print("SQL gold:", sql_gold)

    # EXACT MATCH
    if sql_modelo.lower().strip() == sql_gold.lower().strip():
        exact_match += 1

    try:

        res_gold = cursor.execute(sql_gold).fetchall()
        res_model = cursor.execute(sql_modelo).fetchall()

        if res_gold == res_model:
            execution_correct += 1

    except Exception as e:
        execution_error += 1
        print("Error ejecución:", e)


conn.close()
print("\n----- RESULTADOS -----")

print("Total preguntas:", total)

print("Exact Match:", exact_match / total)

print("Execution Accuracy:", execution_correct / total)

print("Error Rate:", execution_error / total)