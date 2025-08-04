import click
from flask.cli import with_appcontext
from app.extensions import db
from app.models import User
from werkzeug.security import generate_password_hash

@click.command('init-db')
@with_appcontext
def init_db_command():
    """Inicializar la base de datos."""
    db.create_all()
    click.echo('Base de datos inicializada.')

@click.command('create-admin')
@click.argument('username')
@click.argument('password')
@click.argument('email')
@with_appcontext
def create_admin_command(username, password, email):
    """Crear un usuario administrador."""
    user = User.query.filter_by(username=username).first()
    
    if user:
        click.echo(f'El usuario {username} ya existe.')
        return
        
    user = User(
        username=username,
        name='Administrador',
        email=email,
        password_hash=generate_password_hash(password)
    )
    
    db.session.add(user)
    db.session.commit()
    
    click.echo(f'Usuario {username} creado exitosamente.')

def register_commands(app):
    """Registrar comandos CLI en la aplicación."""
    app.cli.add_command(init_db_command)
    app.cli.add_command(create_admin_command)