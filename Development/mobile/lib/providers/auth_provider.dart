import 'package:flutter/foundation.dart';
import 'package:shared_preferences/shared_preferences.dart';
import '../services/api_client.dart';

class AuthProvider extends ChangeNotifier {
  final ApiClient api;
  AuthProvider(this.api);

  static const _tokenKey = 'auth_token';

  String? _token;
  Map<String, dynamic>? _user;
  bool _initialized = false;

  bool get isAuthenticated => _token != null;
  bool get initialized => _initialized;
  Map<String, dynamic>? get user => _user;

  Future<void> restoreSession() async {
    final prefs = await SharedPreferences.getInstance();
    final token = prefs.getString(_tokenKey);
    if (token != null) {
      api.setToken(token);
      _token = token;
      try {
        final res = await api.get('/auth/me');
        _user = res['user'] as Map<String, dynamic>;
      } catch (_) {
        await logout();
      }
    }
    _initialized = true;
    notifyListeners();
  }

  Future<void> register(String name, String email, String password) async {
    final res = await api.post('/auth/register', {'name': name, 'email': email, 'password': password});
    await _applyAuth(res);
  }

  Future<void> login(String email, String password) async {
    final res = await api.post('/auth/login', {'email': email, 'password': password});
    await _applyAuth(res);
  }

  Future<void> _applyAuth(Map<String, dynamic> res) async {
    _token = res['token'] as String;
    _user = res['user'] as Map<String, dynamic>;
    api.setToken(_token);
    final prefs = await SharedPreferences.getInstance();
    await prefs.setString(_tokenKey, _token!);
    notifyListeners();
  }

  Future<void> logout() async {
    _token = null;
    _user = null;
    api.setToken(null);
    final prefs = await SharedPreferences.getInstance();
    await prefs.remove(_tokenKey);
    notifyListeners();
  }
}
