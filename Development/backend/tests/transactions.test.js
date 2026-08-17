require('./setup');
const request = require('supertest');
const app = require('../src/app');
const { sequelize, Category } = require('../src/models');

let token;
let categoryId;

beforeAll(async () => {
  await sequelize.sync({ force: true });

  const category = await Category.create({ name: 'Groceries', type: 'expense', userId: null, isDefault: true });
  categoryId = category.id;

  const res = await request(app)
    .post('/api/auth/register')
    .send({ name: 'Budget Tester', email: 'budget@example.com', password: 'password123' });
  token = res.body.token;
});

afterAll(async () => {
  await sequelize.close();
});

describe('Transactions', () => {
  it('creates a manual transaction', async () => {
    const res = await request(app)
      .post('/api/transactions')
      .set('Authorization', `Bearer ${token}`)
      .send({ amount: 45.2, type: 'expense', merchant: 'Supermarket', categoryId, date: '2026-08-01' });

    expect(res.status).toBe(201);
    expect(res.body.transaction.amount).toBe('45.20');
    expect(res.body.transaction.source).toBe('manual');
  });

  it('rejects a transaction without an amount', async () => {
    const res = await request(app)
      .post('/api/transactions')
      .set('Authorization', `Bearer ${token}`)
      .send({ merchant: 'Supermarket' });
    expect(res.status).toBe(400);
  });

  it('lists only the authenticated user\'s transactions', async () => {
    const res = await request(app).get('/api/transactions').set('Authorization', `Bearer ${token}`);
    expect(res.status).toBe(200);
    expect(res.body.transactions.length).toBe(1);
  });

  it('updates a transaction', async () => {
    const list = await request(app).get('/api/transactions').set('Authorization', `Bearer ${token}`);
    const id = list.body.transactions[0].id;

    const res = await request(app)
      .put(`/api/transactions/${id}`)
      .set('Authorization', `Bearer ${token}`)
      .send({ amount: 50 });

    expect(res.status).toBe(200);
    expect(res.body.transaction.amount).toBe('50.00');
  });

  it('deletes a transaction', async () => {
    const list = await request(app).get('/api/transactions').set('Authorization', `Bearer ${token}`);
    const id = list.body.transactions[0].id;

    const res = await request(app).delete(`/api/transactions/${id}`).set('Authorization', `Bearer ${token}`);
    expect(res.status).toBe(204);

    const after = await request(app).get('/api/transactions').set('Authorization', `Bearer ${token}`);
    expect(after.body.transactions.length).toBe(0);
  });
});
