from flask import Flask, request, redirect

app = Flask(__name__)


# noinspection HttpUrlsUsage
@app.before_request
def before_request():
    if request.url.startswith('http://'):
        url = request.url.replace('http://', 'https://', 1)
        code = 301
        return redirect(url, code), code


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=80)
