# API REST de avistamientos de aves

Trabajo de Ingeniería de Software 2

API REST para registrar avistamientos de aves. Permite crear, consultar, actualizar y eliminar avistamientos. Los datos se guardan en una base de datos SQLite y la API recibe y responde en JSON.

Autor: Nicolas Esteban Matheus

## Tecnologías

- Python 3.10 o superior
- Flask (framework web)
- SQLite, con el módulo `sqlite3` que ya trae Python
- pytest (pruebas)

## Requisitos

- Python 3.10 o superior
- Git
- curl (ya viene en Windows 10/11, macOS y Linux)

## Instalación y ejecución

1. Clonar el repositorio:

```
git clone https://github.com/nicolasmatheus71/api-avistamientos.git
cd api-avistamientos
```

2. Crear y activar el entorno virtual.

Windows (PowerShell):

```
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

Si PowerShell dice que la ejecución de scripts está deshabilitada, ejecutar esto y volver a activar:

```
Set-ExecutionPolicy -Scope Process RemoteSigned
```

Linux o macOS:

```
python3 -m venv .venv
source .venv/bin/activate
```

3. Instalar las dependencias:

```
pip install -r requirements.txt
```

4. Ejecutar la API:

```
python app.py
```

La API queda disponible en `http://127.0.0.1:5000`. La base de datos (`avistamientos.db`) se crea sola la primera vez que se ejecuta.

Si el puerto 5000 está ocupado (en macOS suele usarlo AirPlay), se puede usar otro puerto con la variable `PORT`:

- Windows (PowerShell): `$env:PORT=5001; python app.py`
- Linux o macOS: `PORT=5001 python app.py`

## Recurso: avistamiento

| Campo | Tipo | Descripción |
|---|---|---|
| id | número | Lo asigna el sistema |
| especie | texto | Nombre de la especie, por ejemplo "colibrí" |
| lugar | texto | Dónde se observó |
| fecha | texto | Formato AAAA-MM-DD |
| observador | texto | Quién lo registró |

Todos los campos (menos el `id`) son obligatorios y no pueden estar vacíos.

## Endpoints

| Acción | Petición | Respuesta |
|---|---|---|
| Listar todos | GET /avistamientos | 200 con la lista |
| Ver uno | GET /avistamientos/{id} | 200, o 404 si no existe |
| Registrar | POST /avistamientos | 201 con el avistamiento creado, o 400 si faltan datos |
| Actualizar | PUT /avistamientos/{id} | 200, 404 si no existe, o 400 si faltan datos |
| Eliminar | DELETE /avistamientos/{id} | 204 sin contenido, o 404 si no existe |
| Resumen por especie | GET /avistamientos/resumen | 200 con la cantidad por especie |

## Ejemplos con curl

Los ejemplos usan los archivos JSON de la carpeta `ejemplos/`. Se deben ejecutar desde la raíz del proyecto, con la API corriendo en otra terminal. En Windows PowerShell hay que escribir `curl.exe` en lugar de `curl`.

Se recomienda seguirlos en orden, porque el primero crea el avistamiento con id 1.

### Registrar un avistamiento (POST)

```
curl -i -X POST http://127.0.0.1:5000/avistamientos -H "Content-Type: application/json" -d @ejemplos/nuevo.json
```

Respuesta: `201 Created`

```json
{"especie":"colibrí","fecha":"2026-10-04","id":1,"lugar":"Bogotá","observador":"Laura"}
```

### Listar todos (GET)

```
curl -i http://127.0.0.1:5000/avistamientos
```

Respuesta: `200 OK`

```json
[{"especie":"colibrí","fecha":"2026-10-04","id":1,"lugar":"Bogotá","observador":"Laura"}]
```

### Ver uno (GET)

```
curl -i http://127.0.0.1:5000/avistamientos/1
```

Respuesta: `200 OK` con el avistamiento. Si el id no existe, responde `404 Not Found`:

```json
{"error":"Avistamiento no encontrado"}
```

### Actualizar (PUT)

```
curl -i -X PUT http://127.0.0.1:5000/avistamientos/1 -H "Content-Type: application/json" -d @ejemplos/actualizado.json
```

Respuesta: `200 OK`

```json
{"especie":"águila","fecha":"2026-10-05","id":1,"lugar":"Chingaza","observador":"Laura"}
```

### Resumen por especie (opcional)

```
curl -i http://127.0.0.1:5000/avistamientos/resumen
```

Respuesta: `200 OK`

```json
[{"cantidad":1,"especie":"águila"}]
```

### Eliminar (DELETE)

```
curl -i -X DELETE http://127.0.0.1:5000/avistamientos/1
```

Respuesta: `204 No Content` (sin cuerpo). Si el id no existe, responde `404 Not Found`.

### Ejemplo de error 400

```
curl -i -X POST http://127.0.0.1:5000/avistamientos -H "Content-Type: application/json" -d @ejemplos/incompleto.json
```

Respuesta: `400 Bad Request`

```json
{"error":"Faltan datos o están vacíos: lugar, fecha, observador"}
```

## Códigos de estado

| Código | Cuándo se usa |
|---|---|
| 200 | La consulta o la actualización salió bien |
| 201 | El avistamiento se creó |
| 204 | El avistamiento se eliminó (no devuelve cuerpo) |
| 400 | Faltan datos, están vacíos, la fecha no cumple AAAA-MM-DD o el cuerpo no es un JSON válido |
| 404 | El avistamiento o la ruta no existe |
| 405 | El método HTTP no está permitido en esa ruta |

## Pruebas

El proyecto tiene 15 pruebas automáticas que cubren los endpoints y los códigos de estado. Usan una base de datos temporal, así que no afectan los datos reales. Con el entorno virtual activo:

```
pytest
```

## Estructura del proyecto

```
api-avistamientos/
├── app.py              # Rutas de la API y validaciones
├── database.py         # Conexión y consultas a SQLite
├── requirements.txt    # Dependencias
├── pytest.ini          # Configuración de pytest
├── ejemplos/           # JSON de ejemplo para los curl
└── tests/
    └── test_api.py     # Pruebas automáticas
```

## Decisiones de diseño

- PUT reemplaza el avistamiento completo, por eso exige todos los campos.
- DELETE responde 204 sin cuerpo.
- Las consultas SQL usan parámetros (`?`) para evitar inyección SQL.
- Las validaciones están en una sola función (`validar_datos`) que usan POST y PUT.
- Los errores también se devuelven en JSON.

## Uso de inteligencia artificial

Usé IA como apoyo para planear y escribir el código: Claude (Anthropic), modelo Sonnet 5.5. 
