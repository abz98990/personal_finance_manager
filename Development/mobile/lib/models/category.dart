class Category {
  final String id;
  final String name;
  final String type;
  final String? icon;
  final String? color;

  Category({required this.id, required this.name, required this.type, this.icon, this.color});

  factory Category.fromJson(Map<String, dynamic> json) => Category(
        id: json['id'] as String,
        name: json['name'] as String,
        type: json['type'] as String,
        icon: json['icon'] as String?,
        color: json['color'] as String?,
      );
}
