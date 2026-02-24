from typing import Any, Optional


class MyClass:
    """A simple example class"""

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
