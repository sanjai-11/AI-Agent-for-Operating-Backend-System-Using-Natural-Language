from flask import Flask

app = Flask(__name__)

@app.route('/')
def home():
    print("Route accessed")
    return "Hello, World!"

if __name__ == '__main__':
    print("Starting server...")
    app.run(debug=True)