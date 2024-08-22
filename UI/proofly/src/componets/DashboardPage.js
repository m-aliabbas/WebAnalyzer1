import React, { useState, useEffect } from 'react';
import { Container, Typography, Grid, Pagination, Box, Paper } from '@mui/material';
import axios from 'axios';
import Card from './Card'; // Assuming Card component is in the same directory
import { API_BASE_URL } from './Config'; // Import the base URL

const DashboardPage = () => {
  const [cards, setCards] = useState([]);
  const [page, setPage] = useState(1);
  const cardsPerPage = 10;

  useEffect(() => {
    const fetchCards = async () => {
      try {
        const response = await axios.get(`${API_BASE_URL}/get-parent-docs/`);
        const fetchedCards = response.data.map(card => ({
          id: card.id,
          title: card.url,
          progress: card.status,
          tags: card.tags, // Display tags as chips
          halt_status: card.halt_status
        }));
        
        setCards(fetchedCards);
      } catch (error) {
        console.error("Error fetching cards:", error);
      }
    };
    fetchCards();
  }, []);

  const pageCount = Math.ceil(cards.length / cardsPerPage);

  const handlePageChange = (event, value) => {
    setPage(value);
  };

  const displayCards = cards.slice((page - 1) * cardsPerPage, page * cardsPerPage);

  return (
    <Container>
      <Paper elevation={3} sx={{ padding: 3, backgroundColor: '#f5f5f5' }}>
        <Typography variant="h4" component="h1" gutterBottom>
          Dashboard Page
        </Typography>
        <Typography variant="body1" gutterBottom>
          This is the dashboard page content.
        </Typography>
        <Grid container spacing={2}>
          {displayCards.map((card) => (
            <Grid item xs={12} key={card.id}>
              <Card id={card.id} title={card.title} progress={card.progress} tags={card.tags} halt_status={card.halt_status} />
            </Grid>
          ))}
        </Grid>
        <Box sx={{ marginTop: 2, display: 'flex', justifyContent: 'center' }}>
          <Pagination
            count={pageCount}
            page={page}
            onChange={handlePageChange}
            color="primary"
          />
        </Box>
      </Paper>
    </Container>
  );
};

export default DashboardPage;
