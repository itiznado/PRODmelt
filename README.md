# API de Producción de Insumos (ES3)

API RESTful construida con Django REST Framework sobre el proyecto de la Evaluación 2. Permite consultar, crear, modificar y eliminar evaluaciones de producción de insumos mediante peticiones HTTP que responden en JSON.

> Evaluación ES3 · T13V41 Programación Back End · INACAP
> Autor: `<Ignacio Tiznado>`

---

## 1. Descripción

El sistema evalúa si un insumo necesita producirse, a partir de su **stock actual** y de la **venta proyectada**. La decisión la toma la función `decidir()` de `solucion.py`, escrita en la ES1 y reutilizada sin cambios desde la Eva 2.

En esta evaluación se agrega una **API REST** que convive con la aplicación web anterior:

| Parte | Ruta | Cliente | Formato |
|---|---|---|---|
| Aplicación web (Eva 2) | `/`, `/registros/...` | Navegador | HTML + sesión |
| **API (ES3)** | `/api/...` | Cualquier cliente HTTP | JSON + token |

Ambas comparten el mismo modelo, la misma base de datos y la misma regla de negocio. Las vistas HTML de la Eva 2 **no fueron modificadas**.

## 2. Tecnologías

- Python 3 y Django
- Django REST Framework (DRF) con `rest_framework.authtoken`
- drf-spectacular (documentación OpenAPI / Swagger)
- SQLite
- python-decouple (variables de entorno)

## 3. Estructura del proyecto

```
meltpizzas/
├── manage.py
├── solucion.py              # Regla de negocio decidir() (ES1, sin cambios)
├── requirements.txt
├── .env.example             # Variables de entorno de ejemplo
├── produccion/
│   ├── settings.py          # Incluye el bloque REST_FRAMEWORK
│   └── urls.py              # Rutas raíz: web, API, token y Swagger
├── calculo/
│   ├── models.py            # Registro (con borrado lógico)
│   ├── views.py             # Vistas HTML de la Eva 2 (intactas)
│   ├── urls.py              # Rutas HTML de la Eva 2
│   ├── serializers.py       # ES3: validación y conversión a JSON
│   ├── api_views.py         # ES3: ViewSet de la API
│   └── permissions.py       # ES3: permisos diferenciados
└── pruebas/                 # Evidencias de las pruebas HTTP
```

## 4. Instalación y ejecución

```bash
# 1. Crear y activar el entorno virtual
python -m venv venv
venv\Scripts\activate            # Windows
# source venv/bin/activate       # Linux / macOS

# 2. Instalar dependencias
pip install -r requirements.txt

# 3. Configurar variables de entorno
copy .env.example .env           # Windows  (cp en Linux / macOS)
# Edita .env y completa los valores (ver .env.example)

# 4. Crear las tablas (incluye la tabla de tokens de DRF)
python manage.py migrate

# 5. Crear usuarios de prueba (ver sección 5)
python manage.py createsuperuser

# 6. Levantar el servidor
python manage.py runserver
```

Opcional, para cargar datos históricos de la ES1: `python manage.py shell < cargar_datos.py`.

Con el servidor activo:

- Aplicación web: <http://127.0.0.1:8000/>
- API: <http://127.0.0.1:8000/api/registros/>
- Documentación Swagger: <http://127.0.0.1:8000/api/docs/>

## 5. Usuarios y permisos

Los usuarios se gestionan con `django.contrib.auth`. No se almacenan contraseñas en el código ni en este repositorio.

| Usuario | `is_staff` | Puede hacer en la API |
|---|:---:|---|
| Administrador (superusuario) | Sí | Leer, crear, editar y eliminar |
| `lector` | No | Leer y crear. Editar y eliminar devuelve `403` |

## 6. Decisiones de configuración de DRF

El bloque `REST_FRAMEWORK` de `settings.py` declara explícitamente cuatro decisiones:

```python
REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": ["rest_framework.authentication.TokenAuthentication"],
    "DEFAULT_PERMISSION_CLASSES": ["rest_framework.permissions.IsAuthenticated"],
    "DEFAULT_PAGINATION_CLASS": "rest_framework.pagination.PageNumberPagination",
    "PAGE_SIZE": 10,
    "DEFAULT_SCHEMA_CLASS": "drf_spectacular.openapi.AutoSchema",
}
```

**`TokenAuthentication` en lugar de sesión por cookie.** Una API la consumen clientes que no son navegadores (scripts, aplicaciones móviles, otros servicios) y que no manejan cookies de forma natural. El token viaja en `Authorization` de cada petición, de modo que el servidor no guarda estado de sesión (*stateless*). Además, como el navegador no envía el token por sí solo, la API no queda expuesta a ataques CSRF, por lo que no se usa `@csrf_exempt` en ninguna parte.

**`IsAuthenticated` como permiso por defecto.** Es un criterio de seguridad por defecto: cualquier endpoint nuevo queda protegido a menos que se indique lo contrario. El ViewSet de registros lo reemplaza por un permiso más fino (sección 8).

**Paginación con `PAGE_SIZE = 10`.** Sin paginación, una consulta de lista devolvería todas las filas de la tabla, lo que se vuelve lento. Con 10 elementos por página la respuesta es acotada y el cliente navega con los enlaces `next` y `previous`.

**`AutoSchema` de drf-spectacular.** Genera el esquema OpenAPI a partir del código, de modo que la documentación se mantiene sincronizada con la API sin escribirla a mano.

## 7. Cómo se aplica la regla de negocio en la API

- `decidir()` **se importa** desde `solucion.py`; no se reescribe ni se duplica.
- El cliente envía solo las **entradas**: `insumo`, `stock_actual` y `venta_proyectada`.
- Los campos `estado`, `detalle` y `fecha` están declarados en `read_only_fields` del serializer. Si el cliente los incluye en la petición, **se ignoran**. Así nadie puede forzar un estado y saltarse la regla.
- En `POST`, `PUT` y `PATCH` el ViewSet ejecuta `decidir()` antes de guardar. En un `PATCH` parcial, los valores que el cliente no envía se toman del registro existente, de modo que el resultado siempre se recalcula y nunca queda desactualizado.
- Los valores negativos se rechazan con `400` mediante `validate_stock_actual` y `validate_venta_proyectada`. Los campos `stock_actual` y `venta_proyectada` se declaran obligatorios, porque aunque el modelo admite `null`, `decidir()` fallaría con un error `500` si recibiera `None`.
- `DELETE` ejecuta **borrado lógico** (`soft_delete()`): la fila permanece en la base con `eliminado=True` y deja de aparecer en la API.

## 8. Endpoints

Todos los endpoints de `registros` requieren la cabecera `Authorization: Token <token>`.

| URL | Método | Permiso | Cuerpo (JSON) | Respuesta exitosa | Errores |
|---|---|---|---|---|---|
| `/api/token/` | `POST` | Público | `username`, `password` | `200` con `{"token": "..."}` | `400` |
| `/api/registros/` | `GET` | Autenticado | — | `200`, lista paginada | `401` |
| `/api/registros/` | `POST` | Autenticado | `insumo`, `stock_actual`, `venta_proyectada` | `201`, registro con `estado` y `detalle` calculados | `400`, `401` |
| `/api/registros/{id}/` | `GET` | Autenticado | — | `200` | `401`, `404` |
| `/api/registros/{id}/` | `PUT` | Staff | `insumo`, `stock_actual`, `venta_proyectada` | `200`, resultado recalculado | `400`, `401`, `403`, `404` |
| `/api/registros/{id}/` | `PATCH` | Staff | Cualquier campo de entrada | `200`, resultado recalculado | `400`, `401`, `403`, `404` |
| `/api/registros/{id}/` | `DELETE` | Staff | — | `204` sin contenido | `401`, `403`, `404` |
| `/api/registros/aceptados/` | `GET` | Autenticado | — | `200`, solo los que requieren producción | `401` |

Notas:

- Los permisos los define `PermisoDiferenciadoRegistro` (`calculo/permissions.py`): lectura y creación para cualquier usuario autenticado; edición y eliminación solo para `is_staff`.
- La lista de `/api/registros/` admite `?page=N` para navegar entre páginas.
- `/api/registros/aceptados/` devuelve una lista simple, sin paginar.

## 9. Formato de las respuestas y códigos de estado

**Lista (`GET /api/registros/`):**

```json
{
  "count": 25,
  "next": "http://127.0.0.1:8000/api/registros/?page=2",
  "previous": null,
  "results": [
    {
      "id": 1,
      "insumo": "Queso",
      "stock_actual": 3.0,
      "venta_proyectada": 5.0,
      "estado": "Aceptado: Produccion requerida",
      "detalle": "Faltan 4.00 unidades por preparar.",
      "fecha": "2026-10-05T15:30:00Z"
    }
  ]
}
```

**Error de validación (`400`):** un arreglo de mensajes por campo.

```json
{"stock_actual": ["El stock actual no puede ser negativo."]}
```

**Sin credenciales (`401`)**, **sin permiso (`403`)** y **no encontrado (`404`)**:

```json
{"detail": "Authentication credentials were not provided."}
{"detail": "You do not have permission to perform this action."}
{"detail": "Not found."}
```

| Código | Cuándo se produce |
|:---:|---|
| `200 OK` | Lectura o actualización correcta |
| `201 Created` | Registro creado |
| `204 No Content` | Registro eliminado (lógicamente) |
| `400 Bad Request` | Datos inválidos o incompletos |
| `401 Unauthorized` | Falta el token o es inválido: el servidor no sabe quién es el cliente |
| `403 Forbidden` | Token válido, pero el usuario no tiene permiso para esa acción |
| `404 Not Found` | El registro no existe o fue eliminado lógicamente |

## 10. Ejemplos con `curl`

Reemplaza `<TOKEN>` por el token obtenido. En Windows PowerShell usa `curl.exe`; para el cuerpo se recomienda un archivo (`-d @archivo.json`) y así evitar problemas con las comillas.

**Obtener token**

```bash
curl -X POST http://127.0.0.1:8000/api/token/ \
  -H "Content-Type: application/json" \
  -d '{"username": "<usuario>", "password": "<clave>"}'
```

**Listar registros**

```bash
curl -i http://127.0.0.1:8000/api/registros/ \
  -H "Authorization: Token <TOKEN>"
```

**Crear un registro**

```bash
curl -i -X POST http://127.0.0.1:8000/api/registros/ \
  -H "Authorization: Token <TOKEN>" \
  -H "Content-Type: application/json" \
  -d '{"insumo": "Queso", "stock_actual": 3, "venta_proyectada": 5}'
```

**Crear con datos inválidos (devuelve `400`)**

```bash
curl -i -X POST http://127.0.0.1:8000/api/registros/ \
  -H "Authorization: Token <TOKEN>" \
  -H "Content-Type: application/json" \
  -d '{"insumo": "Queso", "stock_actual": -1, "venta_proyectada": 5}'
```

**Consultar el detalle**

```bash
curl -i http://127.0.0.1:8000/api/registros/1/ \
  -H "Authorization: Token <TOKEN>"
```

**Actualizar parcialmente (recalcula `estado` y `detalle`)**

```bash
curl -i -X PATCH http://127.0.0.1:8000/api/registros/1/ \
  -H "Authorization: Token <TOKEN_STAFF>" \
  -H "Content-Type: application/json" \
  -d '{"stock_actual": 20}'
```

**Eliminar (borrado lógico)**

```bash
curl -i -X DELETE http://127.0.0.1:8000/api/registros/1/ \
  -H "Authorization: Token <TOKEN_STAFF>"
```

**Consultar solo los que requieren producción**

```bash
curl -i http://127.0.0.1:8000/api/registros/aceptados/ \
  -H "Authorization: Token <TOKEN>"
```

**Petición sin token (devuelve `401`)**

```bash
curl -i http://127.0.0.1:8000/api/registros/
```

## 11. Documentación interactiva

La API se documenta con OpenAPI mediante drf-spectacular:

| Ruta | Contenido |
|---|---|
| `/api/docs/` | Swagger UI: permite probar los endpoints desde el navegador |
| `/api/redoc/` | Documentación de lectura (ReDoc) |
| `/api/schema/` | Esquema OpenAPI en bruto |

Para probar endpoints protegidos en Swagger: pulsar **Authorize** e ingresar `Token <tu_token>` (con la palabra `Token` y un espacio antes del valor).

## 12. Evidencias de prueba

La carpeta `pruebas/` contiene el registro de las peticiones HTTP realizadas con `<curl / Postman / Thunder Client>`:

| Archivo | Caso | Resultado |
| `01_sin_token_401` | Petición sin token | `401` |
| `04_crear_datos_invalidos` | Creación con datos inválidos | `400` |
| `05_lector_intenta_borrar` | Usuario sin privilegios intenta eliminar | `403` |
| `03_crear_con_token` | Creación válida | `201` |
| `08_admin_borra` | Eliminación por usuario staff | `204` |

Los tokens se reemplazaron por `<TOKEN>` en las evidencias.

## 13. Seguridad

- El archivo `.env` está en `.gitignore` y no se versiona; se entrega `.env.example` con valores de ejemplo.
- Ningún token ni contraseña está escrito en el código fuente.
- La autorización se valida en el servidor (clases de permisos), no ocultando elementos en una interfaz.
- Las contraseñas se almacenan con el hash nativo de Django.
- `fields` del serializer es una lista explícita; nunca se usa `'__all__'`.

## 14. Limitaciones y posibles mejoras

- El token de `rest_framework.authtoken` **no expira ni rota**. Una mejora sería usar JWT con refresco (por ejemplo, `djangorestframework-simplejwt`).
- La API distingue permisos con `is_staff`, mientras que la aplicación web usa grupos (`admin`, `normal`, `viewer`). Unificar ambos criterios sería una mejora futura.
- El borrado lógico impide recuperar un registro eliminado desde la API; solo es posible desde el administrador de Django.
