# TODO: Implement flashtext
import logging
import os

from pathlib import Path
from collections import defaultdict

import random
import string
import subprocess

from flask import Flask, render_template, request, redirect, flash
from flask_table.html import element
from flask import send_file
from flask_table import Col, Table, LinkCol

from werkzeug.utils import secure_filename
from gevent.pywsgi import WSGIServer

PORT = 80

# Detect OS
try:
    subprocess.run("ipconfig")
    print("PORT: ", PORT)
    windows = True
    linux = False
    print("Windows")
except Exception as exc:
    cmd = "ip a | grep 'inet 192'"
    ps = subprocess.Popen(cmd,shell=True,stdout=subprocess.PIPE,stderr=subprocess.STDOUT)
    output = ps.communicate()[0]
    print(output)
    print("PORT: ", PORT)
    linux = True
    windows = False
    print("Linux")

def searching_all_files(directory):
    dirpath = Path(directory)
    assert(dirpath.is_dir())
    directory_list = defaultdict(list)
    for x in dirpath.iterdir():
        if x.is_file():
            directory_list[str(x)].append(x)     
        if x.is_dir():
            directory_list[str(x)] = searching_all_files(x)
    # Sort dict
    print("a: ", directory_list)
    return directory_list

def make_table(directory_list):
    items = []
    for _, fileitems in directory_list.items():
        for fileitem in fileitems:            
            items.append(str(fileitem))
    items = sorted(items, reverse=True)
    table_items = map(Item, items)
    tableau = ItemTable(table_items, table_id='myTable') 
    return tableau 

class ExternalURLCol(Col):
    def __init__(self, name, url_attr, **kwargs):
        self.url_attr = url_attr
        super(ExternalURLCol, self).__init__(name, **kwargs)

    def td_contents(self, item, attr_list):
        text = self.from_attr_list(item, attr_list)
        url = self.from_attr_list(item, [self.url_attr])
        return element('a', {'href': url}, content=text)

class Item():
    def __init__(self, filepath):
        self.name = filepath
        self.url = "d?file=" + str(filepath)

class ItemTable(Table):
    link = ExternalURLCol('Track', url_attr='url', attr='name')

if __name__ == '__main__':
    app = Flask(__name__)
    app.debug = True
    app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024
    app.config['SECRET_KEY'] = ''.join(random.choice(string.ascii_lowercase) for _ in range(20))
    app.config['UPLOAD_FOLDER'] = Path(Path(__file__).resolve()).parent.parent.joinpath("resources")
    print(app.config['UPLOAD_FOLDER'])

    print("Running app...")
    @app.route('/', methods=['GET', 'POST'])
    def provide():
        if request.method == 'POST':
            # check if the post request has the file part
            if 'file' not in request.files:
                return redirect(request.url)
            file = request.files['file']
            # if user does not select file, browser also
            # submit an empty part without filename
            if file.filename == '':
                return redirect(request.url)
            if linux:
                file.save(app.config['UPLOAD_FOLDER'].joinpath(file.filename).resolve())
            if windows:
                file.save(os.path.join(app.config['UPLOAD_FOLDER'], file.filename))
            flash("Upload successful")

            
        # list files
        directory_list = searching_all_files(app.config['UPLOAD_FOLDER'])

        tableau = make_table(directory_list)
        return render_template("front.html",
                                tableau=tableau)

    @app.route('/d', methods=['GET'])
    def dlfile():
        dl_file = request.args.get('file')
        return send_file(str(dl_file), as_attachment=True)

    print("Starting app...")
    # DEBUG
    if linux:
        app.run()
    # PRD
    if windows:
        HTTP_SERVER = WSGIServer(('0.0.0.0', int(PORT)), app)
        HTTP_SERVER.serve_forever()
