import React, { useState, useEffect } from 'react';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, Label } from 'recharts';
import './PriceGraph.css';

function PriceGraph() {
  const [cruises, setCruises] = useState([]);
  const [selectedCruises, setSelectedCruises] = useState([
    { cruise_code: '', cabin_type: '', fare_type: '' }
  ]);

  useEffect(() => {
    fetch('http://127.0.0.1:5000/cruises')
      .then(res => res.json())
      .then(data => setCruises(data))
      .catch(err => console.error(err));
  }, []);

  const handleChange = (index, field, value) => {
    const updated = [...selectedCruises];
    updated[index][field] = value;

    // Reset dependent fields
    if (field === 'cruise_code') {
      updated[index].cabin_type = '';
      updated[index].fare_type = '';
    } else if (field === 'cabin_type') {
      updated[index].fare_type = '';
    }

    setSelectedCruises(updated);
  };

  const addCruiseSelection = () => {
    setSelectedCruises([...selectedCruises, { cruise_code: '', cabin_type: '', fare_type: '' }]);
  };

  const removeCruiseSelection = index => {
    const updated = selectedCruises.filter((_, i) => i !== index);
    setSelectedCruises(updated);
  };

  const colors = ['#df1212', '#1212df', '#12df12', '#df12df', '#df9e12'];

  // Prepare datasets for each selected cruise
  const chartDataSets = selectedCruises.map(sel => {
    if (!sel.cruise_code || !sel.cabin_type || !sel.fare_type) return [];

    let data = cruises
      .filter(c => c.cruise_code === sel.cruise_code && c.cabin_type === sel.cabin_type && c.fare_type === sel.fare_type)
      .map(c => ({ date: c.date_checked, total_price: c.total_price }));

    data.sort((a, b) => new Date(a.date) - new Date(b.date));
    return data;
  }).filter(ds => ds.length > 0);

  // Merge dates for X-axis
  const allDates = Array.from(new Set(chartDataSets.flatMap(ds => ds.map(d => d.date)))).sort(
    (a, b) => new Date(a.date) - new Date(b.date)
  );

  const mergedData = allDates.map(date => {
    const row = { date };
    chartDataSets.forEach((ds, idx) => {
      const entry = ds.find(d => d.date === date);
      row[`total_price_${idx}`] = entry ? entry.total_price : null;
    });
    return row;
  });

  const cruiseOptions = [...new Set(cruises.map(c => c.cruise_code))];
  const getCabinOptions = cruise_code => [...new Set(cruises.filter(c => c.cruise_code === cruise_code).map(c => c.cabin_type))];
  const getFareOptions = (cruise_code, cabin_type) => [...new Set(cruises.filter(c => c.cruise_code === cruise_code && c.cabin_type === cabin_type).map(c => c.fare_type))];

  return (
    <div className="price-graph-container">
      <h2 className="graph-title">Price Graph</h2>

      {selectedCruises.map((sel, idx) => (
        <div key={idx} className="dropdown-row">
          <label>Cruise Code: </label>
          <select value={sel.cruise_code} onChange={e => handleChange(idx, 'cruise_code', e.target.value)}>
            <option value="">--Select--</option>
            {cruiseOptions.map(c => <option key={c} value={c}>{c}</option>)}
          </select>

          <label>Cabin Type: </label>
          <select value={sel.cabin_type} onChange={e => handleChange(idx, 'cabin_type', e.target.value)}>
            <option value="">--Select--</option>
            {getCabinOptions(sel.cruise_code).map(c => <option key={c} value={c}>{c}</option>)}
          </select>

          <label>Fare Type: </label>
          <select value={sel.fare_type} onChange={e => handleChange(idx, 'fare_type', e.target.value)}>
            <option value="">--Select--</option>
            {getFareOptions(sel.cruise_code, sel.cabin_type).map(f => <option key={f} value={f}>{f}</option>)}
          </select>

          {selectedCruises.length > 1 && (
            <button className="remove-btn" onClick={() => removeCruiseSelection(idx)}>Remove</button>
          )}
        </div>
      ))}

      <div className="add-btn-container">
        <button className="add-btn" onClick={addCruiseSelection}>
          Add Another Cruise
        </button>
      </div>

      {mergedData.length > 0 ? (
        <LineChart className="line-chart" width={800} height={400} data={mergedData} margin={{ top: 20, right: 80, left: 20, bottom: 50 }}>
          <CartesianGrid strokeDasharray="3 3" />
          <XAxis dataKey="date">
            <Label value="Date Checked" offset={-10} position="insideBottom" />
          </XAxis>
          <YAxis domain={['dataMin - 50', 'dataMax + 50']}>
            <Label value="Total Price (£)" angle={-90} position="insideLeft" style={{ textAnchor: 'middle' }} />
          </YAxis>
          <Tooltip />
          <Legend verticalAlign="top" align="right" />
          {chartDataSets.map((_, idx) => (
            <Line
              key={idx}
              type="stepAfter"
              dataKey={`total_price_${idx}`}
              stroke={colors[idx % colors.length]}
              name={selectedCruises[idx].cruise_code}
              connectNulls
            />
          ))}
        </LineChart>
      ) : (
        <p className="instruction-text">Please select cruise, cabin, and fare type to view the graph.</p>
      )}
    </div>
  );
}

export default PriceGraph;
