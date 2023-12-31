"""
程序名称: Central Air Conditioning Management System (CACMS) Backend Service
程序描述:
    - 该Python脚本是为中央空调管理系统设计的后端服务。
    - 基于Flask框架，实现了用户登录、房间管理、设备控制等功能。
    - 包含了API路由处理，用于处理前端发出的网络请求，并与数据库进行交互。
    - 调用多线程技术来处理后台调度任务。

主要模块及其功能:
    1. 登录/登出管理: 提供用户登录和登出功能，验证用户身份并分配相应角色。
    2. 房间管理: 实现对房间的增加和删除功能。
    3. 设备控制: 允许管理员通过API控制中央空调的各项参数。
    4. 状态查询: 提供接口查询特定房间或所有房间的当前状态。
    5. 前台服务: 处理前台的开房和退房流程，包括费用计算和使用详情。

接口说明:
    这个脚本主要设计了flask的13种接口函数，用于前后端交互，涉及到逻辑判断数据库调用以及接口测试。
    - `/api/login`: 用户登录接口
    - `/api/logout`: 用户登出接口
    - `/api/admin/device`: 房间增加和删除接口
    - `/api/admin/devices`: 查询所有房间名称接口
    - `/api/status/<room_id>`: 查询指定房间状态接口
    - `/api/status`: 查询所有房间状态接口
    - `/api/room/check_in`: 前台开房接口
    - `/api/room/check_out`: 前台退房接口
    - `/api/device/client/<room_id>`: 客户端状态更新接口
    - 等

开发者信息:
    - 开发者: [陈悦-2021211882]
    - 开发日期: [2023-12]

备注：
    此脚本中过多的注释是因为软件在实际生产中，需要不断的测试以及不断地修改。

"""
import os
from app import *
from threading import Thread
from flask import request, jsonify, Blueprint
from database import *
from scheduler import Scheduler
import requests
from central_ac import *
import datetime
import hashlib
from sqlalchemy import func
import utils
import re

central_ac = CentralAc()
scheduler = Scheduler(central_ac)

t = Thread(target=scheduler.schedule)

rooms_ip = [{
    "room": "test",
    "port": "5677",
    "ip": "10.129.117.63"
}, {
    "room": "1"
}, {
    "room": "2"
}, {
    "room": "3"
}, {
    "room": "4"
}, {
    "room": "5"
}]



# 登录
@app.route('/api/login', methods=['POST'])
def login_admin():
    """
    username
    password
    :return: {error:bool.
                role:str}  # room/administrator/manager/receptionist
终端测试指令：
curl.exe -v -X post -d '{"username":"administrator_1", "password":"administrator"}' http://localhost:11451/api/login?no-csrf
    """

    params = request.get_json(force=True)
    print("------------------------------------------------------------------------------------------------------------")
    print("登录：", request.path, " 参数为: ", params)
    username = params['username']
    password = params['password']

    ans = User.query.filter(User.username == username).filter(User.password == password).first()

    if ans.type == "administrator":
        role = "AC admin"
    elif ans.type == "receptionist":
        role = "checkout"
    elif ans.type == "manager":
        role = "manager"

    if ans is None:
        print('登录失败')
        return jsonify({'error_code': 100}), 401
    else:
        print('登录成功')
        ret = {'username': username, 'role': role}

        return jsonify(ret), 200
        # make_response(jsonify(response_data))


# 登出
@app.route('/api/logout', methods=['POST'])
def logout_admin():
    """
    当前账号退出
    :return: 204 成功
            401 error

curl.exe -v -X post http://localhost:11451/api/logout?no-csrf
    """

    return 204

weiruzhu = ['test','1', '2', '3', '4', '5']

# 管理员加房
@app.route('/api/admin/device', methods=['put'])
def add_room():
    """
    input:
        room:
            type: string
        public_key:
            type: string # RSA 4096
    :return: 200 room:
                    type: string
            401
终端测试：
curl.exe -v -X put -d '{"room":"test", "public_key":"RSA 4096"}' http://localhost:11451/api/admin/device?no-csrf
    """
    print("------------------------------------------------------------------------------------------------------------")
    params = request.get_json(force=True)
    print("加房：", request.path, " 参数为: ", params)
    room = params['room']
    public_key = params['public_key']

    try:
        if room in scheduler.room_threads.keys():
            print("该房间已入住，请不要加房")
            return jsonify({'error_code': 100}), 401
        weiruzhu.append(room)
        rooms_ip.append({
            "room": room,
            "port": "",
            "ip": ""
        })
        print("当前未入住列表：", weiruzhu)
        return jsonify({'room': room}), 200
    except:
        return jsonify({'error_code': 100}), 401


# 管理员删房
@app.route('/api/admin/device', methods=['delete'])
def delete_room():
    """
    input：
        room:
            type: string
    :return: 200 room:
                    type: string
            401
终端测试：
curl.exe -v -X delete -d '{"room":"test"}' http://localhost:11451/api/admin/device?no-csrf
    """
    print("------------------------------------------------------------------------------------------------------------")
    params = request.get_json(force=True)
    print("删房：", request.path, " 参数为: ", params)
    room = params['room']

    # try:
    if room in weiruzhu:
        weiruzhu.remove(room)
        print(f"未入住'{room}' 已删除", "当前未入住列表为：", weiruzhu)
        rooms_ip = [room_info for room_info in rooms_ip if room_info["room"] != room]
        return jsonify({'room': room}), 200
    elif room in scheduler.room_threads:
        del scheduler.room_threads[room]  # 此处等于scheduler函数中的删房函数
        print(f"已入住'{room}' 已删除")
        rooms_ip = [room_info for room_info in rooms_ip if room_info["room"] != room]
        return jsonify({'room': room}), 200
    else:
        print(f"Room '{room}' not found 未入住或已入住.")
        return jsonify({'error_code': 100}), 401

    # except:
    #     # raise ValueError(f"Room '{room}' not found 未入住或已入住.")
    #     print(f"except")
    #     return jsonify({'error_code': 100}), 401


# 管理员给出所有可利用的设备
@app.route('/api/admin/devices', methods=['get'])
def get_room_list():
    """
    :return: 200 room :
                    type: string array
            401

    调数据库
curl.exe -v -X get http://localhost:11451/api/admin/devices?no-csrf
    """
    try:
        available = scheduler.get_available_room()
        # for room in weiruzhu:
        #     available.append(room)
        return jsonify(available), 200
    except:
        return jsonify({'error_code': 100}), 401


# 管理员控制某一设备
@app.route('/api/admin/devices/<string:room_id>', methods=['post'])
def control_device(room_id):
    """
    input：
        room:
            type: string

        operation:
              type: string
              example:  'start, stop, temperature, wind_speed, mode,'
        data:
              type: string
              example: 26   # different for operations
    :return: 200 返回房间列表
            401
终端测试：
curl.exe -v -X post -d '{"operation":"start, stop, temperature, wind_speed", "data":"1, 0, 23, 3"}' http://localhost:11451/api/admin/devices/test?no-csrf
    """
    print("------------------------------------------------------------------------------------------------------------")

    if room_id not in scheduler.room_threads.keys():
        print("管理员想控制该房间，但该房间", room_id, "不存在")
        return jsonify({'error_code': 100}), 401
    params = request.get_json(force=True)
    print("管理员控制：", request.path, " 参数为: ", params)
    #解析数据
    operation = params['operation']
    data = params['data']
    operations = [element.strip() for element in operation.split(',')]
    datas = [datas.strip() for datas in data.split(',')]
    operation_data = dict(zip(operations, datas))
    start = operation_data.get('start')
    target_temp = operation_data.get('temperature')
    wind_speed = operation_data.get('wind_speed')
    if wind_speed == '3':
        wind_speed = 'HIGH'
    elif wind_speed == '2':
        wind_speed = 'MID'
    elif wind_speed == '1':
        wind_speed = 'LOW'

    power = True
    for room in scheduler.room_threads.values():
        if room.room_id == room_id:
            power = room.power

    # try:
    print("           ", "请求的开关机", bool(int(start)), "房间当前的开关机", power)
    if bool(int(start)) == bool(power) and not bool(int(start)):
        print("房间", room_id, "想重复关机")
        return jsonify({'error_code': 100}), 401

    if bool(int(start)) == bool(power) and bool(int(start)):
        print("更改风速： ", room_id, " 房间号")
        scheduler.deal_with_speed_temp_change(room_id, int(target_temp), wind_speed)

        control_client(room_id, True, target_temp, wind_speed)
    else:
        if start == '1':
            start = 'ON'
            print("开机： ", room_id, "房间号")
            scheduler.deal_with_on_and_off(room_id, int(target_temp), wind_speed, start)
            control_client(room_id, True, target_temp, wind_speed)
        else:
            print("关机： ", room_id, "房间号")
            scheduler.deal_with_on_and_off(room_id, int(25), 'MID', start)
            control_client(room_id, False, target_temp, wind_speed)

    return jsonify({'room': room_id}), 200
    # except:
    #     return jsonify({'error_code': 100}), 401

room_temp = {
    "test": 30
}
# 对某一房间进行状态查询
@app.route('/api/status/<string:room_id>', methods=['GET'])
def get_one_status(room_id):
    """
    room:
        type: string


    :return: 200 room, temperature, wind_speed, mode, sweep, is_on, last_update, 另外加target_temp
            401
curl.exe -v -X get http://localhost:11451/api/status/test?no-csrf
    """

    # try:
    #print("------------------------------------------------------------------------------------------------------------")
    #print("对", room_id, "查询房间状态信息：")
    if room_id not in scheduler.room_threads.keys():
        print("但该房间", room_id, "不在入住列表中")
        return jsonify({'error_code': 100}), 401

    #print(scheduler.room_threads.keys())
    room_message = scheduler.get_room_message(room_id)
    if room_message["wind_speed"] == None or room_message["wind_speed"] == '':
        init_temp = room_temp[room_id]
        room_message = {
            'room': room_id,
            'temperature': init_temp,
            'wind_speed': 2,
            'mode': 'cold',
            # 'sweep': sweep,
            'is_on': False,
            'is_ruzhu': False,
            'target_temp': 25
        }
    else:
        speed_to_num = {'HIGH': 3, 'MID': 2, 'LOW': 1}
        room_message['wind_speed'] = speed_to_num[room_message['wind_speed']]
        for i in scheduler.room_threads.keys():
            if room_id == i:
                room_message['target_temp'] = scheduler.room_threads[i].target_temp
    print(room_message, "回传状态信息")
    json = jsonify(room_message)
    return json, 200
    # except:
    #     return jsonify({'error_code': 100}), 401


# 获取所有房间开关信息
@app.route('/api/status', methods=['get'])
def get_all_status():
    """
    :return: 200 room, is_on(开关机状态)

            401
curl.exe -v -X get http://localhost:11451/api/status?no-csrf
    """
    try:
        json = []
        # for room in weiruzhu:
        #     status[room] = False
        for room in scheduler.room_threads.values():
            status = {}
            status['room'] = room.room_id
            status['is_on'] = room.power
            json.append(status)
        return jsonify(json), 200
    except:
        return jsonify({'error_code': 100}), 401


# 开房
@app.route('/api/room/check_in', methods=['POST'])
def check_in():
    """前台开房
    input：
        roomId
    :return: 200 room,
            401
curl.exe -v -X POST -d '{"room": "test"}' http://localhost:11451/api/room/check_in?no-csrf
    """
    print("------------------------------------------------------------------------------------------------------------")

    params = request.get_json(force=True)
    print("开房：", request.path, " 参数为: ", params)
    room = params['room']
    temp = params['temperature']
    temp = int(temp)

    if room not in room_temp.keys():
        room_temp[room] = temp

    if room not in weiruzhu:
        print("当前未入住列表：",weiruzhu)
        print('这房间您的管理员没加呢，不存在这房间号。')
        return jsonify({'error_code': 100}), 401
    else:
        # try:
        rooms = []
        rooms.append(room)
        #print(rooms)
        temps = []
        temps.append(temp)
        scheduler.add_room(rooms)
        scheduler.set_room_initial_env_temp(rooms, temps)
        json = jsonify('room', room)
        weiruzhu.remove(room)
        print("已入住", room)
        print("当前未入住列表：",weiruzhu)
        return json, 200
        # except:
        #     return jsonify({'error_code': 100}), 401


# 退房
@app.route('/api/room/check_out', methods=['POST'])
def check_out():
    """前台退房
    input：
        roomId:int
    :return: room,
            report_data:
                total_cost
                total_time
                details:
                    start_time
                    end_time
                    temperature
                    wind_speed
                    mode
                    duration
                    cost
    调数据库
curl.exe -v -X POST -d '{"room": "test"}' http://localhost:11451/api/room/check_out?no-csrf
    """
    print("------------------------------------------------------------------------------------------------------------")

    params = request.get_json(force=True)
    print("退房：", request.path, " 参数为: ", params)
    room = params['room']

    order = Order.query.filter_by(room_id=room).order_by(Order.checkin.desc()).first()
    if order is None:
        print("数据库中没有找到与之匹配的房间号")
        return jsonify({'error_code': 100}), 401

    checkin = order.checkin
    #checkout = order.checkout
    checkout = datetime.datetime.now()
    total_time = checkout - checkin

    details = Detail.query.filter_by(room_id=room).order_by(Detail.start_time.desc()).all()
    total_cost = 0.0
    de = []

    # 遍历查询结果并提取所需信息
    for detail in details:
        de.append({
            'start_time': detail.start_time.isoformat(),
            'end_time': detail.end_time.isoformat(),
            'wind_speed': detail.speed,
            'mode': "cold",
            'duration': detail.times_used,
            'cost': detail.fee
        })
        total_cost += detail.fee

    report_data = {
        'total_cost': total_cost,
        'total_time': total_time.total_seconds(),
        'details': de
    }

    delete = []
    delete.append(room)
    scheduler.delete_room(delete)
    weiruzhu.append(room)
    print(report_data)

    return jsonify(report_data), 200


# 客户端连接

@app.route('/api/device/client', methods=['POST'])
def client_connect():
    """
    input：
        room_id
        port    #Port for WebHook
        unique_id   #random Unique ID, 16 characters
        signature   #SHA256withRSA, RSA 4096, sign text = room_id + unique_id + port
    :return:204 succes
            401

curl.exe -v -X POST -d '{"room_id": "test"}' http://localhost:11451/api/device/client?no-csrf
    """
    print("------------------------------------------------------------------------------------------------------------")

    data = request.json
    print("客户端连接：", request.path, " 参数为: ", data)
    room_id = data.get('room_id')
    port = data.get('port')
    client_ip = request.remote_addr

    # 公私钥验证
    # unique_id = data.get('unique_id')
    # signature = data.get('signature')
    # sign_text = room_id + unique_id + str(port)
    # if sign_text == signature:
    #     return 204
    # else:
    #     return jsonify({'error_code': 100}), 401

    tag = True
    for room_ip in rooms_ip:
        if room_ip["room"] == room_id:
            tag = False
            room_ip["port"] = port
            room_ip["ip"] = client_ip
            print("该房间", room_ip["room"], "的ip端口：", room_ip["port"], room_ip["ip"])
    if tag:
        print("想要连接的房间未找到")
        return jsonify({'error_code': 100}), 401
    return jsonify({"message": "succeed"}), 200


# 服务器更改客户端状态
#@app.route('/api/control', methods=['POST'])
def control_client(room_id, is_on: bool, target_temp, wind):
    """
    send:
        operation   # start, stop, temperature, wind_speed, mode
        data        # example: 26  operations
    :return: 204 401
    """
    print("------------------------------------------------------------------------------------------------------------")

    print("管理员改变状态，正在向房间", room_id,"发请求,说明房间已改变:")
    print("每个房间的ip端口为：", rooms_ip)
    port = ''
    client_ip = ''
    for room_ip in rooms_ip:
        if room_ip["room"] == room_id:
            port = room_ip["port"]
            client_ip = room_ip["ip"]

    webhook_url = 'http://' + str(client_ip) + ':' + str(port) + '/api/control'  # 前端提供的Webhook URL
    print("webhookurl:", webhook_url)
    operation = "start, stop, temperature, wind_speed, mode"
    data = ''
    if is_on:
        data += '1, 0'
    else:
        data += '0, 1'
    if wind == "HIGH":
        wind = '3'
    elif wind == "MID":
        wind = '2'
    elif wind == "LOW":
        wind = '1'

    strr = ',' + str(target_temp) + ',' + str(wind) + ',' + 'cold'
    data += strr
    json = {
        "operation": operation,
        "data": data
    }
    print(json)
    # try:
    response = requests.post(webhook_url, json=json)
    response.raise_for_status()
    print("请求已发送成功!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
    # except requests.RequestException as e:
    #     print(f"Error sending webhook: {e}")

    return jsonify({"message": "Online successfully"}), 200


# 客户端主动更改状态
@app.route('/api/device/client/<string:room_id>', methods=['POST'])
def client_change(room_id):
    """
    input：
        room_id
        operation   # start, stop, temperature, wind_speed, mode, sweep
        data        # example: 26  operations
        time        # 更改日期
        unique_id   # random Unique ID, 16 characters
        signature   # SHA256withRSA, RSA 4096, sign text = operation + unique_id + data + time
    :return: 204
            401

curl.exe -v -X POST -d '{"room_id": "test", "operation": "start, stop, temperature, wind_speed, mode", "data": "1, 0, 16, 3, cold", "time": "2023-09-18T11:45:14+08:0", "unique_id": "1145141919810abc", "signature": "SHA256withRSA"}' http://localhost:11451/api/device/client/test?no-csrf
    """
    print("------------------------------------------------------------------------------------------------------------")

    # 解析数据
    params = request.get_json(force=True)
    print("客户端更改房间：", request.path, " 参数为: ", params)
    operation = params['operation']
    data = params['data']
    time = params['time']
    unique_id = params['unique_id']
    signature = params['signature']
    operations = [element.strip() for element in operation.split(',')]
    datas = [datas.strip() for datas in data.split(',')]
    operation_data = dict(zip(operations, datas))
    start = operation_data.get('start')
    target_temp = operation_data.get('temperature')
    wind_speed = operation_data.get('wind_speed')
    if wind_speed == str(3):
        wind_speed = 'HIGH'
    elif wind_speed == str(2):
        wind_speed = 'MID'
    elif wind_speed == str(1):
        wind_speed = 'LOW'

    if room_id not in scheduler.room_threads:
        print("该房间未入住")
        return jsonify({'error_code': 100}), 401

    power = True
    for room in scheduler.room_threads.values():
        if room.room_id == room_id:
            power = room.power

    print("           ", "请求的开关机", bool(int(start)), "房间当前的开关机", power)
    if bool(int(start)) == bool(power) and not bool(int(start)):
        print("房间", room_id, "想重复关机")
        return jsonify({'error_code': 100}), 401

    if bool(int(start)) == bool(power) and bool(int(start)):
        print("更改风速： ", room_id, " 房间号")
        scheduler.deal_with_speed_temp_change(room_id, int(target_temp), wind_speed)

    else:
        if start == '1':
            start = 'ON'
            print("开机： ", room_id, "房间号")
            scheduler.deal_with_on_and_off(room_id, int(target_temp), wind_speed, start)
        else:
            print("关机： ", room_id, "房间号")
            scheduler.deal_with_on_and_off(room_id, int(25), 'MID', start)

    return jsonify({"message": "Online successfully"}), 204




# 管理员给出所有未入住房间信息
@app.route('/api/admin/uncheck_in', methods=['get'])
def get_uncheckin_room_list():
    """

    :return: 200 room :
                    type: string array
            401

    调数据库

curl.exe -v -X get http://localhost:11451/api/admin/uncheck_in?no-csrf
    """
    try:
        # available = scheduler.get_available_room()
        available = []
        for room in weiruzhu:
            available.append(room)
        return jsonify(available), 200
    except:
        return jsonify({'error_code': 100}), 401


if __name__ == '__main__':
    db_init()
    t.start()
    # api = Blueprint('api', __name__, url_prefix='/api')
    # app.register_blueprint(api)
    with app.app_context():
        app.run(port=11451, debug=True, host='0.0.0.0')

    # 测试用例
    # rooms = ['1', '2', '3', '4', '5']
    # temps = ['32', '28', '30', '29', '35']
    # scheduler.add_room(rooms)
    # scheduler.set_room_initial_env_temp(rooms, temps)


    # scheduler.schedule()
"""
调试用，终端命令：
http://localhost:11451/__debugger__/683-942-319
开房test
curl.exe -v -X POST -d '{"room": "test", "temperature": 30}' http://localhost:11451/api/room/check_in?no-csrf
开房test2
curl.exe -v -X POST -d '{"room": "test2", "temperature": 32}' http://localhost:11451/api/room/check_in?no-csrf

客户端更改状态：开机
curl.exe -v -X POST -d '{"room_id": "test", "operation": "start, stop, temperature, wind_speed, mode", "data": "1, 0, 16, 3, cold", "time": "2023-09-18T11:45:14+08:0", "unique_id": "1145141919810abc", "signature": "SHA256withRSA"}' http://localhost:11451/api/device/client/test?no-csrf
关机
curl.exe -v -X POST -d '{"room_id": "test", "operation": "start, stop, temperature, wind_speed, mode", "data": "0, 1, 16, 3, cold", "time": "2023-09-18T11:45:14+08:0", "unique_id": "1145141919810abc", "signature": "SHA256withRSA"}' http://localhost:11451/api/device/client/test?no-csrf

管理员开机
curl.exe -v -X post -d '{"operation":"start, stop, temperature, wind_speed", "data":"1, 0, 18, 3"}' http://localhost:11451/api/admin/devices/test?no-csrf
管理员关机
curl.exe -v -X post -d '{"operation":"start, stop, temperature, wind_speed", "data":"0, 1, 18, 3"}' http://localhost:11451/api/admin/devices/test?no-csrf

"""
