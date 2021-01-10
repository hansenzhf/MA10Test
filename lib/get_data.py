# -*-coding:utf-8-*-
__author__ = 'hank'

import akshare as ak
import os
import sys
import csv

class GetData(object):
    def __init__(self):
        self.local = os.path.abspath('.')
        self.father_path = os.path.dirname(self.local)
        self.list_path = self.father_path + "/resources/"
        self.data_path = self.father_path + "/resources/data/"

    def get_stock_list(self):
        # 获取股票列表
        stock_info_a_code_name_df = ak.stock_info_a_code_name()
        print(stock_info_a_code_name_df)
        file_name = self.list_path + "stock_list.csv"
        stock_info_a_code_name_df['code'] = stock_info_a_code_name_df['code'].astype(str)
        #print(stock_info_a_code_name_df['code'])
        stock_info_a_code_name_df.to_csv(file_name, encoding="utf_8_sig")

    def read_index_code(self):
        # 读取股票列表数据
        file_name = self.list_path + "stock_list.csv"
        with open(file_name, mode='r', encoding='UTF-8') as f:
            reader = csv.reader(f)
            result = list(reader)
        # print(name)
        # print(result[-1])
        code_list = []
        name_list = []
        for line in result[1:]:
            code_list.append(line[1])
            name_list.append(line[2])
        return code_list, name_list        

    def get_data_from_internet(self, code, name):
        '''获取数据并保存到csv'''
        while len(code) < 6:
            code = '0' + code

        if code.startswith('6'):
            code = "sh" + code
        if code.startswith('3') or code.startswith('0'):
            code = "sz" + code

        print(code)
        # 获取原始数据
        original_data = ak.stock_zh_a_daily(symbol=code, adjust="qfq")
        # 取过去200天数据
        try:
            df = original_data.reset_index().iloc[-200:,:6]
        except:
            df = original_data.reset_index().iloc[:, :6]
        # 去除空值且从零开始编号索引
        df = df.dropna(how='any').reset_index(drop=True)
        #print(df)
        # 按日期排序
        df = df.sort_values(by='date', ascending=True)

        # 均线数据
        df['10'] = df.close.rolling(10).mean()
        df['60'] = df.close.rolling(60).mean()
        df['250'] = df.close.rolling(250).mean()

        # 写入csv
        file_name = self.data_path + name + ".csv"
        df.to_csv(file_name)
        print("<" + name + ">数据完成")

        return df

    def get_data_together(self):
        # 获取所有股票数据
        c_list, n_list = self.read_index_code()
        #print(c_list[0], n_list[0])
        count = len(c_list)
        for i in range(0, count):
            try:
                print("开始获取<" + n_list[i] + ">")
                self.get_data_from_internet(c_list[i], n_list[i])     
            except:
                continue

if __name__ == "__main__":
    GetData().get_stock_list()
    #GetData().get_data_together()
    #GetData().get_data_from_internet('sz000001', '平安银行')

