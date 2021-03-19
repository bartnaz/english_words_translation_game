import sqlite3

def sql_select(dbase):
    words = sqlite3.connect('wordsbase.db')
    w = words.cursor()
    query = "SELECT emp_id, pol, ang0, ang1, ang2, ang3 FROM {}".format(dbase)
    w.execute(query)
    results = w.fetchall()
    return results

def clear_processing():
    words = sqlite3.connect('wordsbase.db')
    w = words.cursor()
    query = "DELETE FROM better_processing"
    w.execute(query)
    words.commit()
    words.close()
    return None

def table_count(dbase):
    words = sqlite3.connect('wordsbase.db')
    w = words.cursor()
    query = "SELECT COUNT(*) FROM {}".format(dbase) 
    w.execute(query)
    results = w.fetchall()
    return results

def rand_num_row_query(dbase, random_num):
    # select row from table with id_number corresponding to generated random_num
    words = sqlite3.connect('wordsbase.db')
    w = words.cursor()
    query = "SELECT pol FROM {} WHERE emp_id = {}".format(dbase, random_num)
    w.execute(query)
    results = w.fetchall()
    return results

def insert_into_better_processing(random_num, tlumaczenie):
    words = sqlite3.connect('wordsbase.db')
    w = words.cursor()
    w.execute("INSERT INTO better_processing (generated_num, tlumaczenie) VALUES (?, ?)", (random_num, tlumaczenie,))
    words.commit()
    return None

def select_from_better_processing():
    words = sqlite3.connect('wordsbase.db')
    w = words.cursor()
    w.execute("SELECT * FROM better_processing ORDER BY id DESC LIMIT 2")
    results = w.fetchall()
    return results

def select_from_better_processing_emp_id(dbase, random_num):
    # select row from table with id_number corresponding to generated random_num
    words = sqlite3.connect('wordsbase.db')
    w = words.cursor()
    query = "SELECT * FROM {} WHERE emp_id = {}".format(dbase, random_num)
    w.execute(query)
    results = w.fetchall()
    return results

