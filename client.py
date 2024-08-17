import requests
from time import sleep

API_URL = "http://localhost:8000"  # Replace with your API URL if different

def submit_url(url):
    response = requests.post(f"{API_URL}/analyze/", json={"url": url})
    if response.status_code == 200:
        print(f"Submitted URL: {url} successfully.")
    else:
        print(f"Failed to submit URL: {url}. Status code: {response.status_code}, Response: {response.text}")

def get_task_status(url):
    response = requests.get(f"{API_URL}/status/", params={"url": url})
    if response.status_code == 200:
        status = response.json().get("status")
        print(f"Status for URL {url}: {status}")
        return status
    else:
        print(f"Failed to get status for URL: {url}. Status code: {response.status_code}, Response: {response.text}")
        return None

if __name__ == "__main__":
    urls = [
        "https://example1.com",
        # "https://httpbin.org/get",
        # "https://jsonplaceholder.typicode.com/posts"
    ]

    # Submit URLs for analysis
    for url in urls:
        submit_url(url)
        sleep(1)  # Short delay between submissions

    # Check the status of the tasks
    for url in urls:
        status = None
        while status != 'done':
            status = get_task_status(url)
            if status == 'done':
                print(f"Task for URL {url} is completed.")
            else:
                print(f"Task for URL {url} is still in progress. Checking again in 10 seconds.")
                sleep(10)
