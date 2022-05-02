from crypt import methods
from email import contentmanager
from logging import exception
from ossaudiodev import control_names
from flask_migrate import Migrate
from sys import exit
from decouple import config
from apps.config import config_dict
from apps import create_app, db
from flask import request,render_template,jsonify
import requests, base64
from apps.authentication import blueprint
import json
import pandas as pd
# WARNING: Don't run with debug turned on in production!
DEBUG = config('DEBUG', default=True, cast=bool)
# The configuration
get_config_mode = 'Debug' if DEBUG else 'Production'
try:

    app_config = config_dict[get_config_mode.capitalize()]

except KeyError:
    exit('Error: Invalid <config_mode>. Expected values [Debug, Production] ')

app = create_app(app_config)
app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0
Migrate(app, db)



@app.route('/status', methods = ['POST'])
def status():
    global database
    content=dict()
    content["bot1"]="Online"
    content["success1"]="success"
    content["bot2"]="Online"
    content["success2"]="success"
    status1=status2=0
    content['count']="Bot Offline"
    try:
        test = requests.post('http://10.10.6.68:8080/', json={"req_message":"Hello","key":"WG1cwt3PyDO5u8qEnf8Q9YHKseKESf67jT0PW8WADsbUCVv8USDVUqFJE0BY"})
        status1=test.json()['status']
        test = requests.post('http://10.10.6.68:8080/getData',json={"key":"V2VsY29tZXRvbmV1cmFsaXQ="})
        database=test.json()['intents']       
        content['count']=len(database)
    except requests.exceptions.RequestException as e:
        pass
    if status1!=1:
        content["bot1"]="Offline"
        content["success1"]="danger"
    try: 
        test = requests.post('https://chatapi.neuralit.com/', json={"req_message":"Hello","key":"WG1cwt3PyDO5u8qEnf8Q9YHKseKESf67jT0PW8WADsbUCVv8USDVUqFJE0BY"})
        status2=test.json()['status']
    except requests.exceptions.RequestException as e:
        pass
    if status2!=1:
        content["bot2"]="Offline"
        content["success2"]="danger"
    print(content)
    return jsonify(content)

@app.route('/index', methods = ['POST'])
def data():
    key='WG1cwt3PyDO5u8qEnf8Q9YHKseKESf67jT0PW8WADsbUCVv8USDVUqFJE0BY'
    temp = dict(request.form)
    reply="Response"
    try:
        res = requests.post('http://10.10.6.68:8080/', json={"req_message":temp["req_message"],"key":key})
        ans= res.json()
        if ans['status']==1:
            ans['output']=base64.b64decode(ans['output']).decode('utf-8')
            reply=ans['output']
    except requests.exceptions.RequestException as e:
        pass
    return render_template('home/index.html', que=temp["req_message"],reply=reply) 


@app.route('/tables', methods = ['POST'])
def getTable():
    print(request.method)
    try:
        test = requests.post('http://10.10.6.68:8080/getData',json={"key":"V2VsY29tZXRvbmV1cmFsaXQ="})
        database=test.json()['intents']
        df=pd.DataFrame(database)
        df.drop('tag', axis=1, inplace=True)
        df.drop('context', axis=1, inplace=True)
        data=df.to_dict('records')
        for i in range(len(data)):
            di=data[i]
            di['patterns']=', '.join(di['patterns']).title()
            di['responses']=', '.join(di['responses'])
            data[i]=di
        return render_template('home/tables.html', records=data)
    except requests.exceptions.RequestException as e:
        pass
    

if DEBUG:
    app.logger.info('DEBUG       = ' + str(DEBUG))
    app.logger.info('Environment = ' + get_config_mode)
    app.logger.info('DBMS        = ' + app_config.SQLALCHEMY_DATABASE_URI)

if __name__ == "__main__":
    app.run(host='0.0.0.0',port=5000, debug=True)
