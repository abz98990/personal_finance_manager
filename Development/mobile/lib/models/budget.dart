import 'category.dart';

class Budget {
  final String id;
  final String categoryId;
  final DateTime month;
  final double limitAmount;
  final double spent;
  final Category? category;

  Budget({
    required this.id,
    required this.categoryId,
    required this.month,
    required this.limitAmount,
    required this.spent,
    this.category,
  });

  double get progress => limitAmount == 0 ? 0 : (spent / limitAmount).clamp(0, 1.5);

  factory Budget.fromJson(Map<String, dynamic> json) => Budget(
        id: json['id'] as String,
        categoryId: json['categoryId'] as String,
        month: DateTime.parse(json['month'] as String),
        limitAmount: double.parse(json['limitAmount'].toString()),
        spent: double.parse((json['spent'] ?? 0).toString()),
        category: json['Category'] != null ? Category.fromJson(json['Category'] as Map<String, dynamic>) : null,
      );
}
