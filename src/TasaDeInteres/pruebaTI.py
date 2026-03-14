import sqlite3
import pandas as pd

conn = sqlite3.connect("C:/Users/isaac/Downloads/proyecto_tesis/src/TasaDeInteres/mi_base.db")

query = """
SELECT e.nombre_entidad, d.sexo, SUM(c.monto_desembolsado) FROM Credito c JOIN Entidades e ON c.id_entidad = e.id_entidad JOIN Deudor d ON c.id_deudor = d.id_deudor GROUP BY e.nombre_entidad, d.sexo;
"""

df = pd.read_sql(query, conn)
print(df)

conn.close()