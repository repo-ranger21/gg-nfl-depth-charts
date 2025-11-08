import express from 'express';
import cors from 'cors';
import helmet from 'helmet';
import rateLimit from 'express-rate-limit';
import { json } from 'body-parser';
import { authMiddleware } from './middleware/auth.middleware';
import { errorMiddleware } from './middleware/error.middleware';
import { logger } from './utils/logger';
import routes from './routes';

const app = express();

// Middleware setup
app.use(cors());
app.use(helmet());
app.use(json());
app.use(rateLimit({
    windowMs: 15 * 60 * 1000, // 15 minutes
    max: 100 // limit each IP to 100 requests per windowMs
}));
app.use(logger);

// Authentication middleware for API routes
app.use('/api/*', authMiddleware);

// Routes
app.use('/api', routes);

// Error handling middleware
app.use(errorMiddleware);

export default app;