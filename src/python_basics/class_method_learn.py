from typing import Any, Optional


class MyClass:
    """演示类方法和实例方法区别的示例类
    
    该类用于展示类变量与实例变量的区别，以及类方法(@classmethod)和实例方法的使用差异。
    主要功能：
    - 通过类方法操作共享的类变量MAP
    - 通过实例方法操作类变量（注意：实际修改的仍是类变量）
    - 演示类变量在所有实例间共享的特性
    """

    MAP = {}

    @classmethod
    def set(cls, key: str, value: Any):
        cls.MAP[key] = value

    @classmethod
    def get(cls, key: str) -> Optional[Any]:
        return cls.MAP.get(key)

    def setValue(self, key: str, value: Any):
        self.MAP[key] = value

    def getValue(self, key: str):
        return self.MAP.get(key)


if __name__ == '__main__':
    MyClass.set('name', 'James')
    print(MyClass.get('name'))
    mc1 = MyClass()
    mc2 = MyClass()
    print(mc1.get('name'))
    mc1.set('name', 'James-1')
    print(mc2.get('name'))
    print(mc1 == mc2)
    print(mc1.MAP == mc2.MAP)
