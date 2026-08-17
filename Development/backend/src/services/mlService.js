const axios = require('axios');

const client = axios.create({
  baseURL: process.env.ML_SERVICE_URL || 'http://localhost:8000',
  timeout: 5000,
});

// Predicts a category for a single transaction description/merchant/amount.
async function categorizeTransaction({ description, merchant, amount }) {
  const { data } = await client.post('/predict/category', {
    description: description || '',
    merchant: merchant || '',
    amount: Number(amount),
  });
  return data; // { category, confidence }
}

// Forecasts next-period spending from a user's historical monthly totals.
async function forecastSpending(history) {
  // history: [{ month: 'YYYY-MM', total: number }, ...] sorted ascending by month
  const { data } = await client.post('/predict/forecast', { history });
  return data; // { nextMonthTotal, trend }
}

module.exports = { categorizeTransaction, forecastSpending };
