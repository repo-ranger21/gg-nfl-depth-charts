import request from 'supertest';
import { app } from '../../src/app';
import { AutomationController } from '../../src/controllers/automation.controller';

describe('Automation Controller', () => {
  beforeEach(() => {
    jest.clearAllMocks();
  });

  describe('POST /api/automation/decision', () => {
    it('should return 200 and the decision result', async () => {
      const mockDecision = { decision: 'approve' };
      jest.spyOn(AutomationController, 'makeDecision').mockResolvedValue(mockDecision);

      const response = await request(app)
        .post('/api/automation/decision')
        .send({ input: 'test input' });

      expect(response.status).toBe(200);
      expect(response.body).toEqual(mockDecision);
    });

    it('should return 400 if input is invalid', async () => {
      const response = await request(app)
        .post('/api/automation/decision')
        .send({ invalidInput: 'test' });

      expect(response.status).toBe(400);
      expect(response.body).toHaveProperty('error');
    });
  });

  describe('POST /api/automation/kpi', () => {
    it('should return 200 and update KPI', async () => {
      const mockKPIUpdate = { success: true };
      jest.spyOn(AutomationController, 'updateKPI').mockResolvedValue(mockKPIUpdate);

      const response = await request(app)
        .post('/api/automation/kpi')
        .send({ kpiData: 'data' });

      expect(response.status).toBe(200);
      expect(response.body).toEqual(mockKPIUpdate);
    });

    it('should return 400 if KPI data is invalid', async () => {
      const response = await request(app)
        .post('/api/automation/kpi')
        .send({ invalidKPI: 'data' });

      expect(response.status).toBe(400);
      expect(response.body).toHaveProperty('error');
    });
  });

  describe('POST /api/automation/rollout', () => {
    it('should return 200 and the rollout plan', async () => {
      const mockRolloutPlan = { plan: 'rollout plan' };
      jest.spyOn(AutomationController, 'createRolloutPlan').mockResolvedValue(mockRolloutPlan);

      const response = await request(app)
        .post('/api/automation/rollout')
        .send({ rolloutData: 'data' });

      expect(response.status).toBe(200);
      expect(response.body).toEqual(mockRolloutPlan);
    });

    it('should return 400 if rollout data is invalid', async () => {
      const response = await request(app)
        .post('/api/automation/rollout')
        .send({ invalidRollout: 'data' });

      expect(response.status).toBe(400);
      expect(response.body).toHaveProperty('error');
    });
  });
});