from collections import deque, defaultdict

def construir_grafo(relaciones):
    grafo = defaultdict(list)

    for r in relaciones:
        t1 = r["tabla_origen"]
        t2 = r["tabla_referida"]
        grafo[t1].append((t2, r))
        grafo[t2].append((t1, r))  # bidireccional para BFS

    return grafo

def encontrar_camino(grafo, origen, destino):
    visitado = set()
    cola = deque([(origen, [])])

    while cola:
        actual, ruta = cola.popleft()
        if actual == destino:
            return ruta  # secuencia de relaciones

        if actual in visitado:
            continue
        visitado.add(actual)

        for vecino, relacion in grafo[actual]:
            if vecino not in visitado:
                cola.append((vecino, ruta + [relacion]))

    return None  # no hay camino
