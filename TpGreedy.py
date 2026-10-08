import json
from g1_student_api import RobotG1
#Funciones greedy

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

def factibilidad(fila, columna, matriz, visitados):
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
    elif (fila, columna) in visitados:            # Ya visitada
        return False
    else:
        return True

def seleccionar(candidatos, fila_destino, columna_destino):
    mejor = candidatos[0]
    menor_distancia = distancia_manhattan(
        mejor[1],
        mejor[2],
        fila_destino,
        columna_destino
    )

    for candidato in candidatos:
        distancia = distancia_manhattan(
            candidato[1],
            candidato[2],
            fila_destino,
            columna_destino
        )

        if distancia < menor_distancia:
            mejor = candidato
            menor_distancia = distancia

    return mejor

#Funciones principales

def planificar_ruta(matriz, inicio, destino, limite_pasos):
    fila_actual, columna_actual = inicio
    fila_destino, columna_destino = destino

    ruta = [inicio]
    visitados = {inicio}
    pasos = 0

    while pasos < limite_pasos:
        if (fila_actual, columna_actual) == destino:
            return ruta, "DESTINO_ALCANZADO", pasos

        candidatos = obtener_candidatos(fila_actual, columna_actual)

        candidatos_factibles = []
        for candidato in candidatos:
            if factibilidad(candidato[1], candidato[2], matriz, visitados):
                candidatos_factibles.append(candidato)

        if len(candidatos_factibles) == 0:
            return ruta, "BLOQUEADO", pasos

        mejor_candidato = seleccionar(
            candidatos_factibles,
            fila_destino,
            columna_destino
        )

        fila_actual = mejor_candidato[1]
        columna_actual = mejor_candidato[2]

        ruta.append((fila_actual, columna_actual))
        visitados.add((fila_actual, columna_actual))
        pasos += 1

    return ruta, "LIMITE_DE_PASOS", pasos

def cargar_mapa(nombre_archivo):
    with open(nombre_archivo, "r", encoding="utf-8") as archivo:
        datos = json.load(archivo)

    matriz = datos["grilla"]
    inicio = tuple(datos["inicio"])
    destino = tuple(datos["destino"])
    tamano_celda = datos["tamano_celda_metros"]
    orientacion_inicial = datos["orientacion_inicial"]
    limite_pasos = datos["maximo_pasos"]

    return matriz, inicio, destino, tamano_celda, orientacion_inicial, limite_pasos

def obtener_direccion(actual, siguiente):

    if siguiente[0] < actual[0]: #Fila siguiente es menor que la actual, entonces se mueve hacia arriba
        return "NORTE"

    elif siguiente[1] > actual[1]: #Columna siguiente es mayor que la actual, entonces se mueve hacia la derecha
        return "ESTE"

    elif siguiente[0] > actual[0]: #Fila siguiente es mayor que la actual, entonces se mueve hacia abajo
        return "SUR"

    else:                          #Columna siguiente es menor que la actual, entonces se mueve hacia la izquierda
        return "OESTE"

def calcular_giro(orientacion_actual, orientacion_nueva):
    orientaciones = ["NORTE", "ESTE", "SUR", "OESTE"]

    actual = orientaciones.index(orientacion_actual)
    nueva = orientaciones.index(orientacion_nueva)

    diferencia = (nueva - actual) % 4

    if diferencia == 0:
        return "SIN_GIRO" #0°
    elif diferencia == 1:
        return "DERECHA" #90°
    elif diferencia == 2:
        return "MEDIA_VUELTA" #180°
    else:
        return "IZQUIERDA" #90°

def ejecutar_ruta(robot, ruta, orientacion_inicial, tamano_celda):
    orientacion_actual = orientacion_inicial

    for i in range(len(ruta) - 1):
        direccion = obtener_direccion(ruta[i], ruta[i + 1])

        giro = calcular_giro(orientacion_actual, direccion)

        if giro == "DERECHA":
            robot.movimiento(adelante=0.0, costado=0.0, giro=-0.5, tiempo=3.2)
            print("Girar a la derecha 90°")

        elif giro == "IZQUIERDA":
            robot.movimiento(adelante=0.0, costado=0.0, giro=0.5, tiempo=3.2)
            print("Girar a la izquierda 90°")
        elif giro == "MEDIA_VUELTA":
            robot.movimiento(adelante=0.0, costado=0.0, giro=0.5, tiempo=6.4)
            print("Girar 180°")

        orientacion_actual = direccion

        robot.movimiento(
            adelante=0.4,
            costado=0.0,
            giro=0.0,
            tiempo=1.25
        )
        print("Avanzar " + str(tamano_celda) + " m")

def generar_instrucciones(ruta, orientacion_inicial, tamano_celda):
    instrucciones = []
    orientacion_actual = orientacion_inicial
    n = 1

    for i in range(len(ruta) - 1):
        direccion = obtener_direccion(ruta[i], ruta[i + 1])
        giro = calcular_giro(orientacion_actual, direccion)

        if giro == "DERECHA":
            instrucciones.append(str(n) + ". GIRAR DERECHA 90°")
            n =+ 1

        elif giro == "IZQUIERDA":
            instrucciones.append(str(n) + ". GIRAR IZQUIERDA 90°")
            n =+ 1

        elif giro == "MEDIA_VUELTA":
            instrucciones.append(str(n) + ". GIRAR 180°")
            n =+ 1

        instrucciones.append(str(n) + ". AVANZAR " + str(tamano_celda) + " m")
        orientacion_actual = direccion
        n =+ 1

    return instrucciones

# Main
matriz, inicio, destino, tamano_celda, orientacion_inicial, limite_pasos = cargar_mapa("Mapa1.json")
ruta, estado, pasos = planificar_ruta(
    matriz,
    inicio,
    destino,
    limite_pasos
)

print("Ruta:", ruta)
print("Estado:", estado)
print("Cantidad de movimientos:", pasos)

instrucciones = generar_instrucciones(
    ruta,
    orientacion_inicial,
    tamano_celda
)

with open("instrucciones.txt", "w", encoding="utf-8") as archivo:
    for instruccion in instrucciones:
        archivo.write(instruccion + "\n")

robot = RobotG1()
robot.conectar()

if estado == "DESTINO_ALCANZADO":
    ejecutar_ruta(
        robot,
        ruta,
        orientacion_inicial,
        tamano_celda
    )

robot.detenerse()
robot.desconectar()