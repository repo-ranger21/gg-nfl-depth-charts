import { Request, Response, NextFunction } from 'express';
import { ZodError } from 'zod';

const errorHandler = (err: any, req: Request, res: Response, next: NextFunction) => {
    if (err instanceof ZodError) {
        return res.status(400).json({
            status: 'error',
            message: 'Validation error',
            errors: err.errors,
        });
    }

    console.error(err); // Log the error for debugging

    return res.status(500).json({
        status: 'error',
        message: 'Internal server error',
    });
};

export default errorHandler;