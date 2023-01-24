from django.shortcuts import render
from configparser import ConfigParser
from .my_lib._mt5_webapi_lib_2023_01_23 import *

# Загрузка конфигурации
config = ConfigParser()
config.read('mt5_reports/config.ini')
DB_HOST = config.get('DATABASE', 'DB_HOST')
DB_PORT = config.get('DATABASE', 'DB_PORT')
DB_USER = config.get('DATABASE', 'DB_USER')
DB_PASSWORD = config.get('DATABASE', 'DB_PASSWORD')
DB_NAME = config.get('DATABASE', 'DB_NAME')
MT5_HOST = config.get('MT5', 'MT5_HOST')
MT5_USER = config.get('MT5', 'MT5_USER')
MT5_PASSWORD = config.get('MT5', 'MT5_PASSWORD')
ON_ITERATION = int(config.get('SLEEP', 'ON_ITERATION'))
ON_ERROR = int(config.get('SLEEP', 'ON_ERROR'))


def index(request):
    # DB_HOST = '127.0.0.1'
    # DB_PORT = '4406'
    # DB_USER = 'MT5_DB'
    # DB_PASSWORD = 'oguhwej743_209()'
    # DB_NAME = 'mt5_real'

    mt5_session = MT5Session(MT5_HOST, MT5_USER, MT5_PASSWORD)
    server_status = 'No WebAPI Connection!'
    if mt5_session.connection:
        server_status = mt5_session.server

    sql_request = """ SELECT ROUND(SUM(Profit + Storage + Commission), 2) as TotalProfit 
                      FROM mt5_deals d, mt5_users u WHERE Action in ('0', '1') and 
                      Profit + Storage + Commission > 0 and d.Login = u.Login and LOCATE('real', u.Group) """
    sql_total_profit = MT5Mysql(DB_HOST, DB_PORT, DB_USER, DB_PASSWORD, DB_NAME, sql_request)
    sql_total_profit = round(sql_total_profit.result[0]['TotalProfit'])

    sql_request = """ SELECT ROUND(SUM(Profit + Storage + Commission), 2) as TotalLoss
                          FROM mt5_deals d, mt5_users u WHERE Action in ('0', '1') and 
                          Profit + Storage + Commission < 0 and d.Login = u.Login and LOCATE('real', u.Group) """
    sql_total_loss = MT5Mysql(DB_HOST, DB_PORT, DB_USER, DB_PASSWORD, DB_NAME, sql_request)
    sql_total_loss = round(sql_total_loss.result[0]['TotalLoss'])

    total_result = round(sql_total_loss + sql_total_profit, 2)

    context = {'title': 'MT5 Reports | Home',
               'mt5_session': str(server_status),
               'common': mt5_session.common,
               'servertime': mt5_session.servertime,
               'total_profit': sql_total_profit,
               'total_loss': sql_total_loss,
               'total_result': total_result}
    return render(request, 'mt5_reports/index.html', context)
