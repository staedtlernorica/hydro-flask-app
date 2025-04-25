from flask import Flask, render_template, request, jsonify, g, redirect, url_for, make_response
from flask_wtf import FlaskForm
from wtforms import MultipleFileField, SubmitField
from werkzeug.utils import secure_filename
import os, sqlite3
from wtforms.validators import InputRequired
from viz.extras import merge_files, parse_xml, get_month_year
from viz.build_viz import build_df, build_viz
import pandas as pd
from viz import chart_color_schemes as col_schemes
import json

app = Flask(__name__)
app.config['SECRET_KEY'] = 'supersecretkey'
app.config['UPLOAD_FOLDER'] = 'static/files'
app.config['ALLOWED_EXTENSIONS'] = {'xml'}
upload_path = f"{os.getcwd()}/{app.config['UPLOAD_FOLDER']}"

class UploadFileForm(FlaskForm):
    file = MultipleFileField("Files", validators=[InputRequired()])
    submit = SubmitField("Upload Files")

DEFAULT_COLORS_SCHEME = col_schemes.schemes['default']

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
    COLORS_SCHEME = json.loads(request.cookies.get('custom_colors', json.dumps(DEFAULT_COLORS_SCHEME)))
    # HAS_CUSTOM_COLORS_SCHEME
    print(DEFAULT_COLORS_SCHEME)
    custom_colors = json.loads(request.cookies.get('custom_colors', '[]'))

    print(custom_colors)
    # return render_template('index.html', colors = COLORS_SCHEME)
    return render_template('index.html', colors = COLORS_SCHEME, has_custom_colors = custom_colors)


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
    COLORS_SCHEME = json.loads(request.cookies.get('custom_colors', json.dumps(DEFAULT_COLORS_SCHEME)))

    plot_html = queryPeriod(queryPeriod = latest_period, func = True, user_color = COLORS_SCHEME)
    return {'date': 'Last 30 days',
            'month_year': month_year_list,
            'plot': plot_html}

# print([print(i) for i in os.environ])

@app.route('/queryPeriod', methods=["GET", "POST"])
def queryPeriod(queryPeriod = None, func = False, **kwargs):
    period = queryPeriod or request.args.get('period')  
    # color = 0
    if func:
        color = kwargs.get('user_color', DEFAULT_COLORS_SCHEME)
    else:
        color = json.loads(request.cookies.get('custom_colors', json.dumps(DEFAULT_COLORS_SCHEME)))
    conn = sqlite3.connect('processed_readings.db')
    queried_df = pd.read_sql_query("SELECT * FROM readings WHERE [Year-Month] = ?", params=(period,), con=conn)

    plot_html = build_viz(queried_df, colorScheme=color)
    if func:
        return plot_html
    return {'plot': plot_html}

@app.route('/color', methods=["GET", "POST"])
def color():
    # print('the request is', request.get_json())
    # g.chartColors = request.get_json().get('colors')
    # g.color = 
    args = request.get_json()
    colors = args['colors']
    period = args['currentPeriod']
    resp = None
    if period == 'empty':
        resp = make_response('')  # Wrap your existing return value
    elif period != 'empty':
        plot_html = queryPeriod(queryPeriod = period, func = True, user_color = colors)
        resp = make_response({'plot': plot_html})  # Wrap your existing return value

    resp.set_cookie('custom_colors', json.dumps(colors))
    return resp

@app.route('/presetColor', methods=["GET", "POST"])
def presetColor():

    return ''

@app.route('/test', methods=["GET", "POST"])
def test():
    return 'test is success'

if __name__ == '__main__':
    app.run(debug=True)