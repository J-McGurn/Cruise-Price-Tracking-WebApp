import React from 'react';
import CruiseList from './CruiseList';
import PriceGraph from './PriceGraph';
import './App.css';

function App() {
  return (
    <>
      <div style={{ padding: '20px', fontFamily: 'Arial' }}>
        <h1>Cruise Tracking App</h1>
        <CruiseList />
      </div>

      <div style={{ padding: '20px', fontFamily: 'Arial' }}>
        <PriceGraph />
      </div>
    </>
  );
}

export default App;
