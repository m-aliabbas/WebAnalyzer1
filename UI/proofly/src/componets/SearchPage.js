import React, { useState } from 'react';
import { ToastContainer, toast } from 'react-toastify';
import 'react-toastify/dist/ReactToastify.css';
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome';
import { faTimes, faSync } from '@fortawesome/free-solid-svg-icons';
import './searchPage.css';

const SearchPage = () => {
  const [tags, setTags] = useState([
    "Best", "Specialist", "Specialised", "Finest", "Most experienced",
    "Superior", "Principle", "Expert", "Amazing", "Speciality",
    "leader", "leaders", "service", "implantologist"
  ]);
  const [searchQuery, setSearchQuery] = useState('');
  const [action, setAction] = useState('Crawl');

  const handleTagRemove = (index) => {
    setTags(tags.filter((_, i) => i !== index));
  };

  const handleRefresh = () => {
    // Simulate refreshing tags from API
    setTags([
      "Best", "Specialist", "Specialised", "Finest", "Most experienced",
      "Superior", "Principle", "Expert", "Amazing", "Speciality",
      "leader", "leaders", "service", "implantologist"
    ]);
    toast.info('Tags refreshed!');
  };

  const handleSubmit = async () => {
    try {
      const response = await fetch('http://127.0.0.1:8000/search/', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          url: searchQuery,
          number_of_pages: 1,  // Hardcoded to 1 page
          option: action,
          tags: tags,
        }),
      });

      if (response.ok) {
        const data = await response.json();
        toast.success(`Your task is added: ${data.message}`);
      } else {
        toast.error('Failed to initiate search task');
      }
    } catch (error) {
      toast.error('An error occurred while processing your request');
    }
  };

  return (
    <>
      <div className="search-page">
        <div className="image-container">
          <img src="/proofly.png" alt="Search" />
        </div>
        <h2 className="main-heading">Achieve Perfection with Proofly’s <br/>Expert Proofreading.</h2>
        <div className="description">
          <p>Achieve Perfection with Proofly’s AI-Powered Proofreading.
             Our advanced technology meticulously
             refines your website content, ensuring clarity, professionalism, and a flawless user experience.</p>
        </div>
        <div className="search-bar">
          <input 
            type="text" 
            placeholder="Search..." 
            value={searchQuery} 
            onChange={(e) => setSearchQuery(e.target.value)} 
          />
        </div>

        <div className="in">
          <div className="tags-container">
            {tags.map((tag, index) => (
              <div className="tag" key={index}>
                {tag}
                <button className="remove-tag" onClick={() => handleTagRemove(index)}>
                  <FontAwesomeIcon icon={faTimes} />
                </button>
              </div>
            ))}
            <button className="refresh-tags" onClick={handleRefresh}>
              <FontAwesomeIcon icon={faSync} />
            </button>
          </div>
        </div>

        <div className="controls-container">
          <select 
            value={action} 
            onChange={(e) => setAction(e.target.value)} 
            className="action-dropdown"
          >
            <option value="Crawl">Crawl</option>
            <option value="Scrape">Scrape</option>
          </select>
        </div>

        <div className='button-out'>
          <button className="submit-button" onClick={handleSubmit}>Submit</button>
        </div>
        <ToastContainer />
      </div>
    </>
  );
};

export default SearchPage;
