import React from 'react';
import PriceGraph from './PriceGraph';
import CruiseTabs from './CruiseTabs';
import Navbar from './Navbar';
import './App.css';

function App() {

  const handleNavbarButtonClick = () => {
    alert('Navbar button clicked!');
  };
  return (
    <>
      <Navbar onButtonClick={handleNavbarButtonClick} />
      <div style={{ padding: '20px', fontFamily: 'Arial' }}>
        <CruiseTabs />
      </div>

      <div style={{ padding: '20px', fontFamily: 'Arial' }}>
        <PriceGraph />
      </div>
    </>
  );
}

export default App;
