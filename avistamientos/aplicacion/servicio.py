from avistamientos.aplicacion.errores import AvistamientoNoEncontrado, DatosInvalidos
from avistamientos.aplicacion.puertos import (
    PuertoDeAvistamientos,
    Reloj,
    RepositorioDeAvistamientos,
)
from avistamientos.aplicacion.validador import ValidadorDeAvistamiento

CAMPOS = ("especie", "lugar", "fecha", "observador")


class ServicioDeAvistamientos(PuertoDeAvistamientos):
    """Implementa el puerto primario: lo que se puede hacer con los avistamientos.

    Recibe los puertos secundarios (repositorio y reloj) por el constructor. No
    sabe si detrás hay SQLite, una lista en memoria, Flask o una prueba.
    """

    def __init__(self, repositorio: RepositorioDeAvistamientos, reloj: Reloj):
        self._repositorio = repositorio
        self._validador = ValidadorDeAvistamiento(reloj)

    def listar(self):
        return self._repositorio.listar()

    def obtener(self, avistamiento_id):
        avistamiento = self._repositorio.obtener(avistamiento_id)
        if avistamiento is None:
            raise AvistamientoNoEncontrado(avistamiento_id)
        return avistamiento

    def registrar(self, datos):
        limpios = self._validar_y_limpiar(datos)
        return self._repositorio.crear(limpios)

    def actualizar(self, avistamiento_id, datos):
        self.obtener(avistamiento_id)  # primero 404 si no existe, luego 400 si no es válido
        limpios = self._validar_y_limpiar(datos)
        return self._repositorio.actualizar(avistamiento_id, limpios)

    def eliminar(self, avistamiento_id):
        if not self._repositorio.eliminar(avistamiento_id):
            raise AvistamientoNoEncontrado(avistamiento_id)

    def resumen_por_especie(self):
        return self._repositorio.resumen_por_especie()

    def _validar_y_limpiar(self, datos):
        errores = self._validador.validar(datos)
        if errores:
            raise DatosInvalidos(errores)
        return {campo: datos[campo].strip() for campo in CAMPOS}