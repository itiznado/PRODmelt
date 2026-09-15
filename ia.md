# ia.md — Bitácora de Uso Crítico de IA

**Herramienta utilizada:** Claude (Anthropic), vía claude.ai.

Este documento registra momentos especificos en el desarrollo en que se consultó a la IA, se evaluó su respuesta, y se corrigió o justificó una decisión en base a esa evaluación.

---

## 1. Placeholder para datos históricos sin migrar (`0` vs `null`)

**Contexto:** Al migrar los registros históricos de `datos.json` (ES1) a la base de datos de Django, surgió el problema de que `solucion.py` original nunca guardaba `stock_actual` ni `venta_proyectada` solo el resultado (`estado`, `detalle`) de `decidir()`. Esos datos de entrada simplemente no existen.

**Prompt (resumido):** Se consultó cómo poblar esos dos campos al migrar los registros antiguos, dado que la ES1 nunca los persistió.

**Respuesta de la IA y análisis crítico:** La IA propuso inicialmente usar `0` como valor placeholder para `stock_actual` y `venta_proyectada` en los registros migrados. Al revisar esta sugerencia, se identificó que era incorrecta: `0` es un valor real (`0` unidades de stock, `$0` de venta proyectada), distinto de "este dato nunca se registró". Guardar `0` habría sido información falsa.

**Corrección implementada:** Se cambiaron los campos `stock_actual` y `venta_proyectada` del modelo `Registro` a `null=True, blank=True`, y el script de carga (`cargar_datos.py`) se ajustó para insertar `None` en vez de `0` en los registros migrados desde la ES1. Esto refleja correctamente en la base de datos que esos valores son desconocidos, no cero.

---

## 2. Protección de acceso por rol: seguridad en el servidor, no en la plantilla

**Contexto:** Al implementar RBAC (roles `admin`, `normal`, `viewer`), se evaluó si ocultar los botones "Editar"/"Eliminar" en el template según el rol del usuario sería una buena medida de seguridad.

**Prompt (resumido):** Se consultó sobre agregar una condición `{% if %}` en `lista.html` para ocultar esos botones a usuarios sin permiso, como mejora de experiencia de usuario.

**Respuesta de la IA y análisis crítico:** La IA fue explícita en que esa condición en el template es **puramente cosmética** y nunca debe considerarse una medida de seguridad real: un usuario con rol `viewer` que conozca o adivine la URL directa (ej. `/registros/1/editar/`) podría intentar acceder igualmente, sin pasar por ningún botón. La seguridad real debe residir exclusivamente en el decorador `@requiere_rol` aplicado a nivel de vista, en el servidor.

**Corrección/decisión implementada:** Se mantuvo `@requiere_rol("admin")` como única barrera real en las vistas `editar` y `eliminar`. Se verificó manualmente (checklist del documento de instrucciones) que un usuario `viewer` autenticado, al intentar acceder directamente a `/registros/1/editar/` por la barra de direcciones, es redirigido por el servidor con un mensaje de error — sin depender de que el botón esté oculto en la interfaz.

---

## 3. Persistencia de contraseñas: confirmación del comportamiento nativo, no implementación propia

**Contexto:** Al crear el usuario de prueba `lector` con `crear_usuarios.py`, surgió la duda de cómo verificar que la contraseña quedaba cifrada, dado que el admin de Django no permite "ver" la contraseña de un usuario existente, solo resetearla.

**Prompt (resumido):** Se consultó por qué el admin solo ofrece "reset password" para un usuario existente y no muestra la contraseña actual.

**Respuesta de la IA y análisis crítico:** Se confirmó que esto es el comportamiento esperado y correcto de Django: las contraseñas se almacenan cifradas con PBKDF2 (algoritmo de un solo sentido), por lo que no existe ningún mecanismo, ni para el superusuario ni para el propio framework, que permita recuperar la contraseña original desde el hash guardado. Esto se verificó consultando directamente `user.password` desde `manage.py shell`, confirmando el formato `pbkdf2_sha256$...` sin exponer ni modificar la contraseña real del usuario.

**Conclusión:** No se implementó código adicional — se confirmó que el cifrado nativo de `django.contrib.auth` (requerido por el criterio 2.1.4) ya cumple el requisito sin necesidad de lógica propia, y que intentar "ver" una contraseña sería, de hecho, una señal de mala práctica de seguridad si fuera posible.

---

## Nota sobre decisiones fuera de alcance

Durante el desarrollo se identificó una mejora futura no requerida por esta evaluación: registrar `stock_actual`/`venta_proyectada` reales desde una fuente externa (tabla de factores de uso por insumo) para auditar con el tiempo si el `factor_uso` de `decidir()` sigue siendo preciso. Se documenta aquí como línea de trabajo futura, no como parte de la entrega actual.

Principalmente esto, como solución a un caso que ya me ocurre en mi trabajo, necesita varias mejoras con datos que ya tenemos en la empresa. Por lo tanto quedan más como un Could Have.