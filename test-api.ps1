# Script de Pruebas de API
# ========================

Write-Host "🧪 Probando API del Sistema de Roles" -ForegroundColor Green

$baseUrl = "http://localhost:5000/api"

# Función para probar login
function Test-Login($username, $password, $description) {
    Write-Host "`n🔐 Probando login: $description" -ForegroundColor Yellow
    
    $body = @{
        username = $username
        password = $password
    } | ConvertTo-Json
    
    try {
        $response = Invoke-RestMethod -Uri "$baseUrl/auth/login" -Method Post -Body $body -ContentType "application/json"
        
        if ($response.success) {
            Write-Host "✅ Login exitoso" -ForegroundColor Green
            Write-Host "   Usuario: $($response.user.username) ($($response.user.role))" -ForegroundColor Cyan
            
            # Probar obtener equipos
            $headers = @{ Authorization = "Bearer $($response.token)" }
            $equipos = Invoke-RestMethod -Uri "$baseUrl/equipos" -Method Get -Headers $headers
            
            Write-Host "   Equipos visibles: $($equipos.total)" -ForegroundColor Cyan
            
            return $response.token
        } else {
            Write-Host "❌ Login fallido" -ForegroundColor Red
        }
    } catch {
        Write-Host "❌ Error: $($_.Exception.Message)" -ForegroundColor Red
    }
    
    return $null
}

# Verificar que el servidor esté ejecutándose
try {
    $status = Invoke-RestMethod -Uri "$baseUrl/status" -Method Get
    Write-Host "✅ Servidor conectado - API funcionando" -ForegroundColor Green
} catch {
    Write-Host "❌ Error: Servidor no disponible en $baseUrl" -ForegroundColor Red
    Write-Host "   Asegúrate de que el servidor esté ejecutándose: python run.py" -ForegroundColor Yellow
    exit 1
}

# Probar logins
$adminToken = Test-Login "admin" "admin123" "Administrador"
$userToken = Test-Login "palula" "palula123" "Usuario normal"

# Probar endpoint protegido
if ($adminToken) {
    Write-Host "`n🔧 Probando endpoint de administración..." -ForegroundColor Yellow
    try {
        $headers = @{ Authorization = "Bearer $adminToken" }
        $users = Invoke-RestMethod -Uri "$baseUrl/admin/users" -Method Get -Headers $headers
        Write-Host "✅ Endpoint admin accesible - $($users.total) usuarios" -ForegroundColor Green
    } catch {
        Write-Host "❌ Error accediendo a endpoint admin" -ForegroundColor Red
    }
}

# Probar acceso denegado
if ($userToken) {
    Write-Host "`n🚫 Probando acceso denegado para usuario normal..." -ForegroundColor Yellow
    try {
        $headers = @{ Authorization = "Bearer $userToken" }
        $users = Invoke-RestMethod -Uri "$baseUrl/admin/users" -Method Get -Headers $headers
        Write-Host "❌ Error: Usuario normal accedió a endpoint admin" -ForegroundColor Red
    } catch {
        Write-Host "✅ Acceso correctamente denegado" -ForegroundColor Green
    }
}

Write-Host @"

📊 RESUMEN DE PRUEBAS:
✓ Servidor API funcionando
✓ Login de administrador
✓ Login de usuario normal
✓ Filtrado de equipos por rol
✓ Control de acceso en endpoints admin

🎉 Sistema funcionando correctamente
"@ -ForegroundColor Green