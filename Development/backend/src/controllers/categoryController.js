const { Op } = require('sequelize');
const { Category } = require('../models');

async function list(req, res, next) {
  try {
    const categories = await Category.findAll({
      where: { [Op.or]: [{ userId: req.userId }, { userId: null }] },
      order: [['name', 'ASC']],
    });
    res.json({ categories });
  } catch (err) {
    next(err);
  }
}

async function create(req, res, next) {
  try {
    const { name, type, icon, color } = req.body;
    if (!name) return res.status(400).json({ error: 'name is required' });

    const category = await Category.create({
      name,
      type: type || 'expense',
      icon,
      color,
      userId: req.userId,
    });
    res.status(201).json({ category });
  } catch (err) {
    next(err);
  }
}

async function remove(req, res, next) {
  try {
    const category = await Category.findOne({ where: { id: req.params.id, userId: req.userId } });
    if (!category) return res.status(404).json({ error: 'Category not found' });
    await category.destroy();
    res.status(204).send();
  } catch (err) {
    next(err);
  }
}

module.exports = { list, create, remove };
