const axios = require('axios');

const client = axios.create({
  baseURL: process.env.ML_SERVICE_URL || 'http://localhost:8000',
  timeout: 5000,
});

async function categorizeTransaction({ description, merchant, amount }) {
  const { data } = await client.post('/predict/category', {
    description: description || '',
    merchant: merchant || '',
    amount: Number(amount),
  });
  return data; // { category, confidence }
}

// history: [{ month: 'YYYY-MM', total: number }, ...] ascending by month
async function forecastSpending(history) {
  const { data } = await client.post('/predict/forecast', { history });
  return data; // { nextMonthTotal, trend }
}

module.exports = { categorizeTransaction, forecastSpending };
