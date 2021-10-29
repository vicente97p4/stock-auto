from flask import Flask, request
from flask_cors import CORS
from flask_restful import reqparse, abort, Api, Resource, fields, marshal_with
import datetime
from stocklab.db_handler.mongodb_handler import MongoDBHandler

app = Flask(__name__)
# Cross Origiin Resource Sharing: 교차 출처 리소스 공유, 브라우저에서 다른 출처의 리소스를 공유하는 방법
CORS(app)
api = Api(app)

code_hname_to_eng = {
    "단축코드": "code",
    "확장코드": "extend_code",
    "종목명": "name",
    "시장구분": "market",
    "ETF구분": "is_etf",
    "주문수량단위": "memedan",
    "기업인수목적회사구분": "is_spac"
}

price_hname_to_eng = {
    "날짜": "date",
    "종가": "close",
    "시가": "open",
    "고가": "high",
    "저가": "low",
    "전일대비": "diff",
    "전일대비구분": "diff_type"
}

code_fields = {
    "code": fields.String,
    "extend_code": fields.String,
    "name": fields.String,
    "memedan": fields.Integer,
    "market": fields.String,
    "is_etf": fields.String,
    "is_spac": fields.String,
    "uri": fields.Url("code")
}
 
code_list_short_fields = {
    "code": fields.String,
    "name": fields.String
} 
code_list_fields = {
    "count": fields.Integer,
    "code_list": fields.List(fields.Nested(code_fields)),
    "uri": fields.Url("codes")
}

price_fields = {
    "date": fields.Integer,
    "start": fields.Integer,
    "close": fields.Integer,
    "open": fields.Integer,
    "high": fields.Integer,
    "low": fields.Integer,
    "diff": fields.Float,
    "diff_type": fields.Integer
}

price_list_fields = {
    "count": fields.Integer,
    "price_list": fields.List(fields.Nested(price_fields)),
 }


mongodb = MongoDBHandler()


# 반환필드: {'count': 반환 개수, 'code_list': [{'code':단축코드, 'name':종목명}]}
# 쿼리는 market으로 받고 market이 없으면 all로 모든 코드정보를 반환한다.
class CodeList(Resource):
    # @marshal_with 데코레이터를 이용해 get 메서드의 데코레이터로 지정하면 정의된 스키마 이외에 다른 데이터는 반환할 수 없다.
    @marshal_with(code_list_fields)
    def get(self):
        # market은 쿼리다. 쿼리는 필요한 조건에 맞는 데이터만 가져오기 위한 방법이다.
        # 쿼리 정보는 request.args.get으로 데이터를 받을 수 있다.
        market = request.args.get('market', default='0', type=str)
        if market == '0':
            results = list(mongodb.find_items({}, 'stocklab', 'code_info'))
        elif market == '1' or market == '2':
            results = list(mongodb.find_items({'시장구분':market}, 'stocklab', 'code_info'))
        result_list = []
        for item in results:
            # MongoDB에는 필드명이 한글로 들어있기 때문에 영문으로 변환하기 위해 code_hname_to_eng 딕셔너리 필요
            code_info = {code_hname_to_eng[field]: item[field] for field in item.keys() if field in code_hname_to_eng}
            result_list.append(code_info)
        return {'code_list': result_list, 'count': len(result_list)}, 200


# 반환필드: {'code': 단축코드, 'extend_code':확장코드, 'name':종목명, 'memdan':주문수량단위, 'market':시장구분, 'is_etf':ETF구분, 'is_spac':기업인수목적회사여부}
class Code(Resource):
    @marshal_with(code_fields)
    def get(self, code):
        result = mongodb.find_item({'단축코드':code}, 'stocklab', 'code_info')
        if result is None:
            return {}, 404

        code_info = {code_hname_to_eng[field]: result[field] for field in result.keys() if field in code_hname_to_eng}
        return code_info


# 반환필드: {'price_list': {'date':날짜, 'start': 시가, 'high': 고가, 'low': 저가, 'end': 종가, 'diff': 전일대비, 'diff_type': 전일대비구분}, 'count': 반환개수}
class Price(Resource):
    @marshal_with(price_list_fields)
    # url에서 정의한 code를 매개변수로 받는다.
    def get(self, code):
        today = datetime.datetime.now().strftime('%Y%m%d')
        default_start_date = datetime.datetime.now() - datetime.timedelta(days=7) # 쿼리가 주어지지 않으면 기본값을 오늘 날짜의 7일 전으로 지정한다.
        start_date = request.args.get('start_date', default=default_start_date.strftime('%Y%m%d'), type=str)
        end_date = request.args.get('end_date', default=today, type=str) # 오늘 날짜를 기본값으로 지정한다.
        results = list(mongodb.find_items({'code':code, '날짜': {"$gte":start_date, "$lte":end_date}}, 'stocklab', 'price_info'))
        result_object = {}
        price_info_list = []

        for item in results:
            price_info = {price_hname_to_eng[field]: item[field] for field in item.keys() if field in price_hname_to_eng}
            price_info_list.append(price_info)

        result_object['price_list'] = price_info_list
        result_object['count'] = len(price_info_list)
        return result_object, 200


# OrderList는 매수, 매도 주문 정보에 대한 필드가 다양한 관계로 marshal_with를 사용하지 않고 데이터를 그대로 반환한다.
# 쿼리는 status 항목 하나를 받고, status가 없으면 all로 모든 주문 정보를 반환한다.
# status가 가질 수 있는 값으로는 buy_ordered, buy_completed, sell_ordered, sell_completed만 허용하며, 그 외의 값은 404 에러를 반환한다.
class OrderList(Resource):
    def get(self):
        status = request.args.get('status', default='all', type=str)
        if status == 'all':
            result_list = list(mongodb.find_items({}, 'stocklab_demo', 'order'))
        elif status in ['buy_ordered', 'buy_completed', 'sell_ordered', 'sell_completed']:
            result_list = list(mongodb.find_items({'status':status}, 'stocklab_demo', 'order'))
        else:
            return {}, 404
        return {'count': len(result_list), 'order_list': result_list}, 200


api.add_resource(CodeList, '/codes', endpoint='codes')
api.add_resource(Code, '/codes/<string:code>', endpoint='code')
api.add_resource(Price, '/codes/<string:code>/price', endpoint='price')
api.add_resource(OrderList, '/orders', endpoint='orders')

if __name__ == '__main__':
    app.run(debug=True)