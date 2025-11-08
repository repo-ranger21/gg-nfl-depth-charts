import { Request, Response, NextFunction } from 'express';
import { ZodError } from 'zod';

export const validateMiddleware = (schema: any) => {
    return (req: Request, res: Response, next: NextFunction) => {
        try {
            schema.parse(req.body);
            next();
        } catch (error) {
            if (error instanceof ZodError) {
                return res.status(400).json({
                    status: 'error',
                    message: 'Validation failed',
                    errors: error.errors,
                });
            }
            next(error);
        }
    };
};