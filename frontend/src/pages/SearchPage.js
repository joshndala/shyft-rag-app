import React, { useState } from "react";
import { searchQuery } from "../api";
import { 
  TextField, 
  Button, 
  Typography, 
  Box, 
  List, 
  Paper, 
  Divider,
  CircularProgress,
  IconButton,
  Card,
  CardContent
} from "@mui/material";
import SearchIcon from '@mui/icons-material/Search';

const SearchPage = () => {
  const [query, setQuery] = useState("");
  const [results, setResults] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [searched, setSearched] = useState(false);

  const handleSearch = async () => {
    if (!query.trim()) return;
    
    setLoading(true);
    setResults([]);
    setError("");
    setSearched(true);

    try {
      const response = await searchQuery(query);
      console.log("API Response:", response.data); // Debugging
      
      if (response.data && response.data.results) {
        setResults(response.data.results);
      } else {
        setResults([]);
      }
    } catch (error) {
      console.error("Error searching:", error);
      setError(error.response?.data?.detail || "Error performing search.");
      setResults([]);
    } finally {
      setLoading(false);
    }
  };

  // Handle Enter key press
  const handleKeyPress = (e) => {
    if (e.key === 'Enter') {
      handleSearch();
    }
  };

  // Format the text for display - add highlighting and truncate if too long
  const formatText = (text) => {
    if (!text) return "";
    
    // Truncate long texts
    const maxLength = 300;
    let displayText = text;
    
    if (text.length > maxLength) {
      displayText = text.substring(0, maxLength) + "...";
    }
    
    return displayText;
  };

  return (
    <Box sx={{ maxWidth: 800, mx: "auto", p: 3 }}>
      <Typography variant="h4" gutterBottom>Search Documents</Typography>
      
      {/* Search input area */}
      <Box sx={{ display: "flex", mb: 3 }}>
        <TextField
          fullWidth
          label="Enter search query"
          variant="outlined"
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          onKeyPress={handleKeyPress}
          disabled={loading}
        />
        <Button 
          variant="contained" 
          onClick={handleSearch} 
          sx={{ ml: 1 }}
          disabled={loading || !query.trim()}
          endIcon={<SearchIcon />}
        >
          {loading ? <CircularProgress size={24} color="inherit" /> : "Search"}
        </Button>
      </Box>
      
      {/* Error message */}
      {error && (
        <Paper 
          elevation={1} 
          sx={{ p: 2, mb: 3, bgcolor: '#ffebee' }}
        >
          <Typography color="error">{error}</Typography>
        </Paper>
      )}
      
      {/* Results */}
      {loading ? (
        <Box sx={{ display: 'flex', justifyContent: 'center', my: 4 }}>
          <CircularProgress size={40} sx={{ mr: 2 }} />
          <Typography variant="h6">Searching...</Typography>
        </Box>
      ) : (
        <>
          {searched && (
            <Typography variant="h6" gutterBottom sx={{ mt: 3 }}>
              {results.length > 0 
                ? `Found ${results.length} results:` 
                : "No results found. Try a different search term."}
            </Typography>
          )}
          
          {results.length > 0 && (
            <List sx={{ mt: 2 }}>
              {results.map((result, index) => (
                <Card key={index} sx={{ mb: 2 }}>
                  <CardContent>
                    <Typography 
                      variant="body1" 
                      sx={{ 
                        whiteSpace: 'pre-wrap',
                        mb: 2
                      }}
                    >
                      {formatText(result.text)}
                    </Typography>
                    
                    <Divider sx={{ my: 1 }} />
                    
                    <Box sx={{ 
                      display: "flex", 
                      justifyContent: "space-between",
                      fontSize: "0.8rem", 
                      color: "text.secondary" 
                    }}>
                      <Typography variant="caption">
                        Score: {result.score ? result.score.toFixed(3) : "N/A"}
                      </Typography>
                      
                      {result.metadata && (
                        <Typography variant="caption">
                          Source: {result.metadata.document_id || 
                                   (result.metadata.filename ? 
                                    result.metadata.filename.split('_').pop() : 
                                    "Unknown")}
                        </Typography>
                      )}
                    </Box>
                  </CardContent>
                </Card>
              ))}
            </List>
          )}
        </>
      )}
    </Box>
  );
};

export default SearchPage;