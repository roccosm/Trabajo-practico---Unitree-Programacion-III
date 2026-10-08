"""
TP 03 - Programacion III - Planificador de rutas con estrategia Greedy
Robot Unitree

Estrategia (esquema de la catedra, Unidad 3):
  - Candidatos:   las 4 celdas vecinas (ARRIBA, DERECHA, ABAJO, IZQUIERDA)
  - Factibilidad: dentro de la grilla, no obstaculo, no zona prohibida, no visitada
  - Seleccion:    menor distancia Manhattan al destino
                  (desempate: ARRIBA -> DERECHA -> ABAJO -> IZQUIERDA)
  - Solucion:     la ultima celda de la ruta es el destino
  - Objetivo:     minimizar la cantidad de movimientos

Uso:
    python tp_greedy_apellido.py
(los archivos mapa1.json, mapa2.json y mapa3.json deben estar en la misma carpeta)
"""

import json
import os


# ------------------------------------------------------------
# LECTURA DEL MAPA
# ------------------------------------------------------------
def cargar_mapa(nombre_archivo):
    archivo = open(nombre_archivo, encoding="utf-8")
    datos = json.load(archivo)
    archivo.close()

    # 1. Que esten todas las claves
    claves = ["grilla", "inicio", "destino", "tamano_celda_metros",
              "orientacion_inicial", "maximo_pasos"]
    for clave in claves:
        if clave not in datos:
            raise ValueError("Falta la clave: " + clave)

    grilla = datos["grilla"]
    inicio = tuple(datos["inicio"])
    destino = tuple(datos["destino"])
    tamano_celda = datos["tamano_celda_metros"]
    orientacion = datos["orientacion_inicial"]
    maximo_pasos = datos["maximo_pasos"]

    # 2. Que la grilla sea valida
    if len(grilla) == 0:
        raise ValueError("La grilla esta vacia")
    for fila in grilla:
        if len(fila) != len(grilla[0]):
            raise ValueError("La grilla no es rectangular")
        for valor in fila:
            if valor != 0 and valor != 1 and valor != 2:
                raise ValueError("La grilla solo admite 0, 1 y 2")

    # 3. Que inicio y destino esten dentro de la grilla y en celda libre
    for nombre, posicion in [("inicio", inicio), ("destino", destino)]:
        fila = posicion[0]
        columna = posicion[1]
        if fila < 0 or fila >= len(grilla) or columna < 0 or columna >= len(grilla[0]):
            raise ValueError("El " + nombre + " esta fuera de la grilla")
        if grilla[fila][columna] != 0:
            raise ValueError("El " + nombre + " no esta en una celda libre")

    # 4. Que los metadatos sean validos
    if orientacion not in ["NORTE", "ESTE", "SUR", "OESTE"]:
        raise ValueError("Orientacion invalida: " + str(orientacion))
    if tamano_celda <= 0:
        raise ValueError("El tamano de celda debe ser mayor a 0")
    if maximo_pasos <= 0:
        raise ValueError("El maximo de pasos debe ser mayor a 0")

    mapa = {}
    mapa["nombre"] = datos.get("nombre", nombre_archivo)
    mapa["grilla"] = grilla
    mapa["inicio"] = inicio
    mapa["destino"] = destino
    mapa["tamano_celda"] = tamano_celda
    mapa["orientacion"] = orientacion
    mapa["maximo_pasos"] = maximo_pasos
    return mapa


# ------------------------------------------------------------
# FUNCIONES DEL GREEDY
# ------------------------------------------------------------
def distancia_manhattan(fila, columna, fila_destino, columna_destino):
    return abs(fila - fila_destino) + abs(columna - columna_destino)


def obtener_candidatos(fila, columna):
    # El orden de esta lista es el criterio de desempate
    candidatos = []
    candidatos.append(("ARRIBA",    fila - 1, columna))
    candidatos.append(("DERECHA",   fila,     columna + 1))
    candidatos.append(("ABAJO",     fila + 1, columna))
    candidatos.append(("IZQUIERDA", fila,     columna - 1))
    return candidatos


def seleccionar(candidatos, fila_destino, columna_destino):
    distancias = []
    for candidato in candidatos:
        distancia = distancia_manhattan(candidato[1], candidato[2], fila_destino, columna_destino)
        distancias.append(distancia)

    # Se devuelve el PRIMER candidato con la menor distancia (desempate)
    menor = min(distancias)
    for i in range(len(distancias)):
        if distancias[i] == menor:
            return candidatos[i]


def factibilidad(fila, columna, matriz, ruta):
    filas = len(matriz)
    columnas = len(matriz[0])

    if fila < 0 or fila >= filas:            # Fuera de la grilla por filas
        return False
    elif columna < 0 or columna >= columnas: # Fuera de la grilla por columnas
        return False
    elif matriz[fila][columna] == 1:         # Obstaculo
        return False
    elif matriz[fila][columna] == 2:         # Zona prohibida
        return False
    elif (fila, columna) in ruta:            # Ya visitada
        return False
    else:
        return True


def solucion(ruta, fila_destino, columna_destino):
    ultima = ruta[-1]
    if ultima[0] == fila_destino and ultima[1] == columna_destino:
        return True
    else:
        return False


def funcion_objetivo(ruta):
    return len(ruta) - 1


def planificar(matriz, inicio, destino, limite_pasos):
    fila_destino, columna_destino = destino
    ruta = [inicio]
    estado = "EN_CURSO"

    while estado == "EN_CURSO":
        fila_actual, columna_actual = ruta[-1]

        if solucion(ruta, fila_destino, columna_destino):
            estado = "DESTINO_ALCANZADO"
        elif funcion_objetivo(ruta) >= limite_pasos:
            estado = "LIMITE_DE_PASOS"
        else:
            candidatos = obtener_candidatos(fila_actual, columna_actual)

            factibles = []
            for candidato in candidatos:
                if factibilidad(candidato[1], candidato[2], matriz, ruta):
                    factibles.append(candidato)

            if len(factibles) == 0:
                estado = "BLOQUEADO"
            else:
                mejor = seleccionar(factibles, fila_destino, columna_destino)
                ruta.append((mejor[1], mejor[2]))

    return ruta, estado


# ------------------------------------------------------------
# RESULTADO Y CAUSA
# ------------------------------------------------------------
def obtener_causa(estado, ruta, destino, limite_pasos):
    if estado == "DESTINO_ALCANZADO":
        return "El robot llego a la celda destino " + str(destino) + "."
    elif estado == "BLOQUEADO":
        return ("No existen candidatos validos para continuar desde " + str(ruta[-1]) +
                ": todos los vecinos son borde, obstaculo, zona prohibida o ya visitados.")
    else:
        return "Se alcanzo el maximo de " + str(limite_pasos) + " pasos permitido."


# ------------------------------------------------------------
# TRADUCCION A INSTRUCCIONES PARA EL ROBOT
# ------------------------------------------------------------
def obtener_orientacion(celda_actual, celda_siguiente):
    if celda_siguiente[0] < celda_actual[0]:
        return "NORTE"
    elif celda_siguiente[1] > celda_actual[1]:
        return "ESTE"
    elif celda_siguiente[0] > celda_actual[0]:
        return "SUR"
    else:
        return "OESTE"


def calcular_giro(orientacion_actual, orientacion_nueva):
    orientaciones = ["NORTE", "ESTE", "SUR", "OESTE"]
    numero_actual = orientaciones.index(orientacion_actual)
    numero_nuevo = orientaciones.index(orientacion_nueva)
    diferencia = (numero_nuevo - numero_actual) % 4

    if diferencia == 0:
        return None
    elif diferencia == 1:
        return "GIRAR DERECHA 90°"
    elif diferencia == 3:
        return "GIRAR IZQUIERDA 90°"
    else:
        return "GIRAR 180°"


def traducir_ruta(ruta, orientacion_inicial, tamano_celda):
    instrucciones = []
    orientacion_actual = orientacion_inicial
    metros = ("%.2f" % tamano_celda).replace(".", ",")

    for i in range(len(ruta) - 1):
        orientacion_nueva = obtener_orientacion(ruta[i], ruta[i + 1])
        giro = calcular_giro(orientacion_actual, orientacion_nueva)

        if giro != None:
            instrucciones.append(giro)
            orientacion_actual = orientacion_nueva

        instrucciones.append("AVANZAR " + metros + " m")

    return instrucciones


# ------------------------------------------------------------
# REPRESENTACION TEXTUAL DE LA RUTA
# ------------------------------------------------------------
def dibujar_ruta(mapa, ruta):
    grilla = mapa["grilla"]
    simbolos = {0: ".", 1: "#", 2: "X"}
    flechas = {"NORTE": "^", "ESTE": ">", "SUR": "v", "OESTE": "<"}

    tablero = []
    for fila in grilla:
        tablero.append([simbolos[valor] for valor in fila])

    # Flecha en cada celda recorrida, hacia donde salio el robot
    for i in range(len(ruta) - 1):
        direccion = obtener_orientacion(ruta[i], ruta[i + 1])
        tablero[ruta[i][0]][ruta[i][1]] = flechas[direccion]

    # Si no llego al destino, se marca donde se detuvo
    if ruta[-1] != mapa["destino"]:
        tablero[ruta[-1][0]][ruta[-1][1]] = "*"

    tablero[mapa["inicio"][0]][mapa["inicio"][1]] = "I"
    tablero[mapa["destino"][0]][mapa["destino"][1]] = "D"

    lineas = []
    encabezado = "    "
    for c in range(len(grilla[0])):
        encabezado = encabezado + str(c) + " "
    lineas.append(encabezado)
    for f in range(len(tablero)):
        lineas.append(" " + str(f) + "  " + " ".join(tablero[f]))
    return lineas


# ------------------------------------------------------------
# PROGRAMA PRINCIPAL
# ------------------------------------------------------------
def ejecutar_mapa(nombre_archivo):
    mapa = cargar_mapa(nombre_archivo)
    ruta, estado = planificar(mapa["grilla"], mapa["inicio"], mapa["destino"], mapa["maximo_pasos"])
    causa = obtener_causa(estado, ruta, mapa["destino"], mapa["maximo_pasos"])
    instrucciones = traducir_ruta(ruta, mapa["orientacion"], mapa["tamano_celda"])

    lineas = []
    lineas.append("=" * 60)
    lineas.append(mapa["nombre"] + "  (" + os.path.basename(nombre_archivo) + ")")
    lineas.append("=" * 60)
    lineas.append("Inicio: " + str(mapa["inicio"]) + " | Destino: " + str(mapa["destino"]) +
                  " | Celda: " + str(mapa["tamano_celda"]) + " m | Orientacion inicial: " +
                  mapa["orientacion"] + " | Maximo de pasos: " + str(mapa["maximo_pasos"]))
    lineas.append("")
    lineas.append("Estado: " + estado)
    lineas.append("Causa: " + causa)
    lineas.append("Movimientos: " + str(funcion_objetivo(ruta)))
    lineas.append("Ruta: " + " -> ".join(["(" + str(c[0]) + "," + str(c[1]) + ")" for c in ruta]))
    lineas.append("")
    lineas.append("Representacion de la ruta (I inicio, D destino, # obstaculo, X prohibida,")
    lineas.append("^ > v < recorrido, * punto donde se detuvo):")
    lineas.extend(dibujar_ruta(mapa, ruta))
    lineas.append("")
    lineas.append("Instrucciones para el robot:")
    for numero in range(len(instrucciones)):
        lineas.append("  " + str(numero + 1) + ". " + instrucciones[numero])
    if estado != "DESTINO_ALCANZADO":
        lineas.append("")
        lineas.append("NOTA: la ruta es parcial, no llega al destino.")
    lineas.append("")
    return lineas


def main():
    carpeta = os.path.dirname(os.path.abspath(__file__))
    archivos = ["mapa1.json", "mapa2.json", "mapa3.json"]

    texto = []
    for archivo in archivos:
        try:
            texto.extend(ejecutar_mapa(os.path.join(carpeta, archivo)))
        except (OSError, ValueError) as error:
            texto.append("[ERROR] " + archivo + ": " + str(error))
            texto.append("")

    salida = "\n".join(texto)
    print(salida)

    # Se guarda el log de las tres ejecuciones
    log = open(os.path.join(carpeta, "log_ejecucion.txt"), "w", encoding="utf-8")
    log.write(salida)
    log.close()


if __name__ == "__main__":
    main()