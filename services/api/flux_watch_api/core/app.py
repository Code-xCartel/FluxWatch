from fastapi import FastAPI


class App(FastAPI):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        if kwargs.get("config"):
            self.config = kwargs["config"]
