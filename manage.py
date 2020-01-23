from flask import Flask

app = Flask(__name__)

class Config():
    debug = True


app.config.from_object(Config)



@app.route("/")
def index():
    return "index page"


if __name__ == '__main__':
    app.run()