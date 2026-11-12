import re
from datetime import datetime

ESPECIE_MINIMO = 3
ESPECIE_MAXIMO = 50
FORMATO_FECHA = re.compile(r"[0-9]{4}-[0-9]{2}-[0-9]{2}")


class ValidadorDeAvistamiento:
    """Regla de negocio: valida los datos de un avistamiento.

    Vive dentro del hexágono, así que no importa Flask, SQLite ni el reloj del
    sistema. El reloj le llega desde afuera por el puerto Reloj.
    """

    def __init__(self, reloj):
        self.reloj = reloj

    def validar(self, datos):
        """Devuelve un diccionario {campo: mensaje}. Si está vacío, los datos son válidos."""
        if not isinstance(datos, dict):
            return {"cuerpo": "debe ser un objeto JSON válido"}

        errores = {}

        especie = self._texto(datos.get("especie"))
        if not especie:
            errores["especie"] = "es obligatoria"
        elif not ESPECIE_MINIMO <= len(especie) <= ESPECIE_MAXIMO:
            errores["especie"] = (
                f"debe tener entre {ESPECIE_MINIMO} y {ESPECIE_MAXIMO} caracteres"
            )

        for campo in ("lugar", "observador"):
            if not self._texto(datos.get(campo)):
                errores[campo] = "es obligatorio"

        mensaje_fecha = self._validar_fecha(self._texto(datos.get("fecha")))
        if mensaje_fecha:
            errores["fecha"] = mensaje_fecha

        return errores

    def _validar_fecha(self, fecha):
        if not fecha:
            return "es obligatoria"
        if not FORMATO_FECHA.fullmatch(fecha):
            return "debe tener el formato AAAA-MM-DD"
        try:
            fecha_real = datetime.strptime(fecha, "%Y-%m-%d").date()
        except ValueError:
            return "no es una fecha válida"
        if fecha_real > self.reloj.hoy():
            return "no puede ser posterior a hoy"
        return None

    @staticmethod
    def _texto(valor):
        return valor.strip() if isinstance(valor, str) else ""