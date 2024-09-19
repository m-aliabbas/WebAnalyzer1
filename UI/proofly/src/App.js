

import './App.css';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome';
import { faBars, faArrowLeft, faArrowRight } from '@fortawesome/free-solid-svg-icons';

import { useState } from 'react';
import Sidebar from './componets/Sidebar';
import SearchPage from './componets/SearchPage';
import DashboardPage from './componets/DashboardPage';
import CardDetailsPage from './componets/CardDetailsPage';
import SubCardDetailsPage from './componets/SubCardDetailsPage';
import WordProcessor from './componets/WordProcessor';
import Keys from './componets/Keys';
import AcmeChallenge from './componets/AcmeChallenge';// New Component
function App() {
  const [isSidebarOpen, setIsSidebarOpen] = useState(true);

  const toggleSidebar = () => {
    setIsSidebarOpen(!isSidebarOpen);
  };

  return (
    <>
      <Router>
        <div className="app">
          <Sidebar isOpen={isSidebarOpen} toggleSidebar={toggleSidebar} />
          <button className={`ii ${isSidebarOpen ? 'button-open' : 'button-closed'}`} onClick={toggleSidebar}>
          <FontAwesomeIcon icon={isSidebarOpen ? faArrowLeft : faArrowRight} />
      </button>
          <div className={`content ${isSidebarOpen ? 'content-open' : 'content-closed'}`}>
            <Routes>
              <Route path="/" element={<SearchPage />} />
              <Route path="/keys" element={<Keys />} />
              <Route path="/wordcorrect" element={<WordProcessor />} />
              <Route path="/dashboard" element={<DashboardPage />} />
              <Route path="/card/:id" element={<CardDetailsPage />} />
              <Route path="/subcard/:subCardId" element={<SubCardDetailsPage />} /> {/* New route for sub-card details */}
              <Route path="/.well-known/acme-challenge/" element={<AcmeChallenge />} />
            </Routes>
          </div>
        </div>
      </Router>
    </>
  );
}

export default App;
