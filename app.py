from flask import Flask, render_template
from flask_wtf import FlaskForm
from wtforms import MultipleFileField, SubmitField
from werkzeug.utils import secure_filename
import os, sys
from wtforms.validators import InputRequired
from viz.extras import merge_files  
from viz.build_viz import build_viz

app = Flask(__name__)
app.config['SECRET_KEY'] = 'supersecretkey'
app.config['UPLOAD_FOLDER'] = 'static/files'
app.config['ALLOWED_EXTENSIONS'] = {'xml'}
upload_path = f'{os.getcwd()}/{app.config['UPLOAD_FOLDER']}'

class UploadFileForm(FlaskForm):
    file = MultipleFileField("Files", validators=[InputRequired()])
    submit = SubmitField("Upload Files")

@app.route('/', methods=['GET',"POST"])
@app.route('/home', methods=['GET',"POST"])
def home():
    form = UploadFileForm()
    if form.validate_on_submit():
        
        for file in form.file.data:
            secured_filename = secure_filename(file.filename)
            file.save(f'{upload_path}/{secured_filename}')
            merged_files = merge_files(upload_path)

        plot_html = build_viz(merged_files)
        return render_template("result.html", plot_html=plot_html)
    
    return render_template('index.html', form=form)

if __name__ == '__main__':
    app.run(debug=True)