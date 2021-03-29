FROM python:3.8

# Preparing
EXPOSE 8080
RUN apt -y update && apt -y upgrade && apt -y install python3 python-pip

WORKDIR /app

# Install 
# COPY install.sh /app 
COPY requirements.txt /app
# RUN sh install.sh
RUN python3 -m pip install -r requirements.txt

# Copying api data
COPY ./data/ /app/data/
COPY config.cfg /app
COPY app.py /app
# COPY run.sh /app
COPY tests.py /app

# Run ./run.sh to start web server
# RUN chmod u+x /app/run.sh
# RUN ./run.sh
ENV API_CONFIG=config.cfg
ENTRYPOINT ["python3"]
CMD ["app.py"]
