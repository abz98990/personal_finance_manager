const { fn, col, literal } = require('sequelize');
const { Transaction } = require('../models');
const { categorizeTransaction, forecastSpending } = require('../services/mlService');

// One-off category prediction, used by the "add transaction" screen before saving.
async function predictCategory(req, res, next) {
  try {
    const { description, merchant, amount } = req.body;
    if (amount === undefined) return res.status(400).json({ error: 'amount is required' });

    const prediction = await categorizeTransaction({ description, merchant, amount });
    res.json(prediction);
  } catch (err) {
    if (err.code === 'ECONNREFUSED' || err.code === 'ECONNABORTED') {
      return res.status(503).json({ error: 'ML service is unavailable' });
    }
    next(err);
  }
}

// Forecasts next month's total expense from this user's monthly history.
async function predictForecast(req, res, next) {
  try {
    const rows = await Transaction.findAll({
      attributes: [
        [fn('to_char', col('date'), 'YYYY-MM'), 'month'],
        [fn('SUM', col('amount')), 'total'],
      ],
      where: { userId: req.userId, type: 'expense' },
      group: [literal("to_char(date, 'YYYY-MM')")],
      order: [[literal("to_char(date, 'YYYY-MM')"), 'ASC']],
      raw: true,
    });

    const history = rows.map((r) => ({ month: r.month, total: Number(r.total) }));
    if (history.length < 2) {
      return res.status(422).json({ error: 'Not enough transaction history to forecast (need at least 2 months)' });
    }

    const forecast = await forecastSpending(history);
    res.json({ history, ...forecast });
  } catch (err) {
    if (err.code === 'ECONNREFUSED' || err.code === 'ECONNABORTED') {
      return res.status(503).json({ error: 'ML service is unavailable' });
    }
    next(err);
  }
}

module.exports = { predictCategory, predictForecast };
