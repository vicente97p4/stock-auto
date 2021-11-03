import React, {Component} from 'react';
import Grid from '@material-ui/core/Grid'
import {withStyles} from '@material-ui/core/styles'
import Paper from '@material-ui/core/Paper'
import CodeSearch from '../components/CodeSearch'
import CodePrice from '../components/CodePrice'
import CodeChart from '../components/CodeChart'
import { mergeClasses } from '@material-ui/styles';

// Material UI는 css를 const styles에 정의한다.
const styles = {
    root: {
        flexGrow: 1,
    },
    paper: {
        height:140,
        width:100,
    },
    control:{
        padding:2,
    },
};

class CodeInfo extends Component{
    constructor(props){
        super(props);
        this.state = {
            selectedCode: ''
        };
    }
    componentDidMount(){

    }
    componentDidUpdate(prevProps, prevState, snapshot){

    }
    handleSelectedCode = (selectedCode) => {
        console.log('CodeInfo handleSelectedCode', selectedCode);
        this.setState({selectedCode}); // 업데이트한 selectedCode의 값을 CodePrice의 code로 다시 넘겨줘야 한다.
    }
    render() {
        return(
            <div>
                <div>
                    <CodeSearch code={this.state.selectedCode} handleSelectedCode={this.handleSelectedCode}/>
                </div>
                <div>
                    <Grid>
                        <Grid container justify="left">
                            
                            <Grid key={"codePrice"} item>
                                <CodePrice code={this.state.selectedCode}/>
                            </Grid>

                            <Grid key={"codeChart"} item>
                                <Paper className={classes.paper}/>
                            </Grid>

                        </Grid>
                    </Grid>
                </div>
            </div>
        );
    }
}

// 위에서 정의한 const styles를 withStyles 메서드를 이용해 CodeInfo의 속성으로 전달할 수 있다.
// withStyles는 CodeInfo 컴포넌트에서 classes라는 속성으로 styles를 전달하는 함축적인 기능이 있다.
// 속성으로 전달한 styles는 this.props를 이용해 render에서 가져올 수 있다.
// 이러한 방식 말고도 render에서 const styles를 바로 선언한 후 사용할 수도 있다.
// 하지만 이 경우 스타일을 정의하는 코드가 컴포넌트를 렌더링하는 코드에 밀접하게 연관되므로
// 코드를 유지보수하는 관점에서 좋지 않은 구현 방법이다.
export default withStyles(styles)(CodeInfo);
