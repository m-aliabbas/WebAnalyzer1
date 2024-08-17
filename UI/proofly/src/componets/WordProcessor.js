import React, { useState } from 'react';
import { ToastContainer, toast } from 'react-toastify';
import 'react-toastify/dist/ReactToastify.css';
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome';
import { faTimes, faSync } from '@fortawesome/free-solid-svg-icons';
import { Button, TextField } from '@mui/material';
import { API_BASE_URL } from './Config'; // Import the base URL
import './searchPage.css';


const WordCorrection = () => {
  const [tags, setTags] = useState([
    "Best", "Specialist", "Specialised", "Finest", "Most experienced",
    "Superior", "Principle", "Expert", "Amazing", "Speciality",
    "leader", "leaders", "service", "implantologist"
  ]);
  const [selectedFile, setSelectedFile] = useState(null);

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

  const handleFileChange = (e) => {
    setSelectedFile(e.target.files[0]);
  };

  const handleSubmit = async () => {
    if (!selectedFile) {
      toast.error('Please upload a file');
      return;
    }

    const formData = new FormData();
    formData.append('file', selectedFile);
    formData.append('tags', JSON.stringify(tags));

    try {
      const response = await fetch(`${API_BASE_URL}/correct/`, {
        method: 'POST',
        body: formData,
      });

      if (response.ok) {
        const data = await response.json();
        toast.success(`Your task is added: ${data.message}`);
      } else {
        toast.error('Failed to initiate correction task');
      }
    } catch (error) {
      toast.error('An error occurred while processing your request');
    }
  };

  return (
    <>
      <div className="search-page">
        <div className="image-container">
          <img src="/proofly.png" alt="Word Correction" />
        </div>
        <h2 className="main-heading">Achieve Perfection with Proofly’s <br />Expert Word Correction.</h2>
        <div className="description">
          <p>Achieve Perfection with Proofly’s AI-Powered Word Correction.
             Our advanced technology meticulously
             refines your documents, ensuring clarity, professionalism, and a flawless user experience.</p>
        </div>

        <div className="file-upload">
          <TextField
            type="file"
            onChange={handleFileChange}
            inputProps={{ accept: '.doc,.docx,.pdf' }}
            fullWidth
            sx={{
              '& .MuiInputBase-root': {
                backgroundColor: '#dadada',
                borderRadius: '8px',
                border: '1px solid black',
              },
              '& .MuiInputBase-input': {
                padding: '18px 10px',
                fontSize: '20px',
                color: 'black',
              },
            }}
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
            <Button
              variant="contained"
              onClick={handleRefresh}
              startIcon={<FontAwesomeIcon icon={faSync} />}
              sx={{
                backgroundColor: '#2c3e50',
                color: 'lightblue',
                borderRadius: '5px',
                marginLeft: '10px',
                '&:hover': {
                  backgroundColor: '#48627a',
                },
              }}
            >
              Refresh Tags
            </Button>
          </div>
        </div>

        <div className='button-out'>
          <Button
            variant="contained"
            onClick={handleSubmit}
            fullWidth
            sx={{
              backgroundColor: '#2c3e50',
              color: 'white',
              padding: '18px 10px',
              borderRadius: '5px',
              fontSize: '20px',
              '&:hover': {
                backgroundColor: '#48627a',
              },
            }}
          >
            Submit
          </Button>
        </div>
        <ToastContainer />
      </div>
    </>
  );
};

export default WordCorrection;
