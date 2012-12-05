import json
import os
import sys

from flask import Flask, Response, render_template, request, redirect, url_for,current_app

import sender
import color

app = Flask(__name__)
queue = None

@app.route('/', methods = ['POST', 'GET'])
def root():
    if request.method == 'POST':
        try:
            red = int(request.form['red'])
            green = int(request.form['green'])
            blue = int(request.form['blue'])
            g.qp.send(color.Color(red, green, blue))
        except:
            pass
        finally:
            return redirect(url_for('root'))
    else:
        return '''<form action="" method="post">
                    <p>R: <input type=text name=red></p>
                    <p>G: <input type=text name=green></p>
                    <p>B: <input type=text name=blue></p>
                    <p><input type=submit value=submit></p>
                  </form>'''


def set_rgb_time(r, g, b, time):
    c = color.Color(r, g, b, time)
    queue.send(c)
    return 'OK ' + repr(c)


@app.route('/api/r/<int:r>/g/<int:g>/b/<int:b>')
def api_rgb(r, g, b):
    return set_rgb_time(r, g, b, 0)


@app.route('/api/r/<int:r>/g/<int:g>/b/<int:b>/time/<int:time>')
def api_rgb_time(r, g, b, time):
    return set_rgb_time(r, g, b, time)


@app.route('/api/list')
def api_list():
    json_list = []
    for col in g.qp.list_queue():
        json_list.append({
            'rgb': [col.red, col.green, col.blue],
            'time': col.time
            })
    return Response(json.dumps(json_list), mimetype='application/json')


@app.route('/sysinfo')
def sysinfo():
    uname = os.uname()
    sysinfo_all = {
            'OS': uname[0],
            'Host': uname[1],
            'Version': uname[2],
            'Description': uname[3],
            'Arch': uname[4]
    }
    return render_template('sysinfo_all.html', pyversion=sys.version,
            sysinfo=sysinfo_all, show_version=True)


if __name__ == '__main__':
    queue = sender.start_sender()
    app.run(debug=True, host='0.0.0.0', port=5000)
