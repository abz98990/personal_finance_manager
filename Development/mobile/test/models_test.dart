import 'package:flutter_test/flutter_test.dart';
import 'package:pfm_app/models/savings_goal.dart';
import 'package:pfm_app/models/budget.dart';
import 'package:pfm_app/models/transaction.dart';

void main() {
  group('SavingsGoal', () {
    test('progress is clamped between 0 and 1', () {
      final goal = SavingsGoal(id: '1', title: 'Test', targetAmount: 100, savedAmount: 150);
      expect(goal.progress, 1.0);
    });

    test('progress is 0 when target is 0', () {
      final goal = SavingsGoal(id: '1', title: 'Test', targetAmount: 0, savedAmount: 0);
      expect(goal.progress, 0.0);
    });

    test('parses from JSON', () {
      final goal = SavingsGoal.fromJson({
        'id': '1',
        'title': 'Emergency Fund',
        'targetAmount': '3000.00',
        'savedAmount': '1200.00',
        'targetDate': null,
      });
      expect(goal.progress, closeTo(0.4, 0.0001));
    });
  });

  group('Budget', () {
    test('parses spend and computes progress', () {
      final budget = Budget.fromJson({
        'id': '1',
        'categoryId': 'c1',
        'month': '2026-08-01',
        'limitAmount': '300.00',
        'spent': 120,
      });
      expect(budget.progress, closeTo(0.4, 0.0001));
    });
  });

  group('Transaction', () {
    test('isIncome reflects type', () {
      final tx = Transaction.fromJson({
        'id': '1',
        'type': 'income',
        'amount': '350.00',
        'date': '2026-08-01',
        'source': 'manual',
      });
      expect(tx.isIncome, isTrue);
    });
  });
}
