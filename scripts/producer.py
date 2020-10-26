# coding: utf-8
import csv
import time
from kafka import KafkaProducer

# 实例化一个KafkaProducer示例，用于向kafka投递信息
producer = KafkaProducer(bootstrap_servers='192.168.100.21:9092')
# 打开数据文件
csvfile = open("../data/user_log.csv", "r", encoding="utf-8")
# 生成一个可用于读取csv文件的reader
reader = csv.reader(csvfile)


def producers(i, title, topic):
    for line in reader:
        name = str(line[i])  # 商品类别在每行日志代码的第2个元素
        if name == title:
            continue  # 去除第一行表头
        print(line[i])
        time.sleep(0.1)  # 每隔0.1秒发送一行数据
        producer.send(topic, line[i].encode('utf8'))

# 漏斗图
def message():
    for line in reader:
        cat = line[2]  # 商品类别在每行日志代码的第2个元素
        action = line[7]
        if cat == "cat_id":
            continue  # 去除第一行表头
        if action == "action":
            continue  # 去除第一行表头
        mydata = cat + " " + action
        print(mydata)
        time.sleep(0.1)  # 每隔0.1秒发送一行数据
        producer.send("message", mydata.encode('utf8'))

if __name__ == '__main__':
    # producers(9, "gender", "gender")           # 性别
    # producers(2, "cat_id", "cat")             # 商品类别
    # producers(10, "province", "province")     # 收获省份
    # producers(8, "age_range", "age")          # 年龄段
    # producers(7, "action", "action")          # 用户购买行为
    message()                  # 漏斗图数据
