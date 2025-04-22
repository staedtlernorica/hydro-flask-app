from flask import Flask, render_template, request, jsonify, g
from flask_wtf import FlaskForm
from wtforms import MultipleFileField, SubmitField
from werkzeug.utils import secure_filename
import os, sqlite3
from wtforms.validators import InputRequired
from viz.extras import merge_files, parse_xml, get_month_year
from viz.build_viz import build_df, build_viz
import pandas as pd
from viz import chart_color_schemes as col_schemes

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
    default_colors = col_schemes.schemes['default']
    return render_template('index.html', colors = default_colors)


@app.route('/upload', methods=["POST"])
def upload():
    dataSrc = request.args.get('dataSrc')
    import xmltodict
    if dataSrc == 'submit':
        xml = xmltodict.parse(request.files['file'].stream.read())
    elif dataSrc == 'sample':
        with open(f'{os.getcwd()}/sample xml/sample.xml', 'r', encoding='utf-8') as file:
            xml = xmltodict.parse(file.read())
    parsed_xml = parse_xml(xml)
    df = build_df(parsed_xml) 
    conn = sqlite3.connect('processed_readings.db')
    df.to_sql('readings', conn, if_exists='replace', index=False)
    
    month_year_list = get_month_year(parsed_xml)
    latest_period = month_year_list[-1]
    plot_html = query(queryPeriod = latest_period, func = True)
    return {'date': 'Last 30 days',
            'month_year': month_year_list,
            'plot': plot_html}

# print([print(i) for i in os.environ])

@app.route('/queryPeriod', methods=["GET", "POST"])
def query(queryPeriod = None, func = False, **color):
    period = queryPeriod or request.args.get('period')  
    color = col_schemes.schemes['default']
    conn = sqlite3.connect('processed_readings.db')
    queried_df = pd.read_sql_query("SELECT * FROM readings WHERE [Year-Month] = ?", params=(period,), con=conn)
    plot_html = build_viz(queried_df, colorScheme=color)
    if func:
        return plot_html
    return {'plot': plot_html}

@app.after_request
def after_request_func(response):
    print("g contents:", vars(g))
    return response

@app.route('/color', methods=["GET", "POST"])
def color():
    print('the request is', request.get_json())
    g.chartColors = request.get_json().get('colors')
    return ''
    # g.color = 
    pass

if __name__ == '__main__':
    app.run(debug=True)