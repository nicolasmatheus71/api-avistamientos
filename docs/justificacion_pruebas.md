# Justificación de las pruebas de la API de avistamientos

Ingeniería de Software 2, Sesión 22. Trabajo individual.

## 1. Qué cambió en el código

Antes, la validación estaba dentro de `app.py`, mezclada con las rutas de Flask. Para probarla había que levantar la API, y la fecha de hoy se tomaba directamente del reloj del sistema. Hice tres cambios:

- Extraje la validación a la clase `ValidadorDeAvistamiento` (archivo `validador.py`). Ahora recibe un diccionario y devuelve los errores por campo, sin depender de Flask ni de la base de datos. Por eso se puede probar como prueba unitaria, rápida y aislada.
- Envolví el reloj en la clase `RelojSistema` (archivo `reloj.py`), que tiene un único método `hoy()`. El validador recibe el reloj por el constructor, así que en las pruebas se puede reemplazar por un reloj fijo.
- `create_app` ahora recibe un reloj opcional y se lo pasa al validador. Las rutas ya no validan: llaman al validador y, si hay errores, responden 400 con el nombre de cada campo que falló.

Con esto la API es más fácil de probar, porque la lógica de negocio quedó separada del framework y la fecha de hoy se puede controlar.

## 2. Tabla de casos de la Parte A

Regla de negocio: la especie tiene entre 3 y 50 caracteres (después de quitar los espacios de los extremos). La fecha tiene formato AAAA-MM-DD y no es posterior a hoy. El lugar y el observador no pueden estar vacíos.

En todos los casos de fecha, el reloj fijo marca el 15 de junio de 2026 (2026-06-15), así que las pruebas dan el mismo resultado cualquier día.

### Especie

Particiones: válida (de 3 a 50), muy corta (menos de 3, incluida la vacía) y muy larga (más de 50).

| Valor | Tipo de caso | Resultado esperado | Por qué este valor |
|---|---|---|---|
| "colibrí" (7) | Representativo | Válida | Un valor normal de la partición válida |
| "ab" (2) | Límite (justo debajo del mínimo) | Error en especie | Es el último valor inválido por abajo |
| "abc" (3) | Límite (mínimo) | Válida | Es el primer valor válido |
| 50 letras "a" | Límite (máximo) | Válida | Es el último valor válido |
| 51 letras "a" | Límite (justo encima del máximo) | Error en especie | Es el primer valor inválido por arriba |
| "" (vacía) | Inválido | Error: es obligatoria | Representa la partición de "sin dato" |
| "  ab  " | Límite con espacios | Error en especie | Con espacios mide 6, pero sin ellos mide 2: comprueba que se quitan los espacios antes de contar |

### Fecha

Particiones: válida (hoy o antes), futura, con formato incorrecto, imposible en el calendario y vacía.

| Valor | Tipo de caso | Resultado esperado | Por qué este valor |
|---|---|---|---|
| "2026-06-14" (ayer) | Representativo | Válida | Un valor normal del pasado |
| "2026-06-15" (hoy) | Límite (máximo permitido) | Válida | Es la última fecha válida |
| "2026-06-16" (mañana) | Límite (justo después de hoy) | Error: no puede ser posterior a hoy | Es la primera fecha inválida por arriba |
| "15/06/2026" | Inválido | Error: formato AAAA-MM-DD | Fecha real, pero con el formato equivocado |
| "2026-02-30" | Inválido | Error: no es una fecha válida | Tiene el formato correcto, pero ese día no existe |
| "" (vacía) | Inválido | Error: es obligatoria | Representa la partición de "sin dato" |

### Lugar, observador y cuerpo

| Valor | Tipo de caso | Resultado esperado | Por qué este valor |
|---|---|---|---|
| lugar "Chingaza" | Representativo | Válido | Un valor normal |
| lugar "   " (solo espacios) | Inválido | Error en lugar | Parece tener texto, pero está vacío |
| observador "" | Inválido | Error en observador | Es la misma regla, aplicada a otro campo |
| El cuerpo es una lista y no un objeto | Inválido | Error en cuerpo | Comprueba que el validador no se rompe con un JSON de otro tipo |

## 3. Por qué cada nivel

(Pendiente)

## 4. Los dobles

(Pendiente)

## 5. Lo que no probé

(Pendiente)

## 6. Lectura de la cobertura

(Pendiente)