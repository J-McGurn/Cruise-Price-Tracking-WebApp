import React, { useState } from 'react';
import POCruisesTable from './POTable';
import PrincessCruisesTable from './PrincessTable';
import './CruiseTabs.css';

function CruiseTabs() {
  const [activeTab, setActiveTab] = useState(null);

  const handleTabClick = (tab) => {
    setActiveTab((prev) => (prev === tab ? null : tab));
  }

  return (
    <div className="cruise-tabs-container">
      {/* Tabs */}
      <div className="tabs">
        <button
          className={`tab ${activeTab === 'po' ? 'active' : ''}`}
          onClick={() => handleTabClick('po')}
        >
          P&O Cruises
        </button>
        <button
          className={`tab ${activeTab === 'princess' ? 'active' : ''}`}
          onClick={() => handleTabClick('princess')}
        >
          Princess Cruises
        </button>
      </div>

      {/* Tab Content */}
      <div className="tab-content">
        {activeTab === 'po' && <POCruisesTable />}
        {activeTab === 'princess' && <PrincessCruisesTable />}
      </div>
    </div>
  );
}

export default CruiseTabs;