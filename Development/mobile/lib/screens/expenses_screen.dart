import 'package:flutter/material.dart';
import 'package:provider/provider.dart';

import '../providers/app_data_provider.dart';
import '../theme.dart';
import '../widgets/transaction_tile.dart';
import 'add_transaction_screen.dart';

class ExpensesScreen extends StatefulWidget {
  const ExpensesScreen({super.key});

  @override
  State<ExpensesScreen> createState() => _ExpensesScreenState();
}

class _ExpensesScreenState extends State<ExpensesScreen> {
  String _search = '';

  @override
  Widget build(BuildContext context) {
    final data = context.watch<AppDataProvider>();
    final query = _search.toLowerCase();
    final transactions = data.transactions.where((t) {
      if (query.isEmpty) return true;
      return (t.merchant ?? '').toLowerCase().contains(query) ||
          (t.category?.name ?? '').toLowerCase().contains(query);
    }).toList();

    return Scaffold(
      appBar: AppBar(title: const Text('Transaction History')),
      body: RefreshIndicator(
        onRefresh: data.loadTransactions,
        child: Padding(
          padding: const EdgeInsets.all(16.0),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.stretch,
            children: [
              _buildSearchBar(),
              const SizedBox(height: 16),
              Expanded(
                child: transactions.isEmpty
                    ? ListView(
                        children: const [
                          SizedBox(height: 80),
                          Center(child: Text('No transactions found', style: TextStyle(color: Colors.grey))),
                        ],
                      )
                    : ListView.builder(
                        itemCount: transactions.length,
                        itemBuilder: (context, i) => TransactionTile(
                          transaction: transactions[i],
                          onDelete: () => data.deleteTransaction(transactions[i].id),
                        ),
                      ),
              ),
            ],
          ),
        ),
      ),
      floatingActionButton: FloatingActionButton(
        backgroundColor: AppColors.primary,
        onPressed: () => Navigator.of(context).push(MaterialPageRoute(builder: (_) => const AddTransactionScreen())),
        child: const Icon(Icons.receipt_long, color: Colors.black87),
      ),
    );
  }

  Widget _buildSearchBar() {
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 16),
      decoration: BoxDecoration(color: AppColors.surface, borderRadius: BorderRadius.circular(12)),
      child: TextField(
        style: const TextStyle(color: Colors.white),
        onChanged: (v) => setState(() => _search = v),
        decoration: const InputDecoration(
          icon: Icon(Icons.search, color: Colors.grey),
          hintText: 'Search transactions, categories...',
          hintStyle: TextStyle(color: Colors.grey),
          border: InputBorder.none,
        ),
      ),
    );
  }
}
