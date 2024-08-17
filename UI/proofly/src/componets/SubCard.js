import React from 'react';
import { Card as MuiCard, CardContent, Typography, Divider, Chip, IconButton } from '@mui/material';
import { styled } from '@mui/system';
import DownloadIcon from '@mui/icons-material/Download';
import PageviewIcon from '@mui/icons-material/Pageview';
import { useNavigate } from 'react-router-dom';
import axios from 'axios';
import { API_BASE_URL } from './Config'; // Import the base URL

const StatusChip = styled(Chip)(({ status }) => ({
  backgroundColor: status === 'done' ? 'green' : status === 'in progress' ? 'blue' : 'red',
  color: 'white',
  position: 'absolute',
  top: '10px',
  right: '10px',
}));

const SubCard = ({ id, title, progress, description }) => {
  const navigate = useNavigate();

  const handleDownloadClick = async () => {
    try {
      const response = await axios.post(
        `${API_BASE_URL}/get_pdf_page/`, // Updated to use API_BASE_URL
        { ids: id },
        { responseType: 'blob' } // This is important to handle binary data
      );

      // Create a URL for the PDF file
      const url = window.URL.createObjectURL(new Blob([response.data]));
      const link = document.createElement('a');
      link.href = url;
      link.setAttribute('download', `${id}.pdf`); // Use ID for the downloaded file name
      document.body.appendChild(link);
      link.click();
      link.parentNode.removeChild(link);
    } catch (error) {
      console.error('Error downloading the PDF:', error);
    }
  };

  const handleShowPageClick = () => {
    navigate(`/subcard/${id}`, { state: { title, progress, description } });
  };

  return (
    <MuiCard sx={{ width: 'calc(345px * 2)', margin: '10px auto', boxShadow: 1, position: 'relative' }}>
      <CardContent sx={{ position: 'relative' }}>
        <StatusChip label={progress} status={progress} />
        <Typography variant="h6" component="div" gutterBottom>
          {title}
        </Typography>
        <Divider sx={{ marginY: 1 }} />
        <Typography variant="body2" color="text.secondary">
          {description}
        </Typography>
        <IconButton
          color="primary"
          aria-label="download"
          sx={{ position: 'absolute', bottom: '10px', right: '50px' }}
          onClick={handleDownloadClick}
        >
          <DownloadIcon />
        </IconButton>
        <IconButton
          color="primary"
          aria-label="show-page"
          sx={{ position: 'absolute', bottom: '10px', right: '10px' }}
          onClick={handleShowPageClick}
        >
          <PageviewIcon />
        </IconButton>
      </CardContent>
    </MuiCard>
  );
};

export default SubCard;
