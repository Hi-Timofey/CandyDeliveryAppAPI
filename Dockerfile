FROM python:3.8

EXPOSE 8080

RUN apt -y update && apt -y upgrade

WORKDIR /app

# Install 
COPY install.sh /app 
COPY requirements.txt /app
RUN sh install.sh

# Copying api data
COPY ./data/ /app/data/
COPY config.cfg /app
COPY app.py /app
COPY run.sh /app
COPY tests.py /app

# Run app.py when the container launches
RUN chmod u+x /app/run.sh
# ENTRYPOINT [ "bash" ]
CMD ./run.sh
