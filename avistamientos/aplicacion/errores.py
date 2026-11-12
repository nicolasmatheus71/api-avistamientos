"""Errores de la aplicación. No saben nada de HTTP: cada adaptador decide cómo mostrarlos."""


class AvistamientoNoEncontrado(Exception):
    """El avistamiento pedido no existe."""

    def __init__(self, avistamiento_id):
        super().__init__(f"No existe el avistamiento {avistamiento_id}")
        self.avistamiento_id = avistamiento_id


class DatosInvalidos(Exception):
    """Los datos no cumplen la regla de negocio. Trae los errores por campo."""

    def __init__(self, errores):
        super().__init__("Datos inválidos")
        self.errores = errores