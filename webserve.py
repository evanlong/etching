from flask import Flask, request
import control
app = Flask(__name__)

def dataToPoints(data):
    ps = data.split()
    points = []
    for p in ps:
        p = p.strip()
        x,y = p.split(",")
        points.append((int(x),int(y)))
    return points

@app.route("/")
def hello():
    return "Hello World!"

@app.route("/draw", methods=["POST"])
def draw():
    data = request.form["data"]
    control.drawPoints(dataToPoints(data))
    
    return "yes"

if __name__ == "__main__":
    app.run(host="0.0.0.0")
