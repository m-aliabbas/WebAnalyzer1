import React, { useState, useEffect } from 'react';
import { Button, TextField, CircularProgress, Grid, Typography, Container, Box } from '@mui/material';
import { ToastContainer, toast } from 'react-toastify';
import 'react-toastify/dist/ReactToastify.css';
import { API_BASE_URL } from './Config'; // Import the base URL
import './searchPage.css';

const KeysPage = () => {
  const [keys, setKeys] = useState({
    OPENAI_API_KEY: '',
    FIRECRAWL_API_KEY: '',
    PASSWORD: ''
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
          FIRECRAWL_API_KEY: apiKeys.FIRECRAWL_API_KEY || '',
          PASSWORD: apiKeys.PASSWORD || ''
        });
        
        setLoading(false);
      } catch (error) {
        toast.error('Failed to fetch keys');
        setLoading(false);
      }
    };

    fetchKeys();
  }, []);

  const handleSave = async () => {
    setLoading(true);
    try {
      const response = await fetch(`${API_BASE_URL}/update_keys/`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          open_ai_key: keys.OPENAI_API_KEY,
          firecrawl_key: keys.FIRECRAWL_API_KEY,
          password: keys.PASSWORD
        }),
      });

      const result = await response.json();
      
      if (response.ok) {
        toast.success(result.message || 'Keys updated successfully');
      } else {
        toast.error(result.message || 'Failed to update keys');
      }
    } catch (error) {
      toast.error('Error updating keys');
    } finally {
      setLoading(false);
    }
  };

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
          <Grid item xs={12} sm={4}>
            <TextField
              label="OpenAI API Key"
              value={keys.OPENAI_API_KEY}
              onChange={(e) => setKeys({ ...keys, OPENAI_API_KEY: e.target.value })}
              fullWidth
              variant="outlined"
            />
          </Grid>
          <Grid item xs={12} sm={4}>
            <TextField
              label="Firecrawl API Key"
              value={keys.FIRECRAWL_API_KEY}
              onChange={(e) => setKeys({ ...keys, FIRECRAWL_API_KEY: e.target.value })}
              fullWidth
              variant="outlined"
            />
          </Grid>
          <Grid item xs={12} sm={4}>
            <TextField
              label="Password"
              value={keys.PASSWORD}
              onChange={(e) => setKeys({ ...keys, PASSWORD: e.target.value })}
              fullWidth
              variant="outlined"
            />
          </Grid>
        </Grid>

      )}

      <Box mt={4}>
        <Button
          variant="contained"
          color="primary"
          fullWidth
          onClick={handleSave}
          disabled={loading}
        >
          {loading ? <CircularProgress size={24} /> : 'Save'}
        </Button>
      </Box>
    </Container>
  );
};

export default KeysPage;
