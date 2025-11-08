import axios, { AxiosRequestConfig } from 'axios';

export const httpClient = axios.create({
    baseURL: process.env.BASE_URL || 'http://localhost:3000',
    timeout: 10000,
});

export const get = async (url: string, config?: AxiosRequestConfig) => {
    try {
        const response = await httpClient.get(url, config);
        return response.data;
    } catch (error) {
        throw error;
    }
};

export const post = async (url: string, data: any, config?: AxiosRequestConfig) => {
    try {
        const response = await httpClient.post(url, data, config);
        return response.data;
    } catch (error) {
        throw error;
    }
};

export const put = async (url: string, data: any, config?: AxiosRequestConfig) => {
    try {
        const response = await httpClient.put(url, data, config);
        return response.data;
    } catch (error) {
        throw error;
    }
};

export const del = async (url: string, config?: AxiosRequestConfig) => {
    try {
        const response = await httpClient.delete(url, config);
        return response.data;
    } catch (error) {
        throw error;
    }
};