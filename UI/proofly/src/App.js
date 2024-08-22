

// import './App.css';
// import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
// import { FontAwesomeIcon } from '@fortawesome/react-fontawesome';
// import { faBars, faArrowLeft, faArrowRight } from '@fortawesome/free-solid-svg-icons';

// import { useState } from 'react';
// import Sidebar from './componets/Sidebar';
// import SearchPage from './componets/SearchPage';
// import DashboardPage from './componets/DashboardPage';
// import CardDetailsPage from './componets/CardDetailsPage';
// import SubCardDetailsPage from './componets/SubCardDetailsPage';
// import WordProcessor from './componets/WordProcessor';
// function App() {
//   const [isSidebarOpen, setIsSidebarOpen] = useState(true);

//   const toggleSidebar = () => {
//     setIsSidebarOpen(!isSidebarOpen);
//   };

//   return (
//     <>
//       <Router>
//         <div className="app">
//           <Sidebar isOpen={isSidebarOpen} toggleSidebar={toggleSidebar} />
//           <button className={`ii ${isSidebarOpen ? 'button-open' : 'button-closed'}`} onClick={toggleSidebar}>
//           <FontAwesomeIcon icon={isSidebarOpen ? faArrowLeft : faArrowRight} />
//       </button>
//           <div className={`content ${isSidebarOpen ? 'content-open' : 'content-closed'}`}>
//             <Routes>
//               <Route path="/" element={<SearchPage />} />
//               <Route path="/wordcorrect" element={<WordProcessor />} />
//               <Route path="/dashboard" element={<DashboardPage />} />
//               <Route path="/card/:id" element={<CardDetailsPage />} />
//               <Route path="/subcard/:subCardId" element={<SubCardDetailsPage />} /> {/* New route for sub-card details */}
//             </Routes>
//           </div>
//         </div>
//       </Router>
//     </>
//   );
// }

// export default App;

import './App.css';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome';
import { faArrowLeft, faArrowRight } from '@fortawesome/free-solid-svg-icons';

import { useState } from 'react';
import Sidebar from './componets/Sidebar';
import SearchPage from './componets/SearchPage';
import DashboardPage from './componets/DashboardPage';
import CardDetailsPage from './componets/CardDetailsPage';
import SubCardDetailsPage from './componets/SubCardDetailsPage';
import WordProcessor from './componets/WordProcessor';
import Login from './componets/Login';

function PrivateRoute({ element: Component, isAuthenticated, ...rest }) {
  return (
    <Route
      {...rest}
      element={isAuthenticated ? <Component /> : <Navigate to="/" />}
    />
  );
}

function App() {
  const [isSidebarOpen, setIsSidebarOpen] = useState(true);
  const [isAuthenticated, setIsAuthenticated] = useState(false);

  const toggleSidebar = () => {
    setIsSidebarOpen(!isSidebarOpen);
  };

  const handleLogin = () => {
    setIsAuthenticated(true);
  };

  return (
    <>
      <Router>
        <div className="app">
          {isAuthenticated && (
            <>
              <Sidebar isOpen={isSidebarOpen} toggleSidebar={toggleSidebar} />
              <button className={`ii ${isSidebarOpen ? 'button-open' : 'button-closed'}`} onClick={toggleSidebar}>
                <FontAwesomeIcon icon={isSidebarOpen ? faArrowLeft : faArrowRight} />
              </button>
            </>
          )}
          <div className={`content ${isSidebarOpen ? 'content-open' : 'content-closed'}`}>
            <Routes>
              <Route path="/" element={<Login onLogin={handleLogin} />} />
              <PrivateRoute path="/wordcorrect" element={<WordProcessor />} isAuthenticated={isAuthenticated} />
              <PrivateRoute path="/dashboard" element={<DashboardPage />} isAuthenticated={isAuthenticated} />
              <PrivateRoute path="/card/:id" element={<CardDetailsPage />} isAuthenticated={isAuthenticated} />
              <PrivateRoute path="/subcard/:subCardId" element={<SubCardDetailsPage />} isAuthenticated={isAuthenticated} />
            </Routes>
          </div>
        </div>
      </Router>
    </>
  );
}

export default App;
