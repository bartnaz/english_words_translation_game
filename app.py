from flask import Flask, render_template, url_for, request, flash, redirect
import sqlite3, os
from random import randrange

app = Flask(__name__)

#secret key config 
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY')

#program variables store
class DataStore():
    dbase = None
    random_num = None
    table_count = None
    pol1 = None
    slowko = None
    tlumaczenie = None
    points = None
data = DataStore()

class number_control():
    control_list = []

class finish_indicator():
    finish = None

@app.route('/')
def home():
    return render_template('homepage.html')

@app.route('/about_page')
def about_page():
    return render_template('about_page.html')

@app.route('/end_page')
def end_page():
    return render_template('end_page.html')

@app.route('/subject_selection', methods=['POST', 'GET'])
def subject_selection():
    #init case after game over - clear control list and reset finish game indicator
    control_list = []
    number_control.control_list = control_list
    finish_indicator.finish = None
    #back to main case - subject selection
    if request.method == 'POST':
        if request.form["submit_button"] == "Graj w budynki":
            data.dbase='wordlist'
            return redirect(url_for("program"))
        elif request.form["submit_button"] == "Graj w odzież":
            data.dbase='clothes'
            return redirect(url_for("program"))
        elif request.form["submit_button"] == "Graj w uczucia":
            data.dbase='emotions'
            return redirect(url_for("program"))
        else:
            return render_template('homepage.html')
    else:
        return render_template('subject_selection.html')

def db_connection():
    #function to establish database connection
    words = sqlite3.connect('wordsbase.db')
    return words

def generate_randnum():
    #db connection
    words = sqlite3.connect('wordsbase.db')
    w = words.cursor()
    #count number of rows in main table
    dbase = data.dbase
    w.execute("SELECT COUNT(*) FROM {}".format(dbase))
    elems = w.fetchall()
    for i in elems:
        table_count = i[0]

    #generate random number in range (1, last row number in table); declare variables to Class
    losowanie = True
    control_list = number_control.control_list
    while losowanie == True:
        #stop generating numbers when control list table is equal to word list lenght
        if len(control_list) == table_count - 1:
            losowanie == False
            finish_indicator.finish = True
            return None
        else:
            random_num = randrange(1,table_count+1)
            if random_num in control_list:
                losowanie = True
            else:
                number_control.control_list.append(random_num)
                losowanie = False 
    #pass data to external class variables
    data.random_num = random_num
    data.table_count = table_count
    return random_num, table_count

def show_random_words():
    #db connection
    words = db_connection()
    w = words.cursor()
    #variables input
    dbase = data.dbase
    random_num = data.random_num
    points = 1
    #select row from table with id_number corresponding to generated random_num    
    w.execute("SELECT pol, ang FROM {} WHERE emp_id = {}".format(dbase, random_num))
    wordss = w.fetchall()
    #loop over query results
    for g in wordss:
        pol = g[0]
        word = g[1] 

    #prepare word to translate
    pol1 = pol
    data.pol1 = pol1 
    #prepare english translation of word pol1
    slowko = word
    data.slowko = slowko
    #request user translation of word pol1
    tlumaczenie = request.form.get('tlumaczenie')
    data.tlumaczenie = tlumaczenie
    #save word and user input into processing table in wordbase.db
    params = [(int(points), str(slowko), str(tlumaczenie))]
    w.executemany("INSERT INTO processing VALUES (NULL, ?, ?, ?)", params)
    words.commit()
    return pol1, slowko, tlumaczenie

def answer_validator():
    words = db_connection()
    w = words.cursor()
    pol1 = data.pol1

    if request.method == 'POST':
        #user answer validation
        w.execute("SELECT slowko FROM processing ORDER BY id DESC LIMIT 2")
        process = w.fetchall()
        slowko1 = process[1]

        w.execute("SELECT tlumaczenie FROM processing ORDER BY id DESC LIMIT 1")
        processs = w.fetchall()
        tlumaczenie1 = processs[0]           
        slowko = slowko1
        tlumaczenie = tlumaczenie1

        #compare user input to word pol1 translation
        if tlumaczenie == slowko:
            flash('Good answer', 'success')
            return render_template('program.html', pol1=pol1, tlumaczenie = request.form.get('tlumaczenie'))
        else:
            flash('Wrong answer', 'danger')
            return render_template('program.html', pol1=pol1, tlumaczenie = request.form.get('tlumaczenie'))   
    else:
        return render_template('program.html', pol1=pol1, tlumaczenie = request.form.get('tlumaczenie'))

    
@app.route('/program', methods=['POST', 'GET'])
def program():
    #function implementation
    if finish_indicator.finish == True:
        return redirect(url_for('end_page'))
    else:
        generate_randnum()
        show_random_words()
        pol1 = data.pol1
        #main case when user clicks "SUBMIT" button
        answer_validator()
        return render_template('program.html', pol1=pol1, tlumaczenie = request.form.get('tlumaczenie'))

if __name__ == '__main__':
    app.run(debug=False)


