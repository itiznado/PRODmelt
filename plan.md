# Plan de Proyecto - Sistema de Cálculo de Producción de Insumos

## 1. Apartado de Negocio

### 1.1. Problema
En el local de pizzas, cada mañana el pizzero o encargado de apertura debe calcular a mano cuánto insumo producir (ej. cajas de queso, lexans de salsa o salseros) para cubrir la meta de venta del día o del fin de semana. Este cálculo se realiza en papeles sueltos, con lápiz pasta o usando la calculadora del celular, recordando de memoria los factores de consumo por millón de pesos en ventas.

A quién le molesta: Al encargado de turno y al equipo de cocina.
Qué le cuesta:
- Tiempo perdido (20 a 30 minutos diarios).
- Errores de cálculo que provocan quiebres de stock a mitad del servicio (quedarse sin queso/salsa) o sobreproducción innecesaria que termina en mermas y comida vencida.
- Pérdida de integridad: los papeles en cocina se mojan con salsa, se rompen o se botan por error.

### 1.2. Propuesta de Solución
Un sistema web en Django que le permite al encargado de turno ingresar el stock remanente de un insumo y la venta proyectada del día, para que el sistema evalúe y decida automáticamente si es necesario producir, cuánto falta preparar o si existe una alerta por sobrestock — con historial persistente, gestión de usuarios por rol y administración de datos.

### 1.3. Evolución del Alcance: de ES1 a Eva 2

La ES1 resolvía el problema con un script de consola que leía y escribía en un archivo `datos.json`, sin control de acceso ni base de datos relacional. Esa solución cumplía el objetivo académico de esa entrega, pero tenía limitaciones reales para un uso continuo: sin control de concurrencia, sin registro de quién hizo cada cambio, y sin forma de auditar ni recuperar información si el archivo se corrompía.

La Eva 2 migra esa misma lógica de decisión (`decidir()`, sin modificar) hacia una arquitectura Django con base de datos SQLite, manteniendo el mismo problema de negocio y la misma regla de decisión de 4 resultados, pero resolviendo las limitaciones estructurales de la ES1.

### 1.4. Priorización MoSCoW (Eva 2)

- **Must (Imprescindible — resuelto en esta entrega):**
  1. Migrar el modelo de datos a una base de datos relacional (SQLite) vía Django ORM, conservando los mismos campos de resultado (`estado`, `detalle`) que la ES1.
  2. Reutilizar `decidir()` de `solucion.py` sin reescribirla ni duplicar su lógica.
  3. CRUD completo (crear, leer, editar, eliminar) sobre la entidad `Registro`, con validación de entradas y recálculo obligatorio de `decidir()` al editar `stock_actual` o `venta_proyectada`.
  4. Borrado lógico (`soft_delete`) — ningún registro se elimina físicamente de la base de datos.
  5. Autenticación de usuarios con sesiones nativas de Django (`django.contrib.auth`).
  6. Control de acceso basado en roles (`admin`, `normal`, `viewer`), validado en el servidor mediante decorador (`@requiere_rol`), nunca solo ocultando elementos en el HTML.
  7. Protección CSRF activa en todos los formularios POST.
  8. Configuración de credenciales sensibles (`SECRET_KEY`, `DEBUG`) mediante variables de entorno, nunca hardcodeadas.
  9. Panel de administración de Django personalizado (`list_display`, `list_filter`, `search_fields`, `readonly_fields`) para auditoría de todos los registros, incluidos los eliminados lógicamente.
  10. Script de migración de los datos históricos de `datos.json` hacia la base de datos, documentando y justificando el tratamiento de campos que la ES1 nunca persistió (`stock_actual`, `venta_proyectada` como `null`, no `0`).

- **Should (Debería tener — resuelto en esta entrega):**
  - Mensajes flash informativos (`messages.success`, `messages.error`) para creación, edición, eliminación y errores de permisos.
  - Manejo de errores amigable ante entradas inválidas (`try/except`), sin exponer errores 500 al usuario final.

- **Could (Deseable — no resuelto en esta entrega):**
  - Paginación en la vista de lista.
  - Ocultar condicionalmente en la interfaz los botones de acciones no permitidas para el rol actual (mejora de UX; la seguridad real ya está resuelta en el servidor con `@requiere_rol`, independiente de esto).
  - Exportación de auditoría desde el panel administrativo.

- **Won't (No tendrá esta entrega):**
  - Motores de base de datos distribuidos externos (PostgreSQL/MySQL en la nube) — se mantiene SQLite conforme al mandato de la evaluación.
  - Recuperación de contraseña por SMTP / correo saliente.
  - Registro público de usuarios (los usuarios y roles son administrados por el operador vía el panel de administración).
  - Persistencia de un `factor_uso` distinto por insumo desde una fuente externa, y auditoría histórica de su precisión — identificado como mejora futura de negocio, fuera del alcance académico de esta evaluación.

---

## 2. Apartado Técnico

### 2.1. Arquitectura

- **Framework:** Django, con la app `calculo` conteniendo modelos, vistas y URLs del dominio.
- **Base de datos:** SQLite gestionada vía Django ORM (`db.sqlite3`, no versionado en Git).
- **Configuración:** variables sensibles (`SECRET_KEY`, `DEBUG`) gestionadas con `python-decouple`, leídas desde `.env` (no versionado) con `.env.example` documentando las claves requeridas.

### 2.2. Modelo de Datos (`calculo/models.py`)

El modelo `Registro` conserva los campos de entrada (`insumo`, `stock_actual`, `venta_proyectada`) y de salida (`estado`, `detalle`) que produce `decidir()`, además de `fecha`, `eliminado` y `fecha_eliminacion` para el borrado lógico. Los campos `stock_actual` y `venta_proyectada` permiten `null` para representar correctamente los registros históricos migrados desde la ES1, donde esos datos de entrada nunca se persistieron.

### 2.3. Regla de Negocio

La función `decidir(insumo, stock_actual, venta_proyectada, factor_uso, stock_maximo)` de `solucion.py` se importa sin modificaciones en las vistas de creación y edición. Se reejecuta obligatoriamente cada vez que cambian `stock_actual` o `venta_proyectada`, evitando que un registro editado quede con un `estado`/`detalle` desactualizado respecto a sus datos actuales.

### 2.4. Roles y Seguridad

Los roles `admin`, `normal` y `viewer` se implementan con grupos nativos de `django.contrib.auth` (`Group`), sin tablas de credenciales propias. El decorador `requiere_rol` valida el rol a nivel de vista en el servidor antes de ejecutar cualquier operación de escritura; la vista `lista` solo exige sesión iniciada, sin restricción de rol. Las contraseñas se cifran automáticamente mediante PBKDF2, comportamiento nativo de Django sin implementación adicional.

### 2.5. Pantalla Web

- **Rutas principales:** `/registros/` (lista), `/registros/crear/`, `/registros/<id>/editar/`, `/registros/<id>/eliminar/` (solo POST), `/login/`, `/logout/`.
- **Templates:** heredan de `base.html` (a nivel de proyecto), que centraliza la visualización de mensajes flash.