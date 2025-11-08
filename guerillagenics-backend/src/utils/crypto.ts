import crypto from 'crypto';

export const generateHash = (data: string): string => {
    return crypto.createHash('sha256').update(data).digest('hex');
};

export const verifyHash = (data: string, hash: string): boolean => {
    const computedHash = generateHash(data);
    return computedHash === hash;
};

export const generateRandomBytes = (size: number): string => {
    return crypto.randomBytes(size).toString('hex');
};