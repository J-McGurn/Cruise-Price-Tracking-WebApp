import React from 'react';
import './Navbar.css';

function Navbar({ onButtonClick }) {
  return (
    <nav className="navbar">
      <div className="navbar-title">Cruise Price Tracker</div>
      <div className="navbar-buttons">
        <button className="navbar-button" onClick={() => onButtonClick('home')}>Info</button>
      </div>
    </nav>
  );
}

export default Navbar;