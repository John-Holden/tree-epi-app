FROM debian:bullseye

EXPOSE 3000
RUN apt-get update  && \
    DEBIAN_FRONTEND=noninteractive apt-get -qq install curl gnupg2

RUN curl -sS https://dl.yarnpkg.com/debian/pubkey.gpg | apt-key add -
RUN echo "deb https://dl.yarnpkg.com/debian/ stable main" | tee /etc/apt/sources.list.d/yarn.list
RUN apt-get update &&  \
    DEBIAN_FRONTEND=noninteractive apt-get -qq install yarn

COPY ./run_front.sh .
RUN chmod +x run_front.sh

