import 'category.dart';

class Transaction {
  final String id;
  final String type; // income | expense
  final double amount;
  final String? merchant;
  final String? description;
  final DateTime date;
  final String source; // manual | ai
  final double? categoryConfidence;
  final Category? category;

  Transaction({
    required this.id,
    required this.type,
    required this.amount,
    this.merchant,
    this.description,
    required this.date,
    required this.source,
    this.categoryConfidence,
    this.category,
  });

  factory Transaction.fromJson(Map<String, dynamic> json) => Transaction(
        id: json['id'] as String,
        type: json['type'] as String,
        amount: double.parse(json['amount'].toString()),
        merchant: json['merchant'] as String?,
        description: json['description'] as String?,
        date: DateTime.parse(json['date'] as String),
        source: json['source'] as String? ?? 'manual',
        categoryConfidence: json['categoryConfidence'] != null
            ? double.parse(json['categoryConfidence'].toString())
            : null,
        category: json['Category'] != null ? Category.fromJson(json['Category'] as Map<String, dynamic>) : null,
      );

  bool get isIncome => type == 'income';
}
