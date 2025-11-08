import { AutomationModel } from '../models/automation.model';
import { ZodError } from 'zod';
import { AutomationValidator } from '../validators/automation.validator';

export class AutomationService {
    async createDecision(data: any) {
        try {
            const validatedData = AutomationValidator.createDecisionSchema.parse(data);
            const decision = await AutomationModel.create(validatedData);
            return decision;
        } catch (error) {
            if (error instanceof ZodError) {
                throw new Error(`Validation Error: ${error.errors}`);
            }
            throw new Error('Error creating decision');
        }
    }

    async updateKPI(id: string, data: any) {
        try {
            const validatedData = AutomationValidator.updateKpiSchema.parse(data);
            const updatedKPI = await AutomationModel.findByIdAndUpdate(id, validatedData, { new: true });
            if (!updatedKPI) {
                throw new Error('KPI not found');
            }
            return updatedKPI;
        } catch (error) {
            if (error instanceof ZodError) {
                throw new Error(`Validation Error: ${error.errors}`);
            }
            throw new Error('Error updating KPI');
        }
    }

    async getRolloutPlans() {
        try {
            const plans = await AutomationModel.find({ type: 'rollout' });
            return plans;
        } catch (error) {
            throw new Error('Error fetching rollout plans');
        }
    }
}