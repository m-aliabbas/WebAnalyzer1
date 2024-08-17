import React, { useState, useEffect } from 'react';
import { Card as MuiCard, CardContent, Typography, Divider, IconButton, Tooltip, Chip, Button, Box } from '@mui/material';
import { styled } from '@mui/system';
import { useNavigate } from 'react-router-dom';
import VisibilityIcon from '@mui/icons-material/Visibility';
import DeleteIcon from '@mui/icons-material/Delete';
import DownloadIcon from '@mui/icons-material/Download';
import axios from 'axios';

const StatusChip = styled(Chip)(({ status }) => ({
  backgroundColor: status === 'done' ? 'green' : status === 'in progress' ? 'blue' : 'red',
  color: 'white',
  position: 'absolute',
  top: '10px',
  right: '10px',
}));

const ButtonContainer = styled('div')({
  position: 'absolute',
  bottom: '10px',
  right: '10px',
  display: 'flex',
  gap: '8px',
});

const TransparentCard = styled(MuiCard)(({ theme }) => ({
  maxWidth: 'calc(345px * 2.5)',
  margin: '10px auto',
  position: 'relative',
  backgroundColor: 'transparent',
  backdropFilter: 'blur(20px)',
  borderRadius: '12px',
  boxShadow: '4px 4px 8px rgba(0, 0, 0, 0.2), -4px -4px 8px rgba(255, 255, 255, 0.2)',
}));

const Card = ({ id, title, progress, tags, onDelete, halt_status }) => {
  const navigate = useNavigate();
  const [isHalted, setIsHalted] = useState(halt_status === true);

  useEffect(() => {
    setIsHalted(halt_status === true);
  }, [halt_status]);

  const handleDetailsClick = () => {
    navigate(`/card/${id}`);
  };

  const handleDeleteClick = async () => {
    if (window.confirm('Are you sure you want to delete this card?')) {
      try {
        const response = await axios.post('http://127.0.0.1:8000/delete_doc/', {
          ids: id,
        });
        alert(response.data.message || 'Card deleted successfully!');
        window.location.reload(); // Reloads the page to reflect the deletion
      } catch (error) {
        console.error('Error deleting card:', error);
        alert('An error occurred while processing your request.');
      }
    }
  };

  const handleHaltToggle = async () => {
    try {
      const apiUrl = isHalted ? 'http://127.0.0.1:8000/unhalt/' : 'http://127.0.0.1:8000/halt/';
      const response = await axios.post(apiUrl, { url: title });
      setIsHalted(!isHalted);
      alert(response.data.message || "Operation completed successfully!");
    } catch (error) {
      console.error("Error halting/unhalting:", error);
      alert("An error occurred while processing your request.");
    }
  };

  const handleDownload = async () => {
    try {
      const response = await axios.post('http://127.0.0.1:8000/get_multipage_pdf/', { ids: id }, {
        responseType: 'blob', // Important to specify this to handle binary data
      });
  
      const url = window.URL.createObjectURL(new Blob([response.data]));
      const link = document.createElement('a');
      link.href = url;
      link.setAttribute('download', `${id}.pdf`); // The ID from the URL as the filename
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
    } catch (error) {
      console.error('Error downloading PDF:', error);
      alert('An error occurred while downloading the file.');
    }
  };

  return (
    <TransparentCard>
      <CardContent>
        <StatusChip label={progress} status={progress} />
        <Typography variant="h5" component="div" gutterBottom>
          {title}
        </Typography>
        <Divider sx={{ marginY: 2 }} />
        <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 1 }}>
          {tags.map((tag, index) => (
            <Chip key={index} label={tag} color="primary" />
          ))}
        </Box>
       
        <ButtonContainer>
          <Button
            variant="contained"
            color={isHalted ? "warning" : "primary"}
            onClick={handleHaltToggle}
          >
            {isHalted ? "Unhalt" : "Halt"}
          </Button>
          <Tooltip title="Download PDF">
            <IconButton color="primary" onClick={handleDownload}>
              <DownloadIcon />
            </IconButton>
          </Tooltip>
          <Tooltip title="Show Details">
            <IconButton color="primary" onClick={handleDetailsClick}>
              <VisibilityIcon />
            </IconButton>
          </Tooltip>
          <Tooltip title="Delete">
            <IconButton color="error" onClick={handleDeleteClick}>
              <DeleteIcon />
            </IconButton>
          </Tooltip>
        </ButtonContainer>
      </CardContent>
    </TransparentCard>
  );
};

export default Card;
