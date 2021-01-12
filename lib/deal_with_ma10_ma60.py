# -*- coding: utf-8 -*-
__author__ = "hank"

import unittest
import sys
import os
import time
import csv
import datetime
sys.path.append("../")
from lib.send_mail import SendMail
from lib.get_data import GetData


# 获取csv文件路径
local_path = os.path.abspath('.')
father_path = os.path.dirname(local_path)
csv_path = father_path + "/resources/"
data_path = father_path + "/resources/data/"

# 读取数据
def read_data(file_path, dict, code):
    if code in dict:
        name = dict[code]
    file_name = file_path + name + ".csv"
    with open(file_name, 'r') as f:
        reader = csv.reader(f)
        result = list(reader)
    #print(name)
    #print(result[-1])
    return result

def save_buy_date(file_path, code, name, date_list):
    # 1. 创建文件对象
    file_name = file_path + "buy_date_record.csv"
    f = open(file_name, "a+", newline='', encoding='UTF-8')

    # 2. 基于文件对象构建 csv写入对象
    csv_writer = csv.writer(f)

    # 3. 构建列表头
    #csv_writer.writerow(["代码", "名称", "买入时间"])

    # 4. 写入csv文件内容
    csv_writer.writerow([code, name, str(date_list)])

    # 5. 关闭文件
    f.close()


# 与当前相差天数
def get_diff_days_to_now(date_str):
    now_time = time.localtime(time.time())
    compare_time = time.strptime(date_str, "%Y-%m-%d")
    #print(now_time, compare_time)
    # 比较日期
    date1 = datetime.datetime(compare_time[0], compare_time[1], compare_time[2])
    date2 = datetime.datetime(now_time[0], now_time[1], now_time[2])
    #print(date1, date2)
    diff_days = (date2 - date1).days
    #print(diff_days)

    return diff_days

class DealWithMA10MA60(object):

    def deal_with_ma60(self):
        # 清理旧记录
        file_name = csv_path + "buy_date_record.csv"
        os.remove(file_name)

        code_list, name_list = GetData().read_index_code()
        dict = {}
        for i in range(0, len(code_list)):
            dict[code_list[i]] = name_list[i]
        #print(first_dict)
        print(time.strftime("%Y-%m-%d", time.localtime()))
        subject = "【买入时机测试结果】" + time.strftime("%Y-%m-%d", time.localtime())
        body = ""

        res_name_list = []
        #dict = {"sz000009": "中国宝安"}
        #dict = {"sz300750": "宁德时代"}
        #print(dict)
        for code in dict:
            name = dict[code]
            print("开始处理<" + name + ">")
            buy_date_list = []

            # 读取csv数据
            try:
                test_data = read_data(data_path, dict, code)
            except Exception as e:
                print("读取数据失败：<" + name + ">.csv")
                continue

            for line in test_data[-180:]:
                #print(line)
                try:
                    last_price = float(line[5])
                    ma10_price = float(line[-3])
                    ma60_price = float(line[-2])
                    line_index = test_data.index(line)

                    # 找到10日线和60日线交叉处
                    if ma10_price > ma60_price and test_data[line_index-2][-2] > test_data[line_index-2][-3] and test_data[line_index+2][-2] < test_data[line_index+2][-3]:
                        i = 0
                        count_ma10 = 0
                        count_last = 0
                        #print(test_data[line_index+20][1])
                        while i < 20:
                            # 这个交叉处后20天,10日线始终在60日线上方，每日收盘价始终在60日上方
                            i += 1
                            if test_data[line_index + 2 + i][-3] > test_data[line_index + 2 + i][-2]:
                                #print("a:" + test_data[line_index + 2 + i][-3] + "b:" + test_data[line_index + 2 + i][-2])
                                count_ma10 += 1
                            if test_data[line_index + 3 + i][5] > test_data[line_index + 3 + i][-2]:
                                #print("c:" + test_data[line_index + 2 + i][-3] + "d:" + test_data[line_index + 2 + i][-2])
                                count_last += 1
                            if count_ma10 == 20 and count_last == 20:
                                buy_date_list.append(test_data[line_index+20][1])
                                #print(test_data[line_index+20][1])
                                if get_diff_days_to_now(test_data[line_index+20][1]) < 20:
                                    res_name_list.append(name)

                except Exception as e:
                    continue
            res = "[" + name + "] 买：" + str(buy_date_list) + "\n"
            print(res)
            body = body + res
            print("【处理完成】")
            save_buy_date(csv_path, code, name, buy_date_list)

        body = ""
        res = "[10日线连续在60日线上方20天买入点5日内提示] " + "\n"
        for r in set(res_name_list):
            res = res + r + "\n"
        print(res)
        body = body + res
        SendMail().send_mail(subject, body)

    def deal_with_ma10(self):
        # 清理旧记录
        file_name = csv_path + "buy_date_record.csv"
        os.remove(file_name)

        code_list, name_list = GetData().read_index_code()
        dict = {}
        for i in range(0, len(code_list)):
            dict[code_list[i]] = name_list[i]
        #print(first_dict)
        print(time.strftime("%Y-%m-%d", time.localtime()))
        subject = "【买入时机测试结果】" + time.strftime("%Y-%m-%d", time.localtime())
        body = ""

        res_name_list = []
        #dict = {"sz000009": "中国宝安"}
        #dict = {"sz300750": "宁德时代"}
        #print(dict)
        for code in dict:
            name = dict[code]
            print("开始处理<" + name + ">")
            buy_date_list = []

            # 读取csv数据
            try:
                test_data = read_data(data_path, dict, code)
            except Exception as e:
                print("读取数据失败：<" + name + ">.csv")
                continue

            for line in test_data[-180:]:
                #print(line)
                try:
                    last_price = float(line[5])
                    ma10_price = float(line[-3])
                    ma60_price = float(line[-2])
                    line_index = test_data.index(line)

                    # 找到连续3天在10日线上
                    if last_price > ma10_price and test_data[line_index-1][5] > test_data[line_index-1][-3] and test_data[line_index-2][5] > test_data[line_index-2][-3] and test_data[line_index-3][5] < test_data[line_index-3][-3]:
                        i = 0
                        count_ma10 = 0
                        count_last = 0
                        #print(test_data[line_index+20][1])
                        while i < 20:
                            # 这个交叉处后20天,10日线始终在60日线上方，每日收盘价始终在60日上方
                            i += 1
                            if test_data[line_index - 20 + i][-3] > test_data[line_index - 20 + i][-2]:
                                #print("a:" + test_data[line_index + 2 + i][-3] + "b:" + test_data[line_index + 2 + i][-2])
                                count_ma10 += 1
                            if test_data[line_index - 20 + i][5] > test_data[line_index - 20 + i][-2]:
                                #print("c:" + test_data[line_index + 2 + i][-3] + "d:" + test_data[line_index + 2 + i][-2])
                                count_last += 1
                            if count_ma10 == 20 and count_last == 20:
                                buy_date_list.append(test_data[line_index][1])
                                #print(test_data[line_index+20][1])
                                if get_diff_days_to_now(test_data[line_index][1]) < 7:
                                    res_name_list.append(name)

                except Exception as e:
                    continue
            res = "[" + name + "] 买：" + str(buy_date_list) + "\n"
            print(res)
            body = body + res
            print("【处理完成】")
            save_buy_date(csv_path, code, name, buy_date_list)

        body = ""
        res = "[连续三天在10日线买入点7日内提示] " + "\n"
        for r in set(res_name_list):
            res = res + r + "\n"
        print(res)
        body = body + res
        SendMail().send_mail(subject, body)


if __name__ == "__main__":
    DealWithMA10MA60().deal_with_ma10()
    
