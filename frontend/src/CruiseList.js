import React, { useState } from 'react';
import './App.css';

function CruiseList() {
  const [cruises, setCruises] = useState([]);
  const [showCruises, setShowCruises] = useState(false);

  const handleClick = async () => {
    setShowCruises(!showCruises);

    if (cruises.length === 0) {
      try {
        const response = await fetch('http://127.0.0.1:5000/cruises/po');
        const data = await response.json();

        // Filter to only distinct cruises by cruise_code
        const uniqueCruises = [];
        const seenCodes = new Set();
        data.forEach(c => {
          if (!seenCodes.has(c.cruise_code)) {
            seenCodes.add(c.cruise_code);
            uniqueCruises.push(c);
          }
        });

        setCruises(uniqueCruises);
      } catch (error) {
        console.error('Error fetching cruises:', error);
      }
    }
  };

  return (
    <div>
      <button className="show-button" onClick={handleClick}>
        {showCruises ? 'Hide Currently Tracked Cruises' : 'Show Currently Tracked Cruises'}
      </button>

      {showCruises && cruises.length > 0 && (
        <table className="cruise-table">
          <thead>
            <tr>
              <th>Cruise Code</th>
              <th>Cruise Name</th>
              <th>Ship Name</th>
              <th>Departure Port</th>
              <th>Departure Date</th>
              <th>Duration</th>
            </tr>
          </thead>
          <tbody>
            {cruises.map((c) => (
              <tr key={c.cruise_code}>
                <td>{c.cruise_code}</td>
                <td>{c.cruise_name}</td>
                <td>{c.ship_name}</td>
                <td>{c.departure_port}</td>
                <td>{c.departure_date}</td>
                <td>{c.duration}</td>
              </tr>
            ))}
          </tbody>
        </table>
      )}
    </div>
  );
}

export default CruiseList;
