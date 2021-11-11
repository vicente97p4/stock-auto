import React, { Component } from 'react';
import Select from 'react-select';
import makeAnimated from 'react-select/lib/animated';
import RadioGroup from '@material-ui/core/RadioGroup';
import Radio from '@material-ui/core/Radio';
import FormControlLabel from '@material-ui/core/FormControlLabel';
import FormControl from '@material-ui/core/FormControl';
import './CodeSearch.css'

class CodeSearch extends Component{
    constructor(props){
        super(props);
        console.log("CodeSearch constructor");
        this.state = { 
            selectedOption:'',
            options : [],
            filteredOptions : [],
            flag: 0,
            etf0: [],
            etf1: [],
            etf2: []
        };
    }
    handleSelectChange = (selectedOption)=>{
        console.log("CodeSearch handleSelectedChange", selectedOption);
        this.props.handleSelectedCode(selectedOption.code);
    }

    handleRadioChange = (event) =>{
        if(event.target.value==="etf0"){
            if(this.state.etf0.length === 0){
                this.state.etf0 = this.state.options.filter(item=>item.is_etf==='0')
            } 
            this.state.filteredOptions = this.state.etf0
        }else if(event.target.value==="etf1"){
            if(this.state.etf1.length === 0){
                this.state.etf1 = this.state.options.filter(item=>item.is_etf==='1')
            } 
            this.state.filteredOptions = this.state.etf1
        }else if(event.target.value==="etf2"){
            
            if(this.state.etf2.length === 0){
                this.state.etf2 = this.state.options.filter(item=>item.is_etf==='2')
            } 
            this.state.filteredOptions = this.state.etf2
        }else if(event.target.value==="all"){
            this.state.filteredOptions = []
        }
        this.setState({flag:0})
    }
    componentDidMount(){
        console.log("CodeSearch componentDidMount");
        let api_url = "http://127.0.0.1:5000/codes";
        fetch(api_url)
            .then(res => res.json())
            .then(data =>{
                console.log("didmount fetch", data);
                data["code_list"].map(function(item){
                    item["value"] = item["code"]
                    item["label"] = item["name"] + "(" + item["code"] +")"
                    item["market"] = item["market"] 
                    item["is_etf"] = item["is_etf"]
                    item["is_spac"] = item["is_spac"]
                });
                this.setState({options:data["code_list"]})
            });
    }
    render(){
        const { selectedOption, options, filteredOptions } = this.state;
        console.log("CodeSearch render", options);
        return  (
            <div>
            {
                <Select
                    onChange={this.handleSelectChange}
                    options={filteredOptions.length > 0?
                                filteredOptions:options}
                    maxMenuHeight={500}
                />
            }
            {
                <RadioGroup
                    onChange={this.handleRadioChange}
                    row
                >
                <FormControlLabel
                    value="all"
                    control={<Radio color="primary" />}
                    label="ALL"
                    labelPlacement="end"
                />
                <FormControlLabel
                    value="etf0"
                    control={<Radio color="primary" />}
                    label="ETF0"
                    labelPlacement="end"
                />
                <FormControlLabel
                    value="etf1"
                    control={<Radio color="primary" />}
                    label="ETF1"
                    labelPlacement="end"
                />
                <FormControlLabel
                    value="etf2"
                    control={<Radio color="primary" />}
                    label="ETF2"
                    labelPlacement="end"
                />
                </RadioGroup>
            }
            </div>
         );
    }
}

export default CodeSearch;