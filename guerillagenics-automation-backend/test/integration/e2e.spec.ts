import request from 'supertest';
import app from '../../src/app'; // Adjust the path if necessary

describe('E2E Tests', () => {
  it('should return health status', async () => {
    const response = await request(app).get('/healthz');
    expect(response.status).toBe(200);
    expect(response.body).toEqual({ status: 'ok' });
  });

  // Add more end-to-end tests as needed
});