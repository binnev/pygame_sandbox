class SingletonInitError(Exception):
    pass


class Singleton:
    instance = None

    @classmethod
    def initialise(cls, *args, **kwargs):
        if cls.instance is None:
            # do __init__ on the class and store the instance on itself...
            # fixme: this means the class *needs* an __init__ method.
            #  Which means the __init__ method could be called by accident
            cls.instance = cls(*args, **kwargs)
            return cls.instance
        else:
            raise Exception(f"You can't create a second {cls.metaclass.__name__}")

    @classmethod
    def get_instance(cls):
        if cls.instance is not None:
            return cls.instance
        else:
            raise Exception(f"You need to instantiate {cls.metaclass.__name__} first")
