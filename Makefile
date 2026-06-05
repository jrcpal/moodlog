.PHONY: dev backend frontend install

dev:
	make -j2 backend frontend

backend:
	bash -c 'cd backend && source venv/bin/activate && python3 manage.py runserver 8001'

frontend:
	bash -c 'source ~/.nvm/nvm.sh && nvm use && cd frontend && npm run dev'

install:
	cd backend && python3 -m venv venv && source venv/bin/activate && pip install -r requirements.txt
	cd frontend && npm install
