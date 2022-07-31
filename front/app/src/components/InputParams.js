import '../styles/app.css';
import 'katex/dist/katex.min.css';
import React, { useState, useEffect, useRef } from 'react';
import { InlineMath } from 'react-katex';
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
      res.json().then((data) => {setVideoRefData(data['video_ref'])})
      if (res.status === 200) {
      } 
      else {
      console.log(`Simulation failed. Status: ${res.status}`)
      }

    } catch (err) {
      console.log(err);
      alert(`Simulation Failed: ${err}`)
    }
  };

  useEffect(() => {
    updateEpiState();
  });

  // Render the simulation input parameter panel
  return (
      <div className='inputParamPanel'>
        <form onSubmit={handleSubmitResp} style={{width: 250}}>
          <label style={labelSize}>  <strong>  Predicted <InlineMath math={secondaryR0Label}/> = {secondaryR0} </strong></label>
          <br></br>
          <label style={labelSize}> <strong> Tree density <InlineMath math={densityRho}/> = {density} </strong></label>
          <p></p>
          <label style={labelSize}>  <InlineMath math={susceptibleHosts}/> Hosts = </label>
          <input className='inputBox' type="number" min="100" max="2000" value={hostNumber} onChange={e => setHostNumber(e.target.value)}/>   
          <progress value={hostNumber} max="2000"></progress> 
          <p></p>
          <label style={labelSize}> <InlineMath math={infectedHosts}/> Hosts = </label>
          <input className='inputBox' type="number" min="1" max="100" value={initiallyInfected}  onChange={e => setInitiallyInfected(e.target.value)}/> 
          <progress value={initiallyInfected} max="100"></progress> 
          <p></p>
          <label style={labelSize} > <InlineMath math={infectedHosts}/> Distribution: </label> 
          <select value={initiallyInfectedDist} onChange={e => setInitiallyInfectedDist(e.target.value)}> 
            <option value="centralised"> Centralised</option>
            <option value="random"> Random </option>  
          </select>  
          <p></p>
          <label style={labelSize}> Infectivity <InlineMath math={infectivityBeta}/> = </label>
          <input className='inputBox' type="number" min="0" max={infectivityUpperLim} step="1" value={infectivity}  onChange={e => setInfectivity(e.target.value)}/>
          <progress value={infectivity} max={infectivityUpperLim}></progress> 
          <p></p>
          <label style={labelSize}> Infection period = </label>
          <input className='inputBox' type="number" min="1" max="500" value={infectiousLT}  onChange={e => setInfectiousLT(e.target.value)}/>
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
          <input className='inputBox' className='inputBox' type="number" min="1" max="2000" value={dispersalScale}  onChange={e => setDispersalScale(e.target.value)} />
          <progress value={dispersalScale} max="2000"></progress> 
          <p></p>
          <label style={labelSize}> Domain width (m) = </label>
          <input className='inputBox' type="number" min="1" max="2000" value={domainX}  onChange={e => setDomainX(e.target.value)}/>
          <progress value={domainX} max="2000"></progress> 
          <p></p>
          <label style={labelSize}> Domain height (m) = </label>
          <input className='inputBox' type="number" min="1" max="2000" value={domainY}  onChange={e => setDomainY(e.target.value)}/>   
          <progress value={domainY} max="2000"></progress> 
          <p></p>
          <label style={labelSize}> Time Steps (days) = </label>
          <input className='inputBox' type="number" min="1" max="1500" value={simulationRT}  onChange={e => setSimulationRT(e.target.value)}/>
          <progress value={simulationRT} max="1500"></progress> 
          <p></p>
          <input className='inputBoxBig' type="submit" value="Simulate"/>
        </form>
        <div className='simulationPanel'>
          <SimulationPanel className='simulationPanel' videoRefData={videoRefData}/>
        </div>
      </div>
  );
}


export default InputParameters;
