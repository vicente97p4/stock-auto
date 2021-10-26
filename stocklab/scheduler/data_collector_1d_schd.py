# 윈도우 작업 스케줄러는 다양한 조건으로 유연성 있게 여러 작업을 수행하기에는 한계가 있다.
# 그래서 파이썬으로 스케줄러를 구현해보았다.
import time
import inspect
from multiprocessing import Process
from datetime import datetime

from apscheduler.schedulers.background import BackgroundScheduler

from stocklab.agent.ebest import EBest
from stocklab.agent.data import Data
from stocklab.db_handler.mongodb_handler import MongoDBHandler

def run_process_collect_code_list():
    print(inspect.stack()[0][3])
    p = Process(target=collect_code_list) # collect_code_list를 호출하는 프로세스 생성
    p.start() # 이 시점부터 부모 프로세스와 자식 프로세스는 개별적으로 동작한다.
    p.join() # 부모 프로세스는 자식 프로세스가 종료될 때까지 기다린다.

def run_process_collect_stock_info():
    print(inspect.stack()[0][3])
    p = Process(target=collect_stock_info) # collect_stock_info를 호출하는 프로세스 생성
    p.start() # 이 시점부터 부모 프로세스와 자식 프로세스는 개별적으로 동작한다.
    p.join() # 부모 프로세스는 자식 프로세스가 종료될 때까지 기다린다.

def collect_code_list():
    ebest=EBest('DEMO')
    mongodb = MongoDBHandler()
    ebest.login()
    result = ebest.get_code_list('ALL')
    mongodb.delete_items({}, 'stocklab', 'code_info')
    mongodb.insert_items(result, 'stocklab', 'code_info')

def collect_stock_info():
    ebest = EBest('DEMO')
    mongodb = MongoDBHandler()
    ebest.login()
    code_list = mongodb.find_items({}, 'stocklab', 'code_info')
    target_code = set([item['단축코드'] for item in code_list])
    today = datetime.today().strftime('%Y%m%d')
    print(today)
    collect_list = mongodb.find_items({'날짜':today}, 'stocklab', 'price_info').distinct('code')

    for col in collect_list:
        target_code.remove(col)
    for code in target_code:
        time.sleep(1)
        print('code:',code)
        result_price = ebest.get_stock_price_by_code(code, '1')
        if len(result_price) > 0:
            print(result_price)
            mongodb.insert_items(result_price, 'stocklab', 'price_info')

        result_credit = ebest.get_credit_trend_by_code(code, today)
        if len(result_credit) > 0:
            mongodb.insert_items(result_credit, 'stocklab', 'credit_info')

        result_short = ebest.get_short_trend_by_code(code, sdate=today, edate=today)
        if len(result_short) > 0:
            mongodb.insert_items(result_short, 'stocklab', 'short_info')

        result_agent = ebest.get_agent_trend_by_code(code, fromdt=today, todt=today)
        if len(result_agent) > 0:
            mongodb.insert_items(result_agent, 'stocklab', 'agent_info')

if __name__ == '__main__':
    scheduler = BackgroundScheduler()
    # 실행할 함수 지정
    # 인자에 특별히 값을 지정하지 않으면 *로 동작하여 매년, 매월, 매일, 매시, 매분, 매초에 동작한다.
    scheduler.add_job(func=run_process_collect_code_list, trigger='cron', day_of_week='mon-fri', hour='22', minute='36', id='1')
    scheduler.add_job(func=run_process_collect_stock_info, trigger='cron', day_of_week='mon-fri', hour='19', minute='00', id='2')
    scheduler.start()

    while True:
        print('running', datetime.now())
        time.sleep(1)