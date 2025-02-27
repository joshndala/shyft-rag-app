import React, { useState, useEffect, useRef } from "react";
import { 
  TextField, 
  Button, 
  Typography, 
  Box, 
  Paper, 
  CircularProgress,
  IconButton
} from "@mui/material";
import SendIcon from '@mui/icons-material/Send';
import { askAI, createAskStreamUrl } from "../api";

const ChatPage = () => {
  const [query, setQuery] = useState("");
  const [response, setResponse] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const eventSourceRef = useRef(null);
  const responseEndRef = useRef(null);

  // Function to scroll to bottom of response
  const scrollToBottom = () => {
    responseEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  // Effect to scroll when response updates
  useEffect(() => {
    scrollToBottom();
  }, [response]);

  // Clean up event source on unmount
  useEffect(() => {
    return () => {
      if (eventSourceRef.current) {
        eventSourceRef.current.close();
      }
    };
  }, []);

  const handleAsk = async () => {
    if (!query.trim()) return;
    
    // Reset states
    setLoading(true);
    setResponse("");
    setError("");
    
    // Close existing connection if any
    if (eventSourceRef.current) {
      eventSourceRef.current.close();
    }
    
    try {
      // Create new event source using the helper function
      const streamUrl = createAskStreamUrl(query);
      console.log("Connecting to stream URL:", streamUrl);
      eventSourceRef.current = new EventSource(streamUrl);
      
      // Handle incoming messages
      eventSourceRef.current.onmessage = (event) => {
        try {
          const data = JSON.parse(event.data);
          console.log("Received data:", data);
          
          // Handle end of stream
          if (data.end) {
            console.log("Stream ended");
            eventSourceRef.current.close();
            setLoading(false);
            return;
          }
          
          // Handle errors
          if (data.error) {
            setError(data.error);
            eventSourceRef.current.close();
            setLoading(false);
            return;
          }
          
          // Append content
          if (data.content) {
            setResponse(prev => prev + data.content);
          }
        } catch (err) {
          console.error('Error parsing stream data:', err);
        }
      };
      
      // Handle connection errors
      eventSourceRef.current.onerror = (err) => {
        console.error('EventSource error:', err);
        setError("Connection error. Please try again.");
        eventSourceRef.current.close();
        setLoading(false);
      };
      
    } catch (err) {
      console.error("Connection setup error:", err);
      setError("Failed to connect to the server.");
      setLoading(false);
    }
  };

  // Handle Enter key press
  const handleKeyPress = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleAsk();
    }
  };

  return (
    <Box sx={{ maxWidth: 800, mx: "auto", p: 3 }}>
      <Typography variant="h4" gutterBottom>Ask AI</Typography>
      
      {/* Question input area */}
      <Box sx={{ mb: 3 }}>
        <TextField
          fullWidth
          label="Ask a question about your documents"
          variant="outlined"
          multiline
          rows={3}
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          onKeyPress={handleKeyPress}
          disabled={loading}
        />
        <Box sx={{ display: 'flex', justifyContent: 'flex-end', mt: 1 }}>
          <Button 
            variant="contained" 
            onClick={handleAsk}
            disabled={loading || !query.trim()}
            endIcon={<SendIcon />}
          >
            {loading ? "Processing..." : "Ask"}
          </Button>
        </Box>
      </Box>
      
      {/* Loading indicator */}
      {loading && (
        <Box sx={{ display: 'flex', justifyContent: 'center', my: 2 }}>
          <CircularProgress size={24} sx={{ mr: 1 }} />
          <Typography>Generating response...</Typography>
        </Box>
      )}
      
      {/* Error message */}
      {error && (
        <Paper 
          elevation={1} 
          sx={{ p: 2, mb: 3, bgcolor: '#ffebee' }}
        >
          <Typography color="error">{error}</Typography>
        </Paper>
      )}
      
      {/* Response area */}
      {response && (
        <Paper elevation={2} sx={{ p: 3, mt: 2, bgcolor: '#f5f5f5', minHeight: '200px' }}>
          <Typography 
            sx={{ 
              whiteSpace: 'pre-wrap',
              '& a': { color: 'primary.main' }
            }}
          >
            {response}
          </Typography>
          <div ref={responseEndRef} />
        </Paper>
      )}
    </Box>
  );
};

export default ChatPage;