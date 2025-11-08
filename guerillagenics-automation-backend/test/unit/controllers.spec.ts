import request from 'supertest';
import { app } from '../../src/app'; // Adjust the import based on your app's structure
import HealthController from '../../src/controllers/health.controller';

describe('HealthController', () => {
  let healthController: HealthController;

  beforeAll(() => {
    healthController = new HealthController();
  });

  it('should return 200 for GET /healthz', async () => {
    const response = await request(app).get('/healthz');
    expect(response.status).toBe(200);
    expect(response.body).toEqual({ status: 'ok' });
  });
});