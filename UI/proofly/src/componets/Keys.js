import React, { useState, useEffect } from 'react';
import { Button, TextField, CircularProgress, Grid, Typography, Container, Box } from '@mui/material';
import { ToastContainer, toast } from 'react-toastify';
import 'react-toastify/dist/ReactToastify.css';
import { API_BASE_URL } from './Config'; // Import the base URL
import './searchPage.css';

const KeysPage = () => {
  const [keys, setKeys] = useState({
    OPENAI_API_KEY: '',
    FIRECRAWL_API_KEY: ''
  });
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    const fetchKeys = async () => {
      setLoading(true);
      try {
        const response = await fetch(`${API_BASE_URL}/get_keys/`);
        const data = await response.json();
        const apiKeys = data.resp[0]; // Access the first object in the "resp" array

        // Extracting and setting the keys
        setKeys({
          OPENAI_API_KEY: apiKeys.OPENAI_API_KEY || '',
          FIRECRAWL_API_KEY: apiKeys.FIRECRAWL_API_KEY || ''
        });

        setLoading(false);
      } catch (error) {
        toast.error('Failed to fetch keys');
        setLoading(false);
      }
    };

    fetchKeys();
  }, []);

  return (
    <Container maxWidth="md">
      <ToastContainer />
      <Typography variant="h4" gutterBottom>
        API Keys
      </Typography>

      {loading ? (
        <Box display="flex" justifyContent="center" alignItems="center" minHeight="200px">
          <CircularProgress />
        </Box>
      ) : (
        <Grid container spacing={3}>
          <Grid item xs={12} sm={6}>
            <TextField
              label="OpenAI API Key"
              value={keys.OPENAI_API_KEY}
              fullWidth
              variant="outlined"
            />
          </Grid>
          <Grid item xs={12} sm={6}>
            <TextField
              label="Firecrawl API Key"
              value={keys.FIRECRAWL_API_KEY}
              fullWidth
              variant="outlined"
            />
          </Grid>
        </Grid>
      )}

      <Box mt={4}>
        <Button variant="contained" color="primary" fullWidth onClick={() => toast.info('Save button clicked!')}>
          Save
        </Button>
      </Box>
    </Container>
  );
};

export default KeysPage;
