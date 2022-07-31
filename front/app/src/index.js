import React from 'react';
import ReactDOM from 'react-dom';
import './styles/index.css';
import headerBanner from './components/header';
import InputParameters from './components/InputParams';
import reportWebVitals from './reportWebVitals';

ReactDOM.render(
  <React.StrictMode>
    
    <div className="App">
    <header className="App-header"> 
        Tree epidemics simulator
    </header>
    <InputParameters/>
    </div>
    
  </React.StrictMode>,
  document.getElementById('root')
);

reportWebVitals();
