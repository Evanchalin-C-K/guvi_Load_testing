# Importing necessary modules and classes from Locust
from locust import SequentialTaskSet, HttpUser, task, events, TaskSet, constant_pacing, between, tag
from locust.event import EventHook
import logging

# creating  event hook instance
send_notification = EventHook()


# Function to send notification with ID, message and additional information.,
def notification(req_id, message="success", **kwargs):
    print("sending notification: ", message, "id: ", req_id, kwargs)


# whenever the send_notification event is triggered,
# the notification function will be called and executed
send_notification.add_listener(notification)


# Define a class for inheriting sequential task that helps to run the tasks in sequential order
class LoadTest(SequentialTaskSet):
    wait = between(1, 2)
    url = "https://65c0f239dc74300bce8d0afe.mockapi.io/users"
    data = {"Name": "Priya", "City": "Chennai", "Country": "India"}

    # Define task to be performed by the simulated user
    @task
    # Perform HTTP GET request
    def get_data(self):
        with self.client.get(self.url + '/' + "8", catch_response=True) as response:
            if response.status_code == 200:
                print(response.json())
        with self.client.get(self.url + '/' + "12", catch_response=False) as response:
            print(response)
        self.interrupt()

    @task
    # Perform HTTP POST request
    def post_data(self):
        with self.client.post(url=self.url, data=self.data, catch_response=True) as response:
            if response.status_code == 201:
                response.success()
                logging.info("data posted successfully\n")
            else:
                response.failure()
                logging.info("error\n")
            self.interrupt()

    @task
    # Perform HTTP UPDATE request
    def update_data(self):
        response = self.client.put(self.url + "/51", data={"City": "Chennai"})
        if response.status_code == 200:
            print("Status : Success")
            logging.info("Success")
        else:
            print("Status : Failure")
            logging.info("Failed")


# Define a class for inheriting TaskSet
class Mytask(TaskSet):
    # Set a constant pacing of 2 second between tasks
    wait = constant_pacing(2)
    url = "https://65c0f239dc74300bce8d0afe.mockapi.io/users"

    @task
    # Perform HTTP DELETE request
    def delete_data(self):
        length = len(self.client.get(self.url).json())
        for i in range(51, length):
            with self.client.delete(self.url + "/" + str(i), catch_response=True) as response:
                if response.success():
                    # Fire notification for successful deletion
                    send_notification.fire(req_id=1, message="data deleted")
                else:
                    # Fire notification for unsuccessful deletion
                    send_notification.fire(req_id=0, message="data not found")
                self.interrupt()


# Event handler for each request
@events.request.add_listener
def on_request(name, request_type, response_time, **kwargs):
    print(name, request_type, response_time, kwargs)


# Define a class inheriting HttpUser, representing simulated user
class LoadTest_(HttpUser):
    host = "https://65c0f239dc74300bce8d0afe.mockapi.io/users"
    tasks = [Mytask, LoadTest]
