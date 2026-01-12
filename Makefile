
#************************************ run - uvicorn - app
run_app11_lin:
	.venv/bin/uvicorn main:main_app --app-dir fastapi-application --host 0.0.0.0 --port 8000 --reload

#************************************ run - uvicorn - app
run_app11_win:
	 .venv\Scripts\uvicorn.exe main:main_app --app-dir fastapi-application --host 0.0.0.0 --port 8000 --reload



#************************************ create - 172.20.0.0/16 - docker network
create-net:
	docker network create -d bridge --subnet=172.20.0.0/16 --ip-range=172.20.0.0/16 --gateway=172.20.0.1 app_net_new

#******************************************************* linux docker-compose
up:
	docker-compose -f docker-compose.yaml build

down:
	docker-compose -f docker-compose.yaml up

#******************************************************* linux alembic
migr_gener:
	venv/bin/alembic revision --autogenerate

migr_to_base:
	venv/bin/alembic upgrade heads

#******************************************************* windows alembic
migr_generW:
	venv/Scripts/alembic revision --autogenerate

migr_to_baseW:
	venv/Scripts/alembic upgrade heads


#******************************************** template -  not working - sudo
chmod:
	sudo chmod -R 755 pg_db/