from flask import Flask
from flask import render_template, request,session, Response, jsonify
import pandas as pd
import os
import glob
from flask_bootstrap import Bootstrap
import numpy as np
from flask_socketio import SocketIO

from static.OD import OD

app = Flask(__name__,"/static")
app.secret_key = 'your_secret_key' 
bootstrap = Bootstrap(app)
socketio = SocketIO(app)

"""First page"""
@app.route("/home")
def first_page():
    return render_template("First_page.html")

"""Video page"""
@app.route('/video_feed')
def video_feed():
    return Response(OD(socketio), mimetype='multipart/x-mixed-replace; boundary=frame')

"""Photo application page"""
@app.route("/photo",methods=["GET","POST"])
def photo():

    return render_template("label_photos.html", video_feed_url="/video_feed")


if __name__ == '__main__':
    socketio.run(app)