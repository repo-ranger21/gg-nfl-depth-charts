import { Router } from 'express';
import { createDecision, updateKPI, rolloutPlan } from '../controllers/automation.controller';
import { validateDecision, validateKPIUpdate, validateRolloutPlan } from '../validators/automation.validator';
import { authMiddleware } from '../middleware/auth.middleware';
import { validateMiddleware } from '../middleware/validate.middleware';

const router = Router();

// POST endpoint for creating a decision
router.post('/decisions', authMiddleware, validateMiddleware(validateDecision), createDecision);

// POST endpoint for updating KPIs
router.post('/kpis', authMiddleware, validateMiddleware(validateKPIUpdate), updateKPI);

// POST endpoint for rollout plans
router.post('/rollout', authMiddleware, validateMiddleware(validateRolloutPlan), rolloutPlan);

export default router;