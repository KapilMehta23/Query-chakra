from flask import Flask, request, render_template, redirect, url_for, jsonify, session
import os
import sys
import json
from dotenv import load_dotenv
from dbconnection import dbactivities
import pygwalker as pyg
import pandas as pd 
from llama import LLM 
from langchain_community.llms import CTransformers
import time 
import pymssql 
from transformers import AutoModelForCausalLM, AutoConfig 
from transformers import (
    AutoModelForCausalLM,
    AutoTokenizer,
    BitsAndBytesConfig,
)
import torch 
from flask import session


nv_path = os.path.join(os.path.dirname(__file__), 'config', '.env')
load_dotenv(dotenv_path=nv_path)

app = Flask(__name__, template_folder='templates',static_folder='static')
app.secret_key = os.environ['FLASK_KEY']

os.environ['TDSDUMP'] = 'stdout'
dbcon = dbactivities()

llm_model = LLM() 

db_schema = dbcon.index()
print('SQL data fetched successfully')

connectionstring = {'Database':os.environ['DB'],
                'user':os.environ['USER'],
                'host':os.environ['HOST'],
                'port':os.environ['PORT']}

current_query = ''
current_table = 'nothing'
time_difference=0

# FLASK APPLICATION
# @app.get('/')
# def index():
#     normalized_data = json.dumps(db_schema)
#     normalized_data = json.loads(normalized_data)
#     databases = dbcon.get_databases()
#     print(connectionstring)
#     return render_template('index.html',json_data=normalized_data, db_data=connectionstring, dbs=databases)

@app.route('/')
def index():
    normalized_data = json.dumps(db_schema)
    normalized_data = json.loads(normalized_data)
    databases = dbcon.get_databases()
    chat_history = session.get('history', "").split("\n")  # Split history into individual messages
    return render_template('index.html', json_data=normalized_data, db_data=connectionstring, dbs=databases, chat_history=chat_history)


# function for llama 
# @app.route('/process_textarea', methods=['POST'])
# def process_textarea():
#     content = request.get_json() 
#     # print("***************************")
#     # print(content)
#     # print("***************************")
#     global current_query 
#     current_query, time_taken = llm_model.generate_query(content['schema'],content['query']) 
#     global time_difference  
#     time_difference = round(time_taken/60,2) 
#     return {'query':current_query, 'time':round(time_taken/60,2)} 

@app.route('/process_textarea', methods=['POST'])
def process_textarea():
    content = request.get_json()
    history = session.get('history', "")
    response, time_taken = llm_model.generate_query(content['schema'], content['query'], history)
    session['history'] = history + "\n" + response  # Update session history
    return {'query': response, 'time': round(time_taken / 60, 2)}


@app.route('/change_db', methods=['POST'])
def change_db():
    content = request.get_json()
    db = content['database']
    global connectionstring
    try:
        if db == connectionstring['Database']:
            return {'status': 300, 'msg': 'no need to change'}
        else:
            dbcon.switch_db(db)
            connectionstring['Database'] = db
            global db_schema
            db_schema = dbcon.index()
            return {'status': 200, 'msg': 'changed successfully'}
    except Exception as e:
        return {'status': 600, 'msg': str(e)}
    
@app.route('/clean_query', methods=['POST'])
def clean_query():
    content = request.get_json()
    global current_query
    current_query = content['query']
    return 'done'

# @app.route('/output_page')
# def output_page():
#     table = json.loads(dbcon.query_outputs(current_query))
#     global current_table
#     current_table = table
#     columns = list(table.keys())
#     indices = list(table[columns[0]].keys())
#     global time_difference
#     return render_template('output.html', db_data=current_query, positions=indices, output=table, gpt_metadata={'tokens':0,'time_taken':time_difference})

@app.route('/output_page')
def output_page():
    table = json.loads(dbcon.query_outputs(current_query))
    global current_table
    current_table = table
    columns = list(table.keys())
    indices = list(table[columns[0]].keys())
    global time_difference
    chat_history = session.get('history', "").split("\n")  # Split history into individual messages
    return render_template('output.html', db_data=current_query, positions=indices, output=table, gpt_metadata={'tokens': 0, 'time_taken': time_difference}, chat_history=chat_history)

@app.route('/render_dashboard')
def render_dashboard():
    if isinstance(current_table,pd.DataFrame):
        df=current_table
    else:
        df = pd.DataFrame(current_table)
    walker = pyg.walk(df,hideDataSourceConfig=True)
    walker_html = walker.to_html()
    return walker_html


@app.route('/reset_history', methods=['GET'])
def reset_history():
    session.pop('history', None)  # Clear conversation history
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)