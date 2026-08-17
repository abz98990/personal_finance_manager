import 'package:flutter/material.dart';
import 'package:intl/intl.dart';

import '../models/transaction.dart';
import '../theme.dart';

const Map<String, IconData> categoryIcons = {
  'local_cafe': Icons.local_cafe,
  'shopping_cart': Icons.shopping_cart,
  'train': Icons.train,
  'subscriptions': Icons.subscriptions,
  'electric_bolt': Icons.electric_bolt,
  'home': Icons.home,
  'local_hospital': Icons.local_hospital,
  'shopping_bag': Icons.shopping_bag,
  'category': Icons.category,
  'work': Icons.work,
};

class TransactionTile extends StatelessWidget {
  final Transaction transaction;
  final VoidCallback? onDelete;

  const TransactionTile({super.key, required this.transaction, this.onDelete});

  @override
  Widget build(BuildContext context) {
    final category = transaction.category;
    final iconData = categoryIcons[category?.icon] ?? Icons.receipt_long;
    final color = category?.color != null
        ? Color(int.parse(category!.color!.replaceFirst('#', '0xFF')))
        : AppColors.primary;
    final sign = transaction.isIncome ? '+' : '-';
    final amountText = '$sign£${transaction.amount.toStringAsFixed(2)}';

    return Container(
      margin: const EdgeInsets.only(bottom: 12.0),
      padding: const EdgeInsets.all(16.0),
      decoration: BoxDecoration(color: AppColors.surface, borderRadius: BorderRadius.circular(16.0)),
      child: Row(
        children: [
          Container(
            padding: const EdgeInsets.all(10),
            decoration: BoxDecoration(color: color.withValues(alpha: 0.2), shape: BoxShape.circle),
            child: Icon(iconData, color: color, size: 24),
          ),
          const SizedBox(width: 16),
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(
                  transaction.merchant ?? transaction.description ?? 'Transaction',
                  style: const TextStyle(color: Colors.white, fontSize: 16, fontWeight: FontWeight.w500),
                ),
                const SizedBox(height: 4),
                Row(
                  children: [
                    Text(category?.name ?? 'Uncategorized', style: const TextStyle(color: Colors.grey, fontSize: 12)),
                    if (transaction.source == 'ai') ...[
                      const SizedBox(width: 6),
                      const Icon(Icons.auto_awesome, size: 12, color: AppColors.accent),
                    ],
                    const SizedBox(width: 8),
                    Text(
                      DateFormat('d MMM').format(transaction.date),
                      style: const TextStyle(color: Colors.grey, fontSize: 12),
                    ),
                  ],
                ),
              ],
            ),
          ),
          Text(
            amountText,
            style: TextStyle(
              color: transaction.isIncome ? AppColors.primary : Colors.white,
              fontSize: 16,
              fontWeight: FontWeight.bold,
            ),
          ),
          if (onDelete != null)
            IconButton(
              icon: const Icon(Icons.close, size: 18, color: Colors.grey),
              onPressed: onDelete,
            ),
        ],
      ),
    );
  }
}
