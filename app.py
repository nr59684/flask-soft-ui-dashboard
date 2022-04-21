from flask_migrate import Migrate
from sys import exit
from decouple import config
from apps.config import config_dict
from apps import create_app, db
from flask import request,render_template
import requests, base64
from apps.authentication import blueprint

# WARNING: Don't run with debug turned on in production!
DEBUG = config('DEBUG', default=True, cast=bool)

# The configuration
get_config_mode = 'Debug' if DEBUG else 'Production'

try:

    app_config = config_dict[get_config_mode.capitalize()]

except KeyError:
    exit('Error: Invalid <config_mode>. Expected values [Debug, Production] ')

app = create_app(app_config)
Migrate(app, db)

@app.route('/index', methods = ['POST', 'GET'])
def data():
    temp = dict(request.form)
    key='WG1cwt3PyDO5u8qEnf8Q9YHKseKESf67jT0PW8WADsbUCVv8USDVUqFJE0BY'
    que= temp['req_message']
    res = requests.post('https://chatapi.hoshihrms.com//', json={"req_message":que,"key":key})
    ans= res.json()
    if ans['status']==1:
        ans['output']=base64.b64decode(ans['output']).decode('utf-8')
        return render_template('home/index.html', question=que, reply=ans['output']) 
if DEBUG:
    app.logger.info('DEBUG       = ' + str(DEBUG))
    app.logger.info('Environment = ' + get_config_mode)
    app.logger.info('DBMS        = ' + app_config.SQLALCHEMY_DATABASE_URI)

if __name__ == "__main__":
    app.run(host='0.0.0.0',port=5000, debug=True)
