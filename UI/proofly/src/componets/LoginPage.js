import React, { useState } from 'react';
import { Button, TextField, Box, Typography, Container, Alert } from '@mui/material';
import { API_BASE_URL } from './Config'; // Import the base URL

function LoginPage({ onLogin }) {
  const [password, setPassword] = useState('');
  const [errorMessage, setErrorMessage] = useState('');

  const handleSubmit = async (e) => {
    e.preventDefault();
    console.log('passwor dis',password)
    try {
      const response = await fetch(`${API_BASE_URL}/auth_xyz/`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ passkey: password }),
        
      });


      if (response.ok) {
        const data = await response.json();
        if (data.key === 'd1g1max') {
          onLogin();
          sessionStorage.setItem('isLoggedIn', 'true');
        } else {
          setErrorMessage('Incorrect password. Please try again.');
        }
      } else {
        setErrorMessage('An error occurred. Please try again.');
      }
    } catch (error) {
      setErrorMessage('An error occurred. Please try again.');
    }
  };

  return (
    <Container component="main" maxWidth="xs">
      <Box
        sx={{
          marginTop: 8,
          display: 'flex',
          flexDirection: 'column',
          alignItems: 'center',
        }}
      >
        <Typography component="h1" variant="h5">
          Login
        </Typography>
        <Box component="form" onSubmit={handleSubmit} sx={{ mt: 1 }}>
          <TextField
            variant="outlined"
            margin="normal"
            required
            fullWidth
            name="password"
            label="Password"
            type="password"
            id="password"
            autoComplete="current-password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
          />
          {errorMessage && (
            <Alert severity="error" sx={{ mt: 2 }}>
              {errorMessage}
            </Alert>
          )}
          <Button
            type="submit"
            fullWidth
            variant="contained"
            sx={{ mt: 3, mb: 2 }}
          >
            Login
          </Button>
        </Box>
      </Box>
    </Container>
  );
}

export default LoginPage;
