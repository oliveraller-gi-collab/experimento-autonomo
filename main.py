# EXPERIMENTO BASE
# El agente irá mejorando este archivo iterativamente

def calcular_promedio(numeros):
    total = 0
    for n in numeros:
        total = total + n
    return total / len(numeros)

def calcular_maximo(numeros):
    maximo = numeros[0]
    for n in numeros:
        if n > maximo:
            maximo = n
    return maximo

if __name__ == "__main__":
    datos = [3, 7, 2, 9, 4, 6, 1, 8, 5]
    print(f"Datos: {datos}")
    print(f"Promedio: {calcular_promedio(datos)}")
    print(f"Maximo: {calcular_maximo(datos)}")
