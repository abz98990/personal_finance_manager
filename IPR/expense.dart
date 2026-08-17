import 'package:flutter/material.dart';

void main() {
  runApp(const ExpensesApp());
}

class ExpensesApp extends StatelessWidget {
  const ExpensesApp({Key? key}) : super(key: key);

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'Expenses',
      theme: ThemeData(
        brightness: Brightness.dark,
        scaffoldBackgroundColor: const Color(0xFF1E232B),
        colorScheme: const ColorScheme.dark(
          primary: Color(0xFF81C784),
          secondary: Color(0xFFDCE775),
        ),
      ),
      home: const ExpensesScreen(),
      debugShowCheckedModeBanner: false,
    );
  }
}

class ExpensesScreen extends StatefulWidget {
  const ExpensesScreen({Key? key}) : super(key: key);

  @override
  _ExpensesScreenState createState() => _ExpensesScreenState();
}

class _ExpensesScreenState extends State<ExpensesScreen> {
  int _selectedIndex = 1; // Index 1 for 'Expenses' tab

  void _onItemTapped(int index) {
    setState(() {
      _selectedIndex = index;
    });
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        backgroundColor: const Color(0xFF262C36),
        elevation: 0,
        centerTitle: true,
        title: const Text(
          'Transaction History',
          style: TextStyle(fontSize: 18, fontWeight: FontWeight.w500, color: Colors.white),
        ),
        actions: [
          IconButton(
            icon: const Icon(Icons.filter_list, color: Colors.white),
            onPressed: () {}, // Filter action placeholder
          ),
        ],
      ),
      body: SingleChildScrollView(
        child: Padding(
          padding: const EdgeInsets.all(16.0),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.stretch,
            children: [
              _buildSearchBar(),
              const SizedBox(height: 24),
              const Text('Today', style: TextStyle(color: Colors.grey, fontSize: 14, fontWeight: FontWeight.bold)),
              const SizedBox(height: 12),
              _buildTransactionCard(Icons.local_cafe, Colors.brown, 'Coffee Shop', 'Food & Drink', '-£4.50'),
              _buildTransactionCard(Icons.train, Colors.blue, 'Subway Ticket', 'Transport', '-£2.80'),
              const SizedBox(height: 24),
              const Text('Yesterday', style: TextStyle(color: Colors.grey, fontSize: 14, fontWeight: FontWeight.bold)),
              const SizedBox(height: 12),
              _buildTransactionCard(Icons.shopping_cart, Colors.green, 'Supermarket', 'Groceries', '-£45.20'),
              _buildTransactionCard(Icons.subscriptions, Colors.redAccent, 'Netflix', 'Entertainment', '-£10.99'),
              _buildTransactionCard(Icons.work, Colors.teal, 'Freelance Client', 'Income', '+£350.00', isIncome: true),
              const SizedBox(height: 24),
              const Text('July 18, 2026', style: TextStyle(color: Colors.grey, fontSize: 14, fontWeight: FontWeight.bold)),
              const SizedBox(height: 12),
              _buildTransactionCard(Icons.electric_bolt, Colors.orange, 'Electric Bill', 'Utilities', '-£65.00'),
            ],
          ),
        ),
      ),
      floatingActionButton: FloatingActionButton(
        onPressed: () {},
        backgroundColor: const Color(0xFF81C784),
        child: const Icon(Icons.receipt_long, color: Colors.black87),
      ),
      bottomNavigationBar: BottomNavigationBar(
        type: BottomNavigationBarType.fixed,
        backgroundColor: const Color(0xFF262C36),
        selectedItemColor: const Color(0xFF81C784),
        unselectedItemColor: Colors.grey,
        currentIndex: _selectedIndex,
        onTap: _onItemTapped,
        items: const [
          BottomNavigationBarItem(icon: Icon(Icons.home), label: 'Home'),
          BottomNavigationBarItem(icon: Icon(Icons.attach_money), label: 'Expenses'),
          BottomNavigationBarItem(icon: Icon(Icons.account_balance_wallet), label: 'Budget'),
          BottomNavigationBarItem(icon: Icon(Icons.person), label: 'Profile'),
        ],
      ),
    );
  }

  Widget _buildSearchBar() {
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 16),
      decoration: BoxDecoration(
        color: const Color(0xFF262C36),
        borderRadius: BorderRadius.circular(12),
      ),
      child: const TextField(
        style: TextStyle(color: Colors.white),
        decoration: InputDecoration(
          icon: Icon(Icons.search, color: Colors.grey),
          hintText: 'Search transactions, categories...',
          hintStyle: TextStyle(color: Colors.grey),
          border: InputBorder.none,
        ),
      ),
    );
  }

  Widget _buildTransactionCard(IconData icon, Color iconColor, String title, String category, String amount, {bool isIncome = false}) {
    return Container(
      margin: const EdgeInsets.only(bottom: 12.0),
      padding: const EdgeInsets.all(16.0),
      decoration: BoxDecoration(
        color: const Color(0xFF262C36),
        borderRadius: BorderRadius.circular(16.0),
      ),
      child: Row(
        children: [
          Container(
            padding: const EdgeInsets.all(10),
            decoration: BoxDecoration(color: iconColor.withOpacity(0.2), shape: BoxShape.circle),
            child: Icon(icon, color: iconColor, size: 24),
          ),
          const SizedBox(width: 16),
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(title, style: const TextStyle(color: Colors.white, fontSize: 16, fontWeight: FontWeight.w500)),
                const SizedBox(height: 4),
                Text(category, style: const TextStyle(color: Colors.grey, fontSize: 12)),
              ],
            ),
          ),
          Text(
            amount,
            style: TextStyle(
              color: isIncome ? const Color(0xFF81C784) : Colors.white,
              fontSize: 16,
              fontWeight: FontWeight.bold,
            ),
          ),
        ],
      ),
    );
  }
}