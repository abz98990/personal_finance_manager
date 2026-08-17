require('./setup');
const request = require('supertest');
const app = require('../src/app');
const { sequelize } = require('../src/models');

let token;

beforeAll(async () => {
  await sequelize.sync({ force: true });
  const res = await request(app)
    .post('/api/auth/register')
    .send({ name: 'Saver', email: 'saver@example.com', password: 'password123' });
  token = res.body.token;
});

afterAll(async () => {
  await sequelize.close();
});

describe('Savings Goals', () => {
  it('creates a goal', async () => {
    const res = await request(app)
      .post('/api/savings-goals')
      .set('Authorization', `Bearer ${token}`)
      .send({ title: 'Emergency Fund', targetAmount: 3000, savedAmount: 1200 });

    expect(res.status).toBe(201);
    expect(res.body.goal.title).toBe('Emergency Fund');
  });

  it('lists goals for the authenticated user', async () => {
    const res = await request(app).get('/api/savings-goals').set('Authorization', `Bearer ${token}`);
    expect(res.status).toBe(200);
    expect(res.body.goals.length).toBe(1);
  });

  it('updates saved amount toward a goal', async () => {
    const list = await request(app).get('/api/savings-goals').set('Authorization', `Bearer ${token}`);
    const id = list.body.goals[0].id;

    const res = await request(app)
      .put(`/api/savings-goals/${id}`)
      .set('Authorization', `Bearer ${token}`)
      .send({ savedAmount: 1500 });

    expect(res.status).toBe(200);
    expect(res.body.goal.savedAmount).toBe('1500.00');
  });
});
