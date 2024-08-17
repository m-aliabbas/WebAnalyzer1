import React, { useState } from 'react';
import { Container, Typography, Grid, Pagination } from '@mui/material';
import Card from './Card'; // Assuming Card component is in the same directory

const DashboardPage = () => {
  const cards = [
    { title: 'Card 1', progress: 'done', description: 'Description for card 1' },
    { title: 'Card 2', progress: 'in progress', description: 'Description for card 2' },
    { title: 'Card 3', progress: 'init', description: 'Description for card 3' },
    { title: 'Card 4', progress: 'done', description: 'Description for card 4' },
    { title: 'Card 5', progress: 'in progress', description: 'Description for card 5' },
    { title: 'Card 6', progress: 'done', description: 'Description for card 6' },
    { title: 'Card 7', progress: 'in progress', description: 'Description for card 7' },
    { title: 'Card 8', progress: 'init', description: 'Description for card 8' },
    { title: 'Card 9', progress: 'done', description: 'Description for card 9' },
    { title: 'Card 10', progress: 'in progress', description: 'Description for card 10' },
  ];

  const [page, setPage] = useState(1);
  const cardsPerPage = 5;
  const pageCount = Math.ceil(cards.length / cardsPerPage);

  const handlePageChange = (event, value) => {
    setPage(value);
  };

  const displayCards = cards.slice((page - 1) * cardsPerPage, page * cardsPerPage);

  return (
    <Container>
      <Typography variant="h4" component="h1" gutterBottom>
        Dashboard Page
      </Typography>
      <Typography variant="body1" gutterBottom>
        This is the dashboard page content.
      </Typography>
      <Grid container spacing={2}>
        {displayCards.map((card, index) => (
          <Grid item xs={12} key={index}>
            <Card title={card.title} progress={card.progress} description={card.description} />
          </Grid>
        ))}
      </Grid>
      <Pagination
        count={pageCount}
        page={page}
        onChange={handlePageChange}
        color="primary"
        sx={{ marginTop: 2, display: 'flex', justifyContent: 'center' }}
      />
    </Container>
  );
};

export default DashboardPage;
