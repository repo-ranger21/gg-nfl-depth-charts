import axios, { AxiosRequestConfig, AxiosResponse } from 'axios';

const httpClient = axios.create({
    baseURL: process.env.API_BASE_URL, // Set your base URL from environment variables
    timeout: 10000, // Set a timeout for requests
    headers: {
        'Content-Type': 'application/json',
    },
});

// Interceptor for handling responses
httpClient.interceptors.response.use(
    (response: AxiosResponse) => {
        return response.data; // Return only the data from the response
    },
    (error) => {
        // Handle errors globally
        return Promise.reject(error.response ? error.response.data : error.message);
    }
);

// Function to make GET requests
export const get = async (url: string, config?: AxiosRequestConfig) => {
    return await httpClient.get(url, config);
};

// Function to make POST requests
export const post = async (url: string, data: any, config?: AxiosRequestConfig) => {
    return await httpClient.post(url, data, config);
};

// Function to make PUT requests
export const put = async (url: string, data: any, config?: AxiosRequestConfig) => {
    return await httpClient.put(url, data, config);
};

// Function to make DELETE requests
export const del = async (url: string, config?: AxiosRequestConfig) => {
    return await httpClient.delete(url, config);
};