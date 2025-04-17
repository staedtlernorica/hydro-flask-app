from flask import Flask, render_template, request, jsonify, g
from flask_wtf import FlaskForm
from wtforms import MultipleFileField, SubmitField
from werkzeug.utils import secure_filename
import os, sys
from wtforms.validators import InputRequired
from viz.extras import merge_files, parse_xml, get_month_year
from viz.build_viz import build_viz

app = Flask(__name__)
app.config['SECRET_KEY'] = 'supersecretkey'
app.config['UPLOAD_FOLDER'] = 'static/files'
app.config['ALLOWED_EXTENSIONS'] = {'xml'}
upload_path = f"{os.getcwd()}/{app.config['UPLOAD_FOLDER']}"

class UploadFileForm(FlaskForm):
    file = MultipleFileField("Files", validators=[InputRequired()])
    submit = SubmitField("Upload Files")

@app.route('/', methods=['GET',"POST"])
@app.route('/home', methods=['GET',"POST"])
def home():
    # form = UploadFileForm()
    # if form.validate_on_submit():
        
    #     for file in form.file.data:
    #         secured_filename = secure_filename(file.filename)
    #         file.save(f'{upload_path}/{secured_filename}')
    #         merged_files = merge_files(upload_path)

    #     plot_html = build_viz(merged_files)
    #     # return render_template("result.html", plot_html=plot_html)
    
    # return render_template('index.html', form=form)
    return render_template('index.html')

@app.route('/upload', methods=["POST"])
def upload():
    import xmltodict
    xml = xmltodict.parse(request.files['file'].stream.read())

    db = get_db()
    cursor = db.execute('SELECT SQLITE_VERSION()')
    version = cursor.fetchone()

    parsed_xml = parse_xml(xml)
    plot_html = 0
    plot_html = build_viz(parsed_xml)
    month_year = get_month_year(parsed_xml)
    month_year.append('Last 30 days')
    # return plot_html
    return {'date': 'Last 30 days',
            'month_year': month_year,
            'plot': plot_html}

# print([print(i) for i in os.environ])

import sqlite3
def get_db():
    if 'db' not in g:
        g.db = sqlite3.connect(':memory')
    return g.db

def close_connection(exception):
    db = g.pop('db', None)
    if db is not None:
        db.close()


@app.route('/query', methods=["POST"])
def query():
    pass

@app.route('/test', methods=["GET", "POST"])
def test():

    return render_template('test.html')

if __name__ == '__main__':
    app.run(debug=True)