from fastapi import APIRouter, Query, HTTPException
from app.database import probar_conexion, get_tables, get_columns
from sqlalchemy import create_engine, text
from sqlalchemy.exc import SQLAlchemyError
from app.utils import construir_grafo, encontrar_camino
from app.openai_client import generar_sql_desde_prompt

router = APIRouter()


@router.get("/")
def root():
    return {"message": "Funciona"}
@router.get("/probar-conexion")
def probar(db_url: str = Query(...)):
    if probar_conexion(db_url):
        return {"ok": True, "mensaje": "Conexión exitosa"}
    else:
        raise HTTPException(status_code=400, detail="No se pudo conectar a la base de datos")

@router.get("/tablas")
def listar_tablas(db_url: str = Query(...)):
    try:
        return {"tablas": get_tables(db_url)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# @router.get("/columnas")
# def listar_columnas(db_url: str = Query(...), tabla: str = Query(...)):
#     try:
#         return {"columnas": get_columns(db_url, tabla)}
#     except Exception as e:
#         raise HTTPException(status_code=500, detail=str(e))
@router.get("/columnas")
def listar_columnas(db_url: str = Query(...), tabla: str = Query(...)):
    try:
        columnas = get_columns(db_url, tabla)
        columnas_limpias = [{"name": col["name"], "type": str(col["type"])} for col in columnas]
        return {"columnas": columnas_limpias}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
@router.get("/consulta")
def consulta_simple(db_url: str, tabla: str, columna_x: str, columna_y: str):
    try:
        engine = create_engine(db_url)
        with engine.connect() as conn:
            query = text(f"""
                SELECT {columna_x} as x, SUM({columna_y}) as y
                FROM {tabla}
                GROUP BY {columna_x}
                ORDER BY {columna_x}
            """)
            result = conn.execute(query)
            return {"resultado": [dict(row) for row in result]}
    except SQLAlchemyError as e:
        raise HTTPException(status_code=500, detail=str(e))
@router.get("/relaciones")
def obtener_relaciones(db_url: str = Query(...)):
    try:
        query = text("""
            SELECT
              tc.table_name AS tabla_origen,
              kcu.column_name AS columna_origen,
              ccu.table_name AS tabla_referida,
              ccu.column_name AS columna_referida
            FROM
              information_schema.table_constraints AS tc
              JOIN information_schema.key_column_usage AS kcu
                ON tc.constraint_name = kcu.constraint_name
              JOIN information_schema.constraint_column_usage AS ccu
                ON ccu.constraint_name = tc.constraint_name
            WHERE
              constraint_type = 'FOREIGN KEY'
        """)

        engine = create_engine(db_url)
        with engine.connect() as conn:
            resultado = conn.execute(query)
            # relaciones = [dict(row) for row in resultado]
            relaciones = list(conn.execute(query).mappings())
            return {"relaciones": relaciones}

    except SQLAlchemyError as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/consulta-join")
def consulta_con_grafo(
    db_url: str,
    columna_x: str,
    columna_y: str
):
    tabla_x, campo_x = columna_x.split(".")
    tabla_y, campo_y = columna_y.split(".")

    # Paso 1: obtener relaciones reales
    query = text("""
        SELECT
          tc.table_name AS tabla_origen,
          kcu.column_name AS columna_origen,
          ccu.table_name AS tabla_referida,
          ccu.column_name AS columna_referida
        FROM information_schema.table_constraints tc
        JOIN information_schema.key_column_usage kcu
          ON tc.constraint_name = kcu.constraint_name
        JOIN information_schema.constraint_column_usage ccu
          ON ccu.constraint_name = tc.constraint_name
        WHERE constraint_type = 'FOREIGN KEY'
    """)

    engine = create_engine(db_url)
    with engine.connect() as conn:
        # relaciones = [dict(row) for row in conn.execute(query)]
        relaciones = list(conn.execute(query).mappings())

    # Paso 2: construir grafo
    grafo = construir_grafo(relaciones)

    # Paso 3: encontrar camino de joins
    camino = encontrar_camino(grafo, tabla_y, tabla_x)
    if not camino:
        raise HTTPException(status_code=400, detail="No hay camino entre las tablas seleccionadas")

    # Paso 4: armar FROM + JOINs
    joins = ""
    tabla_base = tabla_y
    for rel in camino:
        t1 = rel["tabla_origen"]
        c1 = rel["columna_origen"]
        t2 = rel["tabla_referida"]
        c2 = rel["columna_referida"]

        if tabla_base == t1:
            joins += f" JOIN {t2} ON {t1}.{c1} = {t2}.{c2}"
            tabla_base = t2
        else:
            joins += f" JOIN {t1} ON {t2}.{c2} = {t1}.{c1}"
            tabla_base = t1

    # Paso 5: ejecutar consulta final
    sql = text(f"""
        SELECT {columna_x} AS x, SUM({columna_y}) AS y
        FROM {tabla_y}
        {joins}
        GROUP BY {columna_x}
        ORDER BY {columna_x}
    """)

    with engine.connect() as conn:
        resultado = conn.execute(sql)
        return list(resultado.mappings())

@router.get("/generar-consulta")
def generar_consulta(db_url: str = Query(...), pregunta: str = Query(...)):
    try:
        engine = create_engine(db_url)

        with engine.connect() as conn:
            columnas = conn.execute(text("""
                SELECT table_name, column_name, data_type 
                FROM information_schema.columns 
                WHERE table_schema = 'public'
            """)).fetchall()

        # Armar esquema como texto
        esquema = {}
        for tabla, columna, tipo in columnas:
            if tabla not in esquema:
                esquema[tabla] = []
            esquema[tabla].append(f"{columna} ({tipo})")
        esquema_texto = "\n".join(f"{tabla}: {', '.join(cols)}" for tabla, cols in esquema.items())

        # Generar SQL usando OpenAI
        sql_generado = generar_sql_desde_prompt(pregunta, esquema_texto)

        # Ejecutar consulta generada
        with engine.connect() as conn:
            resultado = conn.execute(text(sql_generado))
            filas = list(resultado.mappings())
            columnas = resultado.keys() if filas else []
            return {
                "sql": sql_generado,
                "columnas": columnas,
                "datos": filas
            }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al generar o ejecutar la consulta: {str(e)}")
