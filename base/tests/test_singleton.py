from base.singleton import Singleton


def test_happy_flow():
    class MyList(list, Singleton):
        pass

    assert MyList.instance is None
    ml = MyList.initialise()
    ml.append("a")
    assert MyList.instance is ml
    assert Singleton.instance is None
    ml = MyList.get_instance()
    ml.append("b")
    assert MyList.instance is ml
    assert MyList.instance == ["a", "b"]

    class MyDict(dict, Singleton):
        pass

    assert MyDict.instance is None
    md = MyDict.initialise()
    md["a"] = 1
    assert MyDict.instance is md
    assert Singleton.instance is None
    md = MyDict.get_instance()
    md["b"] = 2
    assert MyDict.instance is md
    assert MyDict.instance == {"a": 1, "b": 2}


def test_inheritance_order_makes_no_difference():
    class SingletonFirst(Singleton, list):
        pass

    class SingletonLast(list, Singleton):
        pass

    assert SingletonFirst.instance is None
    sf = SingletonFirst.initialise()
    assert SingletonFirst.instance is sf
    sf = SingletonFirst.get_instance()
    assert SingletonFirst.instance is sf
    assert Singleton.instance is None

    assert SingletonLast.instance is None
    sl = SingletonLast.initialise()
    assert SingletonLast.instance is sl
    sl = SingletonLast.get_instance()
    assert SingletonLast.instance is sl
    assert Singleton.instance is None
