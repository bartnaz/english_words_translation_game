import os
import sqlite3
from random import randrange

from flask import Flask, render_template, url_for, request, flash, redirect

app = Flask(__name__)

# secret key config
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY')


# program variables store
class DataStore:
    def __init__(self, dbase, random_num, table_count, pol1, tlumaczenie, points):
        self.dbase = dbase
        self.random_num = random_num
        self.table_count = table_count
        self.pol1 = pol1
        self.tlumaczenie = tlumaczenie
        self.points = points


class NumberControl:
    control_list = []


class FinishIndicator:
    finish = None


@app.route('/')
def home():
    return render_template('homepage.html')


@app.route('/about_page')
def about_page():
    return render_template('about_page.html')


def clear_processing():
    words = sqlite3.connect('wordsbase.db')
    w = words.cursor()
    w.execute("DELETE FROM better_processing")
    words.commit()
    words.close()
    return None


@app.route('/wordlist_display_selection', methods=['POST', 'GET'])
def wordlist_display_selection():
    # display wordlist selection
    if request.method == 'POST':
        if request.form["submit_button"] == "Pokaż budynki":
            DataStore.dbase = 'buildings'
            return redirect(url_for("wordlist_display"))
        elif request.form["submit_button"] == "Pokaż odzież":
            DataStore.dbase = 'clothes'
            return redirect(url_for("wordlist_display"))
        elif request.form["submit_button"] == "Pokaż uczucia":
            DataStore.dbase = 'emotions'
            return redirect(url_for("wordlist_display"))
        else:
            return render_template('homepage.html')
    else:
        return render_template('wordlist_display_selection.html')


@app.route('/wordlist_display', methods=['GET'])
def wordlist_display():
    # db connection
    words = sqlite3.connect('wordsbase.db')
    w = words.cursor()
    dbase = DataStore.dbase
    w.execute("SELECT emp_id, pol, ang0, ang1, ang2, ang3 FROM {}".format(dbase))
    results = w.fetchall()
    idnum = []
    polword = []
    engword = []
    eng1word = []
    eng2word = []
    eng3word = []
    for d in results:
        idnum.append(d[0])
        polword.append(d[1])
        engword.append(d[2])
        if d[3] != d[2]:
            eng1word.append(d[3])
        else:
            eng1word.append('-')

        if d[4] != d[2]:
            eng2word.append(d[4])
        else:
            eng2word.append('-')

        if d[5] != d[2]:
            eng3word.append(d[5])
        else:
            eng3word.append('-')

    return render_template('wordlist_display.html', results=results, idnum=idnum, polword=polword, engword=engword,
                           eng1word=eng1word, eng2word=eng2word, eng3word=eng3word)


@app.route('/subject_selection', methods=['POST', 'GET'])
def subject_selection():
    # init case after game over - clear control list and reset finish game indicator
    control_list = []
    NumberControl.control_list = control_list
    DataStore.points = 0
    FinishIndicator.finish = None
    # back to main case - subject selection
    if request.method == 'POST':
        if request.form["submit_button"] == "Graj w budynki":
            DataStore.dbase = 'buildings'
            return redirect(url_for("program"))
        elif request.form["submit_button"] == "Graj w odzież":
            DataStore.dbase = 'clothes'
            return redirect(url_for("program"))
        elif request.form["submit_button"] == "Graj w uczucia":
            DataStore.dbase = 'emotions'
            return redirect(url_for("program"))
        else:
            return render_template('homepage.html')
    else:
        return render_template('subject_selection.html')


def db_connection():
    # function to establish database connection
    words = sqlite3.connect('wordsbase.db')
    return words


def generate_randnum():
    # db connection
    words = sqlite3.connect('wordsbase.db')
    w = words.cursor()
    # count number of rows in words table database
    dbase = DataStore.dbase
    w.execute("SELECT COUNT(*) FROM {}".format(dbase))
    elems = w.fetchall()
    elems = elems[0]
    table_count = elems[0]

    # generate random number in range (1, last row number in table); declare variables to Class
    losowanie = True
    control_list = NumberControl.control_list
    while losowanie:
        # stop generating numbers when control list table is equal to word list lenght
        if len(control_list) == table_count:
            losowanie = False
            FinishIndicator.finish = True
            return None
        else:
            random_num = randrange(1, table_count + 1)
            if random_num in control_list:
                losowanie = True
            else:
                NumberControl.control_list.append(random_num)
                losowanie = False
    # pass data to external class variables
    DataStore.random_num = random_num
    DataStore.table_count = table_count
    return random_num


def show_random_words():
    # db connection
    words = db_connection()
    w = words.cursor()
    # variables input
    dbase = DataStore.dbase
    random_num = DataStore.random_num

    # select row from table with id_number corresponding to generated random_num
    w.execute("SELECT pol FROM {} WHERE emp_id = {}".format(dbase, random_num))
    wordss = w.fetchall()

    # loop over query results
    for g in wordss:
        pol = g[0]

    # prepare word to translate
    pol1 = pol
    DataStore.pol1 = pol1

    # request user translation of word pol1
    tlumaczenie = request.form.get('tlumaczenie')
    DataStore.tlumaczenie = tlumaczenie

    # pass user input to processing database for further validation
    w.execute("INSERT INTO better_processing (generated_num, tlumaczenie) VALUES (?, ?)", (random_num, tlumaczenie,))
    words.commit()
    return pol1, tlumaczenie


def answer_validator():
    words = db_connection()
    w = words.cursor()
    
    if request.method == 'POST':
        dbase = DataStore.dbase
        w.execute("SELECT * FROM better_processing ORDER BY id DESC LIMIT 2")
        processs = w.fetchall()
        r_n = processs[1]
        random_num = r_n[1]
        t_l = processs[0]
        tlumaczenie = t_l[2].lower()
        w.execute("SELECT * FROM {} WHERE emp_id = {}".format(dbase, random_num))
        data = w.fetchall()
        all = data[0]
        word = all[2::]

        if FinishIndicator.finish != True:
            # compare user input to word pol1 translation
            if tlumaczenie != '':
                if tlumaczenie in word:
                    flash('Good answer, you get 1 point', 'success')
                    DataStore.points = DataStore.points + 1
                else:
                    flash('Wrong answer', 'danger')
            else:
                flash('Wrong answer', 'danger')
        else: 
            pass
    else:
        return None


@app.route('/program', methods=['POST', 'GET'])
def program():
    # function implementation
    generate_randnum()
    show_random_words()
    pol1 = DataStore.pol1
    # main case when user clicks "SUBMIT" button
    answer_validator()
    points = DataStore.points
    max_points = DataStore.table_count - 1
    if FinishIndicator.finish:
        if points >= 0.75*max_points:
            score = 'good_score'
            clear_processing()
            return render_template('end_page.html', score = score, points = points, max_points = max_points)
        elif points >= 0.5*max_points:
            score = 'ok_score'
            clear_processing()
            return render_template('end_page.html', score = score, points = points, max_points = max_points)
        else:
            score = 'bad_score'
            clear_processing()
            return render_template('end_page.html', score = score, points = points, max_points = max_points)
    else:
        return render_template('program.html', points = points, max_points = max_points, pol1=pol1, tlumaczenie=request.form.get('tlumaczenie'))


if __name__ == '__main__':
    app.run(debug=False)