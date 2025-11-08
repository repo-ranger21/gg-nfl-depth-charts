import pino from 'pino';

const logger = pino({
  level: process.env.LOG_LEVEL || 'info',
  transport: {
    target: 'pino-pretty',
    options: {
      colorize: true,
      translateTime: 'SYS:standard',
      ignore: 'pid,hostname',
    },
  },
});

// Middleware for logging requests
export const requestLogger = (req, res, next) => {
  logger.info({ method: req.method, url: req.url, body: req.body }, 'Incoming request');
  next();
};

// Middleware for logging errors
export const errorLogger = (err, req, res, next) => {
  logger.error({ err, method: req.method, url: req.url }, 'Error occurred');
  next(err);
};

export default logger;