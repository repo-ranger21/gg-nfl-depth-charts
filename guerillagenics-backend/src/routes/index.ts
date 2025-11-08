import { Router } from 'express';
import automationRoutes from './automation.routes';

const router = Router();

// Use automation routes
router.use('/automation', automationRoutes);

export default router;