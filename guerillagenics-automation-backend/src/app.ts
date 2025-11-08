import express from 'express';
import helmet from 'helmet';
import cors from 'cors';
import rateLimit from 'express-rate-limit';
import { setRoutes } from './routes';
import { errorMiddleware } from './middlewares/error.middleware';
import { logger } from './utils/logger';

const app = express();

// Middleware for security
app.use(helmet());
app.use(cors());

// Middleware for logging
app.use((req, res, next) => {
    logger.info(`${req.method} ${req.url}`);
    next();
});

// Rate limiting
const limiter = rateLimit({
    windowMs: 15 * 60 * 1000, // 15 minutes
    max: 100, // limit each IP to 100 requests per windowMs
});
app.use(limiter);

// Parse JSON bodies
app.use(express.json());

// Set up routes
setRoutes(app);

// Error handling middleware
app.use(errorMiddleware);

export default app;