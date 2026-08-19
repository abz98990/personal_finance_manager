const { Op, fn, col, literal } = require('sequelize');
const { Budget, Category, Transaction } = require('../models');

async function list(req, res, next) {
  try {
    const { month } = req.query; // 'YYYY-MM'
    const where = { userId: req.userId };
    if (month) where.month = `${month}-01`;

    const budgets = await Budget.findAll({ where, include: [{ model: Category }] });

    // Spend is attached here so the client can draw progress bars without a second call.
    const withSpend = await Promise.all(
      budgets.map(async (budget) => {
        const monthStr = budget.month.toISOString ? budget.month.toISOString().slice(0, 7) : String(budget.month).slice(0, 7);
        const spentRow = await Transaction.findOne({
          attributes: [[fn('COALESCE', fn('SUM', col('amount')), 0), 'spent']],
          where: {
            userId: req.userId,
            categoryId: budget.categoryId,
            type: 'expense',
            date: {
              [Op.gte]: `${monthStr}-01`,
              [Op.lt]: literal(`'${monthStr}-01'::date + interval '1 month'`),
            },
          },
          raw: true,
        });
        return { ...budget.toJSON(), spent: Number(spentRow?.spent || 0) };
      })
    );

    res.json({ budgets: withSpend });
  } catch (err) {
    next(err);
  }
}

async function upsert(req, res, next) {
  try {
    const { categoryId, month, limitAmount } = req.body;
    if (!categoryId || !month || limitAmount === undefined) {
      return res.status(400).json({ error: 'categoryId, month (YYYY-MM) and limitAmount are required' });
    }

    const [budget] = await Budget.upsert(
      {
        userId: req.userId,
        categoryId,
        month: `${month}-01`,
        limitAmount,
      },
      { returning: true }
    );

    res.status(201).json({ budget });
  } catch (err) {
    next(err);
  }
}

async function remove(req, res, next) {
  try {
    const budget = await Budget.findOne({ where: { id: req.params.id, userId: req.userId } });
    if (!budget) return res.status(404).json({ error: 'Budget not found' });
    await budget.destroy();
    res.status(204).send();
  } catch (err) {
    next(err);
  }
}

module.exports = { list, upsert, remove };
