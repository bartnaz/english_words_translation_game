from flask import Flask, render_template, url_for, request, flash, redirect
import sqlite3, os
from random import randrange

app = Flask(__name__)

#secret key config 
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY')

class DataStore():
    dbase = None

data = DataStore()

@app.route('/')
def home():
    return render_template('homepage.html')

@app.route('/about_page')
def about_page():
    return render_template('about_page.html')

@app.route('/subject_selection', methods=['POST', 'GET'])
def subject_selection():
    #dbase = request.form.get('dbase')
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

@app.route('/program', methods=['POST', 'GET'])
def program():
    #db connection and config
    words = sqlite3.connect('wordsbase.db')
    #dbase = 'wordlist'
    dbase = data.dbase
    #variables initial setup, WRONG implementation TODO repair
    points = 0
    losowanie = True

    #count number of rows in main table
    w = words.cursor()
    w.execute("SELECT COUNT(*) FROM {}".format(dbase))
    elems = w.fetchall()
    
    #TODO replace dummy number of rows check
    for i in elems:
        table_count = i[0]

    #random number generator calling specific sql rows
    #word to translate generator

    random_num = randrange(1,table_count)
    w = words.cursor()
    #save random_number to random_processing table to catch repetitive numbers 
    w.execute("INSERT INTO random_processing (random_num) VALUES (?)", (random_num,))
    words.commit()

    #select row number according to random number id    
    w.execute("SELECT pol, ang FROM {} WHERE emp_id = {}".format(dbase, random_num))
    wordss = w.fetchall()

    for g in wordss:
        pol = g[0]
        word = g[1] 
    #setup word to translate
    pol1 = pol 
    #setup english translation of word pol1
    slowko = word
    #request user translation of word pol1
    tlumaczenie = request.form.get('tlumaczenie')
        
    #save word and user input into processing table in wordbase.db
    params = [(int(points), str(slowko), str(tlumaczenie))]
    w.executemany("INSERT INTO processing VALUES (NULL, ?, ?, ?)", params)
    words.commit()
    
    #case when user clicks "SUBMIT" button
    if request.method == 'POST':
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
            points = points + 1
            #count number of rows of side random_processing table
            w = words.cursor()
            w.execute("SELECT COUNT(*) FROM random_processing")
            randoms = w.fetchall()
    
            #TODO replace dummy number of rows check
            for o in randoms:
                random_num_count = o[0]
            #print(random_num_count)
            #print(table_count)
            if random_num_count < table_count - 1:
                w = words.cursor()
                w.execute("SELECT * FROM random_processing")
                random_num_elems = w.fetchall()
                random_num = randrange(1,table_count)
                while losowanie == True:
                    #print(random_num_elems)
                    #print(random_num)
                    if random_num in random_num_elems:
                        losowanie = True
                    else:
                        w = words.cursor()
                        #save random_number to random_processing table to catch repetitive numbers 
                        w.execute("INSERT INTO random_processing (random_num) VALUES (?)", (random_num,))
                        words.commit()
                        losowanie = False
                return render_template('program.html', pol1=pol1, tlumaczenie = request.form.get('tlumaczenie'))
            else:
                return render_template('program.html', pol1=pol1, tlumaczenie = request.form.get('tlumaczenie'))
        else:
            flash('Wrong answer', 'danger')
            points = points - 1
            #TODO replace dummy number of rows check
            #count number of rows of side random_processing table
            w = words.cursor()
            w.execute("SELECT COUNT(*) FROM random_processing")
            randoms = w.fetchall()
            for o in randoms:
                random_num_count = o[0]

            if random_num_count < table_count - 1:
                w = words.cursor()
                w.execute("SELECT * FROM random_processing")
                random_num_elems = w.fetchall()
                random_num = randrange(1,table_count)
                while losowanie == True:
                    if random_num in random_num_elems:
                        losowanie = True
                    else:
                        w = words.cursor()
                        #save random_number to random_processing table to catch repetitive numbers 
                        w.execute("INSERT INTO random_processing (random_num) VALUES (?)", (random_num,))
                        words.commit()
                        losowanie = False
                return render_template('program.html', pol1=pol1, tlumaczenie = request.form.get('tlumaczenie'))
            else:
                return render_template('program.html', pol1=pol1, tlumaczenie = request.form.get('tlumaczenie'))
    else:
        return render_template('program.html', pol1=pol1, tlumaczenie = request.form.get('tlumaczenie'))
            

if __name__ == '__main__':
    app.run(debug=True)
