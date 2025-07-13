# Wake-on-LAN API Documentation

## Base URL
```
http://localhost:5000/api
```

## Autenticación
La API utiliza autenticación basada en sesiones y tokens. Después del login, puedes usar el token devuelto en el header `Authorization: Bearer <token>`.

## Endpoints

### Status
#### GET /status
Verifica el estado de la API.
```json
Response:
{
  "success": true,
  "message": "Wake-on-LAN API funcionando correctamente",
  "version": "1.0.0",
  "endpoints": { ... }
}
```

### Autenticación

#### POST /auth/login
Inicia sesión en la API.
```json
Request:
{
  "username": "usuario",
  "password": "contraseña"
}

Response:
{
  "success": true,
  "message": "Login exitoso",
  "user": {
    "id": 1,
    "username": "usuario"
  },
  "token": "token_1_usuario"
}
```

#### POST /auth/register
Registra un nuevo usuario.
```json
Request:
{
  "username": "nuevo_usuario",
  "password": "contraseña123"
}

Response:
{
  "success": true,
  "message": "Usuario registrado exitosamente",
  "user": {
    "id": 2,
    "username": "nuevo_usuario"
  }
}
```

#### POST /auth/logout
Cierra la sesión actual.
```json
Response:
{
  "success": true,
  "message": "Logout exitoso"
}
```

### Equipos

#### GET /equipos
Obtiene la lista de todos los equipos con su estado actual.
```json
Response:
{
  "success": true,
  "equipos": [
    {
      "id": 1,
      "nombre": "PC Oficina",
      "mac_address": "AA:BB:CC:DD:EE:FF",
      "ip_address": "192.168.1.100",
      "estado": "encendido"
    }
  ],
  "total": 1
}
```

#### POST /equipos
Crea un nuevo equipo.
```json
Request:
{
  "nombre": "Mi PC",
  "mac_address": "AA:BB:CC:DD:EE:FF"
}

Response:
{
  "success": true,
  "message": "Equipo creado exitosamente",
  "equipo": {
    "id": 1,
    "nombre": "Mi PC",
    "mac_address": "AA:BB:CC:DD:EE:FF"
  }
}
```

#### GET /equipos/{id}
Obtiene información detallada de un equipo específico.
```json
Response:
{
  "success": true,
  "equipo": {
    "id": 1,
    "nombre": "PC Oficina",
    "mac_address": "AA:BB:CC:DD:EE:FF",
    "ip_address": "192.168.1.100",
    "estado": "encendido"
  }
}
```

#### PUT /equipos/{id}
Actualiza la información de un equipo.
```json
Request:
{
  "nombre": "PC Oficina Actualizado",
  "mac_address": "BB:CC:DD:EE:FF:AA"
}

Response:
{
  "success": true,
  "message": "Equipo actualizado exitosamente",
  "equipo": {
    "id": 1,
    "nombre": "PC Oficina Actualizado",
    "mac_address": "BB:CC:DD:EE:FF:AA"
  }
}
```

#### DELETE /equipos/{id}
Elimina un equipo.
```json
Response:
{
  "success": true,
  "message": "Equipo eliminado exitosamente"
}
```

#### POST /equipos/{id}/encender
Envía señal de Wake-on-LAN para encender un equipo.
```json
Response:
{
  "success": true,
  "message": "Señal de encendido enviada a PC Oficina",
  "equipo": {
    "id": 1,
    "nombre": "PC Oficina",
    "mac_address": "AA:BB:CC:DD:EE:FF"
  }
}
```

#### GET /equipos/{id}/estado
Obtiene el estado actual de un equipo específico.
```json
Response:
{
  "success": true,
  "equipo": {
    "id": 1,
    "nombre": "PC Oficina",
    "mac_address": "AA:BB:CC:DD:EE:FF",
    "ip_address": "192.168.1.100",
    "estado": "encendido",
    "online": true
  }
}
```

## Códigos de Error

- `400` - Bad Request: Datos inválidos o faltantes
- `401` - Unauthorized: No autorizado, se requiere autenticación
- `404` - Not Found: Recurso no encontrado
- `409` - Conflict: Conflicto (ej: MAC duplicada, usuario existente)
- `500` - Internal Server Error: Error interno del servidor

## Formato de Errores
```json
{
  "error": "Tipo de error",
  "message": "Descripción detallada del error"
}
```

## Ejemplos de uso con curl

### Login
```bash
curl -X POST http://localhost:5000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username": "admin", "password": "password"}'
```

### Obtener equipos
```bash
curl -X GET http://localhost:5000/api/equipos \
  -H "Authorization: Bearer token_1_admin"
```

### Crear equipo
```bash
curl -X POST http://localhost:5000/api/equipos \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer token_1_admin" \
  -d '{"nombre": "Mi PC", "mac_address": "AA:BB:CC:DD:EE:FF"}'
```

### Encender equipo
```bash
curl -X POST http://localhost:5000/api/equipos/1/encender \
  -H "Authorization: Bearer token_1_admin"
```

## Notas importantes

1. **Formato MAC**: Las direcciones MAC deben estar en formato `AA:BB:CC:DD:EE:FF`
2. **Autenticación**: Todos los endpoints excepto `/status`, `/auth/login` y `/auth/register` requieren autenticación
3. **CORS**: La API tiene CORS habilitado para permitir requests desde aplicaciones web
4. **Estados**: Los equipos pueden tener estados: `encendido`, `apagado`, `desconocido`
5. **Red local**: El Wake-on-LAN solo funciona en la red local donde está ejecutándose el servidor