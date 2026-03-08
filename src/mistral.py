# ===============================
# Imports
# ===============================

from llama_cpp import Llama


from llama_cpp import Llama
import multiprocessing

n_threads = multiprocessing.cpu_count()

llm = Llama(
    model_path="models/mistral-7b-v0.1.Q4_K_M.gguf",
    n_threads=n_threads,
    n_ctx=4096,#4096 funciona bien
    verbose=False
)
prompt = """
### Instruction:
Write just a SQL query to answer the following question.

### Question:
¿Cuál es el cliente que ha gastado más dinero en total y cuánto ha gastado?

### Schema:
CREATE TABLE customers (
   customer_id INTEGER PRIMARY KEY, -- Unique ID for each customer
   name VARCHAR(50), -- Name of the customer
   address VARCHAR(100), -- Mailing address of the customer
    age INTEGER -- Age of the customer
);
CREATE TABLE products (
    product_id INTEGER PRIMARY KEY, -- Unique ID for each product
    name VARCHAR(50), -- Name of the product
    price DECIMAL(10, 2) -- Price of the product
);
CREATE TABLE products_orders (
    order_id INTEGER PRIMARY KEY, -- Unique ID for each order
    customer_id INTEGER, -- ID of the customer who placed the order
    product_id INTEGER, -- ID of the product ordered
    quantity INTEGER, -- Quantity of the product ordered
    order_date DATE -- Date when the order was placed
    FOREIGN KEY (customer_id) REFERENCES customers(customer_id),
    FOREIGN KEY (product_id) REFERENCES products(product_id)
)
### Response:
"""

output = llm(
    prompt,
    max_tokens=256,
    temperature=0.1,
    stop=["###"]
)

print(output["choices"][0]["text"])
