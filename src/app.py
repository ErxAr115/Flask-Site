from flask import Flask, render_template, request, redirect, url_for, flash
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

@app.route('/prueba', methods=['GET', 'POST'])
@login_required
def prueba():
    if request.method == 'GET':
        data = regresarPreguntas(1)
        return render_template('encuestas/prueba.html', data = data)
    elif request.method == 'POST':
        data = regresarPreguntas(1)
        pregunta = request.form.get('pregunta')
        pregunta = int(pregunta)
        mes = int(request.form.get('mes'))
        year = int(request.form.get('year'))
        print(mes, year)
        try:
            cursor = db.connection.cursor()
            sql = "SELECT R.Respuesta, COUNT(RE.respuesta) FROM respuesta R JOIN regencuesta RE on R.idRespuesta = RE.respuesta WHERE (R.idPregunta = {} AND MONTH(RE.fecha_hora) = {} AND YEAR(RE.fecha_hora) = {}) GROUP BY R.Respuesta".format(pregunta, mes, year)
            cursor.execute(sql)
            respuestas = cursor.fetchall()
            query = "Select Pregunta FROM pregunta WHERE idPregunta = {}".format(pregunta)
            cursor.execute(query)
            preg = cursor.fetchone()
            preg = preg[0]
            nombreMes = regresarMes(mes)
            preg = preg + ' (' + nombreMes + ' - ' + str(year) + ')'
        except Exception as ex:
            raise Exception(ex)
        return render_template('encuestas/prueba.html', data = data, respuestas = respuestas, preg = preg)

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

def regresarPreguntas(idEncuesta):
    try:
        cursor = db.connection.cursor()
        sql = "SELECT idPregunta, Pregunta from pregunta where idEncuesta = {}".format(idEncuesta)
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