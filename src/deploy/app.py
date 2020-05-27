#export FLASK_APP=app.py
from flask import Flask
from src.deploy.market import get_prediction

app = Flask(__name__)

@app.route('/flight/<string:flight_number>')
def show_market(flight_number):
    result = get_prediction(flight_number)
    return str(result)

@app.route('/')
def api_root():
    return 'Servicio modelo vivo'

if __name__ == '__main__':
    app.run(host= '0.0.0.0')
