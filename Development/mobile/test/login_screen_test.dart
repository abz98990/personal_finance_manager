import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:provider/provider.dart';
import 'package:pfm_app/providers/auth_provider.dart';
import 'package:pfm_app/services/api_client.dart';
import 'package:pfm_app/screens/login_screen.dart';

void main() {
  Widget buildTestable() {
    return MultiProvider(
      providers: [
        ChangeNotifierProvider(create: (_) => AuthProvider(ApiClient())),
      ],
      child: const MaterialApp(home: LoginScreen()),
    );
  }

  testWidgets('renders email and password fields', (tester) async {
    await tester.pumpWidget(buildTestable());

    expect(find.text('Email'), findsOneWidget);
    expect(find.text('Password'), findsOneWidget);
    expect(find.widgetWithText(ElevatedButton, 'Log In'), findsOneWidget);
  });

  testWidgets('shows validation errors on empty submit', (tester) async {
    await tester.pumpWidget(buildTestable());

    await tester.tap(find.widgetWithText(ElevatedButton, 'Log In'));
    await tester.pump();

    expect(find.text('Enter a valid email'), findsOneWidget);
    expect(find.text('At least 8 characters'), findsOneWidget);
  });

  testWidgets('navigates to register screen', (tester) async {
    await tester.pumpWidget(buildTestable());

    await tester.tap(find.text('Don\'t have an account? Sign up'));
    await tester.pumpAndSettle();

    expect(find.text('Create Account'), findsOneWidget);
  });
}
