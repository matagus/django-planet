def task_faker(ignore_results=False):
    def inner(fx):
        class Task(object):
            def delay(self, *args, **kwargs):
                return fx(*args, **kwargs)
        return Task()

    return inner
