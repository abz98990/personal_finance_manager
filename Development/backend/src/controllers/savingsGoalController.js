const { SavingsGoal } = require('../models');

async function list(req, res, next) {
  try {
    const goals = await SavingsGoal.findAll({
      where: { userId: req.userId },
      order: [['createdAt', 'DESC']],
    });
    res.json({ goals });
  } catch (err) {
    next(err);
  }
}

async function create(req, res, next) {
  try {
    const { title, targetAmount, savedAmount, targetDate, icon, color } = req.body;
    if (!title || !targetAmount) {
      return res.status(400).json({ error: 'title and targetAmount are required' });
    }

    const goal = await SavingsGoal.create({
      userId: req.userId,
      title,
      targetAmount,
      savedAmount: savedAmount || 0,
      targetDate,
      icon,
      color,
    });
    res.status(201).json({ goal });
  } catch (err) {
    next(err);
  }
}

async function update(req, res, next) {
  try {
    const goal = await SavingsGoal.findOne({ where: { id: req.params.id, userId: req.userId } });
    if (!goal) return res.status(404).json({ error: 'Savings goal not found' });

    const { title, targetAmount, savedAmount, targetDate, icon, color } = req.body;
    await goal.update({
      ...(title !== undefined && { title }),
      ...(targetAmount !== undefined && { targetAmount }),
      ...(savedAmount !== undefined && { savedAmount }),
      ...(targetDate !== undefined && { targetDate }),
      ...(icon !== undefined && { icon }),
      ...(color !== undefined && { color }),
    });
    await goal.reload();

    res.json({ goal });
  } catch (err) {
    next(err);
  }
}

async function remove(req, res, next) {
  try {
    const goal = await SavingsGoal.findOne({ where: { id: req.params.id, userId: req.userId } });
    if (!goal) return res.status(404).json({ error: 'Savings goal not found' });
    await goal.destroy();
    res.status(204).send();
  } catch (err) {
    next(err);
  }
}

module.exports = { list, create, update, remove };
