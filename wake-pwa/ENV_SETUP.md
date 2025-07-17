# 🌍 Configuración de Variables de Entorno

Este proyecto utiliza variables de entorno para configurar diferentes aspectos de la aplicación como URLs del API, configuración de timeouts, etc.

## 📋 Variables Disponibles

### 🔗 API y Conexiones
- **`VITE_API_URL`**: URL base del API backend
  - Desarrollo: `http://localhost:5000/api`
  - Producción: `https://equipos.myccontadores.cl/api`

### 📱 Información de la Aplicación
- **`VITE_APP_TITLE`**: Título de la aplicación mostrado en el navegador
- **`VITE_APP_VERSION`**: Versión de la aplicación

### ⚙️ Configuración del Entorno
- **`VITE_ENVIRONMENT`**: Tipo de entorno (`development`, `production`, `staging`)
- **`VITE_DEBUG`**: Habilita logging adicional (`true`/`false`)

### 🔧 Configuración de la Aplicación
- **`VITE_DEFAULT_TIMEOUT`**: Timeout por defecto para peticiones HTTP (en ms)
- **`VITE_MAX_RETRIES`**: Número máximo de reintentos para peticiones fallidas

## 🚀 Configuración Inicial

### 1. Copiar archivo de ejemplo
```bash
cp .env.example .env
```

### 2. Configurar variables para desarrollo local
```bash
# .env
VITE_API_URL=http://localhost:5000/api
VITE_APP_TITLE=Wake-on-LAN Remote
VITE_APP_VERSION=1.0.0
VITE_ENVIRONMENT=development
VITE_DEBUG=true
VITE_DEFAULT_TIMEOUT=10000
VITE_MAX_RETRIES=3
```

### 3. Configurar variables para producción
```bash
# .env.production
VITE_API_URL=https://equipos.myccontadores.cl/api
VITE_APP_TITLE=Wake-on-LAN Remote
VITE_APP_VERSION=1.0.0
VITE_ENVIRONMENT=production
VITE_DEBUG=false
VITE_DEFAULT_TIMEOUT=15000
VITE_MAX_RETRIES=5
```

## 🔒 Seguridad

- ⚠️ **NUNCA** incluyas secrets, passwords o API keys en variables que empiecen con `VITE_`
- Las variables `VITE_*` son expuestas al cliente y visibles en el código compilado
- Para secrets usa variables de entorno del servidor (sin el prefijo `VITE_`)

## 🛠️ Uso en el Código

### Acceso directo
```typescript
const apiUrl = import.meta.env.VITE_API_URL
const isDebug = import.meta.env.VITE_DEBUG === 'true'
```

### Uso con el composable useConfig (recomendado)
```typescript
import { useConfig } from '@/composables/useConfig'

const { apiBaseURL, isDebug, appTitle } = useConfig()

// Logging condicional
const { log, logError } = useConfig()
log('Esto solo se muestra en desarrollo con DEBUG=true')
```

## 📁 Archivos de Entorno

- **`.env`**: Variables para desarrollo local
- **`.env.production`**: Variables para producción
- **`.env.example`**: Plantilla con todas las variables documentadas
- **`.env.local`**: Variables locales (ignorado por git) - opcional

## 🔄 Precedencia de Variables

Vite carga las variables en este orden (la última sobrescribe):
1. `.env`
2. `.env.local`
3. `.env.[mode]` (ej: `.env.production`)
4. `.env.[mode].local`

## 🧪 Testing

Para testing, puedes crear un archivo `.env.test` con configuraciones específicas para pruebas.

## 📖 Más Información

- [Documentación de Variables de Entorno en Vite](https://vitejs.dev/guide/env-and-mode.html)
- [Documentación del composable useConfig](./src/composables/useConfig.ts)