from PyQt5 import QtCore, QtGui, QtWidgets
from qfluentwidgets import BodyLabel, ComboBox, CompactDoubleSpinBox, RadioButton, SwitchButton, TitleLabel
import sys
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QPushButton, QLabel, QTextEdit
from PyQt5.QtCore import Qt, QTimer, QDateTime, QTime
from os.path import isfile
import requests
import json
import hashlib
import rsa
import random
from datetime import datetime
import socket
import threading

# 创建Socket客户端
#client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
#client_socket.connect(('localhost', 8888))


# 生成唯一标识符
unique_id = ''.join(random.choices('abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789', k=16))
# 请求数据
room_id = '2-233'#房间号运行前更改
port = '11451'
#data = '26'#温度temperature
#operation = 'start'#空调状态power
#time = datetime.now().isoformat()#时间timestamp
# 配置服务器的URL
base_url = 'http://localhost:11451/api'#host:port
# 生成签名文本
sign_text = room_id + unique_id + port
signature = hashlib.sha256(sign_text.encode()).hexdigest()

sweep="On"#是否送风
class Ui_Form(object):
    def setupUi(self, Form):
        Form.setObjectName("Form")
        Form.resize(1200, 700)
        self.SwitchButton = SwitchButton(Form)
        self.SwitchButton.setGeometry(QtCore.QRect(450, 140, 91, 22))
        self.SwitchButton.setMaximumSize(QtCore.QSize(16777215, 1000))
        self.SwitchButton.setObjectName("SwitchButton")
        self.SwitchButton.setChecked(False)  # 设置初始状态为False

        self.CompactDoubleSpinBox = CompactDoubleSpinBox(Form)
        self.CompactDoubleSpinBox.setGeometry(QtCore.QRect(450, 220, 79, 33))
        self.CompactDoubleSpinBox.setMinimumSize(QtCore.QSize(79, 33))
        self.CompactDoubleSpinBox.setMaximumSize(QtCore.QSize(1000, 1000))
        self.CompactDoubleSpinBox.setMouseTracking(False)
        self.CompactDoubleSpinBox.setMinimum(16.0)
        self.CompactDoubleSpinBox.setMaximum(34.0)
        self.CompactDoubleSpinBox.setProperty("value", 25.0)
        self.CompactDoubleSpinBox.setObjectName("CompactDoubleSpinBox")
        self.TitleLabel = TitleLabel(Form)
        self.TitleLabel.setGeometry(QtCore.QRect(530, 50, 123, 37))
        self.TitleLabel.setObjectName("TitleLabel")
        self.BodyLabel = BodyLabel(Form)
        self.BodyLabel.setGeometry(QtCore.QRect(460, 110, 61, 21))
        self.BodyLabel.setObjectName("BodyLabel")
        self.BodyLabel_2 = BodyLabel(Form)
        self.BodyLabel_2.setGeometry(QtCore.QRect(460, 190, 63, 19))
        self.BodyLabel_2.setObjectName("BodyLabel_2")
        self.BodyLabel_3 = BodyLabel(Form)
        self.BodyLabel_3.setGeometry(QtCore.QRect(650, 190, 63, 19))
        self.BodyLabel_3.setObjectName("BodyLabel_3")

        self.RadioButton = RadioButton(Form)#中
        self.RadioButton.setGeometry(QtCore.QRect(670, 230, 51, 24))
        self.RadioButton.setObjectName("RadioButton")
        #self.RadioButton.setChecked(True)
        self.RadioButton_2 = RadioButton(Form)#高
        self.RadioButton_2.setGeometry(QtCore.QRect(730, 230, 51, 24))
        self.RadioButton_2.setObjectName("RadioButton_2")
        #self.RadioButton_2.setChecked(True)
        self.RadioButton_3 = RadioButton(Form)#低(默认)
        self.RadioButton_3.setGeometry(QtCore.QRect(600, 230, 51, 24))
        self.RadioButton_3.setObjectName("RadioButton_3")
        self.RadioButton_3.setChecked(True)

        self.BodyLabel_4 = BodyLabel(Form)
        self.BodyLabel_4.setGeometry(QtCore.QRect(660, 110, 63, 19))
        self.BodyLabel_4.setObjectName("BodyLabel_4")
        self.BodyLabel_5 = BodyLabel(Form)
        self.BodyLabel_5.setGeometry(QtCore.QRect(660, 140, 63, 19))
        self.BodyLabel_5.setObjectName("BodyLabel_5")
        self.BodyLabel_6 = BodyLabel(Form)
        self.BodyLabel_6.setGeometry(QtCore.QRect(460, 280, 63, 19))
        self.BodyLabel_6.setObjectName("BodyLabel_6")

        self.ComboBox = ComboBox(Form)
        self.ComboBox.setGeometry(QtCore.QRect(450, 310, 76, 32))
        self.ComboBox.setObjectName("ComboBox")
        self.ComboBox.addItem("制冷")
        self.ComboBox.addItem("制热")

        self.DateTimeLabel = QLabel(Form)
        self.DateTimeLabel.setGeometry(QtCore.QRect(10, 680, 200, 20))
        self.DateTimeLabel.setObjectName("DateTimeLabel")

        self.timer = QTimer(Form)
        self.timer.timeout.connect(self.updateDateTime)
        self.timer.start(1000)

        self.SwitchButton.checkedChanged.connect(self.on_button_state_changed)
        self.CompactDoubleSpinBox.valueChanged.connect(self.on_spinbox_value_changed)
        self.RadioButton.clicked.connect(self.on_radio_button_clicked)
        self.RadioButton_2.clicked.connect(self.on_radio_button_clicked)
        self.RadioButton_3.clicked.connect(self.on_radio_button_clicked)
        self.ComboBox.currentIndexChanged.connect(self.on_combobox_index_changed)

        self.countdown = 3  # 初始化计数器
        self.timer = QTimer()
        self.timer.timeout.connect(self.finalize_changes)

        self.retranslateUi(Form)
        QtCore.QMetaObject.connectSlotsByName(Form)
        # 创建Socket客户端
        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.client_socket.connect(('localhost', 8888))
        
        # 启动接收数据的线程
        self.receive_thread = threading.Thread(target=self.receive_data)
        self.receive_thread.start()

    def retranslateUi(self, Form):
        _translate = QtCore.QCoreApplication.translate
        Form.setWindowTitle(_translate("Form", "Form"))
        self.TitleLabel.setText(_translate("Form", "空调面板"))
        self.BodyLabel.setText(_translate("Form", "空调开关"))
        self.BodyLabel_2.setText(_translate("Form", "设定温度"))
        self.BodyLabel_3.setText(_translate("Form", "设定风速"))
        self.RadioButton_2.setText(_translate("Form", "高"))
        self.RadioButton.setText(_translate("Form", "中"))
        self.RadioButton_3.setText(_translate("Form", "低"))
        self.BodyLabel_4.setText(_translate("Form", "房间号"))
        self.BodyLabel_5.setText(_translate("Form", room_id))
        self.BodyLabel_6.setText(_translate("Form", "设定模式"))
        self.ComboBox.setText(_translate("Form", "制热"))
        self.ComboBox.setText(_translate("Form", "制冷"))
    
    def update_panel(self, data):
        # 将接收到的数据转换为字典
        data_dict = eval(data)
        # 更新空调面板按钮的值
        # 以下是一个简单的示例，你可以根据你的业务逻辑进行修改
        if self.RadioButton.isChecked():
            selected_radio_text = "中"
        elif self.RadioButton_2.isChecked():
            selected_radio_text = "高"
        elif self.RadioButton_3.isChecked():
            selected_radio_text = "低"
        start=data_dict.get("start", "not is_on")
        stop=data_dict.get("stop", "is_on")
        temperature = data_dict.get("设定温度", 25)
        wind_speed = data_dict.get("风速", "低")
        mode = data_dict.get("设定模式", "cold")
        sweep=data_dict.get("是否送风", "On")
        if start=="is_on" and stop=="not is_on":
            self.SwitchButton.setChecked(True)
        if start=="not is_on" and stop=="is_on":
            self.SwitchButton.setChecked(False)
        if temperature!=self.CompactDoubleSpinBox.value():
            self.CompactDoubleSpinBox.setProperty("value", temperature)
        if wind_speed=="低":
            self.RadioButton_3.setChecked(True)
        if wind_speed=="中":
            self.RadioButton.setChecked(True)
        if wind_speed=="高":
            self.RadioButton_2.setChecked(True)
        if mode=="cold" or mode=="Cold":
            self.ComboBox.setCurrentText("制冷")
        if mode=="hot" or mode=="Hot":
            self.ComboBox.setCurrentText("制热")
        if sweep=="On":
            sweep = "On"
        if sweep=="stop":
            sweep = "stop"

    def receive_data(self):
        while True:
            data = self.client_socket.recv(1024).decode()
            if data:
                self.update_panel(data)


    def updateDateTime(self):
        # 更新 QLabel 显示当前日期和时间
        current_time = QTime.currentTime()
        current_date_time = QDateTime.currentDateTime().toString('yyyy-MM-dd hh:mm:ss')
        self.DateTimeLabel.setText(current_date_time)

    def on_button_state_changed(self,checked):
        if checked:
            self.start_timer()
        else:
            self.start_timer()
        
        #data = self.get_panel_data()
        #self.save_data_to_file(data)

    def on_spinbox_value_changed(self):
        self.start_timer()
        #data = self.get_panel_data()
        #self.save_data_to_file(data)

    def on_radio_button_clicked(self):
        self.start_timer()
        #data = self.get_panel_data()
        #self.save_data_to_file(data)

    def on_combobox_index_changed(self):
        self.start_timer()
        #data = self.get_panel_data()
        #self.save_data_to_file(data)

    def start_timer(self):
        self.countdown = 3  # 重置计数器
        self.timer.start(1000)

    def finalize_changes(self):
        self.countdown -= 1
        if self.countdown == 0:
            self.stop_timer()
            data = self.get_panel_data()
            time=data.get('更改时间')
            postdata=[value for key, value in data.items() if key != "更改时间"]
            self.save_data_to_file(data)
            self.client_online(room_id, port, unique_id, signature)
            self.get_current_status(room_id,postdata,time)
    
    def client_online(self,room_id, port, unique_id, signature):
        url = 'http://localhost:11451/api/device/client'
        headers = {'Content-Type': 'application/json'}
        postdata = {
            'room_id': room_id,
            'port': port,
            'unique_id': unique_id,
            'signature': signature
        }
        response = requests.post(url, headers=headers, data=json.dumps(postdata))
        if response.status_code == 204:
            print('客户端连接成功')
        elif response.status_code == 401:
            print('未签名或签名不匹配')
        else:
            print('连接请求失败')
    
    def get_current_status(self,room_id,data,time):
        url = f'http://localhost:11451/api/device/client/{room_id}'
        headers = {'Content-Type': 'application/json'}
        postdata = {
            'room_id': room_id,
            'operation': "空调开关, 设定温度, 风速, 设定模式,是否送风",# start, stop, temperature, wind_speed, mode, sweep
            'data': data,# example: 26  operations
            'time': time,
            'unique_id': unique_id,
            'signature': signature
        }
        response = requests.post(url, headers=headers,data=json.dumps(postdata))
        if response.status_code == 204:
            print('当前状态请求成功')
        elif response.status_code == 401:
            print('未签名或签名不匹配')
        else:
            print('当前状态请求失败')
    
    def stop_timer(self):
        self.timer.stop()

    def get_panel_data(self):
        import datetime
        selected_radio_text = ""
        if self.RadioButton.isChecked():
            selected_radio_text = "中"
        elif self.RadioButton_2.isChecked():
            selected_radio_text = "高"
        elif self.RadioButton_3.isChecked():
            selected_radio_text = "低"
        # 从面板上所有相关的小部件中收集数据
        panel_data = {
            "空调开关": "On" if self.SwitchButton.isChecked() else "Off",
            "设定温度": self.CompactDoubleSpinBox.value(),
            "风速": selected_radio_text,
            "设定模式": self.ComboBox.currentText(),
            "更改时间": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "是否送风": sweep,#默认开启
            # 根据需要添加更多小部件
        }
        #panel_data["更改时间"] = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        return panel_data
    
    def save_data_to_file(self, data):
        import os
        # 获取当前脚本所在的目录
        current_directory = os.path.dirname(os.path.abspath(__file__))
        # 构建保存文件的完整路径
        file_path = os.path.join(current_directory, "client_operation_data.txt")
        with open(file_path, "a") as file:
            file.write(str(data) + "\n")