from flask import Flask, render_template, redirect, url_for, request, flash
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from flask_mysqldb import MySQL
from datetime import datetime, timedelta

app = Flask(__name__)
app.secret_key = 'your_secret_key'

# MySQL Configuration
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = 'radhika'
app.config['MYSQL_DB'] = 'shortlinker'
mysql = MySQL(app)

# Flask-Login Configuration
login_manager = LoginManager(app)
login_manager.login_view = 'login'

# User Class for Flask-Login
class User(UserMixin):
    pass

@login_manager.user_loader
def load_user(user_id):
    cursor = mysql.connection.cursor()
    cursor.execute('SELECT * FROM users WHERE id = %s', (user_id,))
    user_data = cursor.fetchone()
    if user_data:
        user = User()
        user.id = user_data[0]
        return user
    return None

# Routes
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        cursor = mysql.connection.cursor()
        cursor.execute('SELECT * FROM users WHERE username = %s', (username,))
        user_data = cursor.fetchone()

        if user_data and user_data[2] == password:
            user = User()
            user.id = user_data[0]
            login_user(user)
            flash('Logged in successfully!', 'success')
            return redirect(url_for('dashboard'))
        else:
            flash('Invalid username or password', 'error')

    return render_template('login.html')

@app.route('/dashboard')
@login_required
def dashboard():
    return render_template('dashboard.html', user=current_user)

@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Logged out successfully!', 'success')
    return redirect(url_for('index'))

@app.route('/shorten', methods=['POST'])
@login_required
def shorten():
    if request.method == 'POST':
        original_url = request.form['original_url']
        expiration_date = datetime.utcnow() + timedelta(days=2)

        cursor = mysql.connection.cursor()
        cursor.execute('INSERT INTO links (user_id, original_url, expiration_date) VALUES (%s, %s, %s)',
                       (current_user.id, original_url, expiration_date))
        mysql.connection.commit()

        flash('Short link created successfully!', 'success')

    return redirect(url_for('dashboard'))

@app.route('/analytics')
@login_required
def analytics():
    cursor = mysql.connection.cursor()
    cursor.execute('SELECT * FROM links WHERE user_id = %s', (current_user.id,))
    user_links = cursor.fetchall()

    return render_template('analytics.html', user=current_user, user_links=user_links)

if __name__ == '__main__':
    app.run(debug=True,host='localhost',port=8000,use_reloader=False)
