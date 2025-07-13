# 🚀 Guía de Despliegue - Wake-on-LAN API

## 📋 Descripción del Sistema

Sistema completo de Wake-on-LAN con:
- **Backend**: Flask API (Python) en Windows como servicio nativo
- **Frontend**: PWA (Vue.js + Vite) 
- **SSL**: Nginx Proxy Manager (Docker) → Backend nativo
- **Dominio**: equipos.myccontadores.cl

## 🏗️ Arquitectura

```
Internet → equipos.myccontadores.cl (Puerto 443/80)
    ↓
Nginx Proxy Manager (Docker)
    ↓
Backend Flask (Windows Service - Puerto 90)
    ↓
Frontend PWA (Estático)
```

---

## 🔧 BACKEND - Servicio Windows

### 📦 Dependencias

```bash
pip install flask flask-sqlalchemy flask-migrate flask-cors waitress pywin32
```

### 📁 Estructura del Proyecto

```
wake-on-lan-python-flask-api/
├── app/                    # Aplicación Flask
├── instance/              # Base de datos SQLite
├── migrations/            # Migraciones de BD
├── logs/                  # Logs del servicio (se crea auto)
├── server.py             # Servidor HTTP básico
├── service.py            # Servicio Windows
├── config.py             # Configuración
├── run.py               # Punto de entrada
└── wake-pwa/            # Frontend PWA
```

### 🔧 Instalación del Servicio

**1. Instalar como servicio** (PowerShell como Administrador):
```bash
cd C:\ruta\a\tu\proyecto
python service.py install
```

**2. Configurar auto-inicio:**
```bash
python service.py --startup auto install
```

**3. Iniciar servicio:**
```bash
python service.py start
# O desde Services.msc → "Wake-on-LAN API Service"
```

### 📊 Comandos de Control

| Comando | Descripción |
|---------|-------------|
| `python service.py install` | Instalar servicio |
| `python service.py start` | Iniciar servicio |
| `python service.py stop` | Detener servicio |
| `python service.py restart` | Reiniciar servicio |
| `python service.py remove` | Desinstalar servicio |
| `python service.py debug` | Modo debug (consola) |

### 📝 Logs y Monitoreo

**Ubicación de logs:**
- **Archivo**: `logs/wake_service.log`
- **Event Viewer**: Windows Logs → Application → "WakeOnLanAPI"
- **Services.msc**: Click derecho → Properties

**Ver logs en tiempo real:**
```bash
# PowerShell
Get-Content -Path "logs\wake_service.log" -Wait -Tail 10
```

---

## 🌐 NGINX PROXY MANAGER

### 🐳 Docker Compose

Ya tienes NPM corriendo en Docker. Configuración actual:
- Puerto 80: HTTP
- Puerto 81: Admin Panel  
- Puerto 443: HTTPS

### ⚙️ Configuración Proxy Host

**En NPM Admin Panel (puerto 81):**

1. **Proxy Hosts** → **Add Proxy Host**
2. **Details Tab:**
   - Domain Names: `equipos.myccontadores.cl`
   - Scheme: `http`
   - Forward Hostname/IP: `host.docker.internal`
   - Forward Port: `90`
   - ✅ Cache Assets
   - ✅ Block Common Exploits

3. **SSL Tab:**
   - ✅ SSL Certificate: Request a new SSL Certificate  
   - ✅ Force SSL
   - ✅ HTTP/2 Support
   - Email: tu-email@ejemplo.com
   - ✅ I Agree to the Let's Encrypt Terms of Service

### 🔄 Troubleshooting NPM

Si `host.docker.internal` no funciona:

**Opción A - Agregar extra_hosts al docker-compose:**
```yaml
npm-app:
  # ... configuración existente
  extra_hosts:
    - "host.docker.internal:host-gateway"
```

**Opción B - Usar IP del host:**
```bash
# Obtener IP del host
ipconfig | findstr IPv4
# Usar esa IP en lugar de host.docker.internal
```

---

## 🎨 FRONTEND - PWA

### 📱 Estructura

```
wake-pwa/
├── public/
│   ├── wol-192x192.png    # Iconos PWA
│   ├── wol-512x512.png
│   ├── apple-touch-icon.png
│   └── favicon.png
├── src/
│   ├── composables/
│   │   └── useApi.ts      # Configuración API
│   └── components/
└── vite.config.js         # Config PWA
```

### 🔧 Configuración de API

**Archivo**: `src/composables/useApi.ts`
```typescript
const API_BASE_URL = import.meta.env.PROD 
  ? 'https://equipos.myccontadores.cl/api'  // Producción
  : 'http://localhost:5000/api'             // Desarrollo
```

### 🚀 Build y Deploy

```bash
cd wake-pwa

# Desarrollo
npm run dev

# Producción
npm run build
npm run preview

# Deploy (copiar dist/ a servidor web)
```

### 📱 Características PWA

- ✅ Instalable como app nativa
- ✅ Offline cache para API calls
- ✅ Iconos optimizados 
- ✅ SSL requerido para instalación

---

## 🔐 SSL Y DOMINIOS

### 🌍 Configuración DNS

Apuntar subdominio a IP pública:
```
equipos.myccontadores.cl → A → TU.IP.PUBLICA
```

### 🔒 Certificados SSL

NPM maneja automáticamente:
- Let's Encrypt certificates
- Auto-renovación cada 90 días
- Redirección HTTP → HTTPS

---

## 🚨 TROUBLESHOOTING

### ❌ Servicio no inicia

1. **Verificar logs:**
   ```bash
   type logs\wake_service.log
   ```

2. **Ejecutar en modo debug:**
   ```bash
   python service.py debug
   ```

3. **Verificar dependencias:**
   ```bash
   pip install -r requirements.txt
   ```

### ❌ SSL no funciona

1. **Verificar DNS:** `nslookup equipos.myccontadores.cl`
2. **Verificar puerto 80/443 abiertos**
3. **Revisar logs NPM:** Docker logs del contenedor
4. **Reiniciar NPM:** `docker-compose restart npm-app`

### ❌ Frontend no conecta al backend

1. **Verificar URL API en browser:** `https://equipos.myccontadores.cl/api/health`
2. **Verificar CORS en backend**
3. **Rebuilder frontend:** `npm run build`

### ❌ Wake-on-LAN no funciona

1. **Verificar permisos:** Servicio debe ejecutarse como administrador
2. **Verificar red:** Equipos en misma red/VLAN
3. **Verificar ARP table:** `arp -a`

---

## 📋 CHECKLIST DE DESPLIEGUE

### ✅ Backend
- [ ] Dependencias instaladas (`pip install pywin32 waitress flask...`)
- [ ] Servicio instalado (`python service.py install`)
- [ ] Servicio iniciado (`python service.py start`)
- [ ] API responde (`http://localhost:90/api/health`)
- [ ] Logs funcionando (`logs/wake_service.log`)

### ✅ Nginx Proxy Manager
- [ ] Docker containers corriendo
- [ ] Proxy host configurado
- [ ] SSL certificate activo
- [ ] `host.docker.internal:90` accesible

### ✅ Frontend
- [ ] Variables de entorno configuradas
- [ ] Build generado (`npm run build`)
- [ ] PWA installable
- [ ] API calls funcionando

### ✅ Producción
- [ ] DNS apuntando correctamente
- [ ] Firewall configurado (80, 443, 90)
- [ ] Backups configurados
- [ ] Monitoreo activo

---

## 📞 COMANDOS RÁPIDOS

```bash
# Revisar estado del servicio
sc query WakeOnLanAPI

# Ver logs en tiempo real
Get-Content logs\wake_service.log -Wait -Tail 10

# Reiniciar todo el stack
python service.py restart
docker-compose restart npm-app

# Testing API
curl https://equipos.myccontadores.cl/api/health

# Build frontend
cd wake-pwa && npm run build
```

---

## 📝 NOTAS IMPORTANTES

- **Puerto 90**: Backend Flask (solo localhost)
- **Puerto 80/443**: NPM Docker (público)
- **Auto-inicio**: Servicio se inicia con Windows
- **Logs rotan**: Configurar logrotate si crece mucho
- **Backups**: Respaldar `instance/` y configuraciones NPM

---

*📅 Última actualización: $(Get-Date)*
*🔧 Documentado por: Claude Code*