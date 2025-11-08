import { Request, Response, NextFunction } from 'express';

export const authMiddleware = (req: Request, res: Response, next: NextFunction) => {
    const apiKey = req.headers['authorization'];

    if (!apiKey || apiKey !== `Bearer ${process.env.GG_API_KEY}`) {
        return res.status(401).json({ message: 'Unauthorized' });
    }

    next();
};