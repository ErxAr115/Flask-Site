from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
from flask_login import LoginManager, login_user, logout_user, login_required
from flask_mysqldb import MySQL
from config import config
from models.ModelUser import ModelUser
from models.entities.User import User

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

@app.route('/categorias', methods = ['GET', 'POST'])
@login_required
def categorias():
    if request.method == 'POST':
        try:
            tipo = request.form['Tipo']
            cursor = db.connection.cursor()
            sql = "SELECT categoria, COUNT(id) FROM registro_test GROUP BY categoria ORDER BY categoria ASC"
            cursor.execute(sql)
            data = cursor.fetchall()
            print(data)
        except Exception as ex:
            raise Exception(ex)
        return render_template('graficas/categorias.html', data=data, tipo=tipo)
    else:
        return render_template('graficas/categorias.html')

@app.route('/fechas', methods=['GET', 'POST'])
@login_required
def fechas():
    if request.method == 'POST':
        try:
            From = request.form['From']
            To = request.form['To']
            tipo = request.form['Tipo']
            cursor = db.connection.cursor()
            sql = "SELECT categoria, COUNT(id) FROM registro_test WHERE fecha_hora BETWEEN '{}' AND '{}' GROUP BY categoria ORDER By categoria ASC".format(From, To)
            cursor.execute(sql)
            data = cursor.fetchall()
            cursor.close()
            print(data)
            title = 'Periodo: ' + From + ' a ' + To
        except Exception as ex:
            raise Exception(ex)
        return render_template('graficas/fechas.html', data = data, title=title, tipo=tipo)
    else:
        return render_template('graficas/fechas.html')
    
@app.route('/encuestas', methods = ['GET', 'POST'])
@login_required
def encuestas():
    if request.method == 'GET':
        data = regresarEncuestas()
        return render_template('encuestas.html', data = data)
    else:
        encuestas = request.form['marca']
        print(encuestas)
        data = regresarEncuestas()
        return render_template('encuestas.html', data = data)


@app.route('/get_models', methods=['POST'])
def getModels():
    marca = request.form['marca']
    marca = int(marca)
    try:
        cursor = db.connection.cursor()
        sql = "SELECT idPregunta, Pregunta from pregunta where idEncuesta = {}".format(marca)
        cursor.execute(sql)
        data = cursor.fetchall()
        cursor.close()
    except Exception as ex:
        raise Exception(ex)
    modelo = [{'id': row[0], 'name': row[1]} for row in data]
    return jsonify({'modelo': modelo})

def regresarMes(mes:int):
    nombre = ''
    match mes:
        case 1: nombre = 'Enero'
        case 2: nombre = 'Febrero'
        case 3: nombre = 'Marzo'
        case 4: nombre = 'Abril'
        case 5: nombre = 'Mayo'
        case 6: nombre = 'Junio'
        case 7: nombre = 'Julio'
        case 8: nombre = 'Agosto'
        case 9: nombre = 'Septiembre'
        case 10: nombre = 'Octubre'
        case 11: nombre = 'Noviembre'
        case 12: nombre = 'Diciembre'
    return nombre

def regresarEncuestas():
    try:
        cursor = db.connection.cursor()
        sql = "SELECT idEncuesta, Nombre from encuesta"
        cursor.execute(sql)
        data = cursor.fetchall()
        cursor.close()
    except Exception as ex:
        raise Exception(ex)
    return data

def status401(error):
   return redirect(url_for('login'))

def status404(error):
    return render_template('notFound.html'), 404

if __name__ == '__main__':
    app.config.from_object(config['development'])
    app.register_error_handler(401, status401)
    app.register_error_handler(404, status404)
    app.run()