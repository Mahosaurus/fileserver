
from pathlib import Path

import secrets
import subprocess
from sys import platform, exit

from flask import Flask, render_template, request, redirect, flash, send_file
from gevent.pywsgi import WSGIServer

from file_handler import search_all_files, make_table

# Detect OS
os = platform
print(os)
if os == "windows":
    subprocess.run("ipconfig")
    PORT = 80
elif os == "linux":
    PORT = 5556
    ps = subprocess.Popen(
        ["ip", "a"],
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT
    )
    output = ps.communicate()[0]
    filtered_lines = [
        line for line in output.splitlines()
        if b"inet 192" in line
    ]
    print(b"\n".join(filtered_lines))
else:
    print("Unsupported OS")
    exit(1)
print("PORT: ", PORT)
print(f"OS: {platform.capitalize()}")

if __name__ == '__main__':
    app = Flask(__name__)
    app.debug = False
    app.config['MAX_CONTENT_LENGTH'] = 1024 * 1024 * 1024 * 1024 # 1TB
    app.config['SECRET_KEY'] = secrets.token_hex()
    app.config['UPLOAD_FOLDER'] = Path(Path(__file__).resolve()).parent.parent.joinpath("resources").joinpath("upload")
    app.config['FOLDER'] = Path(Path(__file__).resolve()).parent.parent.joinpath("resources")
    app.config['MAX_FORM_MEMORY_SIZE'] = 50 * 1024 * 1024 * 1024 # 50GB


    print("Running app...")
    @app.route('/', methods=['GET', 'POST'])
    def provide():
        if request.method == 'POST':
            # check if the post request has the file part
            if 'file' not in request.files:
                return redirect(request.url)
            files = request.files.getlist("file")

            # if user does not select file, browser also
            # submit an empty part without filename
            for curr_file in files:
                if curr_file.filename == '':
                    return redirect(request.url)
                save_path = app.config['UPLOAD_FOLDER'].joinpath(curr_file.filename)
                curr_file.save(save_path)
            flash("Upload successful")

        # list files
        directory_list = search_all_files(app.config['FOLDER'])

        tableau = make_table(directory_list, app.config['FOLDER'])
        return render_template("front.html", tableau=tableau)

    @app.route('/d', methods=['GET'])
    def dlfile():
        dl_file = request.args.get('file')
        return send_file(str(dl_file), as_attachment=True)

    print("Starting app...")
    # DEBUG
    if platform == "linux":
        app.run(host='0.0.0.0', port=int(PORT))
        #HTTP_SERVER = WSGIServer(('0.0.0.0', int(PORT)), app)
        #HTTP_SERVER.serve_forever()
    # PRD
    if platform == "windows":
        HTTP_SERVER = WSGIServer(('0.0.0.0', int(PORT)), app)
        HTTP_SERVER.serve_forever()
