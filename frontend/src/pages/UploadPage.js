import React, { useState } from "react";
import { uploadFile } from "../api";
import { Button, Typography, Box, CircularProgress } from "@mui/material";

const UploadPage = () => {
    const [file, setFile] = useState(null);
    const [loading, setLoading] = useState(false);
    const [message, setMessage] = useState("");

    const handleFileChange = (event) => {
        setFile(event.target.files[0]);
    };

    const handleUpload = async () => {
        if (!file) return alert("Please select a file to upload.");
        setLoading(true);
        setMessage("");

        try {
            const response = await uploadFile(file);
            setMessage(response.data.message);
        } catch (error) {
            setMessage("Error uploading file.");
        } finally {
            setLoading(false);
        }
    };

    return (
        <Box sx={{ textAlign: "center", mt: 5 }}>
            <Typography variant="h4">Upload Document</Typography>
            <input type="file" onChange={handleFileChange} />
            <Button variant="contained" onClick={handleUpload} sx={{ mt: 2 }}>
                Upload
            </Button>
            {loading && <CircularProgress sx={{ mt: 2 }} />}
            {message && <Typography sx={{ mt: 2 }}>{message}</Typography>}
        </Box>
    );
};

export default UploadPage;