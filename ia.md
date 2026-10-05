# Bitácora de uso crítico de IA: ES3 (API RESTful con DRF)

**Autor:** `<Ignacio TIznado>`
**Herramienta(s):** Claude (`<Sonnet 5.5>`)
**Período:** `<05/10/2026>`

## Cómo usé la IA en esta evaluación

Usé la IA como apoyo para entender y construir la API: configuración de DRF, serializer, ViewSet, permisos, token y documentación. Mi regla fue **no aceptar ninguna sugerencia sin entender qué hace y probarla**. Cada entrada de esta bitácora sigue la misma estructura: consulta, propuesta, análisis crítico y refactorización.
---

## Entrada 1: Consulta de seguridad

**Consulta formulada a la IA:**
Tengo una API con Django REST Framework y TokenAuthentication. Mi POST a /api/registros/ me devuelve 403. ¿Cómo lo soluciono? Explícame la causa.

Propuesta devuelta por la IA:
La IA me guio a revisar la clase de permisos dentro de mis archivos permissions.py u apiviews.py para verificar si tengo un permiso que limita operaciones de modificación. Además de verificar el envio correcto del Token en la petición.

Análisis crítico:
Esta sugerencia no me generó ningun tipo de sospecha o mala implementación. Continue con las instrucciones para comprobar mi problema.

Refactorización implementada: Al verificar todo y cambiar algunas cosas el error desaparecio y pude continuar con el desarrollo.

## Entrada 2: El ejemplo de la guía pertenecía a otro dominio

**Consulta formulada a la IA:**
`"Quiero desarrollar la evaluación 3 en base al archivo de instrucciones adaptado a la evaluacion 2."]`

**Propuesta devuelta:**
El material de la ES3 traía un ejemplo con campos `edad` y `estado`, y un `perform_create` que ejecutaba `decidir(edad, cupos_libres())` importando `cupos_libres` desde `solucion.py`.

**Análisis crítico:**
Mi `solucion.py` no tiene `cupos_libres` y `decidir()` recibe `(insumo, stock_actual, venta_proyectada)`. Copiar el ejemplo habría producido un `ImportError` al arrancar el servidor. Además, en el ejemplo el campo calculado es `estado`, mientras que en mi modelo los campos calculados son `estado` y `detalle`.

**Refactorización implementada:**
Adapté `calculo/serializers.py` y `calculo/api_views.py` a mi dominio: las entradas son `insumo`, `stock_actual` y `venta_proyectada`; `estado`, `detalle` y `fecha` van en `read_only_fields`; y `decidir()` se importa sin modificarla.

---

## Entrada 3: Campos opcionales que provocarían un error 500

**Consulta formulada a la IA:**
Aquí está mi models.py y mi serializer. ¿Qué peticiones POST podrían provocar un error 500 en lugar de un 400? Dame ejemplos de cuerpos JSON que lo causen.

**Propuesta devuelta:**
Al revisar mi `models.py` se señaló que `stock_actual` y `venta_proyectada` son `null=True, blank=True`, por lo que DRF los trataría como opcionales.

**Análisis crítico:**
Si el cliente omite uno de esos campos, `decidir()` compara `None < 0` y lanza `TypeError`, que el cliente vería como `500 Internal Server Error`. El criterio 3.1.3 exige que las validaciones impidan inconsistencias sin arrojar error 500.

**Refactorización implementada:**
Agregué `extra_kwargs` con `required: True` y `allow_null: False` en el serializer, y los métodos `validate_stock_actual` y `validate_venta_proyectada` para rechazar valores negativos.

---

## Entrada 4: Permisos por `is_staff` o por grupos

**Consulta formulada a la IA:**
Mi aplicación web usa grupos (admin, normal, viewer) para los permisos, pero en la API me piden usar is_staff. ¿Por qué podrían ser distintos? ¿Qué problemas puede traer tener ambos criterios en el mismo proyecto?

**Propuesta devuelta:**
La guía diferencia permisos con `is_staff` (lectura y creación para autenticados; edición y borrado solo para staff). Mi aplicación web de la Eva 2 usa en cambio grupos (`admin`, `normal`, `viewer`).

**Análisis crítico:**
Son dos mecanismos distintos y no coinciden: un usuario del grupo `normal` no es staff, y un staff no pertenece necesariamente a un grupo. Mezclarlos sin decidir habría dejado comportamientos inconsistentes entre la web y la API.

**Refactorización implementada:**
Decidí usar `is_staff` en la API, como pide la guía, mediante `PermisoDiferenciadoRegistro` en `calculo/permissions.py`, y dejar las vistas HTML con sus grupos. Dejé anotada la unificación como mejora futura en el README.

---

## Entrada 5: El token no expira

**Consulta formulada a la IA:**
Si alguien roba mi token, ¿cuánto tiempo sirve? ¿Qué alternativas existen y cuándo conviene cada una?

**Propuesta devuelta:**
La guía implementa `TokenAuthentication`. La rúbrica del criterio 3.1.2 menciona, en su nivel máximo, tokens o JWT "con rotación/refresco".

**Análisis crítico:**
El token de `rest_framework.authtoken` es permanente: si se filtra, sirve hasta que se elimine manualmente de la base. No tiene expiración ni rotación.

**Refactorización implementada:**
Mantuve TokenAuthentication por lo que indica la guía

---

## Entrada 6: Credenciales en los archivos de prueba

**Consulta formulada a la IA:**
Voy a entregar una carpeta pruebas/ con evidencias de curl que incluyen peticiones con tokens y un archivo con usuario y contraseña. ¿Qué riesgos tiene entregar eso y cómo debo manejarlo?

**Propuesta devuelta:**
Para ejecutar los `curl` sin problemas de comillas se recomendó guardar el cuerpo de la petición en archivos JSON, incluyendo uno con usuario y contraseña para obtener el token.

**Análisis crítico:**
Esos archivos y los tokens que aparecen en las respuestas quedarían dentro de la carpeta `pruebas/` que se entrega, lo que contradice el requisito de cero exposición de credenciales o tokens.

**Refactorización implementada:**
Eliminé el archivo con la contraseña y reemplacé los tokens reales por `<TOKEN>` en las evidencias.

---

## Reflexión final

Generalmente mi aprendizaje con la IA es limitado, hay varios conceptos que como gran maestra de información maneja de forma feroz que yo no puedo lograr a entender directamente. Es seguro que varias cosas dentro de esta evaluación no haya logrado comprenderlas en su totalidad, sino solo ver que funcionan correctamente. El código de la IA funciono correctamente en gran parte del camino y pocas veces tuve que hacer correcciones o anotaciones e incluso asi tenian más relación con mis errores que los suyos. Si tuviera que cambiar esta forma de desarrollo a otra, seria una que me enseñara y forzara a aplicar cada cambio para lograr entender el proyecto en su totalidad, aunque claro esto significa más uso de tiempo, también es más seguridad al juzgar a la IA.
