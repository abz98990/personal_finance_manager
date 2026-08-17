const { Op, fn, col, literal } = require('sequelize');
const { Transaction, Category } = require('../models');
const { categorizeTransaction } = require('../services/mlService');

async function list(req, res, next) {
  try {
    const { from, to, categoryId, type } = req.query;
    const where = { userId: req.userId };
    if (from || to) {
      where.date = {};
      if (from) where.date[Op.gte] = from;
      if (to) where.date[Op.lte] = to;
    }
    if (categoryId) where.categoryId = categoryId;
    if (type) where.type = type;

    const transactions = await Transaction.findAll({
      where,
      include: [{ model: Category }],
      order: [['date', 'DESC'], ['createdAt', 'DESC']],
    });
    res.json({ transactions });
  } catch (err) {
    next(err);
  }
}

async function create(req, res, next) {
  try {
    const { amount, type, merchant, description, date, categoryId, autoCategorize } = req.body;
    if (!amount) return res.status(400).json({ error: 'amount is required' });

    let resolvedCategoryId = categoryId || null;
    let source = 'manual';
    let categoryConfidence = null;

    if (!resolvedCategoryId && autoCategorize) {
      try {
        const prediction = await categorizeTransaction({ description, merchant, amount });
        const predicted = await Category.findOne({ where: { name: prediction.category } });
        if (predicted) {
          resolvedCategoryId = predicted.id;
          categoryConfidence = prediction.confidence;
          source = 'ai';
        }
      } catch (mlErr) {
        // ML service unavailable/unreachable — fall back to uncategorized manual entry.
        console.warn('ML categorization failed:', mlErr.message);
      }
    }

    const transaction = await Transaction.create({
      userId: req.userId,
      categoryId: resolvedCategoryId,
      type: type || 'expense',
      amount,
      merchant,
      description,
      date: date || new Date(),
      source,
      categoryConfidence,
    });

    res.status(201).json({ transaction });
  } catch (err) {
    next(err);
  }
}

async function update(req, res, next) {
  try {
    const transaction = await Transaction.findOne({ where: { id: req.params.id, userId: req.userId } });
    if (!transaction) return res.status(404).json({ error: 'Transaction not found' });

    const { amount, type, merchant, description, date, categoryId } = req.body;
    await transaction.update({
      ...(amount !== undefined && { amount }),
      ...(type !== undefined && { type }),
      ...(merchant !== undefined && { merchant }),
      ...(description !== undefined && { description }),
      ...(date !== undefined && { date }),
      ...(categoryId !== undefined && { categoryId, source: 'manual', categoryConfidence: null }),
    });
    await transaction.reload();

    res.json({ transaction });
  } catch (err) {
    next(err);
  }
}

async function remove(req, res, next) {
  try {
    const transaction = await Transaction.findOne({ where: { id: req.params.id, userId: req.userId } });
    if (!transaction) return res.status(404).json({ error: 'Transaction not found' });
    await transaction.destroy();
    res.status(204).send();
  } catch (err) {
    next(err);
  }
}

// Monthly totals grouped by category, used for the dashboard and budget screens.
async function summary(req, res, next) {
  try {
    const { month } = req.query; // 'YYYY-MM'
    if (!month) return res.status(400).json({ error: 'month query param (YYYY-MM) is required' });

    const rows = await Transaction.findAll({
      attributes: ['categoryId', 'type', [fn('SUM', col('amount')), 'total']],
      where: {
        userId: req.userId,
        date: { [Op.gte]: `${month}-01`, [Op.lt]: literal(`'${month}-01'::date + interval '1 month'`) },
      },
      group: ['categoryId', 'type'],
      raw: true,
    });

    const categoryIds = rows.map((r) => r.categoryId).filter(Boolean);
    const categories = await Category.findAll({
      where: { id: categoryIds },
      attributes: ['id', 'name', 'icon', 'color'],
      raw: true,
    });
    const categoryById = Object.fromEntries(categories.map((c) => [c.id, c]));

    const breakdown = rows.map((r) => ({
      categoryId: r.categoryId,
      type: r.type,
      total: Number(r.total),
      category: r.categoryId ? categoryById[r.categoryId] || null : null,
    }));

    res.json({ month, breakdown });
  } catch (err) {
    next(err);
  }
}

module.exports = { list, create, update, remove, summary };
