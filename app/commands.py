"""
Comandos personalizados de Flask para gestión del sistema
"""

import click
from flask import current_app
from flask.cli import with_appcontext
# Removido: from werkzeug.security import generate_password_hash - usamos bcrypt
from .models import db, User, Equipo


@click.command()
@click.option('--reset', is_flag=True, help='Resetear datos existentes')
@with_appcontext
def init_roles(reset):
    """Inicializa el sistema de roles con datos básicos."""
    
    if reset:
        click.echo('🔄 Reseteando sistema de roles...')
        # Limpiar asignaciones existentes
        from sqlalchemy import text
        db.session.execute(text("DELETE FROM user_equipos"))
        # Resetear usuarios a solo admin
        User.query.filter(User.username != 'admin').delete()
        db.session.commit()
    
    click.echo('🚀 Inicializando sistema de roles...')
    
    # 1. Configurar usuario admin
    admin = User.query.filter_by(username='admin').first()
    if admin:
        admin.role = 'admin'
        click.echo('👑 Usuario admin configurado')
    else:
        click.echo('❌ Usuario admin no encontrado. Créalo primero.')
        return
    
    # 2. Crear usuario de prueba (usando bcrypt)
    from flask_bcrypt import Bcrypt
    bcrypt = Bcrypt(current_app)
    
    palula = User.query.filter_by(username='palula').first()
    if not palula:
        palula = User(
            username='palula',
            password=bcrypt.generate_password_hash('palula123').decode('utf-8'),
            role='user'
        )
        db.session.add(palula)
        click.echo('👤 Usuario palula creado')
    else:
        palula.role = 'user'
        palula.password = bcrypt.generate_password_hash('palula123').decode('utf-8')
        click.echo('👤 Usuario palula actualizado')
    
    db.session.commit()
    
    # 3. Asignar todos los equipos al admin
    equipos = Equipo.query.all()
    admin_equipos_count = 0
    
    for equipo in equipos:
        if equipo not in admin.equipos_asignados:
            admin.equipos_asignados.append(equipo)
            admin_equipos_count += 1
    
    # 4. Asignar primer equipo a palula
    if equipos and equipos[0] not in palula.equipos_asignados:
        palula.equipos_asignados.append(equipos[0])
        click.echo(f'🔗 Equipo "{equipos[0].nombre}" asignado a palula')
    
    db.session.commit()
    
    # Mostrar resumen
    total_equipos = len(equipos)
    palula_equipos = len(palula.get_equipos_permitidos())
    
    click.echo(f'\n📊 RESUMEN:')
    click.echo(f'👑 Admin: ve {total_equipos} equipos')
    click.echo(f'👤 Palula: ve {palula_equipos} equipo(s)')
    click.echo(f'🖥️ Total equipos: {total_equipos}')
    
    click.echo(f'\n🔐 Credenciales:')
    click.echo(f'   Admin: admin / admin123')
    click.echo(f'   Usuario: palula / palula123')
    
    click.echo(f'\n✅ Sistema de roles inicializado correctamente!')


@click.command()
@with_appcontext  
def show_roles():
    """Muestra el estado actual del sistema de roles."""
    
    click.echo('📊 ESTADO DEL SISTEMA DE ROLES')
    click.echo('=' * 40)
    
    users = User.query.all()
    
    for user in users:
        equipos_count = len(user.get_equipos_permitidos())
        role_emoji = '👑' if user.is_admin() else '👤'
        
        click.echo(f'{role_emoji} {user.username} ({user.role}): {equipos_count} equipos')
        
        if not user.is_admin() and equipos_count > 0:
            for equipo in user.get_equipos_permitidos():
                click.echo(f'   🖥️ {equipo.nombre}')
    
    total_equipos = Equipo.query.count()
    total_users = User.query.count()
    admins = User.query.filter_by(role='admin').count()
    
    click.echo(f'\n📈 Estadísticas:')
    click.echo(f'   Usuarios totales: {total_users}')
    click.echo(f'   Administradores: {admins}')
    click.echo(f'   Equipos totales: {total_equipos}')


@click.command()
@click.argument('username')
@click.argument('equipo_id', type=int)
@with_appcontext
def assign_equipment(username, equipo_id):
    """Asigna un equipo a un usuario."""
    
    user = User.query.filter_by(username=username).first()
    if not user:
        click.echo(f'❌ Usuario {username} no encontrado')
        return
    
    equipo = Equipo.query.get(equipo_id)
    if not equipo:
        click.echo(f'❌ Equipo ID {equipo_id} no encontrado')
        return
    
    if equipo in user.equipos_asignados:
        click.echo(f'⚠️ Equipo {equipo.nombre} ya está asignado a {username}')
        return
    
    user.equipos_asignados.append(equipo)
    db.session.commit()
    
    click.echo(f'✅ Equipo "{equipo.nombre}" asignado a {username}')


@click.command()
@click.argument('username')
@click.argument('equipo_id', type=int)
@with_appcontext
def unassign_equipment(username, equipo_id):
    """Desasigna un equipo de un usuario."""
    
    user = User.query.filter_by(username=username).first()
    if not user:
        click.echo(f'❌ Usuario {username} no encontrado')
        return
    
    equipo = Equipo.query.get(equipo_id)
    if not equipo:
        click.echo(f'❌ Equipo ID {equipo_id} no encontrado')
        return
    
    if equipo not in user.equipos_asignados:
        click.echo(f'⚠️ Equipo {equipo.nombre} no está asignado a {username}')
        return
    
    user.equipos_asignados.remove(equipo)
    db.session.commit()
    
    click.echo(f'✅ Equipo "{equipo.nombre}" desasignado de {username}')


@click.command()
@click.option('--force', is_flag=True, help='Forzar migración sin confirmación')
@with_appcontext
def setup_system(force):
    """Configuración completa del sistema de roles desde cero."""
    
    if not force:
        click.echo('🚀 CONFIGURACIÓN COMPLETA DEL SISTEMA DE ROLES')
        click.echo('=' * 50)
        click.echo('Este comando hará:')
        click.echo('1. Backup de la base de datos actual')
        click.echo('2. Aplicar migraciones pendientes')
        click.echo('3. Inicializar sistema de roles')
        click.echo('4. Configurar usuarios por defecto')
        click.echo('')
        
        if not click.confirm('¿Continuar?'):
            click.echo('Operación cancelada')
            return
    
    import os
    from datetime import datetime
    from flask_migrate import upgrade
    from sqlalchemy import text
    
    click.echo('📁 Creando backup...')
    try:
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        backup_file = f'instance/equipos_backup_{timestamp}.db'
        
        import shutil
        if os.path.exists('instance/equipos.db'):
            shutil.copy2('instance/equipos.db', backup_file)
            click.echo(f'✅ Backup creado: {backup_file}')
        else:
            click.echo('⚠️ No se encontró base de datos existente')
    except Exception as e:
        click.echo(f'❌ Error creando backup: {e}')
        if not force:
            return
    
    click.echo('🔄 Aplicando migraciones...')
    try:
        upgrade()
        click.echo('✅ Migraciones aplicadas exitosamente')
    except Exception as e:
        click.echo(f'❌ Error en migración: {e}')
        return
    
    click.echo('🔍 Verificando estructura de base de datos...')
    try:
        inspector = db.inspect(db.engine)
        tables = inspector.get_table_names()
        
        required_tables = ['user', 'equipo', 'user_equipos']
        missing_tables = [t for t in required_tables if t not in tables]
        
        if missing_tables:
            click.echo(f'❌ Faltan tablas: {missing_tables}')
            return
        
        # Verificar columnas de user
        user_columns = [col['name'] for col in inspector.get_columns('user')]
        if 'role' not in user_columns:
            click.echo('❌ Falta columna role en tabla user')
            return
        
        click.echo('✅ Estructura de base de datos verificada')
        click.echo(f'   Tablas: {len(tables)} encontradas')
        click.echo(f'   Columnas user: {user_columns}')
        
    except Exception as e:
        click.echo(f'❌ Error verificando estructura: {e}')
        return
    
    click.echo('👥 Inicializando usuarios y roles...')
    try:
        from flask_bcrypt import Bcrypt
        bcrypt = Bcrypt(current_app)
        
        # 1. Configurar usuario admin
        admin = User.query.filter_by(username='admin').first()
        if not admin:
            admin = User(
                username='admin',
                password=bcrypt.generate_password_hash('admin123').decode('utf-8'),
                role='admin'
            )
            db.session.add(admin)
            click.echo('✅ Usuario admin creado')
        else:
            admin.role = 'admin'
            admin.password = bcrypt.generate_password_hash('admin123').decode('utf-8')
            click.echo('✅ Usuario admin actualizado')
        
        # 2. Crear/actualizar usuarios de prueba
        test_users = [
            ('palula', 'palula123'),
            ('luis', 'luis123')
        ]
        
        created_users = []
        for username, password in test_users:
            user = User.query.filter_by(username=username).first()
            if not user:
                user = User(
                    username=username,
                    password=bcrypt.generate_password_hash(password).decode('utf-8'),
                    role='user'
                )
                db.session.add(user)
                click.echo(f'👤 Usuario {username} creado')
            else:
                user.role = 'user'
                user.password = bcrypt.generate_password_hash(password).decode('utf-8')
                click.echo(f'👤 Usuario {username} actualizado')
            created_users.append(user)
        
        db.session.commit()
        
        # 3. Asignar equipos
        equipos = Equipo.query.all()
        
        # Admin ve todos los equipos
        for equipo in equipos:
            if equipo not in admin.equipos_asignados:
                admin.equipos_asignados.append(equipo)
        
        # Asignar primer equipo a usuarios de prueba
        if equipos and created_users:
            for i, user in enumerate(created_users):
                if i < len(equipos) and equipos[i] not in user.equipos_asignados:
                    user.equipos_asignados.append(equipos[i])
                    click.echo(f'🔗 Equipo "{equipos[i].nombre}" asignado a {user.username}')
        
        db.session.commit()
        
    except Exception as e:
        click.echo(f'❌ Error inicializando usuarios y roles: {e}')
        return
    
    click.echo('')
    click.echo('🎉 SISTEMA CONFIGURADO EXITOSAMENTE')
    click.echo('=' * 40)
    click.echo('📊 Estado del sistema:')
    
    # Mostrar estado final
    try:
        users = User.query.all()
        
        for user in users:
            equipos_count = len(list(user.get_equipos_permitidos()))
            role_emoji = '👑' if user.is_admin() else '👤'
            
            click.echo(f'{role_emoji} {user.username} ({user.role}): {equipos_count} equipos')
            
            if not user.is_admin() and equipos_count > 0:
                for equipo in user.get_equipos_permitidos():
                    click.echo(f'   🖥️ {equipo.nombre}')
        
        total_equipos = Equipo.query.count()
        total_users = User.query.count()
        admins = User.query.filter_by(role='admin').count()
        
        click.echo(f'📈 Estadísticas:')
        click.echo(f'   Usuarios totales: {total_users}')
        click.echo(f'   Administradores: {admins}')
        click.echo(f'   Equipos totales: {total_equipos}')
        
    except Exception as e:
        click.echo(f'Error mostrando estado: {e}')
    
    click.echo('')
    click.echo('🔐 Credenciales configuradas:')
    click.echo('   👑 Admin:  admin / admin123')
    click.echo('   👤 Usuario: palula / palula123')
    click.echo('   👤 Usuario: luis / luis123')
    click.echo('')
    click.echo('🚀 Próximos pasos:')
    click.echo('   1. Iniciar servidor: python run.py')
    click.echo('   2. Probar API: http://localhost:5000/api/auth/login')
    click.echo('   3. Gestionar equipos: python -m flask assign-equipment <usuario> <equipo>')


@click.command()
@with_appcontext
def verify_system():
    """Verifica que el sistema de roles esté funcionando correctamente."""
    
    click.echo('🔍 VERIFICACIÓN DEL SISTEMA DE ROLES')
    click.echo('=' * 40)
    
    # Verificar tablas
    click.echo('📋 Verificando tablas...')
    try:
        inspector = db.inspect(db.engine)
        tables = inspector.get_table_names()
        
        required_tables = ['user', 'equipo', 'user_equipos', 'alembic_version']
        
        for table in required_tables:
            if table in tables:
                click.echo(f'   ✅ {table}')
            else:
                click.echo(f'   ❌ {table} (FALTANTE)')
        
    except Exception as e:
        click.echo(f'❌ Error verificando tablas: {e}')
        return
    
    # Verificar usuarios
    click.echo('\n👥 Verificando usuarios...')
    try:
        users = User.query.all()
        admin_count = User.query.filter_by(role='admin').count()
        user_count = User.query.filter_by(role='user').count()
        
        click.echo(f'   Total usuarios: {len(users)}')
        click.echo(f'   Administradores: {admin_count}')
        click.echo(f'   Usuarios normales: {user_count}')
        
        # Verificar admin específico
        admin = User.query.filter_by(username='admin').first()
        if admin and admin.role == 'admin':
            click.echo('   ✅ Usuario admin configurado correctamente')
        else:
            click.echo('   ❌ Usuario admin no encontrado o mal configurado')
            
    except Exception as e:
        click.echo(f'❌ Error verificando usuarios: {e}')
    
    # Verificar equipos
    click.echo('\n🖥️ Verificando equipos...')
    try:
        equipos = Equipo.query.all()
        click.echo(f'   Total equipos: {len(equipos)}')
        
        if equipos:
            # Verificar si tienen las nuevas columnas
            sample_equipo = equipos[0]
            has_estado = hasattr(sample_equipo, 'estado')
            has_descripcion = hasattr(sample_equipo, 'descripcion')
            
            click.echo(f'   ✅ Columna estado: {"Sí" if has_estado else "No"}')
            click.echo(f'   ✅ Columna descripción: {"Sí" if has_descripcion else "No"}')
        
    except Exception as e:
        click.echo(f'❌ Error verificando equipos: {e}')
    
    # Verificar asignaciones
    click.echo('\n🔗 Verificando asignaciones...')
    try:
        from sqlalchemy import text
        result = db.session.execute(text('SELECT COUNT(*) FROM user_equipos')).scalar()
        click.echo(f'   Asignaciones totales: {result}')
        
    except Exception as e:
        click.echo(f'❌ Error verificando asignaciones: {e}')
    
    click.echo('\n✅ Verificación completada')


@click.command()
@click.argument('username')
@click.argument('password')
@click.option('--role', default='user', help='Rol del usuario (admin/user)')
@with_appcontext
def create_user(username, password, role):
    """Crear un nuevo usuario con bcrypt."""
    
    # Verificar si el usuario ya existe
    existing_user = User.query.filter_by(username=username).first()
    if existing_user:
        click.echo(f'❌ Error: El usuario {username} ya existe')
        return
    
    # Validar rol
    if role not in ['admin', 'user']:
        click.echo(f'❌ Error: Rol debe ser "admin" o "user", no "{role}"')
        return
    
    # Crear usuario con bcrypt
    from flask_bcrypt import Bcrypt
    bcrypt = Bcrypt(current_app)
    
    new_user = User(
        username=username,
        password=bcrypt.generate_password_hash(password).decode('utf-8'),
        role=role
    )
    
    db.session.add(new_user)
    db.session.commit()
    
    role_emoji = '👑' if role == 'admin' else '👤'
    click.echo(f'✅ Usuario creado: {role_emoji} {username} ({role})')


def init_app(app):
    """Registra los comandos en la aplicación Flask."""
    app.cli.add_command(init_roles)
    app.cli.add_command(show_roles)
    app.cli.add_command(assign_equipment)
    app.cli.add_command(unassign_equipment)
    app.cli.add_command(setup_system)
    app.cli.add_command(verify_system)
    app.cli.add_command(create_user)