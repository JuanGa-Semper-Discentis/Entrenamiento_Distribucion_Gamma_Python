#el presente recibe dos CSV para la ocmparativa y prueba de KS
#   ^^^^  Prueba de Kolmogorov-Smirnov, prueba de bondad
#                    ^^^^  se uso esta debido al enfoque hidrologico

import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import tkinter as tk
from tkinter import scrolledtext
from scipy.stats import ks_2samp
import numpy as np

#import tkinter as tk
#from tkinter import scrolledtext
#from scipy.stats import ks_2samp
#                        ^ https://docs.scipy.org/doc/scipy/reference/generated/scipy.stats.ks_2samp.html
#import numpy as np

#==============================================
#carga de datos y ruta de documentos

#DEFINICION DE RUTA =>>>se debe ser preciso =>>> buscar en archivos en windows o en terminal en LINUX
ruta_hist = r"C:\Users\User\Downloads\Archivo_CSV_Original.csv" #ORIGINAL
ruta_sim = r"C:\Users\User\Downloads\Archivo_CSV_Escenario_X.csv" #ESCENARIO

df_hist = pd.read_csv(ruta_hist, parse_dates=["Fecha"])
df_sim = pd.read_csv(ruta_sim, parse_dates=["Fecha"])

df_hist = df_hist.sort_values("Fecha")
df_sim = df_sim.sort_values("Fecha")

# ================================================
#Funcion de estadisticas similar a las de modelos

#def calculo_estadisticas
def calcular_estadisticas(df):

    media = df["Precipitacion"].mean()
    std = df["Precipitacion"].std()
    p10 = df["Precipitacion"].quantile(0.10) # percentiles recomendados en esta aplicaicon son de 10 y 90 %
    p90 = df["Precipitacion"].quantile(0.90)

    # prob de sequia maxima
    seco = df["Precipitacion"] == 0
    max_sequia = 0
    contador = 0
    #for i in clientes:
    for s in seco:
        if s:
            contador += 1
            max_sequia = max(max_sequia, contador)
        else:
            contador = 0

    return media, std, p10, p90, max_sequia

# ============================================
# calculo de metricas

#media_h, std_h, p25_h, p75_h, seq_h = calc_esta(df_hist)
media_h, std_h, p10_h, p90_h, seq_h = calcular_estadisticas(df_hist)
media_s, std_s, p10_s, p90_s, seq_s = calcular_estadisticas(df_sim)
#                                     ^ definicion de las diferencias porcentuales siguiendo funcion cal_estad
def diff_pct(a, b):
    if a == 0:
        return float('nan')  # estaba dividiendo por cero
    return abs(a-b)/a*100 

diff_media = diff_pct(media_h, media_s)
diff_std = diff_pct(std_h, std_s)
diff_p10 = diff_pct(p10_h, p10_s)
diff_p90 = diff_pct(p90_h, p90_s)

# =====================================
#prueba de Kolmogorov-Smirnov para comparacion de Historicos vs Simulados
###FALTA DOCUMENTAR a fecha de hoy 18/02/26 no encuentro el libro en que se vio esto
#       Definicion de hipotesis:
#           Hipotesis Nula H0 = historicos y generados son la misma distribucion
#           Hipotesis Alternativa H1 = las dis distribuciones son diferentes
#           Estandar en ingenieria de 0.05 => asegura una confianza de 95% => implica no ser tann estricto en variabilidad climatica
#               Mas estrico alfa = 0.10, menos estrico 0.01.

#https://www.mdpi.com/journal/water
#https://www.itl.nist.gov/div898/handbook/eda/section3/eda35g.htm


ks_stat, ks_pvalue = ks_2samp( #de libreria scipy funcion ks_2amp para comparar dos series segun KS
    df_hist["Precipitacion"],
    df_sim["Precipitacion"]
)

# =====================================
# definiicon de exportacion en la validacion
"""
validacion = pd.DataFrame({
    "Métrica":   ["Media", "Desviacion",  "P10", "P90", "Sequia maxima"],
    "Histórico": [media_h,  std_h,         p10_h, p90_h, seq_h],
    "Simulado":  [media_s,  std_s, p10_s, p90_s, seq_s],
    "Dif %":     [diff_media, diff_std, diff_p10, diff_p90, abs(seq_h-seq_s)] error grave => reahcer los escenarios
}) """ # =>>>>> ya se reviso no hay cambio se dejan los escenarios

validacion = pd.DataFrame({
    "Métrica":   ["Media", "Desviacion",  "P10", "P90", "Sequia maxima"],
    "Histórico": [media_h,  std_h,         p10_h, p90_h, seq_h],
    "Simulado":  [media_s,  std_s, p10_s, p90_s, seq_s],
    "Dif %":     [diff_media, diff_std, diff_p10 if not pd.isna(diff_p10) else "N/A (P10=0)", diff_p90, abs(seq_h-seq_s)]
})                                                              # ^ coreccion debido a la division por cero, problema del CSV original

#validacion.to_csv("validacion_modelo.csv", index=False)

# ========================================
# definicion de grafico comparativo
# para la comparacion de distribuciones se deben usar densidades de probalidad y normalizaicon
#uso de superposicion de curvas en kde

plt.figure()
#sns.histplot(df_hist["Precipitacion"], color="blue", label="Historico", kde=True, stat="Func. Densidad o Probalidad") # => origen de error en version 2
#sns.histplot(df_sim["Precipitacion"], color="red", label="Simulado", kde=True, stat="Func. Densidad o Probalidad")
sns.histplot(df_hist["Precipitacion"], color="blue", label="Historico", kde=True)
sns.histplot(df_sim["Precipitacion"], color="red", label="Simulado", kde=True)

plt.legend()
plt.title("Comparacion Hist. vs Simu.")
plt.show()

# ========================================
# def conclusion automatizada

if ks_pvalue > 0.05: #original = 0.05, segun fuentes se debe dejar en este valor
    conclusion = "No se rechaza la hipotesis de igualdad de distribucion (modelo valido)."
else:
    conclusion = "Se rechaza la hipotesis de igualdad (modelo requiere ajuste)."

# =====================================
# tkinter de ventana y resultados

texto_resultado = f"""
VALIDACION_MODELO_ESTOCASTICO

Media_historica: {media_h:.2f}
Media_simulada: {media_s:.2f}
Diferencia: {diff_media:.2f} %

Desviacion_historica: {std_h:.2f}
Desviacion_simulada: {std_s:.2f}
Diferencia: {diff_std:.2f} %

Percentil_10_diferencia: {diff_p10:.2f} %
Percentil_90_diferencia: {diff_p90:.2f} %

Sequia_historica: {seq_h} días
Sequia_simulada: {seq_s} días

Prueba_Kolmogorov-Smirnov_(K-S):
Estadistico_KS: {ks_stat:.4f}
p-value: {ks_pvalue:.4f}

Conclusion:
{conclusion}
"""

ventana = tk.Tk()
ventana.title("Validacion_Modelo")

area_texto = scrolledtext.ScrolledText(ventana, width=85, height=25)
area_texto.pack()
area_texto.insert(tk.END, texto_resultado)
area_texto.configure(state='disabled')

ventana.mainloop()

"""
df.head(5)          # primeras 5 filas
df.tail(5)          # ultimas 5 filas
df.shape            # (filas, columnas) => (2465, 2)
df.columns          # nombres de columnas
df.columns.tolist() # columnas como lista
df.dtypes           # tipo de dato de cada columna
df.info()           # resumen completo
df.describe()       # estadisticas basicas de columnas numericas
"""

"""
Autor: Juan Gabriel Perez Acuña

Fuentes y documentacion:
pandas      :   https://pandas.pydata.org/docs/
numpy       :   https://numpy.org/doc/
scipy       :   https://docs.scipy.org/doc/scipy/
matplotlib  :   https://matplotlib.org/stable/index.html
seaborn     :   https://seaborn.pydata.org/
tkinter     :   https://docs.python.org/3/library/tkinter.html
calendar    :   https://docs.python.org/3/library/calendar.html
datetime    :   https://docs.python.org/3/library/datetime.html
os          :   https://docs.python.org/3/library/os.html

"""