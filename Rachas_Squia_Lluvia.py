# el presente codigo busca las rachas de dias tanto lluviosos como secos
# ademas les da clasificacion en intencidad y ubicacion de estacion lluviosa o seca de Costa Rica


import pandas as pd
#import matplotlib.pyplot as plt
#import seaborn as sns
#import tkinter as tk
#from tkinter import scrolledtext =>cantidad de texto grande mejor usar terminal
#from scipy.stats import ks_2samp
import numpy as np

# usar fechas como date no str
#se recomienda el uso de los escenarios aprobados por KS

ruta_csv = r"C:\Users\User\Downloads\Archivo_CSV_Original.csv" #ORIGINAL
#ruta_csv = r"C:\Users\User\Downloads\Archivo_CSV_Escenario_X.csv" #ESCENARIO

# escenarios elegidos segun KS son el 1 - 2 - 4

"""
<= 0.2 mm  => dia seco (trazas IMN)
0.2 - 5.0  => lluvia baja
5.0 - 20.0 => lluvia normal; > 20.0      => lluvia alta
1  - 5  dias => sequedad baja
6  - 15 dias => sequedad normal; > 15 dias    => sequedad alta
"""

#-----------Clasificacion de precipitaciones
seco = 0.2
lluvia_bajo = 5.0
lluvia_normal = 20.0 #=>>>> mayor a este numero es luvia fuerte IMN
seco_bajo = 5
seco_normal = 15
#est_seca =>>>revisar no definido

#------------------Estaciones en CR
MESES_SECA = [12, 1, 2, 3, 4]  # diciembre, enero, febrero, marzao, abril
def clasificar_estacion(mes):
    return "Seca" if mes in MESES_SECA else "Lluviosa"

#---------clasificacion de dias
def clasificar_dia(mm):
    if mm <= seco: return "Seco"
    elif mm <= lluvia_bajo: return "Lluvia_Baja"
    elif mm <= lluvia_normal: return "Lluvia_Normal"
    else: return "Lluvia_Alta"

#-----------clasificacion de sequia
def clasificar_sequia(dias):
    if dias <= seco_bajo: return "Sequedad_Baja"
    elif dias <= seco_normal: return "Sequedad_Normal"
    else: return "Sequedad_Alta"

#df_hist = pd.read_csv(ruta_hist, parse_dates=["Fecha"])
#df_sim = pd.read_csv(ruta_sim, parse_dates=["Fecha"])
df = pd.read_csv(ruta_csv, parse_dates=["Fecha"])
df = df.sort_values("Fecha").reset_index(drop=True)
df["Estacion"]  = df["Fecha"].dt.month.apply(clasificar_estacion)
df["Categoria"] = df["Precipitacion"].apply(clasificar_dia)

"""
# buscar columna de precipitacion
if "Precipitacion" in df.columns: #verificacion de existencia de columna
    data = df["Precipitacion"].dropna() #dropna elimina espacios vacios
#segun el IMN el minio de lectura es de 0.1 a 0.2mm de agua <= verificar
else:
    columnas_numericas = df.select_dtypes(include=np.number).columns
    #                          ^^^^ solo columnas con valores numericos => columns retorna nombres
    if len(columnas_numericas) == 0:
        raise ValueError("No hay columnas numericas en el archivo CSV")
    #   ^ detiene todo si no encuentra nada
    data = df[columnas_numericas[0]].dropna()
    # ^ usar primera con datos
"""

#--------------extraccion rachas
def extraer_rachas(df):
    rachas = []
        #lluvia_simulada = [] #  definicion de matrices como en elementos
    cat_actual = df["Categoria"].iloc[0]
    inicio = df["Fecha"].iloc[0]
    contador = 1

    for i in range(1, len(df)): #for i in range()
        #fila = df
        fila = df.iloc[i]
        if fila["Categoria"] == cat_actual:
            contador += 1
        else:
            rachas.append((         # aezare
                inicio.date(),
                df["Fecha"].iloc[i - 1].date(),
                contador,
                cat_actual,
                clasificar_estacion(inicio.month)
            ))
            cat_actual = fila["Categoria"]
            inicio     = fila["Fecha"]
            contador   = 1

    rachas.append((
        inicio.date(),
        df["Fecha"].iloc[-1].date(),
        contador,
        cat_actual,
        clasificar_estacion(inicio.month)
    ))
    return rachas

#columnas =["Inicio", "Fin", "Dias"]
cols = ["Fecha_Inicio", "Fecha_Fin", "Duracion_dias", "Categoria", "Estacion"]
df_r = pd.DataFrame(extraer_rachas(df), columns=cols)
df_secos = df_r[df_r["Categoria"] == "Seco"].copy()
#df_secos = df_r[df_r["Categoria"] == "sequia"
df_secos["Tipo_Sequia"] = df_secos["Duracion_dias"].apply(clasificar_sequia) # => ver documentacion

#----imprimir rachas
def imprimir_racha(df_sub, etiqueta):
    if len(df_sub) == 0:
        print(f"\n  {etiqueta}: sin registros.")
        return
    #max_r = df_sub.loc[df_sub["cant_dias"].max()] =>>corregir index
    max_r = df_sub.loc[df_sub["Duracion_dias"].idxmax()]
    min_r = df_sub.loc[df_sub["Duracion_dias"].idxmin()]
    prom = df_sub["Duracion_dias"].mean()
    top3 = df_sub.sort_values("Duracion_dias", ascending=False).head(3)

    print(f"\n  {etiqueta}  ({len(df_sub)} rachas)")
    print(f"  {'─'*55}")
    print(f"  Maxima  : {max_r['Duracion_dias']:>3} dias | {max_r['Fecha_Inicio']} => {max_r['Fecha_Fin']} | {max_r['Estacion']}")
    print(f"  Minima  : {min_r['Duracion_dias']:>3} dias | {min_r['Fecha_Inicio']} => {min_r['Fecha_Fin']} | {min_r['Estacion']}")
    print(f"  Promedio: {prom:.1f} dias") # ordenar mas para mejor visualizacion
    print(f"  Lista de 3 mas largas:")
    for _, r in top3.iterrows():
        print(f"    {str(r['Fecha_Inicio']):<14} => {str(r['Fecha_Fin']):<14} | {r['Duracion_dias']:>3} dias | {r['Estacion']}")
"""
    print( {etiqueta}  ({len(df_sub))")
    print(f"  {'─'*55}")
    print(f"  Max  : {max_r['Duracion_dias']:>3} dias | {max_r['Fecha_Inicio']} ") versionn 1 =
  Ordenar mejor, hay errores de concatenacion
    print(f"  Min  : {min_r['Duracion_dias']:>3} dias | {min_r['Fecha_Inicio']} ")
    print(f"  Prom: {prom:.1f} dias")
    print(f"  Lista de 3 mas largas:") =>hacerlo
"""

#imprimr resultados
total = len(df)
est_seca = df[df["Estacion"] == "Seca"]
est_lluvia = df[df["Estacion"] == "Lluviosa"]
conteo = df["Categoria"].value_counts()

#print("============ Rachas y Estaciones =============") # => se ve muy feo mas orden

print("\n=======================================================")
print("  Analisis Rachas y Eestaciones — Precipitacion ")
print("=======================================================")
print(f"  Archivo  : {ruta_csv.split(chr(92))[-1]}")
print(f"  Periodo  : {df['Fecha'].min().date()} => {df['Fecha'].max().date()}")
print(f"  Total    : {total} dias")

#orednar mas
print("\n─────────────────────────────────────────────────────")
print("  Estaciones climaticas de CR en CSV ")
print("─────────────────────────────────────────────────────")
print(f"  Seca     (dic-abr) : {len(est_seca):>5} dias  ({len(est_seca)/total*100:.1f}%)")
print(f"  Lluviosa (may-nov) : {len(est_lluvia):>5} dias  ({len(est_lluvia)/total*100:.1f}%)")
#print(f"  Lluviosa (may-nov) : {len(lluvia):>5} dias  ({len(est_lluvia)/total*100:.1f}%)") # cambiar lluvia por est_lluvia =>usar .1f un unico decimal
print(f"  Precip. media Seca     : {est_seca['Precipitacion'].mean():.2f} mm/dia")
print(f"  Precip. media Lluviosa : {est_lluvia['Precipitacion'].mean():.2f} mm/dia")

print("\n─────────────────────────────────────────────────────")
print(f"  Clasificacion de Dias")
print("─────────────────────────────────────────────────────")
print(f"  Secos         (<= {seco} mm) : {conteo.get('Seco',0):>5} dias  ({conteo.get('Seco',0)/total*100:.1f}%)")
print(f"  Lluvia Baja   ({seco}-{lluvia_bajo} mm)  : {conteo.get('Lluvia_Baja',0):>5} dias  ({conteo.get('Lluvia_Baja',0)/total*100:.1f}%)")
#print(f"  Lluvia Baja   ({umbral_seco}-{llu} mm)  : {conteo.get('Lluvia_Baja',0):>5} dias  ({conteo.get('Lluvia_Baja',0)/total*100:.1f}%)") # error no definido
print(f"  Lluvia Normal ({lluvia_bajo}-{lluvia_normal} mm) : {conteo.get('Lluvia_Normal',0):>5} dias  ({conteo.get('Lluvia_Normal',0)/total*100:.1f}%)")
#print(f"  Lluvia Normal ({U mm) : {c:>5} dias  ({)") # revisar los nombres hay un enredo
print(f"  Lluvia Alta   (> {lluvia_normal} mm)  : {conteo.get('Lluvia_Alta',0):>5} dias  ({conteo.get('Lluvia_Alta',0)/total*100:.1f}%)")

print("\n=======================================================")
print("  Rachas de lluvias consecutivas ")
print("=======================================================")
imprimir_racha(df_r[df_r["Categoria"] == "Lluvia_Baja"],   "LLUVIA BAJA   ( 0.2 a  5.0 mm/dia)")
imprimir_racha(df_r[df_r["Categoria"] == "Lluvia_Normal"], "LLUVIA NORMAL ( 5.0 a 20.0 mm/dia)")
#   imprimir_racha(df_r[df_r["cat"] == "Lluvia_Normal"], "LLUVIA NORMAL ( 5.0 - 20.0 usar dimensiones mas profesionales
imprimir_racha(df_r[df_r["Categoria"] == "Lluvia_Alta"],   "LLUVIA ALTA   (> 20.0 mm/dia)")

#posible mejora sacar CSV en lugar de imprimir en terminal
print("\n=======================================================")
print("  Dias secos consecutivos o sequia )")
print("=======================================================")
print(f"  Baja   : 1  a  {seco_bajo}  dias")
print(f"  Normal : {seco_bajo+1}  a {seco_normal}  dias")
print(f"  Alta   : > {seco_normal} dias")
imprimir_racha(df_secos[df_secos["Tipo_Sequia"] == "Sequedad_Baja"],   "SEQUEDAD BAJA   ( 1 a  5 dias)")
#       imprimir_racha(df_r[df_r["Cate"] == "Lluvia_Normal"], "LLUVIA NORMAL ( 5.0 - 20.0 #  
imprimir_racha(df_secos[df_secos["Tipo_Sequia"] == "Sequedad_Normal"], "SEQUEDAD NORMAL ( 6 a 15 dias)")
imprimir_racha(df_secos[df_secos["Tipo_Sequia"] == "Sequedad_Alta"],   "SEQUEDAD ALTA   (> 15 dias)")

print("\n================== Fin Script =================\n")

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