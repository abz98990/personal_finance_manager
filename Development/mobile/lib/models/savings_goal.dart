class SavingsGoal {
  final String id;
  final String title;
  final double targetAmount;
  final double savedAmount;
  final DateTime? targetDate;

  SavingsGoal({
    required this.id,
    required this.title,
    required this.targetAmount,
    required this.savedAmount,
    this.targetDate,
  });

  double get progress => targetAmount == 0 ? 0 : (savedAmount / targetAmount).clamp(0, 1);

  factory SavingsGoal.fromJson(Map<String, dynamic> json) => SavingsGoal(
        id: json['id'] as String,
        title: json['title'] as String,
        targetAmount: double.parse(json['targetAmount'].toString()),
        savedAmount: double.parse(json['savedAmount'].toString()),
        targetDate: json['targetDate'] != null ? DateTime.parse(json['targetDate'] as String) : null,
      );
}
