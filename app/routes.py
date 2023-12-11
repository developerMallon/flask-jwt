from flask import g, render_template, request, redirect, url_for, flash, make_response
from functools import wraps
from app import app
import requests
import jwt
import time
from dotenv import dotenv_values

# Essa chave de ser igual a CHAVE QUE A API UTILIZA PARA GERAR O TOKEN
config = dotenv_values(".env")

def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        print("Rota acessada:", request.endpoint)
        access_token = request.cookies.get('access_token')
        print("TOKEN LIDO: ", access_token)

        if not access_token:
            print("TOKEN NÃO ENCONTRADO")
            return redirect(url_for('login'))
        
        # Adicionado para contornar erro no redirect logo após o login
        time.sleep(1)
        print("access_token antes do try: ", access_token)
        try:
            jwt.decode(access_token, config['SECRET_KEY'], algorithms=['HS256'])
        except jwt.ExpiredSignatureError:
            print("TOKEN EXPIRADO: ", access_token)
            return redirect(url_for('login'))
        except jwt.InvalidTokenError:
            print("TOKEN INVALIDO: ", access_token)
            return redirect(url_for('login'))

        return f(*args, **kwargs)

    return decorated

@app.route('/')
@token_required
def index():
    return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    print("Rota acessada:", request.endpoint)
    if request.method == 'POST':
        email = request.form['username']
        password = request.form['password']
        data = { "email": email, "password": password }
        # Autentica na API   
        get_token = requests.post(f"{config['BASE_URL']}/login", data=data)
        
        # Se a resposta for OK extrai o access_token
        if get_token.status_code == 200:
            get_token_data = get_token.json()
            access_token = get_token_data['0']['access_token']

            # Salva o token em um cookie e redireciona para a página index
            response = redirect(url_for('index'))
            response.set_cookie('access_token', access_token, path='/')
            print("TOKEN GRAVADO: ", access_token)  

            return response
        else:
            flash('Login inválido. Verifique seu usuário e senha.', 'error')
            return render_template('login.html')

    return render_template('login.html')

@app.route('/pecas')
@token_required
def pecas():

    return render_template('pecas.html')

@app.route('/servicos')
@token_required
def servicos():

    return render_template('servicos.html')

@app.route('/oficina')
@token_required
def oficina():

    return render_template('oficina.html')

@app.route('/logout')
@token_required
def logout():
    response = redirect(url_for('index'))
    response.set_cookie('access_token', '', expires=0)

    return response

