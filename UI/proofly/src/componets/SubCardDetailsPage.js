import React, { useEffect, useState } from 'react';
import { useLocation, useParams, useNavigate } from 'react-router-dom';
import {
  Container,
  Typography,
  Paper,
  Divider,
  List,
  ListItem,
  Box,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Checkbox,
  Button,
  Snackbar,
  Alert,
  IconButton,
} from '@mui/material';
import DownloadIcon from '@mui/icons-material/Download';
import DeleteIcon from '@mui/icons-material/Delete';
import ArrowBackIcon from '@mui/icons-material/ArrowBack';
import { API_BASE_URL } from './Config'; // Import the base URL

const SubCardDetailsPage = () => {
  const { subCardId } = useParams();
  const location = useLocation();
  const navigate = useNavigate(); // Initialize useNavigate hook
  const { title } = location.state || {};

  const [mainData, setMainData] = useState({ table_data: [], caution_sentences: [] });
  const [selectedTableIds, setSelectedTableIds] = useState([]);
  const [selectedCautionIds, setSelectedCautionIds] = useState([]);
  const [originalResponse, setOriginalResponse] = useState({}); // Store the original response
  const [isSaveDisabled, setIsSaveDisabled] = useState(true); // Disable Save button by default
  const [snackbarOpen, setSnackbarOpen] = useState(false);
  const [snackbarMessage, setSnackbarMessage] = useState('');
  const [snackbarSeverity, setSnackbarSeverity] = useState('success'); // "success" or "error"

  useEffect(() => {
    const fetchData = async () => {
      try {
        const response = await fetch(`${API_BASE_URL}/get_child_page_by_id/`, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({ ids: subCardId }),
        });

        const result = await response.json();
        setMainData(result.main_data);
        setOriginalResponse(result); // Save the original response
      } catch (error) {
        console.error('Error fetching data:', error);
      }
    };

    fetchData();
  }, [subCardId]);

  const handleSelectAllTable = (event) => {
    setSelectedTableIds(event.target.checked ? mainData.table_data.map((_, index) => index) : []);
    setIsSaveDisabled(false); // Enable Save button when changes are made
  };

  const handleSelectTableRow = (index) => (event) => {
    setSelectedTableIds((prevSelected) =>
      event.target.checked ? [...prevSelected, index] : prevSelected.filter((selectedId) => selectedId !== index)
    );
    setIsSaveDisabled(false); // Enable Save button when changes are made
  };

  const handleSelectCautionItem = (index) => (event) => {
    setSelectedCautionIds((prevSelected) =>
      event.target.checked ? [...prevSelected, index] : prevSelected.filter((selectedId) => selectedId !== index)
    );
    setIsSaveDisabled(false); // Enable Save button when changes are made
  };

  const handleDeleteSelected = () => {
    setMainData((prevMainData) => ({
      ...prevMainData,
      table_data: prevMainData.table_data.filter((_, index) => !selectedTableIds.includes(index)),
      caution_sentences: prevMainData.caution_sentences.filter((_, index) => !selectedCautionIds.includes(index)),
    }));
    setSelectedTableIds([]);
    setSelectedCautionIds([]);
    setIsSaveDisabled(false); // Enable Save button when changes are made
  };

  const handleDownloadWord = async () => {
    try {
      const response = await fetch(`${API_BASE_URL}/get_pdf_page/`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ ids: subCardId }),
      });

      if (response.ok) {
        const blob = await response.blob();
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `Document_${subCardId}.pdf`; // Set a filename for the download
        document.body.appendChild(a);
        a.click();
        a.remove();
      } else {
        setSnackbarMessage(`Failed to download PDF: ${response.statusText}`);
        setSnackbarSeverity('error');
        setSnackbarOpen(true);
      }
    } catch (error) {
      setSnackbarMessage(`Error downloading PDF: ${error.message}`);
      setSnackbarSeverity('error');
      setSnackbarOpen(true);
    }
  };

  const handleSave = async () => {
    setIsSaveDisabled(true); // Disable Save button until further changes
    const requestBody = {
      ...originalResponse, // Use the original response data
      main_data: mainData, // Update with the modified main_data
    };

    try {
      console.log('Request body before sending:', requestBody); // Check the data here
      const response = await fetch(`${API_BASE_URL}/update_table_data/`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(requestBody),
      });

      if (response.ok) {
        setSnackbarMessage('Data successfully saved!');
        setSnackbarSeverity('success');
      } else {
        setSnackbarMessage(`Failed to save data: ${response.statusText}`);
        setSnackbarSeverity('error');
      }
    } catch (error) {
      setSnackbarMessage(`Error saving data: ${error.message}`);
      setSnackbarSeverity('error');
    } finally {
      setSnackbarOpen(true); // Show the snackbar with the message
    }
  };

  const handleSnackbarClose = () => {
    setSnackbarOpen(false);
  };

  const handleBackClick = () => {
    navigate(-1); // Navigate back to the previous page
  };

  return (
    <Container>
      <Paper elevation={3} sx={{ padding: 3, marginBottom: 3 }}>
        <Box sx={{ display: 'flex', alignItems: 'center', marginBottom: 2 }}>
          <IconButton onClick={handleBackClick} sx={{ marginRight: 2 }}>
            <ArrowBackIcon />
          </IconButton>
          <Typography variant="h4" component="div" gutterBottom>
            {title} Details
          </Typography>
        </Box>
        <Divider sx={{ marginY: 2 }} />

        <Typography variant="h6" component="div" gutterBottom>
          Data Table
        </Typography>

        <TableContainer component={Paper} sx={{ marginBottom: 3 }}>
          <Table>
            <TableHead>
              <TableRow>
                <TableCell>
                  <Checkbox
                    checked={selectedTableIds.length === mainData.table_data.length}
                    onChange={handleSelectAllTable}
                  />
                </TableCell>
                <TableCell>Original Content</TableCell>
                <TableCell>Highlighted</TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {mainData.table_data.map((data, index) => (
                <TableRow key={index}>
                  <TableCell>
                    <Checkbox
                      checked={selectedTableIds.includes(index)}
                      onChange={handleSelectTableRow(index)}
                    />
                  </TableCell>
                  <TableCell>{data.originalContent}</TableCell>
                  <TableCell dangerouslySetInnerHTML={{ __html: data.highlighted }} />
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </TableContainer>

        <Typography variant="h6" component="div" gutterBottom sx={{ marginTop: 3 }}>
          Caution Sentences
        </Typography>
        <List>
          {mainData.caution_sentences.map((sentence, index) => (
            <ListItem key={index}>
              <Checkbox
                checked={selectedCautionIds.includes(index)}
                onChange={handleSelectCautionItem(index)}
              />
              <Typography component="div" variant="body1" sx={{ marginLeft: 1 }}>
                <li dangerouslySetInnerHTML={{ __html: sentence }} />
              </Typography>
            </ListItem>
          ))}
        </List>

        <Box sx={{ display: 'flex', justifyContent: 'space-between', marginTop: 2 }}>
          <Button
            variant="contained"
            color="error"
            startIcon={<DeleteIcon />}
            onClick={handleDeleteSelected}
            disabled={selectedTableIds.length === 0 && selectedCautionIds.length === 0}
          >
            Delete Selected
          </Button>
          <Button
            variant="contained"
            color="success"
            startIcon={<DownloadIcon />}
            onClick={handleDownloadWord}
          >
            Download as Word
          </Button>
        </Box>

        <Button
          variant="contained"
          color="primary"
          onClick={handleSave}
          disabled={isSaveDisabled} // Disable the Save button if no changes were made
          sx={{
            marginTop: 3,
            width: '100%',
          }}
        >
          Save
        </Button>
      </Paper>

      {/* Snackbar for feedback */}
      <Snackbar
        open={snackbarOpen}
        autoHideDuration={6000}
        onClose={handleSnackbarClose}
      >
        <Alert onClose={handleSnackbarClose} severity={snackbarSeverity} sx={{ width: '100%' }}>
          {snackbarMessage}
        </Alert>
      </Snackbar>
    </Container>
  );
};

export default SubCardDetailsPage;
