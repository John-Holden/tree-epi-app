import '../styles/app.css';
import 'katex/dist/katex.min.css';
import React, { useState, useEffect } from 'react';
import { InlineMath } from 'react-katex';
import {Circles} from "react-loader-spinner";
import Plot from 'react-plotly.js';
import SimulationPanel from './SimPanel';

const labelSize = {
  fontSize: 15
}

function InputParameters() {
 // Initialise simulation parameter
 const ApiHostName = process.env.REACT_APP_API_URL;
 const [videoRefData, setVideoRefData] = useState("sim-out")
 const [dispersaType, setDispersal] = useState("gaussian");
 const [dispersalScale, setDispersalScale] = useState(100);
 const [domainX, setDomainX] = useState(500);
 const [domainY, setDomainY] = useState(500);
 const [hostNumber, setHostNumber] = useState(1000);
 const [infectivity, setInfectivity] = useState(25)
 const [density, setDensity] = useState(0.01)
 const [infectivityUpperLim, setinfectivityUpperLim] = useState('25')
 const [infectiousLT, setInfectiousLT] = useState(10);
 const [simulationRT, setSimulationRT] = useState(100);
 const [initiallyInfected, setInitiallyInfected] = useState(20);
 const [initiallyInfectedDist, setInitiallyInfectedDist] = useState("centralised");
 const [secondaryR0, setSecondaryR0] = useState(0);
 const susceptibleHosts = 'S';
 const infectedHosts = 'I';
 const secondaryR0Label = 'R\_{0}';
 const infectivityBeta = '\\beta';
 const densityRho = '\\rho';
 const [spinner, setSpinner] = useState(false);  
 const [S_field, setS_field] = useState([0])
 const [I_field, setI_field] = useState([0])
 const [R_field, setR_field] = useState([0])
 const [t_field, setT_field] = useState([0])
 const [R0_gen, setR0_gen] = useState([0.00])
 const [R0_avg, setR0_avg] = useState([0.00])

  // Update R0 value, conditional on density, infectivity, & infectious lifetime 
 let updateEpiState = async () => {
  try {
    // Get R0 value and denstiy from backend response
    let res = await fetch(`${ApiHostName}/stateupdate`, 
    { 
      method: "POST",
      body: JSON.stringify({"dispersal_type": dispersaType,
                            "dispersal_param": dispersalScale,
                            "domain_size": [domainX, domainY],
                            "host_number": hostNumber,
                            "infectivity": infectivity,
                            "infectious_lifetime": infectiousLT,
                            "simulation_runtime": simulationRT})
    });
    
    // Update values
    function updateR0andDensity(jsonData) {
      setDensity(jsonData['density'])
      setSecondaryR0(jsonData['R0'])
      setinfectivityUpperLim(jsonData['beta_max'])
    }

    res.json().then((data) => {updateR0andDensity(data)})
    if (res.status === 200) {
    } else {
      console.log(`Failed updating R0. Status: ${res.status}`)
    }
  } catch (err) {
    console.log(err);
    alert(`Failed. Error ${err}`)
  }
 }

  // Submit a simulation request to the backend
 let handleSubmitResp = async (e) => {
    
    if (initiallyInfected > hostNumber) {
      alert('The number of infected hosts is larger than the number of susceptibles!')
      return
    }

    setSpinner(true)
    e.preventDefault();
    
    try {
      let res = await fetch(ApiHostName, 
      { 
        method: "POST",
        body: JSON.stringify({"dispersal_type": dispersaType,
                              "dispersal_param": dispersalScale,
                              "domain_size": [domainX, domainY],
                              "host_number": hostNumber,
                              "infectivity": infectivity,
                              "infectious_lifetime": infectiousLT,
                              "simulation_runtime": simulationRT,
                              "initially_infected_hosts": initiallyInfected,
                              "initially_infected_dist": initiallyInfectedDist})
      });

      function updateOutState(jsonData) {
        setVideoRefData(jsonData['video_ref'])
        setS_field(jsonData['S'])
        setI_field(jsonData['I'])
        setR_field(jsonData['R'])
        setT_field(jsonData['t'])
        setR0_gen(jsonData['R0_gen'])
        setR0_avg(jsonData['R0_avg'])
      }

      res.json().then(data => {updateOutState(data)})
      if (res.status === 200) {
      } 
      else {
      console.log(`Simulation failed. Status: ${res.status}`)
      }

    } catch (err) {
      console.log(err);
      alert(`Simulation Failed: ${err}`)
    }
    setSpinner(false)
  };

  useEffect(() => {
    updateEpiState();
  });

  // Render the simulation input parameter panel
  return (
    <div>
      <div className="container">
        <div className='inputParamPanel'>
          <form onSubmit={handleSubmitResp} style={{width: 250}}>
            <label style={labelSize}>  <strong>  Predicted <InlineMath math={secondaryR0Label}/> = {secondaryR0} </strong></label>
            <br></br>
            <label style={labelSize}> <strong> Tree density <InlineMath math={densityRho}/> = {density} </strong></label>
            <p></p>
            <label style={labelSize}>  <InlineMath math={susceptibleHosts}/> Hosts = </label>
            <input className='inputBox' type="number" min="10" max="2000" value={hostNumber} onChange={e => setHostNumber(e.target.value)} required/>   
            <progress value={hostNumber} max="2000"></progress> 
            <p></p>
            <label style={labelSize}> <InlineMath math={infectedHosts}/> Hosts = </label>
            <input className='inputBox' type="number" min="1" max="100" value={initiallyInfected}  onChange={e => setInitiallyInfected(e.target.value)} required/> 
            <progress value={initiallyInfected} max="100"></progress> 
            <p></p>
            <label style={labelSize} > <InlineMath math={infectedHosts}/> Distribution: </label> 
            <select value={initiallyInfectedDist} onChange={e => setInitiallyInfectedDist(e.target.value)}> 
              <option value="centralised"> Centralised</option>
              <option value="random"> Random </option>  
            </select>  
            <p></p>
            <label style={labelSize}> Infectivity <InlineMath math={infectivityBeta}/> = </label>
            <input className='inputBox' type="number" min="0" max={infectivityUpperLim} step="1" value={infectivity}  onChange={e => setInfectivity(e.target.value)} required/>
            <progress value={infectivity} max={infectivityUpperLim}></progress> 
            <p></p>
            <label style={labelSize}> Infection period = </label>
            <input className='inputBox' type="number" min="1" max="500" value={infectiousLT}  onChange={e => setInfectiousLT(e.target.value)} required/>
            <progress value={infectiousLT} max="500"></progress> 
            <br></br>
            <br></br>
            <label style={labelSize} > Dispersal kernel: </label> 
            <select  className='inputBoxBig' value={dispersaType} onChange={e => setDispersal(e.target.value)}> 
              <option value="gaussian">Gaussian</option>  
              <option value="exponential">Exponential</option>
              <option value="power_Law">Power law</option>
            </select>
            <p></p>
            <label style={labelSize}> Dispersal length (m) = </label>
            <input className='inputBox' type="number" min="1" max="2000" value={dispersalScale}  onChange={e => setDispersalScale(e.target.value)} required/>
            <progress value={dispersalScale} max="2000"></progress> 
            <p></p>
            <label style={labelSize}> Domain width (m) = </label>
            <input className='inputBox' type="number" min="10" max="5000" value={domainX}  onChange={e => setDomainX(e.target.value)} required/>
            <progress value={domainX} max="5000"></progress> 
            <p></p>
            <label style={labelSize}> Domain height (m) = </label>
            <input className='inputBox' type="number" min="10" max="5000" value={domainY}  onChange={e => setDomainY(e.target.value)} required/>   
            <progress value={domainY} max="5000"></progress> 
            <p></p>
            <label style={labelSize}> Time Steps (days) = </label>
            <input className='inputBox' type="number" min="1" max="1500" value={simulationRT}  onChange={e => setSimulationRT(e.target.value)} required/>
            <progress value={simulationRT} max="1000"></progress> 
            <p></p>
            <input className='inputBoxBig' type="submit" value="Simulate"/>
          </form>
          {spinner &&  <Circles width="80" height="80" className='spinner'/>}
        </div>
        <div className='simulationPanel'>
          <SimulationPanel className='simulationPanel' videoRefData={videoRefData}/>
        </div>
        <div className='plot1'>
        <Plot
            data={[
              {
                x: t_field,
                y: S_field,
                type: 'scatter',
                mode: 'lines+markers',
                marker: {color: 'green'},
                name: 'S',
                automargin: true,
              },
              {
                x: t_field,
                y: I_field,
                type: 'scatter',
                mode: 'lines+markers',
                marker: {color: 'red'},
                name: 'I',
                automargin: true,
              },
              {
                x: t_field,
                y: R_field,
                type: 'scatter',
                mode: 'lines+markers',
                marker: {color: 'black'},
                name: 'R',
                automargin: true,
              },
            ]}
            layout={ {width: 600, height: 400, title: 'SIR fields', xaxis:{title:"time"}, yaxis:{title:"host number"} } }
          />
          <Plot
            data={[
              {
                x: R0_gen,
                y: R0_avg,
                type: 'scatter',
                mode: 'lines+markers',
                marker: {color: 'green'},
                name: 'avg R0',
                automargin: true,
              },
            ]}
            layout={ {width: 600, height: 400, title: "Average Secondary Infections", xaxis:{title:"generation"}, yaxis:{title:"Avg R0"}} }
          />
        </div>
      </div>
    </div>
  );
}


export default InputParameters;
