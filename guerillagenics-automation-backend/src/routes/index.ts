import { Router } from 'express';
import HealthController from '../controllers/health.controller';

const router = Router();
const healthController = new HealthController();

export const setRoutes = (app) => {
    app.use('/healthz', router);
    router.get('/', healthController.getHealth.bind(healthController));
    
    // Additional routes can be added here
};