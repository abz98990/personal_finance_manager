const { DataTypes, Model } = require('sequelize');
const sequelize = require('../config/db');

class Budget extends Model {}

Budget.init(
  {
    id: {
      type: DataTypes.UUID,
      defaultValue: DataTypes.UUIDV4,
      primaryKey: true,
    },
    userId: {
      type: DataTypes.UUID,
      allowNull: false,
    },
    categoryId: {
      type: DataTypes.UUID,
      allowNull: false,
    },
    // First day of the budgeted month, e.g. 2026-08-01
    month: {
      type: DataTypes.DATEONLY,
      allowNull: false,
    },
    limitAmount: {
      type: DataTypes.DECIMAL(12, 2),
      allowNull: false,
      validate: { min: 0 },
    },
  },
  {
    sequelize,
    modelName: 'Budget',
    tableName: 'budgets',
    indexes: [{ unique: true, fields: ['userId', 'categoryId', 'month'] }],
  }
);

module.exports = Budget;
