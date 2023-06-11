import time


class Timer:
    def __enter__(self):
        self.start = time.perf_counter()
        return self

    def __exit__(self, *args):
        self.end = time.perf_counter()
        self.time = self.end - self.start


if __name__ == "__main__":
    with Timer() as timer:
        time.sleep(0.5)

    print(timer.time)
