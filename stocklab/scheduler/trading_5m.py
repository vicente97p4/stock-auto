import time
from datetime import datetime, timedelta
from apscheduler.schedulers.background import BackgroundScheduler
from stocklab.agent.ebest import EBest
from stocklab.db_handler.mongodb_handler import MongoDBHandler
from multiprocessing import Process

ebest_demo = EBest('DEMO')
ebest_demo.login()
mongo = MongoDBHandler()

# code_list를 매개변수로 받고 별도의 프로세스를 생성하는 역할을 하며, trading_scenario를 수행한다.
def run_process_trading_scenario(code_list):
    p = Process(target=trading_scenario, args=(code_list,))
    p.start() # process 수행
    p.join() # 해당 process가 끝날 때까지 기다린다.
    print('run process join')

def check_buy_completed_order(code):
    '''
    매수완료된 주문은 매도 주문
    '''
    # 매수완료(buy_completed) 데이터를 가져온다.
    buy_completed_order_list = list(mongo.find_items({"$and":[
        {"code":code}, {"status":"buy_completed"}
    ]}, 'stocklab_demo', 'order'))

    '''
    매도 주문
    '''
    # 가져온 항목에 대해서 수량만큼 +10호가로 매도주문
    for buy_completed_order in buy_completed_order_list:
        buy_price = buy_completed_order['매수완료']['주문가격']
        buy_order_no = buy_completed_order['매수완료']['주문번호']
        tick_size = ebest_demo.get_tick_size(int(buy_price))
        print('tick_size', tick_size)
        sell_price = int(buy_price) + tick_size*10
        sell_order = ebest_demo.order_stock(code, '2', str(sell_price), '1', '00')
        print('order_stock', sell_order)
        mongo.update_item({'매수완료.주문번호':buy_order_no}, {"$set":{'매도주문':sell_order[0], 'status':'sell_ordered'}}, 'stocklab_demo', 'order')

def check_buy_order(code):
    '''
    매수주문 완료 체크
    '''
    # MongoDB에서 code에 대한 매수주문 데이터를 가져온다.
    order_list = list(mongo.find_items({"$and":[
        {'code':code}, {'status':'buy_ordered'}
    ]}, 'stocklab_demo', 'order'))

    # 매수 결과에 대해 체결 수량이 주문 수량과 동일한지 확인한다.
    for order in order_list:
        time.sleep(1)
        code = order['code']
        order_no = order['매수주문']['주문번호']
        order_cnt = order['매수주문']['실물주문수량']
        check_result = ebest_demo.order_check(order_no)
        print('check buy order result', check_result)
        result_cnt = check_result['체결수량']

        # 체결 수량이 주문 수량과 동일하면 매수 완료로 MongoDB에 해당 주문에 대한 정보를 업데이트한다.
        if order_cnt == result_cnt:
            mongo.update_item({'매수주문.주문번호': order_no}, {"$set": {'매수완료':check_result, 'status':'buy_completed'}}, 'stocklab_demo', 'order')
            print('매수완료', check_result)
    return len(order_list)

def check_sell_order(code):
    '''
    매도주문 완료 체크
    '''
    # 매도주문을 가져온다.
    sell_order_list = list(mongo.find_items({"$and": [
        {'code': code}, {'status': 'sell_ordered'}
    ]}, 'stocklab_demo', 'order'))

    # order_check로 체결 수량을 확인한다.
    for order in sell_order_list:
        time.sleep(1)
        code = order['code']
        order_no = order['매도주문']['주문번호']
        order_cnt = order['매도주문']['실물주문수량']
        check_result = ebest_demo.order_check(order_no)
        print('check sell order result', check_result)
        result_cnt = check_result['체결수량']

        # 체결됐다면 sell_completed로 update한다.
        if order_cnt == result_cnt:
            mongo.update_item({'매도주문.주문번호':order_no}, {"$set":{'매도완료':check_result, 'status':'sell_completed'}}, 'stocklab_demo', 'order')
            print('매도완료',check_result)
    return len(sell_order_list)

def trading_scenario(code_list):
    for code in code_list:
        time.sleep(1)
        print(code)
        result = ebest_demo.get_current_call_price_by_code(code) # code 별로 현재 호가를 확인하기 위함
        print('result:',result)
        current_price = result[0]['현재가']
        print('current_price', current_price)

        '''
        매수주문 체결확인
        '''
        buy_order_cnt = check_buy_order(code) # 현재 매수 주문의 상태를 체크, 매수 주문의 수량을 return
        check_buy_completed_order(code) # 매수 완료된 주문에 대해서 +10호가로 매도 주문
        if buy_order_cnt == 0: # 만일 매수 주문 수량이 0일 경우
            '''
            종목을 보유하고 있지 않는 경우 매수
            '''
            order = ebest_demo.order_stock(code, '2', current_price, '2', '00') # 현재가에 매수 주문
            print('order_stock', order)
            order_doc = order[0]
            mongo.insert_item({'매수주문':order_doc, 'code':code, 'status':'buy_ordered'}, 'stocklab_demo', 'order') # 매수 주문 정보 저장

        check_sell_order(code)

if __name__ == '__main__':
    scheduler = BackgroundScheduler()
    day = datetime.now() - timedelta(days=0)
    today = day.strftime('%Y%m%d')
    # 트레이딩은 180640, 005930, 091990 세 종목에 대해 실행했다.
    code_list = ['180640', '005930', '091990']
    print('today:', today)
    # interval 5분 주기는 크론으로 매분 수행한다는 의미와 동일하지만 크론은 매 0분에 시작되는 반면 interval은 프로그램이 시작된 후 5분 뒤 실행된다.
    scheduler.add_job(func=run_process_trading_scenario, trigger='interval', minutes=0, id='demo', kwargs={'code_list':code_list})
    scheduler.start()
    while True:
        print('waiting...', datetime.now())
        time.sleep(1)

# 이 시나리오에는 미체결 주문에 대한 관리를 별도로 하고 있지 않기 때문에 보완이 필요할 수 있다.