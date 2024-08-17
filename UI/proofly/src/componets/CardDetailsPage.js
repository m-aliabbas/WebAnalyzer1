import React, { useEffect, useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { Container, Typography, Card as MuiCard, CardContent, Divider, Box, Chip, IconButton, Paper, Button, Snackbar, Pagination } from '@mui/material';
import { styled } from '@mui/system';
import ArrowBackIcon from '@mui/icons-material/ArrowBack';
import SubCard from './SubCard'; // Assuming SubCard component is in the same directory
import axios from 'axios';
import { API_BASE_URL } from './Config'; // Import the base URL

const StatusChip = styled(Chip)(({ status }) => ({
  backgroundColor: status === 'done' ? 'green' : status === 'in progress' ? 'blue' : 'red',
  color: 'white',
  position: 'absolute',
  top: '10px',
  right: '10px',
}));

const CardDetailsPage = () => {
  const { id } = useParams();
  const navigate = useNavigate();
  const [parentData, setParentData] = useState({ title: '', status: '' });
  const [subCards, setSubCards] = useState([]);
  const [page, setPage] = useState(1);
  const [snackbarOpen, setSnackbarOpen] = useState(false);
  const [snackbarMessage, setSnackbarMessage] = useState('');
  const cardsPerPage = 5;

  useEffect(() => {
    // Fetch parent title and status
    axios.post(`${API_BASE_URL}/get_parent_by_id/`, { ids: id })
      .then(response => setParentData(response.data))
      .catch(error => console.error('Error fetching parent data:', error));

    // Fetch sub-cards
    axios.post(`${API_BASE_URL}/get_child_pages`, { ids: id })
      .then(response => setSubCards(response.data))
      .catch(error => console.error('Error fetching sub-cards:', error));
  }, [id]);

  const handleBackClick = () => {
    navigate(-1); // Navigate to the previous page
  };

  const handleDownload = async () => {
    try {
      setSnackbarMessage('Download started...');
      setSnackbarOpen(true);

      const response = await axios.post(`${API_BASE_URL}/get_multipage_pdf/`, { ids: id }, {
        responseType: 'blob', // Important to specify this to handle binary data
      });
  
      const url = window.URL.createObjectURL(new Blob([response.data]));
      const link = document.createElement('a');
      link.href = url;
      link.setAttribute('download', `${id}.pdf`); // The ID from the URL as the filename
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);

      setSnackbarMessage('Download completed.');
      setSnackbarOpen(true);
    } catch (error) {
      setSnackbarMessage('Error downloading PDF.');
      setSnackbarOpen(true);
      console.error('Error downloading PDF:', error);
    }
  };

  const handleSnackbarClose = () => {
    setSnackbarOpen(false);
  };

  const handlePageChange = (event, value) => {
    setPage(value);
  };

  const pageCount = Math.ceil(subCards.length / cardsPerPage);
  const displayCards = subCards.slice((page - 1) * cardsPerPage, page * cardsPerPage);

  return (
    <Container>
      <MuiCard sx={{ maxWidth: 'calc(345px * 2.5)', margin: '20px auto', boxShadow: 3, position: 'relative' }}>
        <CardContent>
          <Paper elevation={3} sx={{ padding: 2, marginBottom: 2, position: 'relative' }}>
            <IconButton onClick={handleBackClick} sx={{ position: 'absolute', top: '10px', left: '10px' }}>
              <ArrowBackIcon />
            </IconButton>
            <StatusChip label={`Status: ${parentData.status}`} status={parentData.status} sx={{ top: '5px', right: '5px' }} />
            <Typography variant="h5" component="div" gutterBottom sx={{ marginTop: 5 }}>
              {parentData.title}
            </Typography>
            <Button variant="contained" color="primary" onClick={handleDownload} sx={{ marginTop: 2 }}>
              Download
            </Button>
            <Divider sx={{ marginY: 3 }} />
            <Box sx={{ display: 'flex', flexDirection: 'column', alignItems: 'center' }}>
              {displayCards.map((subCard) => (
                <SubCard
                  key={subCard.id} // Assuming id is the unique identifier
                  id={subCard.id}
                  title={subCard.title}
                  progress={subCard.status}
                  description={subCard.url} // Assuming you want to display the URL as description
                />
              ))}
            </Box>
          </Paper>
          <Box sx={{ marginTop: 2, display: 'flex', justifyContent: 'center' }}>
            <Pagination
              count={pageCount}
              page={page}
              onChange={handlePageChange}
              color="primary"
            />
          </Box>
        </CardContent>
      </MuiCard>
      
      <Snackbar
        open={snackbarOpen}
        autoHideDuration={3000}
        onClose={handleSnackbarClose}
        message={snackbarMessage}
      />
    </Container>
  );
};

export default CardDetailsPage;
