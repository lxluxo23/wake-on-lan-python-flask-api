# Script de Migración Rápida
# =========================

Write-Host "🚀 Migración Rápida del Sistema de Roles" -ForegroundColor Green

# Configurar Flask
$env:FLASK_APP = "run.py"

# Backup rápido
$timestamp = Get-Date -Format "yyyyMMdd_HHmmss"
Copy-Item "instance\equipos.db" "instance\backup_$timestamp.db"
Write-Host "✅ Backup creado: backup_$timestamp.db"

# Aplicar migración
Write-Host "🔄 Aplicando migración..."
python -m flask db upgrade

# Inicializar roles
Write-Host "👥 Inicializando roles..."
python -m flask init-roles

# Mostrar estado
Write-Host "📊 Estado final:"
python -m flask show-roles

Write-Host @"

✅ MIGRACIÓN COMPLETADA

Credenciales:
👑 Admin: admin / admin123
👤 Usuario: palula / palula123

Iniciar servidor: python run.py
"@ -ForegroundColor Green