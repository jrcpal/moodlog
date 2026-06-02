.PHONY: dev backend frontend install

dev:
	make -j2 backend frontend

backend:
	cd backend && source venv/bin/activate && python manage.py runserver 8001

frontend:
	cd frontend && npm run dev

install:
	cd backend && python -m venv venv && source venv/bin/activate && pip install -r requirements.txt
	cd frontend && npm install
