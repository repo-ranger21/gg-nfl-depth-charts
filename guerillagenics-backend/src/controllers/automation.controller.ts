import { Request, Response } from 'express';
import { AutomationService } from '../services/automation.service';
import { validateAutomationInput } from '../validators/automation.validator';

export class AutomationController {
    private automationService: AutomationService;

    constructor() {
        this.automationService = new AutomationService();
    }

    public async createDecision(req: Request, res: Response): Promise<void> {
        try {
            const validatedInput = validateAutomationInput(req.body);
            const decision = await this.automationService.createDecision(validatedInput);
            res.status(201).json(decision);
        } catch (error) {
            res.status(400).json({ error: error.message });
        }
    }

    public async updateKPI(req: Request, res: Response): Promise<void> {
        try {
            const { id } = req.params;
            const validatedInput = validateAutomationInput(req.body);
            const updatedKPI = await this.automationService.updateKPI(id, validatedInput);
            res.status(200).json(updatedKPI);
        } catch (error) {
            res.status(400).json({ error: error.message });
        }
    }

    public async rolloutPlan(req: Request, res: Response): Promise<void> {
        try {
            const validatedInput = validateAutomationInput(req.body);
            const rollout = await this.automationService.rolloutPlan(validatedInput);
            res.status(200).json(rollout);
        } catch (error) {
            res.status(400).json({ error: error.message });
        }
    }
}