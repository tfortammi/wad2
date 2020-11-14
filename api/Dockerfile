FROM python:3.7
RUN apt-get update -y
RUN apt-get install -y python-pip python-dev build-essential
COPY . main.py
COPY . wad-project-backup-4f432f39d484.json
RUN pip install -r requirements.txt
ENTRYPOINT [ "python" ]
CMD ["main.py"]