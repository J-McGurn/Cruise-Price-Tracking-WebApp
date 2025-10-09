import React, { useState, useEffect } from 'react';
import './App.css';

function POCruisesTable() {
  const [cruises, setCruises] = useState([]);

  useEffect(() => {
    const fetchCruises = async () => {
      try {
        const response = await fetch('https://cruise-price-tracking-webapp.onrender.com/cruises/po');
        const data = await response.json();

        // ✅ Filter to only unique cruise_code entries
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
        console.error('Error fetching P&O cruises:', error);
      }
    };

    fetchCruises();
  }, []);

  return (
    <div>
      {cruises.length === 0 ? (
        <p>Loading P&O Cruises...</p>
      ) : (
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

export default POCruisesTable;
