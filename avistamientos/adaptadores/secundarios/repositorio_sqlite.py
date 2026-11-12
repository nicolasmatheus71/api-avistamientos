import sqlite3
from contextlib import contextmanager

from avistamientos.aplicacion.puertos import RepositorioDeAvistamientos

COLUMNAS = "id, especie, lugar, fecha, observador"


class RepositorioSqlite(RepositorioDeAvistamientos):
    """Adaptador del puerto RepositorioDeAvistamientos que guarda en SQLite.

    Solo necesita la ruta del archivo. No usa Flask: abre una conexión por
    operación y la cierra al terminar.
    """

    def __init__(self, ruta):
        self._ruta = ruta

    @contextmanager
    def _conexion(self):
        conexion = sqlite3.connect(self._ruta)
        conexion.row_factory = sqlite3.Row
        try:
            yield conexion
            conexion.commit()
        finally:
            conexion.close()

    def crear_tabla(self):
        """Crea la tabla avistamientos si no existe."""
        with self._conexion() as db:
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

    def listar(self):
        with self._conexion() as db:
            filas = db.execute(
                f"SELECT {COLUMNAS} FROM avistamientos ORDER BY id"
            ).fetchall()
        return [dict(fila) for fila in filas]

    def obtener(self, avistamiento_id):
        with self._conexion() as db:
            fila = db.execute(
                f"SELECT {COLUMNAS} FROM avistamientos WHERE id = ?",
                (avistamiento_id,),
            ).fetchone()
        return dict(fila) if fila else None

    def crear(self, datos):
        with self._conexion() as db:
            cursor = db.execute(
                "INSERT INTO avistamientos (especie, lugar, fecha, observador) "
                "VALUES (?, ?, ?, ?)",
                (datos["especie"], datos["lugar"], datos["fecha"], datos["observador"]),
            )
            nuevo_id = cursor.lastrowid
        return self.obtener(nuevo_id)

    def actualizar(self, avistamiento_id, datos):
        with self._conexion() as db:
            cursor = db.execute(
                "UPDATE avistamientos SET especie = ?, lugar = ?, fecha = ?, observador = ? "
                "WHERE id = ?",
                (
                    datos["especie"],
                    datos["lugar"],
                    datos["fecha"],
                    datos["observador"],
                    avistamiento_id,
                ),
            )
            cambiadas = cursor.rowcount
        if cambiadas == 0:
            return None
        return self.obtener(avistamiento_id)

    def eliminar(self, avistamiento_id):
        with self._conexion() as db:
            cursor = db.execute(
                "DELETE FROM avistamientos WHERE id = ?", (avistamiento_id,)
            )
            return cursor.rowcount > 0

    def resumen_por_especie(self):
        with self._conexion() as db:
            filas = db.execute(
                "SELECT especie, COUNT(*) AS cantidad FROM avistamientos "
                "GROUP BY especie ORDER BY cantidad DESC, especie"
            ).fetchall()
        return [dict(fila) for fila in filas]