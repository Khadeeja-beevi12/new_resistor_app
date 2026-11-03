"""Load test: locust -f locustfile.py --host https://resistor.yourcompany.com"""
from locust import HttpUser, task, between


class Student(HttpUser):
    wait_time = between(2, 6)

    def on_start(self):
        self.client.get("/")

    @task(3)
    def play(self):
        c = self.client.get("/api/challenge").json()
        self.client.post("/api/check", json={"token": c["token"], "answer": "220"})

    @task(1)
    def hint(self):
        c = self.client.get("/api/challenge").json()
        self.client.post("/api/hint", json={"token": c["token"], "answer": ""})

    @task(1)
    def decode(self):
        self.client.post("/api/decode", json={"b1": "Yellow", "b2": "Violet", "mult": "Red", "tol": "Gold"})
