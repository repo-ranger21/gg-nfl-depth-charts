import { z } from 'zod';

export const createAutomationSchema = z.object({
  name: z.string().min(1, 'Name is required'),
  description: z.string().optional(),
  parameters: z.object({
    threshold: z.number().min(0, 'Threshold must be a non-negative number'),
    frequency: z.enum(['daily', 'weekly', 'monthly'], {
      errorMap: () => ({ message: 'Frequency must be daily, weekly, or monthly' }),
    }),
  }),
});

export const updateKpiSchema = z.object({
  kpiId: z.string().uuid('Invalid KPI ID format'),
  value: z.number().min(0, 'Value must be a non-negative number'),
});

export const rolloutPlanSchema = z.object({
  planId: z.string().uuid('Invalid Plan ID format'),
  status: z.enum(['pending', 'in_progress', 'completed'], {
    errorMap: () => ({ message: 'Status must be pending, in_progress, or completed' }),
  }),
});