import { z } from 'zod';
import dotenv from 'dotenv';

dotenv.config();

const envSchema = z.object({
  PORT: z.string().default('3000'),
  MONGODB_URI: z.string().url(),
  GG_API_KEY: z.string(),
});

const env = envSchema.parse(process.env);

export const config = {
  port: env.PORT,
  mongodbUri: env.MONGODB_URI,
  apiKey: env.GG_API_KEY,
};