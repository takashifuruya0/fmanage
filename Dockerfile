FROM python:3.7
ENV PYTHONUNBUFFERED 1

# WORKDIR /home/
# RUN apt-get update && \
#     apt-get install git -y  && \
#     mkdir -p /var/log/gunicorn && \
#     touch /var/log/gunicorn/logfile && \
#     touch /var/log/gunicorn/elogfile && \
#     git clone https://github.com/takashifuruya0/mune

WORKDIR /home/fmanage
ENV GOOGLE_APPLICATION_CREDENTIALS /home/fmanage/testiam.json
#ADD .env .env
#ADD mune/develop.py mune/develop.py
ADD requirements.txt requirements.txt
RUN pip3 install -r requirements.txt

EXPOSE 8000