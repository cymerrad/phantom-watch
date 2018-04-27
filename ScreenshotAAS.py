from flask import Flask, render_template, request, redirect
import urllib
import urlparse

app = Flask(__name__)

_main = "main.html"
_receipt = "receipt.html"


@app.route('/')
def root():
    return redirect("/index")


@app.route('/index')
def index():
    error_msg = ""
    test_array = []

    if request.args.get('error_msg'):
        error_msg
    test_array = request.args.get('test_array')
    test_array2 = request.args.get('test_array[]')

    print("[]: {}\nno []: {}".format(test_array2, test_array))
    test_array = request.form['test_array']
    return render_template(_main, error_msg=error_msg, test_array=test_array)


@app.route('/request')
def handle_request():
    error_msg = ""
    if 'links' not in request.form:
        error_msg += "No links; "
    if 'email' not in request.form:
        error_msg += "None email; "
    if len(error_msg) > 0:
        return reroute_with_errors(error_msg)

    links = request.form['links']
    email = request.form['email']

    return reroute_with_errors(["Everything is fine, this is just a test", links, email])


def reroute_with_errors(error_msg):
    test_array = ['dupa', 'cycki']
    data = {'error_msg': error_msg, 'test_array[]': test_array}
    url_parts = list(urlparse.urlparse("/index"))
    url_parts[4] = urllib.urlencode(data)
    url = urlparse.urlunparse(url_parts)
    return redirect(url)


def reroute_with_receipt(email):
    return render_template(_receipt, email=email)


if __name__ == '__main__':
    app.run()
