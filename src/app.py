from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
import pandas as pd
import sqlite3
import matplotlib.pyplot as plt
import seaborn as sns

# Driver
chrome_options = webdriver.ChromeOptions()
driver = webdriver.Chrome(
    service=Service(ChromeDriverManager().install()),
    options=chrome_options
)

#NOTA !!!
# TENGO TANTAS COSAS INSTALADAS QUE NO SE PORQUE NO FUNCIONA EL CODIGO EN EL REPOSITORIO.
#Gracias por su comprensión

URL = "https://companies-market-cap-copy.vercel.app/index.html"
driver.get(URL)

# Esperar la tabla
WebDriverWait(driver, 30).until(
    EC.presence_of_element_located((By.TAG_NAME, "table"))
)

# Obtener el HTML 
html = driver.page_source

# HTML a bs4
soup = BeautifulSoup(html, 'html.parser')

# Tabla con los datos 
tabla = soup.find_all("table", limit=1)[0]

# Extraer las filas
filas = tabla.find_all('tr')

# Lista para almacenar datos
datos_Tesla = []

# Iterar y extraer datos
for fila in filas[1:]:  # Saltar la 1 fila que contiene  encabezados
    celdas = fila.find_all("td")
    
    # Verificar si hay datos
    if len(celdas) > 1:
        # Extraer los datos de cada celda (solo Fecha e Ingresos)
        fecha = celdas[0].text.strip()
        ingresos = celdas[1].text.strip()
        
        # append los datos 
        datos_Tesla.append([fecha, ingresos])

# Cerrar navegador
driver.quit()


print("Datos extraídos:")
for dato in datos_Tesla:
    print(dato)  




df = pd.DataFrame(datos_Tesla, columns=["Fecha", "Ingresos"])

print("\nDataFrame original:")
print(df)

# Eliminar $ y B
df["Ingresos"] = df["Ingresos"].str.replace("$", "").str.replace("B", "")

# Convertir ingresos a numérico, forzar errores a NaN
df["Ingresos"] = pd.to_numeric(df["Ingresos"], errors='coerce')

# Eliminar filas NaN en la ingresos
df = df.dropna(subset=["Ingresos"])

# Ordenar por fecha
df = df.sort_values('Fecha')


print("\nDataFrame final limpio")
print(df)

# Inserción en SQLite

# Conectar a la base de datos (o crearla si no existe)
conexion = sqlite3.connect("tesla_data.db")
cursor = conexion.cursor()

# Crear la tabla si no existe
cursor.execute("""
CREATE TABLE IF NOT EXISTS tesla_finanzas (
    Fecha TEXT PRIMARY KEY,
    Ingresos REAL
)
""")

# Insertar los datos del DataFrame en la tabla
df.to_sql("tesla_finanzas", conexion, if_exists="replace", index=False)

# Guardar los cambios y cerrar la conexión
conexion.commit()
conexion.close()

print("Datos insertados correctamente en la base de datos SQLite.")

# Configurar estilo
sns.set(style="whitegrid")

# Gráfico de líneas: Tendencias de Ingresos a lo largo del tiempo
plt.figure(figsize=(10, 6))
plt.plot(df["Fecha"], df["Ingresos"], marker="o", label="Ingresos")
plt.title("Tendencias de Ingresos de Tesla")
plt.xlabel("Fecha")
plt.ylabel("Ingresos (en billones)")
plt.legend()
plt.show()

# Gráfico de barras: Comparación de Ingresos por año
plt.figure(figsize=(10, 6))
sns.barplot(x="Fecha", y="Ingresos", data=df, color="blue")
plt.title("Comparación de Ingresos de Tesla por Año")
plt.xlabel("Fecha")
plt.ylabel("Ingresos (en billones)")
plt.xticks(rotation=45)
plt.show()

# Gráfico de dispersión: Relación entre Fecha e Ingresos
plt.figure(figsize=(10, 6))
sns.scatterplot(x="Fecha", y="Ingresos", data=df, s=100)
plt.title("Relación entre Fecha e Ingresos de Tesla")
plt.xlabel("Fecha")
plt.ylabel("Ingresos (en billones)")
plt.show()