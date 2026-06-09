from extensions import app

@app.route("/")
def home():

    return """
    <h1>Ask Your Doubt V1</h1>

    <a href='/admin-login'>Admin Login</a>

    <br><br>

    <a href='/teacher-login'>Teacher Login</a>
    """

from routes import admin
from routes import teacher
from routes import student

if __name__ == "__main__":

    app.run(
        host="0.0.0.0",
        port=9000,
        debug=True
    )