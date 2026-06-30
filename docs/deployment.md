# Deployment guidance

## Demonstrator use

This repository is designed for local use or a private demonstration environment. It generates only fixed-seed synthetic output and makes no external data calls.

## Local run

```bash
python3 -m venv .venv
source .venv/bin/activate
python3 -m pip install -r requirements.txt
python3 -m streamlit run app.py
```

## Private Streamlit deployment

Use a private repository and configure `app.py` as the entry point. Do not deploy real patient, service-user or operational data into a general demonstrator environment. Any future live pilot should be deployed in an approved, governed environment agreed with the participating organisations.

## Container run

```bash
docker build -t pie-wy-demo .
docker run -p 8501:8501 pie-wy-demo
```
