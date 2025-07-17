# Script de Migración Completa del Sistema de Roles
# Wake-on-LAN Flask API
# =====================================================

param(
    [switch]$Force,
    [switch]$SkipBackup
)

Write-Host @"
╔══════════════════════════════════════════════════════════════╗
║                 MIGRACIÓN SISTEMA DE ROLES                  ║
║                    Wake-on-LAN API                          ║
╚══════════════════════════════════════════════════════════════╝
"@ -ForegroundColor Cyan

# Verificar que estamos en el directorio correcto
if (-not (Test-Path "run.py")) {
    Write-Host "❌ Error: No estás en el directorio correcto del proyecto" -ForegroundColor Red
    Write-Host "   Navega al directorio wake-on-lan-python-flask-api primero" -ForegroundColor Yellow
    exit 1
}

# Verificar entorno virtual
if (-not $env:VIRTUAL_ENV) {
    Write-Host "⚠️  Advertencia: No hay entorno virtual activo" -ForegroundColor Yellow
    Write-Host "   Se recomienda activar el entorno virtual primero" -ForegroundColor Yellow
    
    if (-not $Force) {
        $continue = Read-Host "¿Continuar de todos modos? (y/N)"
        if ($continue -ne "y" -and $continue -ne "Y") {
            Write-Host "Operación cancelada" -ForegroundColor Yellow
            exit 0
        }
    }
}

# Configurar Flask
$env:FLASK_APP = "run.py"
Write-Host "🔧 Flask configurado: $env:FLASK_APP" -ForegroundColor Green

# 1. BACKUP
if (-not $SkipBackup) {
    Write-Host "`n📁 Creando backup de seguridad..." -ForegroundColor Yellow
    $timestamp = Get-Date -Format "yyyyMMdd_HHmmss"
    $backupFile = "instance\equipos_backup_$timestamp.db"
    
    try {
        Copy-Item "instance\equipos.db" $backupFile -ErrorAction Stop
        Write-Host "✅ Backup creado: $backupFile" -ForegroundColor Green
    } catch {
        Write-Host "❌ Error creando backup: $($_.Exception.Message)" -ForegroundColor Red
        exit 1
    }
} else {
    Write-Host "⚠️  Saltando backup (--SkipBackup especificado)" -ForegroundColor Yellow
}

# 2. VERIFICAR ESTADO ACTUAL
Write-Host "`n📊 Verificando estado actual de la base de datos..." -ForegroundColor Yellow
try {
    $currentVersion = python -m flask db current 2>&1
    Write-Host "📍 Versión actual: $currentVersion" -ForegroundColor Cyan
} catch {
    Write-Host "❌ Error verificando estado: $($_.Exception.Message)" -ForegroundColor Red
}

# 3. APLICAR MIGRACIÓN
Write-Host "`n🔄 Aplicando migración del sistema de roles..." -ForegroundColor Yellow
try {
    $upgradeResult = python -m flask db upgrade 2>&1
    if ($LASTEXITCODE -eq 0) {
        Write-Host "✅ Migración aplicada exitosamente" -ForegroundColor Green
    } else {
        throw "Error en migración: $upgradeResult"
    }
} catch {
    Write-Host "❌ Error aplicando migración: $($_.Exception.Message)" -ForegroundColor Red
    Write-Host "   Revisa los logs anteriores para más detalles" -ForegroundColor Yellow
    exit 1
}

# 4. VERIFICAR NUEVA ESTRUCTURA
Write-Host "`n🔍 Verificando nueva estructura de base de datos..." -ForegroundColor Yellow
try {
    python -c @"
from app import create_app
from app.models import db

app = create_app()
with app.app_context():
    inspector = db.inspect(db.engine)
    tables = inspector.get_table_names()
    
    print('📋 Tablas disponibles:')
    for table in tables:
        print(f'   ✓ {table}')
    
    print('\n🔧 Columnas de user:')
    for col in inspector.get_columns('user'):
        print(f'   - {col["name"]}: {col["type"]}')
    
    print('\n🔧 Columnas de equipo:')
    for col in inspector.get_columns('equipo'):
        print(f'   - {col["name"]}: {col["type"]}')
    
    print('\n✅ Estructura de base de datos verificada')
"@
} catch {
    Write-Host "❌ Error verificando estructura: $($_.Exception.Message)" -ForegroundColor Red
}

# 5. INICIALIZAR SISTEMA DE ROLES
Write-Host "`n👥 Inicializando sistema de roles..." -ForegroundColor Yellow
try {
    $initResult = python -m flask init-roles 2>&1
    Write-Host $initResult -ForegroundColor White
    
    if ($LASTEXITCODE -eq 0) {
        Write-Host "✅ Sistema de roles inicializado" -ForegroundColor Green
    } else {
        throw "Error inicializando roles: $initResult"
    }
} catch {
    Write-Host "❌ Error inicializando roles: $($_.Exception.Message)" -ForegroundColor Red
    exit 1
}

# 6. MOSTRAR ESTADO FINAL
Write-Host "`n📊 Estado final del sistema:" -ForegroundColor Yellow
try {
    python -m flask show-roles
} catch {
    Write-Host "❌ Error mostrando estado: $($_.Exception.Message)" -ForegroundColor Red
}

# 7. CONFIGURAR CREDENCIALES DE ADMINISTRADOR
Write-Host "`n🔐 Configurando credenciales de administrador..." -ForegroundColor Yellow
try {
    python -c @"
from app import create_app
from app.models import User, db
from flask_bcrypt import Bcrypt

app = create_app()
bcrypt = Bcrypt(app)

with app.app_context():
    admin = User.query.filter_by(username='admin').first()
    if admin:
        admin.role = 'admin'
        admin.password = bcrypt.generate_password_hash('admin123').decode('utf-8')
        db.session.commit()
        print('✅ Usuario admin configurado')
        print('   Username: admin')
        print('   Password: admin123')
    else:
        # Crear admin si no existe
        admin = User(
            username='admin',
            password=bcrypt.generate_password_hash('admin123').decode('utf-8'),
            role='admin'
        )
        db.session.add(admin)
        db.session.commit()
        print('✅ Usuario admin creado')
        print('   Username: admin')
        print('   Password: admin123')
"@
} catch {
    Write-Host "❌ Error configurando admin: $($_.Exception.Message)" -ForegroundColor Red
}

# 8. RESUMEN FINAL
Write-Host @"

╔══════════════════════════════════════════════════════════════╗
║                    MIGRACIÓN COMPLETADA                     ║
╚══════════════════════════════════════════════════════════════╝

🎉 El sistema de roles ha sido instalado exitosamente

📋 Características instaladas:
   ✓ Control de acceso basado en roles (RBAC)
   ✓ Usuarios admin y normales
   ✓ Asignación de equipos por usuario
   ✓ API con filtrado por permisos
   ✓ Tokens JWT para autenticación

🔐 Credenciales por defecto:
   👑 Admin:  admin / admin123
   👤 Usuario: palula / palula123

🚀 Próximos pasos:
   1. Iniciar servidor: python run.py
   2. Probar login: http://localhost:5000/api/auth/login
   3. Gestionar usuarios: python -m flask assign-equipment <usuario> <equipo_id>

📁 Backup guardado en: $backupFile
"@ -ForegroundColor Green

Write-Host "`n¿Deseas iniciar el servidor ahora? (y/N): " -ForegroundColor Cyan -NoNewline
$startServer = Read-Host

if ($startServer -eq "y" -or $startServer -eq "Y") {
    Write-Host "`n🚀 Iniciando servidor Flask..." -ForegroundColor Yellow
    Write-Host "   Presiona Ctrl+C para detener el servidor" -ForegroundColor Yellow
    Write-Host "   API disponible en: http://localhost:5000" -ForegroundColor Cyan
    python run.py
}