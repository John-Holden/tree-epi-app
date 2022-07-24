import '../styles/app.css';
import 'katex/dist/katex.min.css';
import React, { useState, useEffect } from 'react';
import { InlineMath } from 'react-katex';

const labelSize = {
  fontSize: 15
}

function InputParameters() {
  // Initialise simulation parameter
  const ApiHostName = process.env.REACT_APP_API_URL;
  const [message, setMessage] = useState("");
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

  // Update the infectivity parameter & R0 value
  function updateInfectivity(e) {
    setInfectivity(e.target.value)
  }

  // Update the number of hosts & R0 value
  function updateHosts(e) {
    setHostNumber(e.target.value)
  }

  // Update the domain width
  function updateDomainX(e) {
    setDomainX(e.target.value)
  }

  // Update the domain height
  function updateDomainY(e) {
    setDomainY(e.target.value)
  }

  function updateInfectiousPeriod(e) {
    setInfectiousLT(e.target.value)

  }

  function updateDispersalLength(e) {
    setDispersalScale(e.target.value)
  }


 // Update R0 value, conditional on density, infectivity, & infectious lifetime 
 let updateEpiState = async () => {

  function updateR0andDensity(jsonData) {
    setDensity(jsonData['density'])
    setSecondaryR0(jsonData['R0'])
    setinfectivityUpperLim(jsonData['beta_max'])
    console.log('infectivity uppper lim ', infectivityUpperLim)
  }

  try {
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
  
    // res.json().then((data) => {setSecondaryR0(data['R0'])})
    res.json().then((data) => {updateR0andDensity(data)})

    console.log('density:', density)
    console.log('R0:', secondaryR0)


    // res.json().then((data) => {setDensity(data['density'])})
    if (res.status === 200) {
    } else {
      console.log(`Failed updating R0. Status: ${res.status}`)
    }
  } catch (err) {
    console.log(err);
    alert(`Failed. Error ${err}`)
  }
 }
 
 
  // Submit a simulation to the backend
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
      res.json().then((data) => {console.log("back end resp: ", data['message'])})
      if (res.status === 200) {
        setMessage("[i] Successful");
      } 
      else {
        setMessage(`[e] Failed, status: ${res.status}`)
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
        <form onSubmit={handleSubmitResp} style={{width: 180}}>
          <label style={labelSize}> Predicted <InlineMath math={secondaryR0Label}/>: {secondaryR0} </label>
          <label style={labelSize}> Tree density <InlineMath math={densityRho}/>: {density} </label>
          <p></p>
          <label style={labelSize}>  <InlineMath math={susceptibleHosts}/> Hosts: {hostNumber} </label>
          <input type="range" min="100" max="2000" value={hostNumber}  onChange={updateHosts}/>   
          <p></p>
          <label style={labelSize}> <InlineMath math={infectedHosts}/> Hosts: {initiallyInfected} </label>
          <input type="range" min="1" max="100" value={initiallyInfected}  onChange={e => setInitiallyInfected(e.target.value)}/> 
          <p></p>
          <label style={labelSize} > <InlineMath math={infectedHosts}/> Distribution </label> 
          <select value={initiallyInfectedDist} onChange={e => setInitiallyInfectedDist(e.target.value)}> 
            <option value="centralised"> Centralised</option>
            <option value="random"> Random </option>  
          </select>  
          <p></p>
          <label style={labelSize}> Infectivity <InlineMath math={infectivityBeta}/>: {infectivity} </label>
          <input type="range" min="0" max={infectivityUpperLim} step="1" value={infectivity}  onChange={updateInfectivity}/> 
          <p></p>
          <label style={labelSize}> Infectious period: {infectiousLT} </label>
          <input type="range" min="1" max="500" value={infectiousLT}  onChange={updateInfectiousPeriod}/>  
          <br></br>
          <label style={labelSize} > Dispersal Kernel: </label> 
          <select value={dispersaType} onChange={e => setDispersal(e.target.value)}> 
            <option value="gaussian">Gaussian</option>  
            <option value="exponential">Exponential</option>
            <option value="inverse_power_Law">Inverse power law</option>
          </select>
          <p></p>
          <label style={labelSize}> Dispersal length: {dispersalScale}(m) </label>
          <input type="range" min="1" max="2000" value={dispersalScale}  onChange={updateDispersalLength} />   
          <p></p>
          <label style={labelSize}> Domain width: {domainX}(m) : </label>
          <input type="range" min="1" max="2000" value={domainX}  onChange={updateDomainX}/>   
          <p></p>
          <label style={labelSize}> Domain height: {domainY}(m) : </label>
          <input type="range" min="1" max="2000" value={domainY}  onChange={updateDomainY}/>   
          <p></p>
          <label style={labelSize}> Time Steps (days): {simulationRT} </label>
          <input type="range" min="1" max="2000" value={simulationRT}  onChange={e => setSimulationRT(e.target.value)}/>
          <p></p>
          <input type="submit" value="Simulate"/>
        </form>
      </div>
  );
}

export default InputParameters;
