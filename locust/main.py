from locust import HttpLocust, TaskSet, task


class WebsiteTasks(TaskSet):

    @task
    def add_users(self):
        self.client.post("/add_records", {
            "active_stream_name": "marks-new-stream",
            "num_users": "1000"
        })


class WebsiteUser(HttpLocust):
    task_set = WebsiteTasks
    min_wait = 5000
    max_wait = 15000
