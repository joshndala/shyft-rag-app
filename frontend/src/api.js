import axios from "axios";

export const BASE_URL = "http://127.0.0.1:8000"; // Backend URL

// Upload document
export const uploadFile = async (file) => {
    const formData = new FormData();
    formData.append("file", file);
    return axios.post(`${BASE_URL}/upload/`, formData, {
        headers: { "Content-Type": "multipart/form-data" },
    });
};

// Search for documents
export const searchQuery = async (query, options = {}) => {
    const { topK = 5, semanticWeight = 0.7, keywordWeight = 0.3 } = options;
    
    return axios.get(`${BASE_URL}/search/`, { 
        params: { 
            query,
            top_k: topK,
            semantic_weight: semanticWeight,
            keyword_weight: keywordWeight
        } 
    });
};

// Ask AI a question (non-streaming)
export const askAI = async (query, options = {}) => {
    const { stream = false } = options;
    
    return axios.get(`${BASE_URL}/ask/`, { 
        params: { 
            query,
            stream 
        } 
    });
};

// Helper method to create event source URL for streaming
export const createAskStreamUrl = (query) => {
    const encodedQuery = encodeURIComponent(query);
    return `${BASE_URL}/ask/?query=${encodedQuery}&stream=true`;
};