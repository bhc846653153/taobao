# encoding:utf-8
# !/usr/bin/env python
import json
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
    consumer = KafkaConsumer('action_result', bootstrap_servers='192.168.100.21:9092')

    pv = 0 #点击 0
    cart = 0 #加入购物车
    buy = 0#购买 2
    fav = 0# 收藏 3


    for msg in consumer:
        socketio.sleep(3)
        data_json = msg.value.decode('utf8')
        data_list = json.loads(data_json)
        for data in data_list:
            if '0' in data.keys():
                pv= data['0']
            elif '1' in data.keys():
                cart = data['2']
            elif '2' in data.keys():
                buy = data['2']
            elif '3' in data.keys():
                fav = data['3']
            else:
                continue
        print(pv,buy ,fav)
        socketio.emit('server_response', {'data': [pv,buy,fav,cart]}, namespace='/test')
                # 注意：这里不需要客户端连接的上下文，默认 broadcast = True
@app.route('/')
def index():
    return render_template('loudou_action.html', async_mode=socketio.async_mode)


@socketio.on('connect', namespace='/test')
def test_connect():
    global thread
    with thread_lock:
        if thread is None:
            thread = socketio.start_background_task(target=background_thread)


if __name__ == '__main__':
    # background_thread()
    socketio.run(app, debug=True)