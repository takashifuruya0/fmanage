FROM python:3.7
ENV PYTHONUNBUFFERED 1
ENV DISPLAY=:99
EXPOSE 8000

# install google chrome
RUN wget -q -O - https://dl-ssl.google.com/linux/linux_signing_key.pub | apt-key add - && \
    sh -c 'echo "deb [arch=amd64] http://dl.google.com/linux/chrome/deb/ stable main" >> /etc/apt/sources.list.d/google-chrome.list'  && \
    apt-get -y update && apt-get install -y google-chrome-stable

# install chromedriver
RUN apt-get install -yqq unzip && \
    wget -O /tmp/chromedriver.zip http://chromedriver.storage.googleapis.com/`curl -sS chromedriver.storage.googleapis.com/LATEST_RELEASE`/chromedriver_linux64.zip && \
    unzip /tmp/chromedriver.zip chromedriver -d /usr/local/bin/ && \
    rm /tmp/chromedriver.zip
# RUN apt update && apt upgrade -y
COPY requirements.txt requirements.txt
RUN pip3 install -r requirements.txt
# COPY files
COPY ./ /home/fmanage/
WORKDIR /home/fmanage
