from datetime import date

from avistamientos.aplicacion.puertos import Reloj


class RelojSistema(Reloj):
    """Adaptador del puerto Reloj: entrega la fecha de hoy según el computador."""

    def hoy(self):
        return date.today()