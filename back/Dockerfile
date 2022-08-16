FROM debian:bullseye

RUN apt-get update  && \
    DEBIAN_FRONTEND=noninteractive apt-get -qq install python3 pip libjsoncpp-dev ffmpeg

COPY src/requirements.txt .
RUN pip install -r requirements.txt
EXPOSE 5000
COPY run_back.sh .
RUN chmod +x run_back.sh


