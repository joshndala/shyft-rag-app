import React from "react";
import { BrowserRouter as Router, Routes, Route, Link } from "react-router-dom";
import { AppBar, Toolbar, Button, Container } from "@mui/material";
import UploadPage from "./pages/UploadPage";
import SearchPage from "./pages/SearchPage";
import ChatPage from "./pages/ChatPage";

const App = () => {
    return (
        <Router>
            <AppBar position="static">
                <Toolbar>
                    <Button color="inherit" component={Link} to="/">Upload</Button>
                    <Button color="inherit" component={Link} to="/search">Search</Button>
                    <Button color="inherit" component={Link} to="/chat">Chat</Button>
                </Toolbar>
            </AppBar>
            <Container>
                <Routes>
                    <Route path="/" element={<UploadPage />} />
                    <Route path="/search" element={<SearchPage />} />
                    <Route path="/chat" element={<ChatPage />} />
                </Routes>
            </Container>
        </Router>
    );
};

export default App;