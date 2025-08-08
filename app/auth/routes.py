from flask import (
    render_template, flash, redirect, url_for, request, 
    jsonify, session, current_app
)
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField
from wtforms.validators import DataRequired, Length, Regexp
import os
from werkzeug.security import generate_password_hash, check_password_hash
from app.auth import bp
from app.models import User
from app.extensions import db, csrf
from functools import wraps
import jwt
from datetime import datetime, timedelta
import re

class LoginForm(FlaskForm):
    username = StringField('Usuario', validators=[
        DataRequired(),
        Length(min=3, max=20),
        Regexp(r'^[a-zA-Z0-9_-]+$', message='El usuario solo puede contener letras, números, guiones y guiones bajos')
    ])
    password = PasswordField('Contraseña', validators=[
        DataRequired(),
        Length(min=8),
        Regexp(r'^(?=.*[A-Za-z])(?=.*\d)[A-Za-z\d]{8,}$', 
            message='La contraseña debe tener al menos 8 caracteres, incluyendo al menos una letra y un número')
    ])

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        token = None
        
        # Verificar si hay token en la cabecera Authorization
        if 'Authorization' in request.headers:
            auth_header = request.headers['Authorization']
            if auth_header.startswith('Bearer '):
                token = auth_header.split(' ')[1]
        
        # También verificar en cookies o session
        if not token:
            token = session.get('token')
            
        if not token:
            if request.is_json:
                return jsonify({'error': 'No autorizado'}), 401
            flash('Por favor inicie sesión para acceder a esta página', 'error')
            return redirect(url_for('auth.login'))
            
        try:
            # Decodificar token
            data = jwt.decode(
                token, 
                current_app.config['SECRET_KEY'],
                algorithms=['HS256']
            )
            
            # Obtener usuario actual
            current_user = User.query.get(data['sub'])
            if not current_user:
                raise Exception('Usuario no encontrado')
                
        except Exception as e:
            if request.is_json:
                return jsonify({'error': str(e)}), 401
            flash('Sesión inválida. Por favor inicie sesión nuevamente.', 'error')
            return redirect(url_for('auth.login'))
            
        # Agregar usuario al contexto
        return f(current_user, *args, **kwargs)
        
    return decorated_function

@bp.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    
    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data
        
        # Verificar credenciales
        user = User.query.filter_by(username=username).first()
        
        if not user or not check_password_hash(user.password_hash, password):
            flash('Usuario o contraseña incorrectos', 'error')
            return redirect(url_for('auth.login'))
            
        # Limpiar sesiones anteriores
        session.clear()
            
        # Generar token JWT con más claims de seguridad
        token = jwt.encode({
            'sub': user.id,
            'name': user.name,
            'iat': datetime.utcnow(),
            'exp': datetime.utcnow() + timedelta(hours=24),
            'jti': os.urandom(16).hex(),  # JWT ID único
            'ip': request.remote_addr
        }, current_app.config['SECRET_KEY'], algorithm='HS256')
        
        # Guardar token en session con httponly
        session['token'] = token
        session.permanent = True  # Usar duración configurada de la sesión
        
        return redirect(url_for('main.index'))
        
    return render_template('auth/login.html', form=form)

@bp.route('/logout')
def logout():
    session.pop('token', None)
    flash('Has cerrado sesión correctamente', 'success')
    return redirect(url_for('auth.login'))

@bp.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        name = request.form.get('name')
        email = request.form.get('email')
        
        # Verificar si el usuario ya existe
        existing_user = User.query.filter(
            (User.username == username) | (User.email == email)
        ).first()
        
        if existing_user:
            flash('El usuario o email ya está registrado', 'error')
            return redirect(url_for('auth.register'))
            
        # Crear nuevo usuario
        new_user = User(
            username=username,
            name=name,
            email=email,
            password_hash=generate_password_hash(password)
        )
        
        db.session.add(new_user)
        db.session.commit()
        
        flash('Usuario registrado exitosamente. Por favor inicie sesión.', 'success')
        return redirect(url_for('auth.login'))
        
    return render_template('auth/register.html')