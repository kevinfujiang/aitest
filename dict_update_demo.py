"""
演示Python字典update()方法的各种用法和效果
"""

def demo_basic_update():
    """基本update操作"""
    print("=== 基本update操作 ===")
    
    dict1 = {'a': 1, 'b': 2}
    dict2 = {'b': 3, 'c': 4}
    
    print(f"原始dict1: {dict1}")
    print(f"原始dict2: {dict2}")
    
    # update会修改原字典
    dict1.update(dict2)
    print(f"update后dict1: {dict1}")
    print(f"dict2保持不变: {dict2}")
    
    # 结果：相同key会被覆盖，新key会被添加

def demo_update_with_kwargs():
    """使用关键字参数更新"""
    print("\n=== 使用关键字参数更新 ===")
    
    my_dict = {'name': 'Alice', 'age': 25}
    print(f"原始字典: {my_dict}")
    
    # 使用关键字参数
    my_dict.update(age=26, city='Beijing')
    print(f"使用kwargs更新后: {my_dict}")

def demo_update_with_tuples():
    """使用元组列表更新"""
    print("\n=== 使用元组列表更新 ===")
    
    my_dict = {'x': 10}
    tuple_list = [('y', 20), ('z', 30)]
    
    print(f"原始字典: {my_dict}")
    print(f"元组列表: {tuple_list}")
    
    my_dict.update(tuple_list)
    print(f"更新后: {my_dict}")

def demo_update_with_iterator():
    """使用迭代器更新"""
    print("\n=== 使用迭代器更新 ===")
    
    my_dict = {'a': 1}
    
    # 使用生成器表达式
    my_dict.update((f'key_{i}', i) for i in range(3))
    print(f"使用生成器更新: {my_dict}")

def demo_in_place_modification():
    """演示就地修改特性"""
    print("\n=== 就地修改特性 ===")
    
    original_dict = {'data': [1, 2, 3]}
    another_ref = original_dict  # 引用同一个对象
    
    print(f"修改前:")
    print(f"  original_dict: {original_dict}")
    print(f"  another_ref: {another_ref}")
    print(f"  是否同一对象: {original_dict is another_ref}")
    
    # update操作
    original_dict.update({'new_key': 'new_value'})
    
    print(f"\n修改后:")
    print(f"  original_dict: {original_dict}")
    print(f"  another_ref: {another_ref}")
    print(f"  是否同一对象: {original_dict is another_ref}")
    
    # 证明是就地修改，不是创建新对象

def demo_comparison_with_merge():
    """与字典合并操作对比"""
    print("\n=== 与 | 操作符对比 ===")
    
    dict1 = {'a': 1, 'b': 2}
    dict2 = {'b': 3, 'c': 4}
    
    print(f"dict1: {dict1}")
    print(f"dict2: {dict2}")
    
    # update - 修改原字典
    dict1_copy = dict1.copy()
    dict1_copy.update(dict2)
    print(f"update结果: {dict1_copy}")
    print(f"原dict1是否改变: {dict1}")  # 原字典被修改了
    
    # | 操作符 - 创建新字典
    dict1 = {'a': 1, 'b': 2}
    result = dict1 | dict2
    print(f"| 操作符结果: {result}")
    print(f"原dict1是否改变: {dict1}")  # 原字典未改变

def demo_performance_consideration():
    """性能考虑示例"""
    print("\n=== 性能考虑 ===")
    
    import time
    
    # 大量数据更新场景
    large_dict = {f'key_{i}': i for i in range(10000)}
    updates = {f'key_{i}': i*2 for i in range(5000, 15000)}
    
    # 测试update性能
    start_time = time.time()
    large_dict.update(updates)
    end_time = time.time()
    
    print(f"更新了 {len(updates)} 个键值对")
    print(f"耗时: {end_time - start_time:.6f} 秒")
    print(f"最终字典大小: {len(large_dict)}")

if __name__ == '__main__':
    demo_basic_update()
    demo_update_with_kwargs()
    demo_update_with_tuples()
    demo_update_with_iterator()
    demo_in_place_modification()
    demo_comparison_with_merge()
    demo_performance_consideration()