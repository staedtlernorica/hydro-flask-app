from flask import Flask, render_template
from flask_wtf import FlaskForm
from wtforms import MultipleFileField, SubmitField
from werkzeug.utils import secure_filename
import os, sys
from wtforms.validators import InputRequired


app = Flask(__name__)
app.config['SECRET_KEY'] = 'supersecretkey'
app.config['UPLOAD_FOLDER'] = 'static/files'
app.config['ALLOWED_EXTENSIONS'] = {'xml'}

class UploadFileForm(FlaskForm):
    file = MultipleFileField("Files", validators=[InputRequired()])
    submit = SubmitField("Upload Files")

@app.route('/', methods=['GET',"POST"])
@app.route('/home', methods=['GET',"POST"])
def home():
    form = UploadFileForm()
    if form.validate_on_submit():
        
        files_filenames = []
        merged_files = []
        for file in form.file.data:
            secured_filename = secure_filename(file.filename)
            file.save(os.getcwd() + '/' + os.path.join(app.config['UPLOAD_FOLDER'], secured_filename))
            # files_filenames.append(file_filename)

            from viz.extras import parse_xml  
            import xmltodict, json  
            with open(os.getcwd() + '/' + app.config['UPLOAD_FOLDER'] + '/' + file.filename) as xml_file:
                # merged_files.append(parse_xml(xml_file))
                data_dict = xmltodict.parse(xml_file.read())
                json_data = json.dumps(data_dict)

                for i in range(4, len(data_dict['feed']['entry'])):
                    metadata = data_dict['feed']['entry'][i]['content']['espi:IntervalBlock']['espi:interval']
                    readings = data_dict['feed']['entry'][i]['content']['espi:IntervalBlock']['espi:IntervalReading']
                    day_start = metadata['espi:start']

                    for hourly_readings in readings:       
                        reading_start = hourly_readings['espi:timePeriod']['espi:start']
                        reading_value = hourly_readings['espi:value']
                        merged_files.append({
                            'day (unix)': day_start,
                            'hour (unix)': reading_start,
                            'reading': reading_value
                        })

        from viz.build_viz import build_viz
        plot_html = build_viz(merged_files)
        return render_template("result.html", plot_html=plot_html)
    
    return render_template('index.html', form=form)

if __name__ == '__main__':
    app.run(debug=True)