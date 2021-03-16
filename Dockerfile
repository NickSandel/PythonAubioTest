FROM python:3.8-slim
WORKDIR /app
COPY requirements.txt requirements.txt
RUN apt-get update \
&& apt-get install gcc -y \
&& apt-get clean
RUN pip install --upgrade setuptools
RUN pip install -r requirements.txt
COPY . .
CMD [ "python3", "-m" , "flask", "run", "--host=0.0.0.0"]