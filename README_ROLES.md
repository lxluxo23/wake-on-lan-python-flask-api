# Sistema de Roles - Wake-on-LAN

## 🎯 Descripción

Sistema de control de acceso basado en roles (RBAC) para la aplicación Wake-on-LAN, que permite:

- **Administradores**: Acceso completo a todos los equipos
- **Usuarios**: Acceso solo a equipos asignados específicamente

## 🚀 Configuración

### 1. Ejecutar Migraciones

```bash
export FLASK_APP=run.py
python3 -m flask db upgrade
```

### 2. Inicializar Sistema de Roles

```bash
# Configuración inicial
python3 -m flask init-roles

# Ver estado actual
python3 -m flask show-roles
```

## 🔧 Comandos Disponibles

### Gestión de Roles

```bash
# Inicializar sistema (crea usuario palula, asigna equipos)
flask init-roles

# Resetear y reinicializar
flask init-roles --reset

# Ver estado actual del sistema
flask show-roles
```

### Gestión de Asignaciones

```bash
# Asignar equipo a usuario
flask assign-equipment palula 5

# Desasignar equipo de usuario  
flask unassign-equipment palula 5
```

## 🔐 Credenciales por Defecto

| Usuario | Password | Rol | Acceso |
|---------|----------|-----|--------|
| admin | admin123 | admin | Todos los equipos |
| palula | palula123 | user | Equipos asignados |

## 📊 Estructura de Base de Datos

### Tablas Principales

- **user**: Usuarios con roles
- **equipo**: Equipos existentes + nuevas columnas
- **user_equipos**: Relación many-to-many
- **user_equipos_meta**: Metadatos de asignaciones

### Nuevas Columnas

**user**: `role`, `created_at`
**equipo**: `descripcion`, `ip_address`, `estado`, `created_at`, `updated_at`

## 🎯 Endpoints de API

### Autenticación
- `POST /auth/login` - Login de usuario

### Equipos (con control de acceso)
- `GET /equipos` - Lista equipos según permisos
- `GET /equipos/<id>` - Detalle de equipo (si tiene acceso)
- `POST /equipos/<id>/encender` - Wake-on-LAN (si tiene acceso)

### Administración (solo admin)
- `GET /admin/users` - Listar usuarios
- `POST /admin/users` - Crear usuario
- `POST /admin/assign-equipo` - Asignar equipo
- `POST /admin/unassign-equipo` - Desasignar equipo

### Información de Usuario
- `GET /me` - Información del usuario actual

## 🧪 Pruebas

```bash
# Verificar que admin ve todos los equipos
curl -X POST http://localhost:5000/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username": "admin", "password": "admin123"}'

# Usar token para acceder a equipos
curl -X GET http://localhost:5000/equipos \
  -H "Authorization: Bearer <TOKEN>"

# Verificar que usuario normal solo ve equipos asignados
curl -X POST http://localhost:5000/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username": "palula", "password": "palula123"}'
```

## 🔄 Rollback

Para deshacer el sistema de roles:

```bash
export FLASK_APP=run.py
python3 -m flask db downgrade
```

## 📝 Notas

- El sistema mantiene los equipos de producción existentes
- Solo agrega funcionalidad de roles sin afectar datos existentes
- Usa herramientas nativas de Flask (Flask-Migrate, Flask-CLI)
- Estructura limpia sin scripts auxiliares