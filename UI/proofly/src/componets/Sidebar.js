    
    
import React from 'react';
import { NavLink } from 'react-router-dom';
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome';

import { faSearch, faTachometerAlt,faBars, faFileWord } from '@fortawesome/free-solid-svg-icons';
import './sidebar.css';

const Sidebar = ({ isOpen}) => {
  return (
        <>
        <div className={`sidebar ${isOpen ? 'open' : 'closed'}`}>
      <div className="links">
        <NavLink exact to="/" activeClassName="active">
          <FontAwesomeIcon icon={faSearch} className="icon" />
          Search
        </NavLink>
        <NavLink exact to="/wordcorrect" activeClassName="active">
          <FontAwesomeIcon icon={faFileWord} className="icon" />
          Word File Processor
        </NavLink>
        <NavLink to="/dashboard" activeClassName="active">
          <FontAwesomeIcon icon={faTachometerAlt} className="icon" />
          Dashboard
        </NavLink>
      </div>
      <div className="profile">
        <img src="https://via.placeholder.com/50" alt="Profile" />
        <div className="profile-info">
          <h3>John Doe</h3>
          <p>john.doe@example.com</p>
        </div>
      </div>
    </div>
  </>
  );
};

export default Sidebar;
