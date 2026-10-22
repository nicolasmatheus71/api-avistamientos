from datetime import date


class RelojSistema:
    """Entrega la fecha de hoy según el reloj del computador."""

    def hoy(self):
        return date.today()