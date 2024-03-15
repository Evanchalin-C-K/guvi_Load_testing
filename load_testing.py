from locust import SequentialTaskSet, HttpUser, task, events, TaskSet, constant_pacing, between, tag
from locust.event import EventHook
import logging

send_notification = EventHook()


def notification(req_id, message="success", **kwargs):
    print("sending notification: ", message, "id: ", req_id, kwargs)


send_notification.add_listener(notification)


class Mytask(TaskSet):
    wait = constant_pacing(1)
    url = "https://65c0f239dc74300bce8d0afe.mockapi.io/users"

    @task
    def delete_data(self):
        length = len(self.client.get(self.url).json())
        for i in range(51, length):
            with self.client.delete(self.url + "/" + str(i), catch_response=True) as response:
                if response.success():
                    send_notification.fire(req_id=1, message="data deleted")
                else:
                    send_notification.fire(req_id=0, message="data not found")
                self.interrupt()


class LoadTest(SequentialTaskSet):
    wait = between(1, 2)
    url = "https://65c0f239dc74300bce8d0afe.mockapi.io/users"
    data = {"Name": "Priya", "City": "Chennai", "Country": "India"}

    @task
    def get_data(self):
        with self.client.get(self.url + '/' + "8", catch_response=True) as response:
            if response.status_code == 200:
                print(response.json())
        with self.client.get(self.url + '/' + "12", catch_response=False) as response:
            print(response)
        self.interrupt()

    @task
    def post_data(self):
        with self.client.post(url=self.url, data=self.data, catch_response=True) as response:
            if response.status_code == 201:
                response.success()
                logging.info("data posted successfully")
            else:
                response.failure()
                logging.info("error")
            self.interrupt()


@events.request.add_listener
def on_request(name, request_type, response_time, **kwargs):
    print(name, request_type, response_time, kwargs)


class LoadTest_(HttpUser):
    host = "https://65c0f239dc74300bce8d0afe.mockapi.io/users"
    tasks = [Mytask, LoadTest]
