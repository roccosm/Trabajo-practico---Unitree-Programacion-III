import json

def cargar_mapa(archivo):
    with open(archivo, "r", encoding="utf-8") as archivo_json:
        datos = json.load(archivo_json)

    nombre = datos["nombre"]
    matriz = datos["grilla"]
    inicio = tuple(datos["inicio"])
    destino = tuple(datos["destino"])
    tamano_celda = datos["tamano_celda_metros"]
    orientacion_inicial = datos["orientacion_inicial"]
    limitePasos = datos["maximo_pasos"]

    return nombre, matriz, inicio, destino, tamano_celda, orientacion_inicial, limitePasos

def distancia_manhattan(fila, columna, fila_destino, columna_destino):
    return abs(fila - fila_destino) + abs(columna - columna_destino)

def obtener_candidatos(fila, columna):
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

    for i in range(len(distancias)):
        if distancias[i] == min(distancias):
            mejor = candidatos[i]
            break

    return mejor

def factibilidad (fila_actual, columna_actual, matriz, visitados):

    filas = len(matriz)
    columnas = len(matriz[0])

    if fila_actual < 0 or fila_actual >= filas: #Fuera de la grilla por filas
        return False
    elif columna_actual < 0 or columna_actual >= columnas: #Fuera de la grilla por columnas
        return False
    elif matriz[fila_actual][columna_actual] == 1: #Celda obstaculo
        return False
    elif matriz[fila_actual][columna_actual] == 2: #Celda prohibida
        return False
    elif (fila_actual, columna_actual) in visitados: #Fue visitada
        return False
    else:
        return True

def solucion(fila_actual, columna_actual, fila_destino, columna_destino, pasos, limitePasos,matriz, visitados):
    if fila_actual == fila_destino and columna_actual == columna_destino:
        print("Se ha llegado al destino")
        return True

    candidatos = obtener_candidatos(fila_actual, columna_actual)
    candidatos_factibles = []

    for candidato in candidatos:
        if factibilidad(candidato[1], candidato[2], matriz, visitados):
            candidatos_factibles.append(candidato)

    if len(candidatos_factibles) == 0:
        print("El robot quedó bloqueado")
        return True

    elif pasos >= limitePasos:
        print("Se alcanzó el límite de pasos")
        return True
    
    else:
        return False

#-------------------------------------------
"""
Anotaciones:
- Usar set para reducir complejidad temporal de factibilidad
- Ver orientación de los movimientos
- Agregar lectura de JSON
- Traducir la ruta a instrucciones físicas
- Tener en cuenta orientación inicial
- Tener en cuenta tamaño de celda
- Mostrar resultado final
- Mostrar cantidad de movimientos
- Probar con los 3 mapas
- Generar representación de la ruta
- Guardar logs/capturas
"""

nombre, matriz, inicio, destino, tamano_celda, orientacion_inicial, limitePasos = cargar_mapa("mapa1.json")
    
fila_actual, columna_actual = inicio
fila_destino, columna_destino = destino
ruta = [inicio]
visitados = {inicio}
pasos = 0

while not solucion(fila_actual, columna_actual, fila_destino, columna_destino, pasos, limitePasos, matriz):
    pasos += 1
    candidatos = obtener_candidatos(fila_actual, columna_actual)
    
    candidatos_factibles = []
    for candidato in candidatos:
        if factibilidad(candidato[1], candidato[2], matriz, visitados):
            candidatos_factibles.append(candidato)

    mejor_candidato = seleccionar(candidatos_factibles, fila_destino, columna_destino)

    fila_actual, columna_actual = mejor_candidato[1], mejor_candidato[2]
    ruta.append((fila_actual, columna_actual))
    visitados.add((fila_actual, columna_actual))
