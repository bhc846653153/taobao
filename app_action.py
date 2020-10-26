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
consumer = KafkaConsumer('action_result', bootstrap_servers='192.168.100.21:9092')

# 后台线程 产生数据，即刻推送至前端
def background_thread():
    count = 0
    while True:
        click = 0
        join = 0
        buy = 0
        collect = 0
        for msg in consumer:
            data_json = msg.value.decode('utf8')
            data_list = json.loads(data_json)
            socketio.sleep(2)
            count += 1
            # 获取系统时间（只取分:秒）
            t = time.strftime('%M:%S', time.localtime())
            for data in data_list:
                if '0' in data.keys():
                    click = data['0']
                elif '1' in data.keys():
                    join = data['1']
                elif '2' in data.keys():
                    buy = data['2']
                elif '3' in data.keys():
                    collect = data['3']
                else:
                    continue
            click = str(click)
            join = str(join)
            buy = str(buy)
            collect = str(collect)
            socketio.emit('server_response',
                          {'data': [t, click, join, buy, collect], 'count': count},
                          namespace='/test')
            # 注意：这里不需要客户端连接的上下文，默认 broadcast = True

@app.route('/index')
def index_line():
    return render_template('action_index.html', async_mode=socketio.async_mode)

@app.route('/')
def index_bar():
    return render_template('action.html', async_mode=socketio.async_mode)


@socketio.on('connect', namespace='/test')
def test_connect():
    global thread
    with thread_lock:
        if thread is None:
            thread = socketio.start_background_task(target=background_thread)


if __name__ == '__main__':
    socketio.run(app, debug=True)