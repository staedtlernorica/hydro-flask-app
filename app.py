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
            with open(os.getcwd() + '/' + app.config['UPLOAD_FOLDER'] + '/' + file.filename) as xml_file:
                merged_files.append(parse_xml(xml_file))

        from viz.build_viz import build_viz

        # return build_viz.build_viz(merged_files)
        plot_html = build_viz(merged_files)
        return render_template("result.html", plot_html=plot_html)

        # Pass the HTML to the template
        # return render_template('result.html', plot_div=plot_div)

    
    return render_template('index.html', form=form)

if __name__ == '__main__':
    app.run(debug=True)