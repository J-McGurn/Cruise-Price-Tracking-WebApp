import React, { useState, useEffect } from 'react';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Label } from 'recharts';
import './PriceGraph.css';

function PriceGraph() {
  const [poCruises, setPoCruises] = useState([]);
  const [princessCruises, setPrincessCruises] = useState([]);
  const [selectedCruises, setSelectedCruises] = useState([]);

  // Fetch both cruise datasets
  useEffect(() => {
    Promise.all([
      fetch('https://cruise-price-tracking-webapp.onrender.com/cruises/po').then(res => res.json()),
      fetch('https://cruise-price-tracking-webapp.onrender.com/cruises/princess').then(res => res.json())
    ])
      .then(([poData, princessData]) => {
        setPoCruises(poData);
        setPrincessCruises(princessData);
      })
      .catch(err => console.error(err));
  }, []);

  const handleChange = (index, field, value) => {
    const updated = [...selectedCruises];
    updated[index][field] = value;

    if (field === 'cruiseLine') {
      updated[index].cruise_code = '';
      updated[index].cabin_type = '';
      updated[index].fare_type = '';
    } else if (field === 'cruise_code') {
      updated[index].cabin_type = '';
      updated[index].fare_type = '';
    } else if (field === 'cabin_type') {
      updated[index].fare_type = '';
    }

    setSelectedCruises(updated);
  };

  const addCruiseSelection = () => {
    setSelectedCruises([
      ...selectedCruises,
      { cruiseLine: '', cruise_code: '', cabin_type: '', fare_type: '' }
    ]);
  };

  const removeCruiseSelection = index => {
    setSelectedCruises(selectedCruises.filter((_, i) => i !== index));
  };

  const colors = [
    '#df1212', '#1212df', '#12df12', '#df12df', '#df9e12',
    '#12dfdf', '#df5612', '#5612df', '#12df56', '#df12a6'
  ];
  const getColor = idx => colors[idx % colors.length];

  const getDataForLine = (line) =>
    line === 'po' ? poCruises : line === 'princess' ? princessCruises : [];

  const cruiseMap = {
    ...poCruises.reduce((acc, c) => ({ ...acc, [c.cruise_code]: c.cruise_name }), {}),
    ...princessCruises.reduce((acc, c) => ({ ...acc, [c.cruise_code]: c.cruise_name }), {})
  };

  const chartDataSets = selectedCruises.map(sel => {
    if (!sel.cruise_code || !sel.cabin_type || !sel.fare_type) return [];
    const data = getDataForLine(sel.cruiseLine)
      .filter(c =>
        c.cruise_code === sel.cruise_code &&
        c.cabin_type === sel.cabin_type &&
        c.fare_type === sel.fare_type
      )
      .map(c => ({ date: c.date_checked, total_price: c.total_price }));
    data.sort((a, b) => new Date(a.date) - new Date(b.date));
    return data;
  }).filter(ds => ds.length > 0);

  const allDates = Array.from(
    new Set([
      ...poCruises.map(c => c.date_checked),
      ...princessCruises.map(c => c.date_checked)
    ])
  ).sort((a, b) => new Date(a) - new Date(b));

  const mergedData = allDates.map(date => {
    const row = { date };
    chartDataSets.forEach((ds, idx) => {
      const entry = ds.find(d => d.date === date);
      row[`total_price_${idx}`] = entry ? entry.total_price : null;
    });
    return row;
  });

  const getCruiseOptions = (line) =>
    [...new Set(getDataForLine(line).map(c => c.cruise_code))];
  const getCabinOptions = (line, cruise_code) =>
    [...new Set(getDataForLine(line)
      .filter(c => c.cruise_code === cruise_code)
      .map(c => c.cabin_type))];
  const getFareOptions = (line, cruise_code, cabin_type) =>
    [...new Set(getDataForLine(line)
      .filter(c => c.cruise_code === cruise_code && c.cabin_type === cabin_type)
      .map(c => c.fare_type))];

  return (
    <div className="price-graph-container">
      <h2 className="graph-title">Price Graph</h2>

      {selectedCruises.length > 0 ? (
        selectedCruises.map((sel, idx) => (
          <div key={idx} className="dropdown-row">
            <label>Cruise Line: </label>
            <select
              value={sel.cruiseLine}
              onChange={e => handleChange(idx, 'cruiseLine', e.target.value)}
            >
              <option value="">--Select--</option>
              <option value="po">P&O Cruises</option>
              <option value="princess">Princess Cruises</option>
            </select>

            <label>Cruise: </label>
            <select
              value={sel.cruise_code}
              onChange={e => handleChange(idx, 'cruise_code', e.target.value)}
            >
              <option value="">--Select--</option>
              {getCruiseOptions(sel.cruiseLine).map(c => (
                <option key={c} value={c}>
                  {c} – {cruiseMap[c] || 'Unknown'}
                </option>
              ))}
            </select>

            <label>Cabin Type: </label>
            <select
              value={sel.cabin_type}
              onChange={e => handleChange(idx, 'cabin_type', e.target.value)}
            >
              <option value="">--Select--</option>
              {getCabinOptions(sel.cruiseLine, sel.cruise_code).map(c => (
                <option key={c} value={c}>{c}</option>
              ))}
            </select>

            <label>Fare Type: </label>
            <select
              value={sel.fare_type}
              onChange={e => handleChange(idx, 'fare_type', e.target.value)}
            >
              <option value="">--Select--</option>
              {getFareOptions(sel.cruiseLine, sel.cruise_code, sel.cabin_type).map(f => (
                <option key={f} value={f}>{f}</option>
              ))}
            </select>

            {selectedCruises.length > 0 && (
              <button className="remove-btn" onClick={() => removeCruiseSelection(idx)}>
                Remove
              </button>
            )}
          </div>
        ))
      ) : (
        <p className="instruction-text">
          Click "Add Another Cruise" to begin comparing prices.
        </p>
      )}

      <div className="add-btn-container">
        <button className="add-btn" onClick={addCruiseSelection}>
          Add Another Cruise
        </button>
      </div>

      {chartDataSets.length > 0 && mergedData.length > 0 && (
        <>
          <LineChart
            className="line-chart"
            width={window.innerWidth * 0.75}
            height={400}
            data={mergedData}
            margin={{ top: 20, right: 0, left: 0, bottom: 10 }}
          >
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis dataKey="date">
              <Label value="Date Checked" offset={-10} position="insideBottom" />
            </XAxis>
            <YAxis
              domain={['auto', 'auto']}
              tickFormatter={(value) => {
                const num = Number(value);
                if (isNaN(num)) return ''; // ignore bad values
                return `£${Math.round(num).toLocaleString()}`;
              }}
            >
              <Label
                value="Total Price (£)"
                angle={-90}
                position="insideLeft"
                style={{ textAnchor: 'middle' }}
              />
            </YAxis>
            <Tooltip
              formatter={(value) => {
                const num = Number(value);
                if (isNaN(num)) return '—';
                return `£${Math.round(num).toLocaleString()}`;
              }}
            />
            {chartDataSets.map((_, idx) => (
              <Line
                key={idx}
                type="stepAfter"
                dataKey={`total_price_${idx}`}
                stroke={getColor(idx)}
                name={`${selectedCruises[idx].cruise_code} – ${cruiseMap[selectedCruises[idx].cruise_code] || ''}`}
                connectNulls
              />
            ))}
          </LineChart>

          <div style={{ textAlign: "center", marginTop: "10px" }}>
            {selectedCruises.map((sel, idx) => (
              <span
                key={idx}
                style={{
                  margin: "0 12px",
                  color: getColor(idx),
                  display: "inline-flex",
                  alignItems: "center"
                }}
              >
                <span
                  style={{
                    display: "inline-block",
                    width: "12px",
                    height: "12px",
                    borderRadius: "50%",
                    backgroundColor: getColor(idx),
                    marginRight: "6px"
                  }}
                />
                {sel.cruise_code} – {cruiseMap[sel.cruise_code] || 'Unknown'}
              </span>
            ))}
          </div>
        </>
      )}
    </div>
  );
}

export default PriceGraph;