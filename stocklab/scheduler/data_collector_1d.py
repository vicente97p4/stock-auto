# 종목 코드 번호와 주식 가격 정보를 수집하는 모듈
from datetime import datetime
from stocklab.agent.ebest import EBest
from stocklab.db_handler.mongodb_handler import MongoDBHandler

ebest = EBest('DEMO') # 이베스트 커넥션 생성
ebest.login() # 로그인

mongodb = MongoDBHandler() # MongoDB 커넥션 생성

# 종목 코드를 수집하는 메서드
# MongoDB에 code_info 컬렉션을 모두 삭제하고 받아온 결과 삽입
# 만일 종목코드를 모두 보관하고 싶다면 삭제하지 않고 update 메서드의 upsert 옵션을 이용해도 됨
# 하지만 여기서는 사라진 회사의 종목코드를 보관하는 것은 의미 없다고 판단하여 삭제함
def collect_code_list():
    result = ebest.get_code_list('ALL')
    mongodb.delete_items({}, 'stocklab', 'code_info')
    mongodb.insert_items(result, 'stocklab', 'code_info')

# 주식 가격을 수집하는 코드
# 앞서 갱신한 code_info에서 수집할 종목 코드를 target_code에 저장한다.
def collect_stock_info():
    code_list = mongodb.find_items({}, 'stocklab', 'code_info') 
    target_code = set([item['단축코드'] for item in code_list]) # 수집할 종목 코드를 target_code에 저장
    
    # 오늘 날짜로 수집된 데이터가 있다면 target_code에서 제외
    # 재실행하면 데이터가 중복으로 수집되는데, 중복이 발생하면 데이터를 추가로 가공해야 하기 때문에 애초에 수집 단계에서 중복이 발생하지 않도록 하기 위함
    today = datetime.today().strftime('%Y%m%d')
    collect_list = mongodb.find_items({'날짜':today}, 'stocklab', 'price_info').distinct('code') 
    for col in collect_list:
        target_code.remove(col)
    
    # 최종적으로 수집해야 하는 종목 코드는 target_code에 저장되며, get_stock_price_by_code를 이용해 1일 치 데이터를 가져온다.
    # 수집한 데이터는 price_info에 넣는다.
    for code in target_code:
        result_price = ebest.get_stock_price_by_code(code, '1')
        if len(result_price) > 0:
            mongodb.insert_items(result_price, 'stocklab', 'price_info')

if __name__ == '__main__':
    collect_code_list()
    collect_stock_info()