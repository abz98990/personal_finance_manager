import 'package:flutter/material.dart';
import 'package:provider/provider.dart';

import '../models/category.dart';
import '../providers/app_data_provider.dart';
import '../theme.dart';
import '../widgets/transaction_tile.dart';
import 'savings_screen.dart';

class BudgetScreen extends StatelessWidget {
  const BudgetScreen({super.key});

  @override
  Widget build(BuildContext context) {
    final data = context.watch<AppDataProvider>();

    return Scaffold(
      appBar: AppBar(title: const Text('Budgets'), automaticallyImplyLeading: false),
      body: RefreshIndicator(
        onRefresh: data.loadBudgets,
        child: ListView(
          padding: const EdgeInsets.all(16.0),
          children: [
            Card(
              color: AppColors.surface,
              shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(16)),
              child: ListTile(
                leading: const Icon(Icons.savings, color: AppColors.accent),
                title: const Text('Smart Savings Plans', style: TextStyle(color: Colors.white)),
                subtitle: const Text('Track your savings goals', style: TextStyle(color: Colors.grey)),
                trailing: const Icon(Icons.chevron_right, color: Colors.grey),
                onTap: () => Navigator.of(context).push(MaterialPageRoute(builder: (_) => const SavingsScreen())),
              ),
            ),
            const SizedBox(height: 24),
            Row(
              mainAxisAlignment: MainAxisAlignment.spaceBetween,
              children: [
                const Text('This Month', style: TextStyle(color: Colors.white, fontSize: 18, fontWeight: FontWeight.bold)),
                TextButton.icon(
                  onPressed: () => _showAddBudgetDialog(context, data.categories.where((c) => c.type == 'expense').toList()),
                  icon: const Icon(Icons.add, size: 18),
                  label: const Text('Add budget'),
                ),
              ],
            ),
            const SizedBox(height: 8),
            if (data.budgets.isEmpty)
              const Padding(
                padding: EdgeInsets.symmetric(vertical: 24),
                child: Center(child: Text('No budgets set for this month yet', style: TextStyle(color: Colors.grey))),
              )
            else
              ...data.budgets.map((b) => _BudgetCard(
                    title: b.category?.name ?? 'Uncategorized',
                    spent: b.spent,
                    limit: b.limitAmount,
                    icon: categoryIcons[b.category?.icon] ?? Icons.category,
                  )),
          ],
        ),
      ),
    );
  }

  void _showAddBudgetDialog(BuildContext context, List<Category> expenseCategories) {
    Category? selected = expenseCategories.isNotEmpty ? expenseCategories.first : null;
    final limitController = TextEditingController();

    showDialog(
      context: context,
      builder: (dialogContext) => StatefulBuilder(
        builder: (dialogContext, setState) => AlertDialog(
          backgroundColor: AppColors.surface,
          title: const Text('Set Budget', style: TextStyle(color: Colors.white)),
          content: Column(
            mainAxisSize: MainAxisSize.min,
            children: [
              DropdownButtonFormField<Category>(
                initialValue: selected,
                dropdownColor: AppColors.surface,
                style: const TextStyle(color: Colors.white),
                items: expenseCategories.map((c) => DropdownMenuItem(value: c, child: Text(c.name))).toList(),
                onChanged: (c) => setState(() => selected = c),
              ),
              const SizedBox(height: 12),
              TextField(
                controller: limitController,
                style: const TextStyle(color: Colors.white),
                keyboardType: const TextInputType.numberWithOptions(decimal: true),
                decoration: const InputDecoration(labelText: 'Monthly limit (£)'),
              ),
            ],
          ),
          actions: [
            TextButton(onPressed: () => Navigator.of(dialogContext).pop(), child: const Text('Cancel')),
            ElevatedButton(
              onPressed: () {
                final limit = double.tryParse(limitController.text);
                if (selected != null && limit != null && limit > 0) {
                  context.read<AppDataProvider>().upsertBudget(categoryId: selected!.id, limitAmount: limit);
                  Navigator.of(dialogContext).pop();
                }
              },
              child: const Text('Save'),
            ),
          ],
        ),
      ),
    );
  }
}

class _BudgetCard extends StatelessWidget {
  final String title;
  final double spent;
  final double limit;
  final IconData icon;

  const _BudgetCard({required this.title, required this.spent, required this.limit, required this.icon});

  @override
  Widget build(BuildContext context) {
    final progress = limit == 0 ? 0.0 : (spent / limit).clamp(0, 1.5).toDouble();
    final overBudget = spent > limit;

    return Container(
      margin: const EdgeInsets.only(bottom: 16),
      padding: const EdgeInsets.all(20),
      decoration: BoxDecoration(color: AppColors.surface, borderRadius: BorderRadius.circular(16)),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            children: [
              Container(
                padding: const EdgeInsets.all(12),
                decoration: BoxDecoration(color: AppColors.primary.withValues(alpha: 0.2), borderRadius: BorderRadius.circular(12)),
                child: Icon(icon, color: AppColors.primary, size: 28),
              ),
              const SizedBox(width: 16),
              Expanded(
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text(title, style: const TextStyle(color: Colors.white, fontSize: 18, fontWeight: FontWeight.bold)),
                    const SizedBox(height: 4),
                    Text('£${spent.toStringAsFixed(0)} of £${limit.toStringAsFixed(0)}', style: const TextStyle(color: Colors.grey, fontSize: 14)),
                  ],
                ),
              ),
              Text(
                '${(progress * 100).toInt()}%',
                style: TextStyle(color: overBudget ? AppColors.danger : AppColors.primary, fontSize: 20, fontWeight: FontWeight.bold),
              ),
            ],
          ),
          const SizedBox(height: 20),
          ClipRRect(
            borderRadius: BorderRadius.circular(8),
            child: LinearProgressIndicator(
              value: progress.clamp(0, 1).toDouble(),
              minHeight: 10,
              backgroundColor: Colors.grey.withValues(alpha: 0.2),
              valueColor: AlwaysStoppedAnimation<Color>(overBudget ? AppColors.danger : AppColors.primary),
            ),
          ),
        ],
      ),
    );
  }
}
