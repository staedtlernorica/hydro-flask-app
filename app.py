
# # A very simple Flask Hello World app for you to get started with...

# from flask import Flask

# app = Flask(__name__)

# @app.route('/')
# def hello_world():
#     return 'Hello from Flask! This is where I will be doing all my Toronto Hydro charting magic'

from flask import Flask, render_template, request, jsonify

app = Flask(__name__)

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/about')
def about():

    import plotly.express as px
    # Create a simple Plotly Express figure (e.g., a scatter plot)
    df = px.data.iris()  # Using the iris dataset from Plotly
    fig = px.scatter(df, x='sepal_width', y='sepal_length', color='species')

    # Convert the figure to HTML
    plot_html = fig.to_html(full_html=False)

    # Render the HTML template and pass the plot HTML to it
    return render_template('about.html', plot_html=plot_html)


@app.route('/hydro-viz')
def hydro_viz():
    return render_template('hydro-viz.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    # Check if the request has the file part
    if 'file' not in request.files:
        return jsonify({"error": "No file part"}), 400

    file = request.files['file']
    
    # If no file is selected
    if file.filename == '':
        return jsonify({"error": "No selected file"}), 400

    # Read the file contents as text
    try:
        file_contents = file.read().decode('utf-8')  # Assuming it's a text file

        return 'yay got the file'
        # return jsonify({"file_contents": file_contents})
    
    except UnicodeDecodeError:
        return jsonify({"error": "Unable to decode file"}), 400


if __name__ == '__main__':
    app.run(debug=True)
