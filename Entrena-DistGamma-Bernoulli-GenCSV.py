#el presente recibe un archivo CSV, entrena una distribucion Gamma
# y genera un CSV a partir del Random de dias lluviosos o no lluviosos
# es buena practica tener un CSV con el nombre de la salida para evitar posibles errores

import pandas as pd
import numpy as np
from scipy.stats import gamma #estadisticas basadas en numpy, solo he usado matlab
from datetime import timedelta #se podria usar timestamp para pandas =>fecha inteligente

#DEFINICION DE RUTA =>>>se debe ser preciso =>>> buscar en archivos en windows o en terminal en LINUX
ruta_csv_entrada = r"C:\Users\User\Downloads\Archivo_CSV_Original.csv" #ORIGINAL
ruta_csv_salida = r"C:\Users\User\Downloads\Archivo_CSV_Escenario_X.csv" #ESCENARIO


# ===============================
#carga de datos historicas
def cargar_datos(ruta_csv_entrada):
    df = pd.read_csv(ruta_csv_entrada, parse_dates=["Fecha"])
    df = df.sort_values("Fecha")
    return df


# ===============================
#Ajuste con Dist Gamma Thom
#DOCUMENTOS EN CARPETA

""" version 1
def ajustar_gamma_thom(precipitaciones): #distribucion gamma thom
    #filtra solo dias con lluvia (>0)
    lluvia = precipitaciones[precipitaciones > 0] #correcion de valor pasa de 0 a 0.2, error en K-S

    media = np.mean(lluvia) #original = lluvia
    var = np.var(lluvia) #original = lluvia # el otro script pide correcion del modelo =>error

    #parametriozacion con momentos
    alpha = (media ** 2) / var
    beta = var / media

    return alpha, beta
"""

def ajustar_gamma_thom(precipitaciones): # entrenamiento de cuanto llueve al llover
    # solo dias con lluvia REAL (excluye seco 0.0 y traza 0.2 del IMN)
    lluvia = precipitaciones[precipitaciones > 0.2]  # ← corregido
    media    = np.mean(lluvia)
    varianza = np.var(lluvia)
    alpha = (media ** 2) / varianza
    beta  = varianza / media
    return alpha, beta

# ===============================
#prob de dias lluviosos segun documentos
""" version 1
def probabilidad_lluvia(precipitaciones):
    #dias_lluvia = np.sum(precipitaciones > 0) #>>>>error en prueba KS corregir
    dias_lluvia = np.sum(precipitaciones > 0) # >>> no forzar resultados => actulaizcion 06/03/26 error en script de K-S
    total_dias = len(precipitaciones)
    return dias_lluvia / total_dias
"""

def probabilidad_lluvia(precipitaciones): # entrena con que frecuencia llueve
    # retorna los 3 estados separados
    p_seco = (precipitaciones == 0.0).mean()   # 34.2%
    p_traza = (precipitaciones == 0.2).mean()   # 18.5%
    p_lluvia = (precipitaciones  > 0.2).mean()   # 47.4%
    return p_seco, p_traza, p_lluvia

# ===============================
#generacion de serie simulada
""" version 1
def generar_lluvia_simu(alpha, beta, p_lluvia, fecha_inicio, anos=8): # las fechas pivotean de un lado a otro mejor usar misma cantidad de dias y mismas fechas para evitar pivoteo
    
    dias_totales = anos * 365
    fechas = [fecha_inicio + timedelta(days=i) for i in range(dias_totales)]

    lluvia_simu = []

    for _ in range(dias_totales):
        if np.random.rand() < p_lluvia:
            valor = gamma.rvs(alpha, scale=beta)
        else:
            valor = 0.0
        lluvia_simu.append(round(valor, 2))

    df_sim 
    = pd.DataFrame({
        "Fecha": fechas,
        "Precipitacion": lluvia_simu
    }

    return df_sim
    """

""" version 2
def generar_lluvia_simulada(alpha, beta, p_lluvia, fecha_inicio, fecha_fin):
    
    fechas = pd.date_range(start=fecha_inicio, end=fecha_fin, freq="D")
    dias_totales = len(fechas)

    lluvia_simulada = []

    for _ in range(dias_totales):
        if np.random.rand() < p_lluvia:
            valor = gamma.rvs(alpha, scale=beta)
        else:
            valor = 0.0
        lluvia_simulada.append(round(valor, 2))

    df_sim = pd.DataFrame({
        "Fecha": fechas,
        "Precipitacion": lluvia_simulada
    })

    return df_sim
"""

def generar_lluvia_simulada(alpha, beta, p_seco, p_traza, p_lluvia, fecha_inicio, fecha_fin):
        #   ^ generacion de datos nuevos, misma cantidad que CSV original, 2465 dias nuevos
    fechas = pd.date_range(start=fecha_inicio, end=fecha_fin, freq="D") #   Correccion en fecha final
    dias_totales = len(fechas)

    lluvia_simulada = [] #  definicion de matrices como en elementos
    for _ in range(dias_totales):
        r = np.random.rand()
        if r < p_seco:
            valor = 0.0 # dia seco
        elif r < p_seco + p_traza:
            valor = 0.2  # dia de traza IMN
        else:
            valor = round(gamma.rvs(alpha, scale=beta), 2)  # lluvia real Gamma
        lluvia_simulada.append(valor) #     => agrega guarda

    return pd.DataFrame({"Fecha": fechas, "Precipitacion": lluvia_simulada}) #          Guarda CSV


# =====================================
#ejecucion del modelo version 2
def ejecutar_modelo(ruta_csv_entrada, ruta_csv_salida):
    
    df = cargar_datos(ruta_csv_entrada)
    alpha, beta = ajustar_gamma_thom(df["Precipitacion"])
    p_seco, p_traza, p_lluvia = probabilidad_lluvia(df["Precipitacion"])

    print("parametros Gamma:") #imprimir mejor en terminal
    print("alpha = ", round(alpha, 4))
    print("beta = ", round(beta, 4))
    print("p_seco = ", round(p_seco,   4), f"({p_seco*100:.1f}%)") # => mejor dejarlo en un decimal = .1f
    print("p_traza = ", round(p_traza,  4), f"({p_traza*100:.1f}%)")
    print("p_lluvia = ", round(p_lluvia, 4), f"({p_lluvia*100:.1f}%)")

    fecha_inicio = pd.Timestamp("2026-01-01")
    fecha_fin = pd.Timestamp("2032-09-30")

    df_simulado = generar_lluvia_simulada(alpha, beta, p_seco, p_traza, p_lluvia, fecha_inicio, fecha_fin)
    df_simulado.to_csv(ruta_csv_salida, index=False)
    print("Archivo generado correctamente.")

# ====================================
# ejecucion del script
if __name__ == "__main__":
    ejecutar_modelo(ruta_csv_entrada, ruta_csv_salida) #=>forma de forzar la ejecucion del script

#NOTA: el error de verificacion de K-S viene debido a los estados que maneja el IMNN
# estado seco = 0.0 mm
# estado traza = 0.2 mm
# estado de lluvia real que es mayor a 0.2 mm


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