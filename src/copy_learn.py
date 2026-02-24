import copy

# 原始数据：一个超级容易踩坑的嵌套结构
original = {
    'name': 'Kevin',
    'age': 18,
    'scores': [95, 98, 99],
    'info': {'city': 'San Jose', 'hobbies': ['game', 'coding']}
}

# 三种“拷贝”方式
a = original          # 直接赋值（根本不是拷贝！）
b = copy.copy(original)
c = copy.deepcopy(original)
print("a == b == c ->", a == b == c)
print("a is original ->", a is original)
print("a is b ->", a is b)
print("a is c ->", a is c)
print("b is c ->", b is c)
# 修改原始数据中的嵌套结构，观察浅拷贝和深拷贝的区别
original['scores'].append(100)
original['info']['hobbies'].append('reading')

print("\n修改后三者的值：")
print("a:", a)  # a 会跟随 original 的变化
print("b:", b)  # b 的顶层数据不变，但嵌套的列表和字典会变化
print("c:", c)  # c 完全独立，不受影响

print("\n修改后三者相等吗？")
print("a == b:", a == b)  # False，因为嵌套结构被修改了
print("b == c:", b == c)  # False，因为嵌套结构被修改了
print("a == c:", a == c)  # False，因为嵌套结构被修改了

print("\n三者的嵌套结构是否相同？")
print("a['scores'] is original['scores']:", a['scores'] is original['scores'])  # True
print("b['scores'] is original['scores']:", b['scores'] is original['scores'])  # True（浅拷贝）
print("c['scores'] is original['scores']:", c['scores'] is original['scores'])  # False（深拷贝）

print("修改前三者相等吗？")
print(a == b == c)   # True  值都一样
print(a is b is c)   # False  只有 a 和 original 是同一个对象