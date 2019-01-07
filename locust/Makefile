py-install:
	pip install -r requirements.txt

run: py-install
	locust -f main.py --port 5000 --host=http://app:8080
