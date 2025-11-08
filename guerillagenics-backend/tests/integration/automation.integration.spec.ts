import request from 'supertest';
import app from '../../src/app'; // Adjust the path as necessary

describe('Automation Integration Tests', () => {
  it('should create a new automation decision', async () => {
    const response = await request(app)
      .post('/api/automation/decision')
      .send({
        // Add the necessary fields for the decision creation
        name: 'Test Decision',
        criteria: 'Some criteria',
      })
      .set('Authorization', `Bearer ${process.env.GG_API_KEY}`); // Use the appropriate token

    expect(response.status).toBe(201);
    expect(response.body).toHaveProperty('id');
    expect(response.body.name).toBe('Test Decision');
  });

  it('should update an existing KPI', async () => {
    const response = await request(app)
      .put('/api/automation/kpi/1') // Replace with a valid KPI ID
      .send({
        value: 100,
      })
      .set('Authorization', `Bearer ${process.env.GG_API_KEY}`);

    expect(response.status).toBe(200);
    expect(response.body).toHaveProperty('value', 100);
  });

  it('should return 404 for non-existing route', async () => {
    const response = await request(app)
      .get('/api/non-existing-route')
      .set('Authorization', `Bearer ${process.env.GG_API_KEY}`);

    expect(response.status).toBe(404);
  });

  // Add more tests as necessary for other endpoints and behaviors
});