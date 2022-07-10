import '../styles/app.css'
import React, { useState, useRef} from 'react';


function SimulationPanel() {
  const simulationPath = './media/sim.mp4'
  const catImagePath = 'https://tree-epi-site-bucket.s3.etu-west-2.amazonaws.com/Thinking-of-getting-a-cat.png'

  const vidRef = useRef(null);
  const buttonRef = useRef(null);
  const [buttonText, setButtonText] = useState('>');
  
  const onButtonClick = () => {
    if (vidRef.current.paused) {
      vidRef.current.play()
      setButtonText('||')
    }
    else {
      vidRef.current.pause()
      setButtonText('>')
    }
  }

  const isSimGenerated = () => {
    try {
      const simulation = require(`${simulationPath}`)
      console.log('succces', simulation)
     return true;
    } catch (err) {
      console.log('fail')
     return false;
    }
  };

  const mySim = isSimGenerated()
  
  if  ( mySim == false) {
    console.log('Sim not generate, rendering cat')
    return (
        <div className='simulationPanel'> 
            <p> Image not here</p> 
            <img src={catImagePath} />
          </div>
    );
  }
  
  else {
    console.log('rendering vid')
    const mySim = require(`${simulationPath}`) 
    return (
        <div className='simulationPanel'> 
            <video ref={vidRef} src={mySim} type="video/mp4"> </video> 
        <button ref={buttonRef} onClick={() => onButtonClick()}> {buttonText} </button>
        </div>
    );
}}

export default SimulationPanel;
