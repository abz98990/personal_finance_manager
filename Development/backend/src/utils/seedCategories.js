require('dotenv').config();
const { sequelize, Category } = require('../models');

const DEFAULT_CATEGORIES = [
  { name: 'Food & Drink', type: 'expense', icon: 'local_cafe', color: '#8D6E63' },
  { name: 'Groceries', type: 'expense', icon: 'shopping_cart', color: '#66BB6A' },
  { name: 'Transport', type: 'expense', icon: 'train', color: '#42A5F5' },
  { name: 'Entertainment', type: 'expense', icon: 'subscriptions', color: '#EF5350' },
  { name: 'Utilities', type: 'expense', icon: 'electric_bolt', color: '#FFA726' },
  { name: 'Rent', type: 'expense', icon: 'home', color: '#AB47BC' },
  { name: 'Health', type: 'expense', icon: 'local_hospital', color: '#26A69A' },
  { name: 'Shopping', type: 'expense', icon: 'shopping_bag', color: '#EC407A' },
  { name: 'Other', type: 'expense', icon: 'category', color: '#78909C' },
  { name: 'Income', type: 'income', icon: 'work', color: '#81C784' },
];

async function seed() {
  await sequelize.sync();
  for (const cat of DEFAULT_CATEGORIES) {
    await Category.findOrCreate({
      where: { name: cat.name, userId: null },
      defaults: { ...cat, isDefault: true, userId: null },
    });
  }
  console.log(`Seeded ${DEFAULT_CATEGORIES.length} default categories.`);
  await sequelize.close();
}

seed().catch((err) => {
  console.error(err);
  process.exit(1);
});
