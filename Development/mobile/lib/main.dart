import 'package:flutter/material.dart';
import 'package:provider/provider.dart';

import 'providers/auth_provider.dart';
import 'providers/app_data_provider.dart';
import 'services/api_client.dart';
import 'screens/login_screen.dart';
import 'screens/root_shell.dart';
import 'theme.dart';

void main() {
  final api = ApiClient();
  runApp(PfmApp(api: api));
}

class PfmApp extends StatelessWidget {
  final ApiClient api;
  const PfmApp({super.key, required this.api});

  @override
  Widget build(BuildContext context) {
    return MultiProvider(
      providers: [
        ChangeNotifierProvider(create: (_) => AuthProvider(api)..restoreSession()),
        ChangeNotifierProvider(create: (_) => AppDataProvider(api)),
      ],
      child: MaterialApp(
        title: 'Smart PFM',
        debugShowCheckedModeBanner: false,
        theme: appTheme,
        home: const AppRoot(),
      ),
    );
  }
}

class AppRoot extends StatelessWidget {
  const AppRoot({super.key});

  @override
  Widget build(BuildContext context) {
    final auth = context.watch<AuthProvider>();

    if (!auth.initialized) {
      return const Scaffold(body: Center(child: CircularProgressIndicator()));
    }

    return auth.isAuthenticated ? const RootShell() : const LoginScreen();
  }
}
