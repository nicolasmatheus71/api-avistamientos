import sqlite3

from flask import current_app, g


def get_db():
    """Devuelve la conexión a SQLite de la petición actual."""
    if "db" not in g:
        g.db = sqlite3.connect(current_app.config["DATABASE"])
        g.db.row_factory = sqlite3.Row
    return g.db


def close_db(error=None):
    """Cierra la conexión cuando termina la petición."""
    db = g.pop("db", None)
    if db is not None:
        db.close()


def init_db():
    """Crea la tabla avistamientos si no existe."""
    db = get_db()
    db.execute(
        """
        CREATE TABLE IF NOT EXISTS avistamientos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            especie TEXT NOT NULL,
            lugar TEXT NOT NULL,
            fecha TEXT NOT NULL,
            observador TEXT NOT NULL
        )
        """
    )
    db.commit()


def listar_avistamientos():
    filas = get_db().execute(
        "SELECT id, especie, lugar, fecha, observador FROM avistamientos ORDER BY id"
    ).fetchall()
    return [dict(fila) for fila in filas]


def obtener_avistamiento(avistamiento_id):
    fila = get_db().execute(
        "SELECT id, especie, lugar, fecha, observador FROM avistamientos WHERE id = ?",
        (avistamiento_id,),
    ).fetchone()
    return dict(fila) if fila else None


def crear_avistamiento(especie, lugar, fecha, observador):
    db = get_db()
    cursor = db.execute(
        "INSERT INTO avistamientos (especie, lugar, fecha, observador) VALUES (?, ?, ?, ?)",
        (especie, lugar, fecha, observador),
    )
    db.commit()
    return obtener_avistamiento(cursor.lastrowid)


def actualizar_avistamiento(avistamiento_id, especie, lugar, fecha, observador):
    db = get_db()
    cursor = db.execute(
        "UPDATE avistamientos SET especie = ?, lugar = ?, fecha = ?, observador = ? WHERE id = ?",
        (especie, lugar, fecha, observador, avistamiento_id),
    )
    db.commit()
    if cursor.rowcount == 0:
        return None
    return obtener_avistamiento(avistamiento_id)


def eliminar_avistamiento(avistamiento_id):
    db = get_db()
    cursor = db.execute("DELETE FROM avistamientos WHERE id = ?", (avistamiento_id,))
    db.commit()
    return cursor.rowcount > 0


def resumen_por_especie():
    filas = get_db().execute(
        "SELECT especie, COUNT(*) AS cantidad FROM avistamientos "
        "GROUP BY especie ORDER BY cantidad DESC, especie"
    ).fetchall()
    return [dict(fila) for fila in filas]