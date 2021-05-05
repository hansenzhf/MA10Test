# -*-coding:utf-8-*-
__author__ = 'hank'

import akshare as ak
import os
import sys
import csv
import pandas as pd

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
        # 取过去600天数据
        try:
            df = original_data.reset_index().iloc[-600:,:6]
        except:
            df = original_data.reset_index().iloc[:, :6]
        # 去除空值且从零开始编号索引
        df = df.dropna(how='any').reset_index(drop=True)
        #print(df)
        # 按日期排序
        df = df.sort_values(by='date', ascending=True)

        # 均线数据
        # df['10'] = df.close.rolling(10).mean()
        # df['60'] = df.close.rolling(60).mean()
        # df['250'] = df.close.rolling(250).mean()
        df['120'] = df.close.rolling(120).mean()
        df['180'] = df.close.rolling(180).mean()
        df['240'] = df.close.rolling(240).mean()

        # 写入csv
        file_name = self.data_path + name + ".csv"
        df.to_csv(file_name)
        print("<" + name + ">数据完成")

        return df

    def get_minute_data_from_internet(self, code, name, period):
        '''获取数据并保存到csv'''
        while len(code) < 6:
            code = '0' + code

        if code.startswith('6'):
            code = "sh" + code
        if code.startswith('3') or code.startswith('0'):
            code = "sz" + code

        print(code)
        # 获取原始数据
        original_data = ak.stock_zh_a_minute(symbol=code, period=period, adjust="qfq")
        # 取过去50天数据
        try:
            df = original_data.reset_index().iloc[-200:,:6]
        except:
            df = original_data.reset_index().iloc[:, :6]
        # 去除空值且从零开始编号索引
        df = df.dropna(how='any').reset_index(drop=True)
        print(df)
        # 按日期排序
        df = df.sort_values(by='day', ascending=True)

        # 均线数据
        df['10'] = df.close.rolling(10).mean()
        df['150'] = df.close.rolling(150).mean()
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

    def get_index_price(self, code):
        # newest_data 
        df = ak.stock_zh_index_spot()
        # print(df)       
        newest_data = float(pd.to_numeric(df.loc[df[u'代码']==code, '最新价']).astype('float'))

        # history_data
        history_data = ak.stock_zh_index_daily_em(symbol=code)
        file_name = str(code) + ".csv"
        history_data.to_csv(file_name)
        #print(original_data)
        return (newest_data, history_data.iloc[-20,2])

    def get_index_price_25(self, code):
        # newest_data 
        df = ak.stock_zh_index_spot()
        # print(df)       
        newest_data = float(pd.to_numeric(df.loc[df[u'代码']==code, '最新价']).astype('float'))

        # history_data
        history_data = ak.stock_zh_index_daily_em(symbol=code)
        #print(original_data)
        return (newest_data, history_data.iloc[-25,2])



    def etf_history_data(self, code):
        df = ak.fund_etf_hist_sina(symbol=code)
        print(df)
        file_name = str(code) + ".csv"
        df.to_csv(file_name)
        print("获取ETF数据成功")
        return df

if  __name__ == "__main__":
    #GetData().get_stock_list()
    #GetData().get_data_together()
    #GetData().get_index_price("sz399006")
    #GetData().get_minute_data_from_internet('sz002475', 'lixunjingmi', '60')
    GetData().etf_history_data("sz159949")
    GetData().etf_history_data("sh510300")
