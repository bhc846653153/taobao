# encoding:utf-8
# !/usr/bin/env python
import json
import psutil
import time
from threading import Lock
from flask import Flask, render_template
from flask_socketio import SocketIO
from kafka import KafkaConsumer


async_mode = None
app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(app, async_mode=async_mode)
thread = None
thread_lock = Lock()


# 后台线程 产生数据，即刻推送至前端
def background_thread():
    consumer = KafkaConsumer('cat_result', bootstrap_servers='192.168.100.21:9092')
    cat = 0
    count =0
    for msg in consumer:
        socketio.sleep(5)
        data_json = msg.value.decode('utf8')
        data_list = json.loads(data_json)
        for data in data_list:
            for keys,value in data.items():
                cat =keys
                count = value
                print(cat,count)
                socketio.emit('server_response', {'data': [cat,count]}, namespace='/test')
                # 注意：这里不需要客户端连接的上下文，默认 broadcast = True
                # 获取系统cpu使用率 non-blocking


@app.route('/')
def index():
    return render_template('cat_index.html', async_mode=socketio.async_mode)


@socketio.on('connect', namespace='/test')
def test_connect():
    global thread
    with thread_lock:
        if thread is None:
            thread = socketio.start_background_task(target=background_thread)


if __name__ == '__main__':
    socketio.run(app, debug=True)