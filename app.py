from flask import Flask, render_template
from flask_wtf import FlaskForm
from wtforms import MultipleFileField, SubmitField
from werkzeug.utils import secure_filename
import os, sys
from wtforms.validators import InputRequired
import plotly.graph_objs as go
import plotly.offline as offline

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
    # form = UploadFileForm()
    # if form.validate_on_submit():
    #     file = form.file.data # First grab the file
    #     file.save(os.path.join(os.path.abspath(os.path.dirname(__file__)),app.config['UPLOAD_FOLDER'],secure_filename(file.filename))) # Then save the file

    #     import xmltodict
    #     with open(app.config['UPLOAD_FOLDER'] + '/' + file.filename) as xml_file:
    #         data_dict = xmltodict.parse(xml_file.read())
    #         return data_dict
        
    #     return "File has been uploaded."
    
    # return render_template('index.html', form=form)
    form = UploadFileForm()
    if form.validate_on_submit():
        
        import xmltodict, json
        files_filenames = []
        merged_files = []
        for file in form.file.data:
            file_filename = secure_filename(file.filename)
            file.save(os.getcwd() + '/' + os.path.join(app.config['UPLOAD_FOLDER'], file.filename))
            # files_filenames.append(file_filename)



            with open(os.getcwd() + '/' + app.config['UPLOAD_FOLDER'] + '/' + file.filename) as xml_file:
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

            # return merged_files

        from viz import build_viz

        # return build_viz.build_viz(merged_files)
        plot_html = build_viz.build_viz(merged_files)
        return render_template("result.html", plot_html=plot_html)

        # Pass the HTML to the template
        # return render_template('result.html', plot_div=plot_div)

    
    return render_template('index.html', form=form)

if __name__ == '__main__':
    app.run(debug=True)