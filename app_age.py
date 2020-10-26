# encoding:utf-8
# !/usr/bin/env python
import psutil
import time
from threading import Lock
from flask import Flask, render_template
from flask_socketio import SocketIO
from kafka import KafkaConsumer
import json

async_mode = None
app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(app, async_mode=async_mode)
thread = None
thread_lock = Lock()
consumer = KafkaConsumer('age_result', bootstrap_servers='192.168.100.21:9092')

# 后台线程 产生数据，即刻推送至前端
def background_thread():
    count = 0
    while True:
        one = 0
        two = 0
        three = 0
        four = 0
        five = 0
        six = 0
        seven = 0
        for msg in consumer:
            data_json = msg.value.decode('utf8')
            data_list = json.loads(data_json)
            socketio.sleep(2)
            count += 1
            # 获取系统时间（只取分:秒）
            t = time.strftime('%M:%S', time.localtime())
            for data in data_list:
                if '1' in data.keys():
                    one = data['1']
                elif '2' in data.keys():
                    two = data['2']
                elif '3' in data.keys():
                    three = data['3']
                elif '4' in data.keys():
                    four = data['4']
                elif '5' in data.keys():
                    five = data['5']
                elif '6' in data.keys():
                    six = data['6']
                elif '7' in data.keys():
                    seven = data['7']
                else:
                    continue
            one = str(one)
            two = str(two)
            three = str(three)
            four = str(four)
            five = str(five)
            six = str(six)
            seven = str(seven)
            # 获取系统时间（只取分:秒）
            socketio.emit('server_response',
                          {'data': [t, one, two, three, four, five, six, seven], 'count': count},
                          namespace='/test')
            # 注意：这里不需要客户端连接的上下文，默认 broadcast = True

@app.route('/')
def index():
    return render_template('age_index.html', async_mode=socketio.async_mode)


@socketio.on('connect', namespace='/test')
def test_connect():
    global thread
    with thread_lock:
        if thread is None:
            thread = socketio.start_background_task(target=background_thread)


if __name__ == '__main__':
    socketio.run(app, debug=True)