from flask import Flask, render_template, request, jsonify, g
from flask_wtf import FlaskForm
from wtforms import MultipleFileField, SubmitField
from werkzeug.utils import secure_filename
import os, sys, sqlite3
from wtforms.validators import InputRequired
from viz.extras import merge_files, parse_xml, get_month_year
from viz.build_viz import build_df, build_viz
import pandas as pd

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
    parsed_xml = parse_xml(xml)
    df = build_df(parsed_xml)
    
    conn = sqlite3.connect(':memory:')
    df.to_sql('readings', conn, if_exists='replace', index=False)
    
    


    month_year_list = get_month_year(parsed_xml)
    # month_year.append('Last 30 days')     #not sure about doing last 30 days anymore
    latest_period = month_year_list[-1]
    
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM readings WHERE [Year-Month] = ?", (latest_period,))
    rows = cursor.fetchall()
    
    queried_df = pd.read_sql_query("SELECT * FROM readings WHERE [Year-Month] = ?", params=(latest_period,), con=conn)
    print(queried_df.head(10))
    plot_html = 0
    plot_html = build_viz(queried_df)
    
    # return plot_html
    return {'date': 'Last 30 days',
            'month_year': month_year_list,
            'plot': plot_html}

# print([print(i) for i in os.environ])




    db = sqlite3.connect(':memory:')



@app.route('/query', methods=["POST"])
def query():
    pass

@app.route('/test', methods=["GET", "POST"])
def test():

    return render_template('test.html')

if __name__ == '__main__':
    app.run(debug=True)