from flask import Flask, render_template, request
import json
import sys
import pickle
from pprint import pprint
from werkzeug.routing import BaseConverter
from scheduler import Scheduler
from data_server import DataServer

app = Flask(__name__)
data = DataServer()

class RegexConverter(BaseConverter):
    def __init__(self, url_map, *items):
        super(RegexConverter, self).__init__(url_map)
        self.regex = items[0]

app.url_map.converters['regex'] = RegexConverter

@app.route('/')
def home():
    return render_template('home.html')

@app.route('/picker/<regex("[imnvrl]"):smer>/<regex("[01]{4}"):code>')
def picker(smer, code):
    years = decode_years(code)
    courses = []
    for year in years:
        courses.extend([c for c in data.get_modules()[smer][year]])
    return render_template('picker.html', courses=courses)


@app.route('/api/scheduler/<regex("[imnvrl]"):smer>', methods=['POST'])
def schedule(smer):
    picked_dict = request.form()
    picked = []
    for course in picked_dict:
        picked.append([course, 'lecture', 0])
        picked.append([course, 'exercise', 0])
    for i, _ in enumerate(picked):
        picked[i][2] = [x for x in data.get_courses() if x['description'] == picked[i][0]
                                                    and x['course_type'] == picked[i][1]
                                                    and smer in x['modules']]
    scheduler = Scheduler(picked)
    res = scheduler.find()
    pprint(res)
    return {'courses': res}

@app.route('/api')
def api_root():
    return data.get_modules()

@app.route('/api/<regex("[imnvrl]"):smer>/<regex("[01]{4}"):code>')#, methods=['GET', 'POST'])
def api_smer(smer, code):
    years = decode_years(code)
    return {y: data.get_modules()[smer][y] for y in years}

@app.route('/api/courses')#, methods=['GET', 'POST'])
def api_courses():
    return {'courses': data.get_courses()}

@app.errorhandler(404)
def page_not_found(e):
    return render_template('error.html', error_code="404", error_message="Not found")

def decode_years(code):
    years = []
    for i in range(4):
        if int(code[i]):
            years.append(i+1)
    return years

if __name__ == '__main__':
    app.run(host='localhost', port=3333)