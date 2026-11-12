"""Puertos del hexágono.

Un puerto es la interfaz de una conversación con el exterior. La aplicación los
define y los adaptadores los implementan, así que las dependencias van de afuera
hacia adentro.

- Puerto primario: lo que la aplicación ofrece a quien la usa (la API web, las pruebas).
- Puertos secundarios: lo que la aplicación necesita del exterior (guardar datos, saber la fecha).
"""

from abc import ABC, abstractmethod


# ---------- Puerto primario (lado de quien usa la aplicación) ----------


class PuertoDeAvistamientos(ABC):
    """Operaciones que la aplicación ofrece sobre los avistamientos."""

    @abstractmethod
    def listar(self):
        """Devuelve la lista de avistamientos."""

    @abstractmethod
    def obtener(self, avistamiento_id):
        """Devuelve un avistamiento o lanza AvistamientoNoEncontrado."""

    @abstractmethod
    def registrar(self, datos):
        """Valida y guarda un avistamiento nuevo. Lanza DatosInvalidos si no es válido."""

    @abstractmethod
    def actualizar(self, avistamiento_id, datos):
        """Reemplaza un avistamiento. Lanza AvistamientoNoEncontrado o DatosInvalidos."""

    @abstractmethod
    def eliminar(self, avistamiento_id):
        """Borra un avistamiento o lanza AvistamientoNoEncontrado."""

    @abstractmethod
    def resumen_por_especie(self):
        """Devuelve cuántos avistamientos hay de cada especie."""


# ---------- Puertos secundarios (lado de lo que la aplicación usa) ----------


class RepositorioDeAvistamientos(ABC):
    """Dónde se guardan los avistamientos. La aplicación no sabe si es SQLite u otra cosa."""

    @abstractmethod
    def listar(self):
        """Devuelve todos los avistamientos ordenados por id."""

    @abstractmethod
    def obtener(self, avistamiento_id):
        """Devuelve el avistamiento o None si no existe."""

    @abstractmethod
    def crear(self, datos):
        """Guarda un avistamiento nuevo y lo devuelve con su id."""

    @abstractmethod
    def actualizar(self, avistamiento_id, datos):
        """Reemplaza los datos y devuelve el avistamiento, o None si no existe."""

    @abstractmethod
    def eliminar(self, avistamiento_id):
        """Borra el avistamiento. Devuelve True si existía."""

    @abstractmethod
    def resumen_por_especie(self):
        """Devuelve [{"especie": ..., "cantidad": ...}] de mayor a menor cantidad."""


class Reloj(ABC):
    """De dónde sale la fecha de hoy."""

    @abstractmethod
    def hoy(self):
        """Devuelve la fecha de hoy (datetime.date)."""