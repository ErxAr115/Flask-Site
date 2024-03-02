from flask import Flask, render_template, request, redirect, url_for, flash
from flask_login import LoginManager, login_user, logout_user, login_required
from flask_mysqldb import MySQL
from config import config
from models.ModelUser import ModelUser
from models.entities.User import User
from datetime import datetime

app = Flask(__name__)
db = MySQL(app)
login_manager_app = LoginManager(app)

@login_manager_app.user_loader
def load_user(id):
    return ModelUser.getByID(db, id)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        user = User(0, request.form['email'], request.form['password'])
        logged_user = ModelUser.login(db, user)
        if logged_user != None:
            if logged_user.password:
                login_user(logged_user)
                return redirect(url_for('home'))
            else:
                flash('Contraseña Incorrecta')
                return render_template('auth/login.html')
        else:
            flash('Usuario no encontrado')
            return render_template('auth/login.html')
    else:
        return render_template('auth/login.html')
    
@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('login'))
    
@app.route('/home')
@login_required
def home():
    return render_template('home.html')

@app.route('/categorias')
@login_required
def categorias():
    try:
        cursor = db.connection.cursor()
        sql = "SELECT categoria, COUNT(id) FROM registro_test GROUP BY categoria ORDER BY categoria ASC"
        cursor.execute(sql)
        data = cursor.fetchall()
        print(data)
        cursor.close()
    except Exception as ex:
        raise Exception(ex)
    return render_template('graficas/categorias.html', data = data)

@app.route('/fechas', methods=['GET', 'POST'])
@login_required
def fechas():
    if request.method == 'POST':
        try:
            From = request.form['From']
            To = request.form['To']
            cursor = db.connection.cursor()
            sql = "SELECT categoria, COUNT(id) FROM registro_test WHERE fecha_hora BETWEEN '{}' AND '{}' GROUP BY categoria ORDER By categoria ASC".format(From, To)
            cursor.execute(sql)
            data = cursor.fetchall()
            cursor.close()
            print(data)
        except Exception as ex:
            raise Exception(ex)
        return render_template('graficas/fechas.html', data = data)
    else:
        return render_template('graficas/fechas.html')
    
@app.route('/encuestas')
@login_required
def encuestas():
    return render_template('encuestas.html')

def status401(error):
   return redirect(url_for('login'))

def status404(error):
    return render_template('notFound.html'), 404

def convertToList(row, indice):
    lista_numeros = []
    for element in row:
        num = element[indice]
        lista_numeros.append(num)
    return lista_numeros

if __name__ == '__main__':
    app.config.from_object(config['development'])
    app.register_error_handler(401, status401)
    app.register_error_handler(404, status404)
    app.run()