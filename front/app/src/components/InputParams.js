import '../styles/app.css';
import 'katex/dist/katex.min.css';
import React, { useState } from 'react';
import { InlineMath } from 'react-katex';
// import module_exports from '../environments';

const labelSize = {
  fontSize: 15
}

function InputParameters() {
  const ApiHostName = process.env.REACT_APP_API_URL;
  const [message, setMessage] = useState("");
  const [dispersaType, setDispersal] = useState("gaussian");
  const [dispersalScale, setDispersalScale] = useState(100);
  const [domainX, setDomainX] = useState(500);
  const [domainY, setDomainY] = useState(500);
  const [hostNumber, setHostNumber] = useState(1000);
  const [secondaryR0, setSecondaryR0] = useState(2.0);
  const [infectiousLT, setInfectiousLT] = useState(100);
  const [simulationRT, setSimulationRT] = useState(1000);
  const [initiallyInfected, setInitiallyInfected] = useState(20);
  const [initiallyInfectedDist, setInitiallyInfectedDist] = useState("centralised");
  const susceptibleHosts = 'S';
  const infectedHosts = 'I';
  const secondaryR0Label = 'R\_{0}';
 let handleSubmitResp = async (e) => {
    e.preventDefault();
    try {
      let res = await fetch(ApiHostName, 
      { 
        method: "POST",
        body: JSON.stringify({"dispersal_type": dispersaType,
                              "dispersal_param": dispersalScale,
                              "domain_size": [domainX, domainY],
                              "host_number": hostNumber,
                              "secondary_R0": secondaryR0,
                              "infectious_lifetime": infectiousLT,
                              "simulation_runtime": simulationRT,
                              "initially_infected_hosts": initiallyInfected,
                              "initially_infected_dist": initiallyInfectedDist})
      });
      res.json().then((data) => {console.log("back end resp: ", data['message'])})
      if (res.status === 200) {
        console.log('api url :: ', process.env.REACT_APP_API_URL)
        setMessage("successfull");
        console.log('successfull post')
        setMessage("error");
      } else {
        console.log('failed failed')
      }
    } catch (err) {
      console.log(err);
      alert(`${message}, dispersal type is ${dispersaType}`)
    }
  };


  return (
      <div className='inputParamPanel'>
        <form onSubmit={handleSubmitResp} style={{width: 185}}>
          <label style={labelSize}>  <InlineMath math={susceptibleHosts}/> Hosts: {hostNumber} </label>
          <input type="range" min="1" max="2000" value={hostNumber}  onChange={e => setHostNumber(e.target.value)}/>   
          <br></br>
          <label style={labelSize}> <InlineMath math={infectedHosts}/> Hosts: {initiallyInfected} </label>
          <input type="range" min="1" max="100" value={initiallyInfected}  onChange={e => setInitiallyInfected(e.target.value)}/> 
          <br></br>
          <label style={labelSize} > <InlineMath math={infectedHosts}/> Distribution </label> 
          <select value={initiallyInfectedDist} onChange={e => setInitiallyInfectedDist(e.target.value)}> 
            <option value="centralised"> Centralised</option>
            <option value="random"> Random </option>  
          </select>  
          <br></br>
          <label style={labelSize}> Secondary <InlineMath math={secondaryR0Label}/>: {secondaryR0} </label>
          <input type="range" min="0" max="10" step="0.1" value={secondaryR0}  onChange={e => setSecondaryR0(e.target.value)}/> 
          <br></br>
          <label style={labelSize}> Infectious period: {infectiousLT} </label>
          <input type="range" min="1" max="500" value={infectiousLT}  onChange={e => setInfectiousLT(e.target.value)}/>  
          <br></br>
          <label style={labelSize} > Dispersal Kernel: </label> 
          <select value={dispersaType} onChange={e => setDispersal(e.target.value)}> 
            <option value="gaussian">Gaussian</option>  
            <option value="exponential">Exponential</option>
            <option value="inverse_power_Law">Inverse power law</option>
          </select>
          <br></br>
          <label style={labelSize}> Dispersal length: {dispersalScale}(m) </label>
          <input type="range" min="1" max="2000" value={dispersalScale}  onChange={e => setDispersalScale(e.target.value)}/>   
          <br></br>
          <label style={labelSize}> Domain width: {domainX}(m) : </label>
          <input type="range" min="1" max="2000" value={domainX}  onChange={e => setDomainX(e.target.value)}/>   
          <label style={labelSize}> Domain height: {domainY}(m) : </label>
          <input type="range" min="1" max="2000" value={domainY}  onChange={e => setDomainY(e.target.value)}/>   
          <br></br>
          <label style={labelSize}> Time Steps (days): {simulationRT} </label>
          <input type="range" min="1" max="2000" value={simulationRT}  onChange={e => setSimulationRT(e.target.value)}/>
          <p></p>
          <input type="submit" value="Simulate" />
        </form>
      </div>
  );
}

export default InputParameters;
