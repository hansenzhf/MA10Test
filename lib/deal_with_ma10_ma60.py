# -*- coding: utf-8 -*-
__author__ = "hank"

import unittest
import pandas
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

def pd_read_data(file_path, dict, code):
    if code in dict:
        name = dict[code]
    file_name = file_path + name + ".csv"
    return pandas.read_csv(file_name)

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
        try:
            os.remove(file_name)
        except:
            print("csv is not exist.")

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
        tt = list(set(res_name_list))
        tt.sort()
        for r in tt:
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
                    if (last_price > ma10_price and 
                        test_data[line_index-1][5] > test_data[line_index-1][-3] and 
                        test_data[line_index-2][5] > test_data[line_index-2][-3] and 
                        test_data[line_index-3][5] < test_data[line_index-3][-3] and 
                        test_data[line_index-4][5] < test_data[line_index-4][-3]):
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
        tt = list(set(res_name_list))
        tt.sort()
        for r in tt:
            res = res + r + "\n"
        print(res)
        body = body + res
        SendMail().send_mail(subject, body)

    def deal_with_trend(self):
        # 清理旧记录
        file_name = csv_path + "buy_date_record.csv"
        os.remove(file_name)

        code_list, name_list = GetData().read_index_code()
        dict = {}
        for i in range(0, len(code_list)):
            dict[code_list[i]] = name_list[i]
        # print(first_dict)
        print(time.strftime("%Y-%m-%d", time.localtime()))
        subject = "【买入时机测试结果】" + time.strftime("%Y-%m-%d", time.localtime())
        body = ""

        res_name_list = []
        # dict = {"sz000009": "中国宝安"}
        dict = {"sz300750": "宁德时代"}
        # print(dict)
        for code in dict:
            name = dict[code]
            #print("开始处理<" + name + ">")
            buy_date_list = []

            # 读取csv数据
            try:
                #test_data = read_data(data_path, dict, code)
                df = pd_read_data(data_path, dict, code)
            except Exception as e:
                print("读取数据失败：<" + name + ">.csv")
                continue

            idx_max = df['close'].idxmax()
            print(idx_max)
            print(df.loc[idx_max, 1])            

            if get_diff_days_to_now(df.loc[idx_max, 1]) < 70:
                buy_date_list.append(df.loc[idx_max, 1])
                res_name_list.append(name)


            res = "[" + name + "] 买：" + str(buy_date_list) + "\n"
            print(res)
            body = body + res
            print("【处理完成】")
            save_buy_date(csv_path, code, name, buy_date_list)

        body = ""
        res = "[trend提示] " + "\n"
        tt = list(set(res_name_list))
        tt.sort()
        for r in tt:
            res = res + r + "\n"
        print(res)
        body = body + res
        #SendMail().send_mail(subject, body)

    def deal_with_ma120(self):
        # 清理旧记录
        file_name = csv_path + "buy_date_record.csv"
        try:
            os.remove(file_name)
        except:
            print("csv is not exist.")

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

            for line in test_data[-600:]:
                #print(line)
                try:
                    last_price = float(line[5])
                    ma120_price = float(line[-3])
                    ma180_price = float(line[-2])
                    ma240_price = float(line[-1])
                    line_index = test_data.index(line)

                    # 找到每日和120日线交叉处
                    if last_price > ma120_price and test_data[line_index-2][-1] > test_data[line_index-2][5] and test_data[line_index+2][-1] < test_data[line_index+2][5]:
                        i = 0
                        count_ma120 = 0
                        count_last = 0
                        #print(test_data[line_index+20][1])
                        while i < 90:
                            # 这个交叉处后90天,日线始终在120日线上方，每日收盘价始终在120日上方，120日线始终在240日线上方
                            i += 1
                            if test_data[line_index + 2 + i][-3] > test_data[line_index + 2 + i][-1]:
                                #print("a:" + test_data[line_index + 2 + i][-3] + "b:" + test_data[line_index + 2 + i][-2])
                                count_ma120 += 1
                            if test_data[line_index + 3 + i][5] > test_data[line_index + 3 + i][-3]:
                                #print("c:" + test_data[line_index + 2 + i][-3] + "d:" + test_data[line_index + 2 + i][-2])
                                count_last += 1
                            if count_ma120 == 90 and count_last == 90:
                                buy_date_list.append(test_data[line_index+90][1])
                                #print(test_data[line_index+20][1])
                                # 距离现在20天内的日期列入
                                if get_diff_days_to_now(test_data[line_index+90][1]) < 20:
                                    res_name_list.append(name)

                except Exception as e:
                    continue
            res = "[" + name + "] 买：" + str(buy_date_list) + "\n"
            print(res)
            body = body + res
            print("【处理完成】")
            save_buy_date(csv_path, code, name, buy_date_list)

        body = ""
        res = "[日线连续在120日线上方90天买入点20日内提示] " + "\n"
        tt = list(set(res_name_list))
        tt.sort()
        for r in tt:
            res = res + r + "\n"
        print(res)
        body = body + res
        SendMail().send_mail(subject, body)

    def deal_with_ma240(self):
        # 清理旧记录
        file_name = csv_path + "buy_date_record.csv"
        try:
            os.remove(file_name)
        except:
            print("csv is not exist.")

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

            for line in test_data[-600:]:
                #print(line)
                try:
                    last_price = float(line[-5])
                    ma120_price = float(line[-3])
                    ma180_price = float(line[-2])
                    ma240_price = float(line[-1])
                    line_index = test_data.index(line)

                    # 找到每日和240日线交叉处
                    #if ((last_price > ma240_price) and (test_data[line_index-2][-1] > test_data[line_index-2][5])) and (test_data[line_index+2][-1] < test_data[line_index+2][5]):

                    #print(type(test_data[line_index - 2][-1]), type(test_data[line_index - 2][-5]))
                    if (float(test_data[line_index - 2][-1]) > float(test_data[line_index - 2][-5])) and (last_price > ma240_price):
                        i = 0
                        count_ma240 = 0
                        count_last = 0
                        print(line_index, line[1], last_price, ma240_price, test_data[line_index - 2][1], test_data[line_index - 2][-1],
                         test_data[line_index - 2][-5])
                        while i < 50:
                            # 这个交叉处后50天,日线始终在240日线上方，每日收盘价始终在240日上方
                            i += 1
                            if test_data[line_index + 1 + i][-5] > test_data[line_index + 1 + i][-1]:
                                #print("a:" + test_data[line_index + 2 + i][-3] + "b:" + test_data[line_index + 2 + i][-2])
                                count_ma240 += 1
                            if count_ma240 == 50:
                                #buy_date_list.append(test_data[line_index+50][1])
                                #print(test_data[line_index+20][1])
                                # 距离现在80天内的日期列入
                                if get_diff_days_to_now(test_data[line_index+50][1]) < 80:
                                    buy_date_list.append(test_data[line_index][1])
                                    res_name_list.append(name + ' ' + str(test_data[line_index][1]))

                except Exception as e:
                    continue
            res = "[" + name + "] 买：" + str(buy_date_list) + "\n"
            print(res)
            body = body + res
            print("【处理完成】")
            save_buy_date(csv_path, code, name, buy_date_list)

        body = "Total:" + str(len(res_name_list)) + "\n"
        res = "[日线连续在240日线上方50天买入点80日内提示] " + "\n"
        print("Total:" + str(len(res_name_list)))
        tt = list(set(res_name_list))
        tt.sort()
        for r in tt:
            res = res + r + "\n"
        print(res)
        body = body + res
        SendMail().send_mail(subject, body)

    def deal_with_ma120_ma240(self):
        # 清理旧记录
        file_name = csv_path + "buy_date_record.csv"
        try:
            os.remove(file_name)
        except:
            print("csv is not exist.")

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

            for line in test_data[-600:]:
                #print(line)
                try:
                    last_price = float(line[-5])
                    ma120_price = float(line[-3])
                    ma180_price = float(line[-2])
                    ma240_price = float(line[-1])
                    line_index = test_data.index(line)

                    # 找到每日和240日线交叉处
                    #if ((last_price > ma240_price) and (test_data[line_index-2][-1] > test_data[line_index-2][5])) and (test_data[line_index+2][-1] < test_data[line_index+2][5]):

                    #print(type(test_data[line_index - 2][-1]), type(test_data[line_index - 2][-5]))
                    if (float(test_data[line_index - 2][-1]) > float(test_data[line_index - 2][-5])) and (last_price > ma240_price):
                        i = 0
                        count_ma120 = 0
                        count_last = 0
                        print(line_index, line[1], last_price, ma240_price, test_data[line_index - 2][1], test_data[line_index - 2][-3],
                         test_data[line_index - 2][-5])
                        while i < 80:
                            # 这个交叉处后80天,日线始终在120日线上方，每日收盘价始终在120日上方
                            i += 1
                            if test_data[line_index + 1 + i][-5] > test_data[line_index + 1 + i][-3]:
                                #print("a:" + test_data[line_index + 2 + i][-3] + "b:" + test_data[line_index + 2 + i][-2])
                                count_ma120 += 1
                            if count_ma120 == 80:
                                #buy_date_list.append(test_data[line_index+50][1])
                                #print(test_data[line_index+20][1])
                                # 距离现在60天内的日期列入
                                if get_diff_days_to_now(test_data[line_index+80][1]) < 60:
                                    buy_date_list.append(test_data[line_index][1])
                                    res_name_list.append(name + ' ' + str(test_data[line_index][1]))

                except Exception as e:
                    continue
            res = "[" + name + "] 买：" + str(buy_date_list) + "\n"
            print(res)
            body = body + res
            print("【处理完成】")
            save_buy_date(csv_path, code, name, buy_date_list)

        body = "Total:" + str(len(res_name_list)) + "\n"
        res = "[日线进入240日上方连续在120日线上方80天买入点60日内提示] " + "\n"
        print("Total:" + str(len(res_name_list)))
        tt = list(set(res_name_list))
        tt.sort()
        for r in tt:
            res = res + r + "\n"
        print(res)
        body = body + res
        SendMail().send_mail(subject, body)



    def deal_with_ma240_down(self):
        # 清理旧记录
        file_name = csv_path + "buy_date_record.csv"
        try:
            os.remove(file_name)
        except:
            print("csv is not exist.")

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

            for line in test_data[-600:]:
                #print(line)
                try:
                    last_price = float(line[-5])
                    ma120_price = float(line[-3])
                    ma180_price = float(line[-2])
                    ma240_price = float(line[-1])
                    line_index = test_data.index(line)

                    # 找到每日和240日线交叉处
                    #if ((last_price > ma240_price) and (test_data[line_index-2][-1] > test_data[line_index-2][5])) and (test_data[line_index+2][-1] < test_data[line_index+2][5]):

                    #print(type(test_data[line_index - 2][-1]), type(test_data[line_index - 2][-5]))
                    if (float(test_data[line_index - 2][-1]) < float(test_data[line_index - 2][-5])) and (last_price < ma240_price):
                        i = 0
                        count_ma240 = 0
                        count_last = 0
                        print(line_index, line[1], last_price, ma240_price, test_data[line_index - 2][1], test_data[line_index - 2][-1],
                         test_data[line_index - 2][-5])
                        while i < 30:
                            # 这个交叉处后30天,日线始终在240日线上方，每日收盘价始终在240日上方
                            i += 1
                            if test_data[line_index + 1 + i][-5] < test_data[line_index + 1 + i][-1]:
                                #print("a:" + test_data[line_index + 2 + i][-3] + "b:" + test_data[line_index + 2 + i][-2])
                                count_ma240 += 1
                            if count_ma240 == 30:
                                buy_date_list.append(test_data[line_index+30][1])
                                #print(test_data[line_index+20][1])
                                # 距离现在30天内的日期列入
                                if get_diff_days_to_now(test_data[line_index+30][1]) < 30:
                                    res_name_list.append(name)

                except Exception as e:
                    continue
            res = "[" + name + "] 买：" + str(buy_date_list) + "\n"
            print(res)
            body = body + res
            print("【处理完成】")
            save_buy_date(csv_path, code, name, buy_date_list)

        body = "Total:" + str(len(res_name_list)) + "\n"
        res = "[日线连续在240日线下方30天买入点30日内提示] " + "\n"
        print("Total:" + str(len(res_name_list)))
        tt = list(set(res_name_list))
        tt.sort()
        for r in tt:
            res = res + r + "\n"
        print(res)
        body = body + res
        SendMail().send_mail(subject, body)

    def two_eight_turn(self):
        subject = "【二八轮动测试结果】" + time.strftime("%Y-%m-%d", time.localtime())        

        code_300 = 'sh000300'
        p300_1, p300_20 = GetData().get_index_price(code_300)
        delta300 = p300_1 - p300_20
        percent300 = delta300/p300_20
        body_1 = "【沪深300】: %f（今天）, %f（20天前）, %f（差值）, %f%%（差值百分比）\n" % (p300_1, p300_20, delta300, percent300*100)
        code_cyb = 'sz399006'
        pcyb_1, pcyb_20 = GetData().get_index_price(code_cyb)
        deltacyb = pcyb_1 - pcyb_20
        percent_cyb = deltacyb/pcyb_20
        body_2 = "【创业板】:  %f（今天）, %f（20天前）, %f（差值）, %f%%（差值百分比）\n" % (pcyb_1, pcyb_20, deltacyb, percent_cyb*100)

        if percent_cyb > percent300 and percent_cyb > 0:
            body_3 = "【买入】创业板ETF\n"
        elif percent300 > percent_cyb and percent300 > 0:
            body_3 = "【买入】300ETF\n"
        else:
            body_3 = "【买入】银华日利\n"
        
        body = body_1 + body_2 + body_3
        print(body)
        SendMail().send_mail(subject, body)   
      
    def two_eight_turn_v2(self):
        subject = "【二八轮动20天测试结果】" + time.strftime("%Y-%m-%d", time.localtime())        

        code_300 = 'sh000300'
        p300_1, p300_20 = GetData().get_index_price(code_300)
        delta300 = p300_1 - p300_20
        percent300 = delta300/p300_20
        body_1 = "【沪深300】: %f（今天）, %f（20天前）, %f（差值）, %f%%（差值百分比）\n" % (p300_1, p300_20, delta300, percent300*100)
        code_cyb = 'sz399006'
        pcyb_1, pcyb_20 = GetData().get_index_price(code_cyb)
        deltacyb = pcyb_1 - pcyb_20
        percent_cyb = deltacyb/pcyb_20
        body_2 = "【创业板】:  %f（今天）, %f（20天前）, %f（差值）, %f%%（差值百分比）\n" % (pcyb_1, pcyb_20, deltacyb, percent_cyb*100)

        if percent_cyb > percent300 and percent_cyb > 0:
            body_3 = "【买入】创业板ETF\n"
        elif percent300 > percent_cyb and percent300 > 0:
            body_3 = "【买入】300ETF\n"
        else:
            body_3 = "【买入】纳指100\n"
        
        body = body_1 + body_2 + body_3
        print(body)
        SendMail().send_mail(subject, body)   
      

    def two_eight_turn_v3(self):
        subject = "【二八轮动25天间隔测试结果】" + time.strftime("%Y-%m-%d", time.localtime())        

        code_300 = 'sh000300'
        p300_1, p300_20 = GetData().get_index_price_25(code_300)
        delta300 = p300_1 - p300_20
        percent300 = delta300/p300_20
        body_1 = "【沪深300】: %f（今天）, %f（25天前）, %f（差值）, %f%%（差值百分比）\n" % (p300_1, p300_20, delta300, percent300*100)
        code_cyb = 'sz399006'
        pcyb_1, pcyb_20 = GetData().get_index_price_25(code_cyb)
        deltacyb = pcyb_1 - pcyb_20
        percent_cyb = deltacyb/pcyb_20
        body_2 = "【创业板】:  %f（今天）, %f（25天前）, %f（差值）, %f%%（差值百分比）\n" % (pcyb_1, pcyb_20, deltacyb, percent_cyb*100)

        if percent_cyb > percent300 and percent_cyb > 0:
            body_3 = "【买入】创业板ETF\n"
        elif percent300 > percent_cyb and percent300 > 0:
            body_3 = "【买入】300ETF\n"
        else:
            body_3 = "【买入】纳指100\n"
        
        body = body_1 + body_2 + body_3
        print(body)
        SendMail().send_mail(subject, body)   
      

if __name__ == "__main__":
    #DealWithMA10MA60().deal_with_ma120_ma240()
    DealWithMA10MA60().two_eight_turn_v2()
    #DealWithMA10MA60().two_eight_turn_v3()
    
