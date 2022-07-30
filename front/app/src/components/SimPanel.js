import '../styles/app.css'
import React from 'react';

function SimulationPanel(videoRefData) {

  let videoRef = videoRefData.parentToChild
  videoRef = `./media/${videoRef}.mp4`
  const catImagePath = 'https://tree-epi-site-bucket.s3.etu-west-2.amazonaws.com/Thinking-of-getting-a-cat.png'

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
    return (
        <div className='simulationPanel'> 
            <p> Image not here</p> 
            <img src={catImagePath} />
          </div>
    );
  }
  
  else {
    const simulation = require(`${videoRef}`)
    return (
        <div className='simulationPanel'> 
            <video src={simulation} type="video/mp4" controls> </video> 
        </div>
    );
}}

export default SimulationPanel;
