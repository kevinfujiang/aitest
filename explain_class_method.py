"""
解释为什么 mc1 == mc2 为 False，但 mc1.MAP == mc2.MAP 为 True
"""
from typing import Any, Optional


class MyClass:
    """A simple example class"""
    
    # 类变量 - 所有实例共享
    MAP = {}

    def __init__(self):
        self.instance_map = {}

    @classmethod
    def set(cls, key: str, value: Any):
        cls.MAP[key] = value

    @classmethod
    def get(cls, key: str) -> Optional[Any]:
        return cls.MAP.get(key)

    def setClassValue(self, key: str, value: Any):
        # 注意：这里修改的是类变量，不是实例变量
        self.MAP[key] = value

    def getClassValue(self, key: str):
        return self.MAP.get(key)

    def setInstValue(self, key: str, value: Any):
        self.instance_map[key] = value

    def getInstValue(self, key: str, default: Any = None):
        return self.instance_map.get(key, default)

# 创建两个实例
mc1 = MyClass()
mc2 = MyClass()

print("=== 对象身份比较 ===")
print(f"mc1 的 id: {id(mc1)}")
print(f"mc2 的 id: {id(mc2)}")
print(f"mc1 == mc2: {mc1 == mc2}")  # False - 因为是两个不同的对象实例
print(f"mc1 is mc2: {mc1 is mc2}")  # False - 不是同一个对象

print("\n=== MAP 属性比较 ===")
print(f"mc1.MAP 的 id: {id(mc1.MAP)}")
print(f"mc2.MAP 的 id: {id(mc2.MAP)}")
print(f"mc1.MAP == mc2.MAP: {mc1.MAP == mc2.MAP}")  # True - 指向同一个字典对象
print(f"mc1.MAP is mc2.MAP: {mc1.MAP is mc2.MAP}")  # True - 是同一个对象

print("\n=== 验证 MAP 是类变量 ===")
MyClass.MAP['test'] = 'shared'
print(f"通过类访问: {MyClass.MAP}")
print(f"通过实例1访问: {mc1.MAP}")
print(f"通过实例2访问: {mc2.MAP}")

print("\n=== 修改 MAP 内容 ===")
mc1.setClassValue('name', 'James')
print(f"修改后 mc1.MAP: {mc1.MAP}")
print(f"修改后 mc2.MAP: {mc2.MAP}")
print(f"两个实例的 MAP 仍然是同一个对象: {mc1.MAP is mc2.MAP}")

print("\n=== 修改 instance MAP 内容 ===")
mc1.setInstValue('name', 'James-22')
mc2.setInstValue('name', 'James-33')
print(mc1.getInstValue("name"))
print(mc2.getInstValue("name"))
