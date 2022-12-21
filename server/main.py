import sys
from flask import Flask, request, Response, render_template
import logging
import mysql.connector
from mysql.connector import Error
import pandas as pd
from matplotlib import pyplot as plt
import seaborn as sns
from matplotlib.ticker import MaxNLocator
from matplotlib.patches import FancyBboxPatch
import numpy as np


sys.path.append('DB/')
import DBinfo

DB_IP = DBinfo.DB_IP
DB_USER = DBinfo.DB_USER
DB_PASSWD = DBinfo.DB_PASSWD
DB_NAME = DBinfo.DB_NAME

found_objects_list = []
timestamp_list = []
camera_id_list = []

app = Flask(__name__)

def insert_into_record(cam_id, values):
    try:
        connection_db = mysql.connector.connect(host=DB_IP, user=DB_USER, passwd=DB_PASSWD, db=DB_NAME)
        try:
            cursor = connection_db.cursor()
            values = values.replace("'", "").replace(" ", "")[1:-1]
            #print(cam_id, values)
            cursor.execute(f'INSERT INTO RECORD (CAMERA_ID, DATETIME, ITEMS) '
                           f'VALUES ("{cam_id}", CURRENT_TIMESTAMP, "{values}")')
        except Error as e:
            logging.error("Error while inserting data into RECEIVER_MSG_SAMPLE: " + str(e))
        finally:
            connection_db.commit()
            cursor.close()
            connection_db.close()
    except Error as e:
        logging.error("Error while connecting to DB: " + str(e))

def get_data():
    df = None
    try:
        connection_db = mysql.connector.connect(host=DB_IP, user=DB_USER, passwd=DB_PASSWD, db=DB_NAME)
        try:
            cursor = connection_db.cursor()
            cursor.execute("SELECT * FROM RECORD");
            columns = cursor.description
            result = [{columns[index][0]: column for index, column in enumerate(value)} for value in
                      cursor.fetchall()]
            df = pd.DataFrame(result)
        except Error as e:
            logging.error('Error while querying DB: ' + str(e))
        finally:
            cursor.close()
            connection_db.close()
            return df
    except Error as e:
        logging.error("Error while connecting to DB", e)


#implement read of existing files
@app.route('/datastream', methods=['POST'])
def my_form():
    data = list(request.form.values())
    # print(data)
    cam_id = data[0]
    values = data[1]
    insert_into_record(cam_id, values)
    return Response(status=204)

found_objects_str = ''
sqlString = ''
cam_id = ''
checkboxValues = []

'''
def login():
    connection_db = mariadb.connect(host=DB_IP, user=DB_USER, passwd=DB_PASSWD, db=DB_NAME)
    cursor = connection_db.cursor()
    if request.method == 'POST':
        cam_id = request.form['user']
        for check in list(request.form.getlist('oggetto')):
            checkboxValues.append(check)
        found_objects_str = "','".join(checkboxValues)
    sqlString =("SELECT count(*) qty, ITEMS FROM RECORD WHERE DATETIME >= CURRENT_DATE and CAMERA_ID='{}'and ITEMS in ('{}')".format(cam_id, found_objects_str))
    cursor.execute(sqlString);
    columns = cursor.description
    result = [{columns[index][0]: column for index, column in enumerate(value)} for value in
              cursor.fetchall()]
    return result
'''

def get_items():
    df = get_data()
    items_list = list(df.ITEMS.array)
    items_dict = {}

    for i in items_list:
        for e in i.split(','):
            if e == "" or e == " ":
                continue
            if e not in items_dict:
                items_dict[e] = 1
            else:
                items_dict[e] += 1
    return items_dict.keys()


def grafici(cam_id, selected_items):
    df = get_data()
    df = df.loc[df['CAMERA_ID'] == cam_id]
    # print(list(df.ITEMS.array))
    items_list = list(df.ITEMS.array)
    items_dict = {}
    time_list = list(df.DATETIME.array)

    for i in items_list:
        for e in i.split(','):
            if e == "" or e == " ":
                continue
            if e not in selected_items:
                continue
            if e not in items_dict:
                items_dict[e] = 1
            else:
                items_dict[e] += 1
    #print(items_dict)

    for e in items_dict.keys():
        items_dict[e] = items_dict[e] / len(items_list) * 100

    data = {'ITEMS': items_dict.keys(),
            'Percentage': items_dict.values(),
            }

    df1 = pd.DataFrame(data)
    fig, ax = plt.subplots()
    sns.barplot(data=df1, x="ITEMS", y="Percentage", ax=ax, palette="GnBu_d")
    ax.set_ylabel('%')
    ax.set_title('Items appared')

    new_patches = []
    for patch in reversed(ax.patches):
        # print(bb.xmin, bb.ymin,abs(bb.width), abs(bb.height))
        bb = patch.get_bbox()
        color = patch.get_facecolor()
        p_bbox = FancyBboxPatch((bb.xmin, bb.ymin),
                                abs(bb.width), abs(bb.height),
                                boxstyle="round,pad=0.1,rounding_size=0.3",
                                ec="none", fc=color,
                                mutation_aspect=15
                                )
        patch.remove()
        new_patches.append(p_bbox)

    for patch in new_patches:
        ax.add_patch(patch)
    sns.despine(left=True, bottom=True)

    ax.tick_params(axis=u'both', which=u'both', length=0)
    plt.tight_layout()

    plt.savefig('static/GraficoPerc.svg')

    #print(list(items_dict.keys()))
    time_dict_keys = list(items_dict.keys()).copy()
    time_dict_keys.insert(0, "DATETIME")
    time_based_dict = {}
    for c in time_dict_keys:
        time_based_dict[c] = []
    #prendo tutti gli items che selezionerò dall'html e li plotto, ignoro tutti gli altri
    for ct in df.index:
        time_based_dict["DATETIME"].append(df.loc[ct]["DATETIME"])
        for i in items_dict.keys():
            time_based_dict[i].append(0)
        for i in df.loc[ct]["ITEMS"].split(","): #
            if i not in selected_items:
                continue
            time_based_dict[i][-1] += 1
    df2 = pd.DataFrame(time_based_dict)

    max_occurrence = 0
    for f in df.ITEMS.array:
        frame_occurrences_dict = {}
        if f == "" or f == " ":
            continue
        for e in f.split(','):
            if e == "" or e == " ":
                continue
            if e not in selected_items:
                continue
            if e not in frame_occurrences_dict.keys():
                frame_occurrences_dict[e] = 1
            else:
                frame_occurrences_dict[e] += 1
        if max(frame_occurrences_dict.values()) > max_occurrence:
            max_occurrence = max(frame_occurrences_dict.values())
    max_occurrence += 1

    fig, ax = plt.subplots()
    sns.lineplot(data=df2, ax=ax)
    sns.color_palette("Set2")
    ax.set_ylabel('Occurrence')
    ax.set_title('Items appared')
    ax.yaxis.set_major_locator(MaxNLocator(integer=True))
    ax.set(ylim=(0, max_occurrence)) #difficile ci siano più di 3 oggetti uguali nella stessa inquadratura (caso webcam locale)
    plt.savefig('static/GraficoApparizioni.svg')

    df2 = df2.set_index("DATETIME")
    fig, ax = plt.subplots()
    sns.lineplot(data=df2, ax=ax)
    sns.color_palette("Set2")
    ax.set_ylabel('Occurrence')
    ax.set_title('Items appared')
    ax.yaxis.set_major_locator(MaxNLocator(integer=True))
    ax.set(ylim=(0, max_occurrence))
    plt.savefig('static/GraficoApparizioni2.svg')

@app.route('/login', methods=['POST'])
def login():
    form_data = list(request.form.values())
    cam_id = form_data[0]
    selected_items = form_data[1:]
    df = get_data()
    if cam_id not in df.CAMERA_ID.unique():
        return home(err = True)
    grafici(cam_id, selected_items)
    return render_template("grafici.html", CAMERA_ID = cam_id )

@app.route('/')
def home(err=False): #aggiungere metodo di visualizzazione dei dati inseriti
    return render_template("login.html", items = get_items(), err=err)
#mix fra dati della fotocamera e dati di home

if __name__ == '__main__':
    app.run(use_reloader=True, debug=True, port=80)
