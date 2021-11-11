import React, { Component } from 'react';

class OrderList extends Component{
    constructor(props){
        super(props);
        this.state = { 
            orderList : [],
            flag:0
        };
    }
    componentDidMount(){
        console.log("OrderList componentDidMount");
        let api_url = "http://127.0.0.1:5000/orders";
        let options = [];
        fetch(api_url)
            .then(res => res.json())
            .then(data =>{
                console.log("didmount fetch", data);
                this.state.orderList = data['order_list']
                this.setState({flag:1});
                console.log('operated', this.state.orderList)
            });
        
    }
    render(){
        let num=1
        return  (
            <table border="1">
                <th>번호</th>
                <th>코드</th>
                <th>종목명</th>
                <th>단축종목번호</th>
                <th>실물주문수량</th>
                <th>주문금액</th>
                <th>주문번호</th>
                {
                    this.state.orderList.map(it => {
                        return (<tr><td>{num++}</td><td>{it['code']}</td> <td>{it['매수주문']['종목명']}</td> <td>{it['매수주문']['단축종목번호']}</td> <td>{it['매수주문']['실물주문수량']}</td> <td>{it['매수주문']['주문금액']}</td> <td>{it['매수주문']['주문번호']}</td></tr>)
                    })
                }
            </table>
         );
    }
}

export default OrderList;