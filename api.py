from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow
import os
from flask_cors import CORS
import re
import json
import configparser
app = Flask(__name__)

basedir = os.path.abspath(os.path.dirname(__file__))
config = configparser.ConfigParser()
config.read('config.ini')
pw = config['SERVER_INFO']['PASSWORD']
ip = config['SERVER_INFO']['SERVER_IP']
db_name = config['SERVER_INFO']['DB_NAME']
app.config['SQLALCHEMY_DATABASE_URI'] = "mssql+pymssql://sa:{}@{}/{}".format(pw, ip, db_name)
#params = urllib.parse.quote_plus('DRIVER={SQL Server};SERVER=HARRISONS-THINK;DATABASE=LendApp;Trusted_Connection=yes;')
#app.config['SQLALCHEMY_DATABASE_URI'] = "mssql+pyodbc:///?odbc_connect=%s" % params

db = SQLAlchemy(app)
ma = Marshmallow(app)

CORS(app)
app.config['CORS_HEADERS'] = 'Content-Type'


class Student(db.Model):
    student_id = db.Column(db.Integer, primary_key=True)
    student_name = db.Column(db.String(100), nullable=False)

    def __init__(self, student_name):
        self.student_name = student_name

class StudentSchema(ma.Schema):
    class Meta:
        # Fields to expose
        fields = ('student_id', 'student_name')


student_schema = StudentSchema()
students_schema = StudentSchema(many=True)

@app.route("/")
def index():
    return "it works"
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#
#         Student CRUD          #
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#
# endpoint to create new student
#++++++++++++++++++++++++++++++++
@app.route("/student", methods=["POST"])
def add_student():
    columns = ['student_name']
    col_values = []
    for c in columns:
        if c in request.values:
            col_values.append(request.values[c])
        else:
            col_values.append("")
        
    new_student = Student(*col_values)
    
    db.session.add(new_student)
    db.session.commit()

    return {'message': 'successfully create new student'},200
#++++++++++++++++++++++++++++++++

# endpoint to show all students
#================================
@app.route("/student", methods=["GET"])
def get_student():
    all_students = Student.query.all()
    result = students_schema.dump(all_students)

    result_json = students_schema.jsonify(result)

    return result_json
#================================

# endpoint to get student detail by id
#$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$
@app.route("/student/<id>", methods=["GET"])
def student_detail(id):
    student = Student.query.get(id)

    return student_schema.jsonify(student)
#$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$

# endpoint to update student
#@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
@app.route("/student/<id>", methods=["PUT"])
def student_update(id):
    student = Student.query.get(id)
    columns = ['student_id', 'student_name']
    for c in columns:
        if c in request.values:
            setattr(student, c, request.values[c])
            

    db.session.commit()
    return {'message': 'successfully update student'}, 200
#@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@

# endpoint to delete student
#--------------------------------
@app.route("/student/<id>", methods=["DELETE"])
#@check_token
def student_delete(id):
    student = Student.query.get(id)

    db.session.delete(student)
    db.session.commit()

    return {'message': 'successfully delete student'}, 200
#--------------------------------

if __name__ == '__main__':
    app.run(debug = True, host="0.0.0.0", port=8080)
    # app.run(debug=True)
