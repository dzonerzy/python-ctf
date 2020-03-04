from app import Application
from app import init_app

if __name__ == "__main__":
	init_app(Application)
	print(Application.config)
	Application.run(host="localhost", port=5555)
