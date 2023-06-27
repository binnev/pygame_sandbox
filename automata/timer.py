import time


class Timer:
    """
    Timer that works as a context manager. You can wrap a block of code like this:
        with Timer() as timer:
            do_stuff()

        print(timer.time)
    """

    def __enter__(self):
        self.start = time.perf_counter()
        return self

    def __exit__(self, *args):
        self.end = time.perf_counter()
        self.time = self.end - self.start
