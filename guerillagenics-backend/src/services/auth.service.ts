import { Request, Response } from 'express';
import jwt from 'jsonwebtoken';
import { User } from '../models/user.model';
import { AuthPayload } from '../types/index';
import { env } from '../config/env';

export class AuthService {
    static async verifyToken(token: string): Promise<AuthPayload | null> {
        try {
            const decoded = jwt.verify(token, env.JWT_SECRET) as AuthPayload;
            return decoded;
        } catch (error) {
            return null;
        }
    }

    static async authenticateUser(username: string, password: string): Promise<User | null> {
        const user = await User.findOne({ username });
        if (user && user.comparePassword(password)) {
            return user;
        }
        return null;
    }

    static generateToken(user: User): string {
        const payload: AuthPayload = {
            id: user._id,
            username: user.username,
        };
        return jwt.sign(payload, env.JWT_SECRET, { expiresIn: '1h' });
    }
}