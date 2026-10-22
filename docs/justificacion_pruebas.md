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

Usé dos niveles. El nivel unitario prueba una sola pieza, el validador, sin Flask ni base de datos. El nivel de integración prueba la API completa a través de HTTP, con la ruta, el validador y una base de datos SQLite temporal.

**`test_fecha_de_manana_es_invalida_por_ser_posterior_a_hoy` (unitaria).** Es unitaria porque la regla "no puede ser posterior a hoy" está toda dentro del validador. No necesita HTTP ni base de datos, y con el reloj fijo se puede probar el valor límite exacto (el día siguiente a hoy). Es muy rápida y, si falla, se sabe que el problema está en el validador.

**`test_registrar_guarda_el_avistamiento_y_se_puede_consultar_con_get` (integración).** Es de integración porque cruza varias fronteras: la petición HTTP, la ruta de Flask, el validador, la base de datos y la respuesta en JSON. Primero hace un POST y después un GET al id nuevo. Una prueba unitaria no puede comprobar que el avistamiento realmente se guardó ni que el id lo asignó la base de datos.

**`test_registrar_con_especie_de_2_caracteres_responde_400_y_no_guarda` (integración).** Aquí está la diferencia que pide el taller. La prueba unitaria del validador solo sabe que, con una especie de 2 caracteres, el validador devuelve un error. No puede detectar que la ruta se olvide de llamar al validador, o que lo llame y ignore el resultado, y en esos casos la API respondería 201 y guardaría un dato inválido. La prueba de integración sí lo detecta, porque revisa que el código de estado sea 400 y que no se guarde nada.

Como los casos límite ya están cubiertos a nivel unitario, en integración solo repetí un caso por cada comportamiento (por ejemplo, un solo caso de especie corta). Así evito pruebas duplicadas, más lentas y más difíciles de mantener.

## 4. Los dobles

Usé un doble: `RelojFijo`, que es un **stub**. Un stub solo devuelve respuestas fijas para controlar lo que entra a la pieza que se prueba. `RelojFijo.hoy()` siempre responde el 15 de junio de 2026. No es un mock, porque no verifico cuántas veces ni cómo se llamó al reloj. Tampoco es un fake, porque un fake tiene una implementación real simplificada (por ejemplo, un repositorio en memoria) y el reloj fijo no tiene ninguna lógica.

El reloj se inyecta por el constructor de `ValidadorDeAvistamiento` y por `create_app(reloj=...)`. Por eso el mismo stub sirve en las pruebas unitarias y en las de integración.

Sin el doble habría dos problemas. Si escribiera la fecha de mañana a mano ("2026-06-16"), la prueba pasaría hoy y fallaría cuando pase esa fecha, porque ya sería del pasado. Y si calculara "mañana" con `date.today()` dentro de la prueba, repetiría la misma lógica que quiero probar, y podría fallar justo a medianoche.

No usé un doble para la base de datos. En las pruebas de integración quiero comprobar que la API habla con SQLite de verdad, por eso cada prueba usa un archivo temporal propio (`tmp_path`), que da independencia sin necesidad de un doble. Además, el proyecto no tiene capa de servicio ni de repositorio, así que no había dónde poner un fake sin crear código extra solo para eso.

Hice además dos pruebas con el reloj real (sin stub), usando fechas del año 2000 y del 2999, que dan el mismo resultado cualquier día. Comprueban que, cuando no se pasa ningún reloj, la API usa de verdad el reloj del sistema.

## 5. Lo que no probé

1. **El arranque del servidor con `python app.py` y `create_app()` sin configuración.** La cobertura lo marca como la línea 90 y la rama 26->29 de `app.py`. No lo probé porque habría que levantar un servidor real y crear el archivo `avistamientos.db` del proyecto, y eso ensucia las pruebas y las hace menos independientes. Ya lo verifiqué a mano con los comandos curl del README. El costo es alto y el valor es bajo.
2. **La rama defensiva de `actualizar_avistamiento`.** Es el `return None` de la línea 71 de `database.py`, que se ejecuta si el UPDATE no cambia ninguna fila. Por la API no se puede llegar ahí, porque la ruta comprueba antes que el avistamiento existe y responde 404. Probarla obligaría a llamar a la función directamente. Decidí no hacerlo; si algún día la ruta deja de comprobar la existencia, entonces sí haría falta.
3. **Repetir en integración todos los casos límite de la especie y la fecha.** Ya están en las pruebas unitarias, que son más rápidas y precisas. Repetirlos por HTTP daría más pruebas pero no más información.

## 6. Lectura de la cobertura

Comando usado:

```
pytest --cov=app --cov=database --cov=validador --cov=reloj --cov-branch --cov-report=term-missing
```

Resultado final (38 pruebas pasan: 22 de integración y 16 unitarias):

```
Name           Stmts   Miss Branch BrPart  Cover   Missing
----------------------------------------------------------
app.py            64      1     14      2    96%   26->29, 90
database.py       41      1      6      1    96%   71
reloj.py           4      0      0      0   100%
validador.py      40      0     18      0   100%
----------------------------------------------------------
TOTAL            149      2     38      3    97%
```

Medí cobertura de sentencias y también de ramas (`--cov-branch`), para ver si cada `if` se probó por sus dos caminos.

En la primera medición, con 36 pruebas, `reloj.py` estaba en 75 %. La línea 8 (`return date.today()`) nunca se ejecutaba, porque todas las pruebas usaban el stub. Eso me mostró que probaba la lógica de la fecha, pero no la conexión con el reloj real. Escribí dos pruebas con el reloj real y `reloj.py` subió a 100 %.

Los huecos que quedan son los tres de la sección 5, y decidí que no vale la pena cubrirlos. `validador.py`, que es donde está la regla de negocio, quedó al 100 % de sentencias y de ramas.

Una cobertura alta no prueba que el código esté bien. Solo dice qué líneas se ejecutaron, no si las pruebas verifican algo. Por eso cada prueba tiene su `assert` sobre el comportamiento y no solo sobre el código de estado.