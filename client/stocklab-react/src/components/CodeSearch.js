// 자동완성(AutoComplete)을 지원하는 드롭다운(Dropdown) 형태의 컴포넌트로 종목 검색을 지원한다.
//Material UI에서는 자동 완성 기능이 있는 컴포넌트는 제공하지 않는다.
// react-select 컴포넌트를 이용해봤다.
import React, {Component} from "react";
import Select from 'react-select';
import makeAnimated from 'react-select/animated';
import RadioGroup from '@material-ui/core/RadioGroup';
import Radio from '@material-ui/core/Radio';
import FormControlLabel from "@material-ui/core/FormControlLabel";
import FormControl from "@material-ui/core/FormControl";

class CodeSearch extends Component{
    constructor(props){
        super(props);
        console.log('CodeSearch constructor')
        this.state = {
            selectedOption: '', // Dropdown 항목에서 최종적으로 선택한 종목의 코드 번호가 저장된다.
            options: [], // 모든 종목 정보 저장
            filteredOptions: [] // SPAC이나 ETF 종목만 조회할 때 사용할 변수
        };
    }
    handleSelectChange = (selectedOption) => {
        this.props.handleSelectedCode(selectedOption.code)
    }
    handleRadioChange = (event) => { // 이벤트 오브젝트 값이 전달된다.
        if(event.target.value === 'spac'){ // 라디오 버튼의 value에 값을 할당받을 수 있다.
            this.setState({ // 조건에 맞는 값만 필터링 해서 filtered Options를 반영한다.
                filteredOptions:this.state.options.filter(item=>item.is_spac === 'Y')
            })
        }else if(event.target.value === 'etf'){
            this.setState({
                filteredOptions:this.state.options.filter(item=>item.is_etf === '1')
            })
        }else if(event.target.value === 'all'){
            this.setState({
                filteredOptions:[]
            })
        }
    }
    // 컴포넌트의 라이프 사이클에 해당하는 메서드
    // 컴포넌트가 생성되고 render 메서드가 호출된 다음 브라우저에 컴포넌트가 mount되면 호출되는 메서드이다.
    // 일반적으로 네트워크를 이용해 초기 데이터를 적재(Load)할 때 이 메서드를 이용한다.
    // 그리고 componentDidMount에서 setState를 호출하면 다시 render 메서드가 호출된다.
    // 호출 순서: constructor -> render -> componentDidMount -> render
    // 단, 데이터를 적재할 때 시간이 오래 걸리면 사용자에게 혼선을 줄 수 있다.
    // 사용자는 첫 번째 render 시점에 화면을 보게 되지만, 두 번째 render 시점까지 아무런 데이터도 보이지 않는다.
    // 따라서 시간이 오래 걸리는 작업이라면 constructor 부분에서 데이터를 적재하는 것도 하나의 방법이 될 수 있다.
    // 하지만 이 프로젝트에서는 시간이 오래 걸리지 않기 때문에 componentDidMount에서
    // 개발한 API 서버로 데이터를 요청한 다음 적제한다.
    componentDidMount(){
        console.log('CodeSearch did mount');
        let api_url = 'http://127.0.0.1:5000/codes'
        let options = [];
        fetch(api_url).then(res=>res.json()) // API서버로 데이터를 요청할 때 fetch 함수 사용, 받은 데이터를 json으로 변환한다.
        .then(data => { // json으로 변환된 data에서 result 필드의 각 항목을 알맞은 데이터 폼으로 변환
            data['result'].map(function(item){
                item['value'] = item['code']
                item['label'] = item['name'] + '(' + item['code'] + ')'
                item['market'] = item['market']
                item['is_etf'] = item['is_etf']
                item['is_spac'] = item['is_spac']
            });
            this.setState({options:data['result']}) // 변환 후 options 리스트에 저장한 다음 업데이트
        });
    }
    render(){
        const {selectedOption, options, filteredOptions} = this.state;
        console.log('CodeSearch render', options);
        return (
            <div>
                {
                    <Select
                        onChange={this.handleSelectChange}
                        options={filteredOptions.length > 0 ? filteredOptions : options}
                    />
                }
                {
                    <FormControl component='fieldset'>
                        <RadioGroup
                            onChange={this.handleRadioChange}
                            row
                        >
                        <FormControlLabel
                            value='all'
                            control={<Radio color='primary'/>}
                            label = 'ALL'
                            labelPlacement='end'
                        />
                        <FormControlLabel
                            value='etf'
                            control={<Radio color='primary'/>}
                            label = 'ETF'
                            labelPlacement='end'
                        />
                        <FormControlLabel
                            value='spac'
                            control={<Radio color='primary'/>}
                            label = 'SPAC'
                            labelPlacement='end'
                        />
                        </RadioGroup>
                    </FormControl>
                }
            </div>
        );
    }
}
export default CodeSearch;
