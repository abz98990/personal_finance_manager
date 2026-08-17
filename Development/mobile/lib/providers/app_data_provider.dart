import 'package:flutter/foundation.dart' hide Category;
import 'package:intl/intl.dart';
import '../models/category.dart';
import '../models/transaction.dart';
import '../models/budget.dart';
import '../models/savings_goal.dart';
import '../services/api_client.dart';

/// Central app state: categories, transactions, budgets and savings goals
/// for the signed-in user, plus the ML forecast for the current month.
class AppDataProvider extends ChangeNotifier {
  final ApiClient api;
  AppDataProvider(this.api);

  List<Category> categories = [];
  List<Transaction> transactions = [];
  List<Budget> budgets = [];
  List<SavingsGoal> savingsGoals = [];
  Map<String, dynamic>? forecast;

  bool loading = false;
  String? error;

  String get currentMonth => DateFormat('yyyy-MM').format(DateTime.now());

  double get monthSpend => transactions
      .where((t) => t.type == 'expense' && DateFormat('yyyy-MM').format(t.date) == currentMonth)
      .fold(0.0, (sum, t) => sum + t.amount);

  double get monthIncome => transactions
      .where((t) => t.type == 'income' && DateFormat('yyyy-MM').format(t.date) == currentMonth)
      .fold(0.0, (sum, t) => sum + t.amount);

  Future<void> loadAll() async {
    loading = true;
    error = null;
    notifyListeners();
    try {
      await Future.wait([loadCategories(), loadTransactions(), loadBudgets(), loadSavingsGoals()]);
      await loadForecast();
    } catch (e) {
      error = e.toString();
    } finally {
      loading = false;
      notifyListeners();
    }
  }

  Future<void> loadCategories() async {
    final res = await api.get('/categories');
    categories = (res['categories'] as List).map((e) => Category.fromJson(e)).toList();
  }

  Future<void> loadTransactions() async {
    final res = await api.get('/transactions');
    transactions = (res['transactions'] as List).map((e) => Transaction.fromJson(e)).toList();
  }

  Future<void> loadBudgets() async {
    final res = await api.get('/budgets', query: {'month': currentMonth});
    budgets = (res['budgets'] as List).map((e) => Budget.fromJson(e)).toList();
  }

  Future<void> loadSavingsGoals() async {
    final res = await api.get('/savings-goals');
    savingsGoals = (res['goals'] as List).map((e) => SavingsGoal.fromJson(e)).toList();
  }

  Future<void> loadForecast() async {
    try {
      forecast = await api.get('/ml/predict/forecast');
    } catch (_) {
      forecast = null; // Not enough history yet, or ML service unavailable.
    }
  }

  Future<void> addTransaction({
    required double amount,
    required String type,
    String? merchant,
    String? description,
    String? categoryId,
    bool autoCategorize = false,
    DateTime? date,
  }) async {
    await api.post('/transactions', {
      'amount': amount,
      'type': type,
      if (merchant != null) 'merchant': merchant,
      if (description != null) 'description': description,
      if (categoryId != null) 'categoryId': categoryId,
      'autoCategorize': autoCategorize,
      'date': (date ?? DateTime.now()).toIso8601String().split('T').first,
    });
    await loadTransactions();
    await loadBudgets();
    notifyListeners();
  }

  Future<void> deleteTransaction(String id) async {
    await api.delete('/transactions/$id');
    await loadTransactions();
    await loadBudgets();
    notifyListeners();
  }

  Future<void> upsertBudget({required String categoryId, required double limitAmount}) async {
    await api.post('/budgets', {'categoryId': categoryId, 'month': currentMonth, 'limitAmount': limitAmount});
    await loadBudgets();
    notifyListeners();
  }

  Future<void> addSavingsGoal({required String title, required double targetAmount, double savedAmount = 0}) async {
    await api.post('/savings-goals', {'title': title, 'targetAmount': targetAmount, 'savedAmount': savedAmount});
    await loadSavingsGoals();
    notifyListeners();
  }

  Future<void> updateSavingsGoalProgress(String id, double savedAmount) async {
    await api.put('/savings-goals/$id', {'savedAmount': savedAmount});
    await loadSavingsGoals();
    notifyListeners();
  }

  void clear() {
    categories = [];
    transactions = [];
    budgets = [];
    savingsGoals = [];
    forecast = null;
    notifyListeners();
  }
}
