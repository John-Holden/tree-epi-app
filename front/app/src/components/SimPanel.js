import '../styles/app.css'
import React, {useEffect, useRef, useState, forwardRef} from 'react';

function SimulationPanel( props ) {

  let videoRef = props['videoRefData']
  videoRef = `./media/${videoRef}.mp4`
   
  const isSimGenerated = () => {
    try {
     require(`${videoRef}`)
     return true;
    } 
    catch (err) {
     return false;
    }
  };

  const mySim = isSimGenerated()
  
  if  ( mySim == false) {
    //  Sim not generate, rendering cat
    videoRef = './media/sim-out.mp4'
  }
  

  const simulation = require(`${videoRef}`)
  return (
      <div className='simulationPanel'> 
          <video width="750" height="500"  src={simulation} type="video/mp4" controls> </video> 
      </div>
  );
}

export default SimulationPanel;
