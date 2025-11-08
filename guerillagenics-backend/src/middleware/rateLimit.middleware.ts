import { Request, Response, NextFunction } from 'express';
import rateLimit from 'express-rate-limit';

const createRateLimiter = (windowMs: number, max: number) => {
    return rateLimit({
        windowMs, // Time window in milliseconds
        max, // Limit each IP to max requests per windowMs
        message: {
            status: 429,
            error: 'Too many requests, please try again later.',
        },
    });
};

export default createRateLimiter;