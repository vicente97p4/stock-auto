from multiprocessing import Process
import time
from datetime import datetime, timedelta
import inspect

from apscheduler.jobstores.base import JobLookupError
from apscheduler.schedulers.background import BlockingScheduler, BackgroundScheduler

from stocklab.agent.ebest import EBest
from stocklab.agent.data import Data
from stocklab.db_handler.mongodb_handler import MongoDBHandler

ebest_ace = EBest('ACE')
ebest_ace.login()
mongo = MongoDBHandler()

def run_process_trading_scenario(code_list, date):
    p = Process(target=run_trading_scenario, args=(code_list, date))
    p.start()
    p.join()
    print('run process join')

def run_trading_scenario(code_list, date):
    tick=0 # tick은 9:00을 0으로 설정했다. 과거 데이터를 조회하는 시간 단위로 사용한다.
    print(code_list, date, tick)

    # 9:00 ~ 9:20까지만 테스트한다.
    while tick < 20:
        print('tick:', tick)
        for code in code_list:
            current_price = ebest_ace.get_price_n_min_by_code(date, code, tick) # 각 tick마다 각 코드에 대한 과거 가격 정보 조회
            print('current price', current_price)
            time.sleep(1)

            # 시가로 주문하고 주문 정보를 mongoDB에 저장
            buy_order_list = ebest_ace.order_stock(code, '2', current_price,['시가'], '2', '00') 
            buy_order = buy_order_list[0]
            buy_order['amount'] = 2 # 주문 수량 정보를 남기기 위해 amount를 추가한다.
            mongo.insert_item(buy_order, 'stocklab_test', 'order')

            # sell 역시 동일하게 진행한다.
            sell_order_list = ebest_ace.order_stock(code, '1', current_price['종가'], '1', '00')
            sell_order = sell_order_list[0]
            sell_order['amount'] = 1
            mongo.insert_item(sell_order, 'stocklab_test', 'order')
        tick += 1

if __name__ == '__main__':
    scheduler = BackgroundScheduler()
    codes = ['180640', '005930']
    day = datetime.now() - timedelta(days=4)
    day = day.strftime('%Y%m%d')
    print(day)
    # trigger를 date로 하여 한 번 만 실행할 수 있게 하였다.
    # 실행 즉시 스케줄이 실행될 수 있게 run_date=datetime.now()를 줬다.
    scheduler.add_job(func=run_process_trading_scenario, trigger='date', run_date=datetime.now(), id='test', kwargs={'code_list':codes, 'date':day})
    scheduler.start()