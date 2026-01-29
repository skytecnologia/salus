# salus

Salus is a web application that allows health patients to manage their medical records.


python -m uvicorn src.main:app --host 0.0.0.0 --port 8008 --reload --env-file conf/.env.local