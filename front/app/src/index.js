import React from 'react';
import ReactDOM from 'react-dom';
import './styles/index.css';
import SimulationPanel from './components/SimPanel';
import InputParameters from './components/InputParams';
import reportWebVitals from './reportWebVitals';

ReactDOM.render(
  <React.StrictMode>
    
    <div className="App">
    <header className="App-header">
      
      {/* <SimulationPanel /> */}
      <InputParameters />

    </header>
    </div>
    
  </React.StrictMode>,
  document.getElementById('root')
);

reportWebVitals();
