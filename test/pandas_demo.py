import pandas as pd
import akshare as ak

dir_path = r"D:\\01 个人\\I\\demo\\spider_data\\"

def sort_data(file_name):
    file_path = dir_path + file_name
    df = pd.read_csv(file_path, encoding='gbk')
    df = df.sort_values(df.columns[5], ascending=False)
    print(df[:5])

def get_data(file_name, day):
    file_path = dir_path + file_name
    if day == 1:
        indic = "今日"
    elif day == 5:
        indic = "5日"
    else:
        indic = "10日"
    stock_sector_fund_flow_rank_df = ak.stock_sector_fund_flow_rank(indicator=indic, sector_type="行业资金流")
    print(stock_sector_fund_flow_rank_df)
    stock_sector_fund_flow_rank_df.to_csv(file_path, index=0, encoding='gbk')

if __name__ == "__main__":
    #sort_data("20210121_hy.csv")
    get_data("20210121_1d.csv", 1)
    get_data("20210121_5d.csv", 5)
    get_data("20210121_10d.csv", 10)
