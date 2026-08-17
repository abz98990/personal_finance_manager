import 'package:flutter/material.dart';
import 'package:provider/provider.dart';

import '../providers/app_data_provider.dart';
import '../providers/auth_provider.dart';
import '../theme.dart';
import '../widgets/transaction_tile.dart';

class HomeScreen extends StatelessWidget {
  const HomeScreen({super.key});

  @override
  Widget build(BuildContext context) {
    final data = context.watch<AppDataProvider>();
    final user = context.watch<AuthProvider>().user;

    return Scaffold(
      appBar: AppBar(
        title: Text('Hi, ${user?['name']?.toString().split(' ').first ?? 'there'}'),
        automaticallyImplyLeading: false,
      ),
      body: RefreshIndicator(
        onRefresh: data.loadAll,
        child: data.loading && data.transactions.isEmpty
            ? const Center(child: CircularProgressIndicator())
            : ListView(
                padding: const EdgeInsets.all(16.0),
                children: [
                  _SummaryCard(income: data.monthIncome, spend: data.monthSpend),
                  const SizedBox(height: 16),
                  if (data.forecast != null) _ForecastCard(forecast: data.forecast!),
                  const SizedBox(height: 24),
                  const Text('Recent Transactions', style: TextStyle(color: Colors.white, fontSize: 18, fontWeight: FontWeight.bold)),
                  const SizedBox(height: 12),
                  if (data.transactions.isEmpty)
                    const Padding(
                      padding: EdgeInsets.symmetric(vertical: 24),
                      child: Center(child: Text('No transactions yet', style: TextStyle(color: Colors.grey))),
                    )
                  else
                    ...data.transactions.take(5).map((t) => TransactionTile(transaction: t)),
                ],
              ),
      ),
    );
  }
}

class _SummaryCard extends StatelessWidget {
  final double income;
  final double spend;
  const _SummaryCard({required this.income, required this.spend});

  @override
  Widget build(BuildContext context) {
    final net = income - spend;
    return Container(
      padding: const EdgeInsets.all(20),
      decoration: BoxDecoration(color: AppColors.surface, borderRadius: BorderRadius.circular(16)),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          const Text('This Month', style: TextStyle(color: Colors.grey, fontSize: 13)),
          const SizedBox(height: 8),
          Text(
            '£${net.toStringAsFixed(2)}',
            style: TextStyle(
              color: net >= 0 ? AppColors.primary : AppColors.danger,
              fontSize: 32,
              fontWeight: FontWeight.bold,
            ),
          ),
          const SizedBox(height: 16),
          Row(
            children: [
              Expanded(child: _MiniStat(label: 'Income', value: income, color: AppColors.primary)),
              Expanded(child: _MiniStat(label: 'Spent', value: spend, color: AppColors.danger)),
            ],
          ),
        ],
      ),
    );
  }
}

class _MiniStat extends StatelessWidget {
  final String label;
  final double value;
  final Color color;
  const _MiniStat({required this.label, required this.value, required this.color});

  @override
  Widget build(BuildContext context) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Text(label, style: const TextStyle(color: Colors.grey, fontSize: 12)),
        Text('£${value.toStringAsFixed(2)}', style: TextStyle(color: color, fontSize: 16, fontWeight: FontWeight.w600)),
      ],
    );
  }
}

class _ForecastCard extends StatelessWidget {
  final Map<String, dynamic> forecast;
  const _ForecastCard({required this.forecast});

  @override
  Widget build(BuildContext context) {
    final trend = forecast['trend'] as String? ?? 'stable';
    final nextMonth = (forecast['nextMonthTotal'] as num?)?.toDouble() ?? 0;
    final trendIcon = trend == 'increasing'
        ? Icons.trending_up
        : trend == 'decreasing'
            ? Icons.trending_down
            : Icons.trending_flat;

    return Container(
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        gradient: const LinearGradient(colors: [AppColors.surface, AppColors.background]),
        border: Border.all(color: AppColors.accent.withValues(alpha: 0.3)),
        borderRadius: BorderRadius.circular(16),
      ),
      child: Row(
        children: [
          Icon(trendIcon, color: AppColors.accent, size: 32),
          const SizedBox(width: 16),
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                const Text('AI Forecast', style: TextStyle(color: AppColors.accent, fontSize: 12, fontWeight: FontWeight.bold)),
                const SizedBox(height: 4),
                Text(
                  'Projected spend next month: £${nextMonth.toStringAsFixed(2)} ($trend)',
                  style: const TextStyle(color: Colors.white, fontSize: 14),
                ),
              ],
            ),
          ),
        ],
      ),
    );
  }
}
