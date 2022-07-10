FROM debian:bullseye

RUN apt-get update  && \
    DEBIAN_FRONTEND=noninteractive apt-get -qq install python3 pip

COPY src/requirements.txt .
COPY src/run_back.sh .
RUN pip install -r requirements.txt
EXPOSE 5000
RUN chmod +x run_back.sh


