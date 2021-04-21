FROM python:3.8-slim-buster

ENV DEBIAN_FRONTEND noninteractive
ENV USER username@dms
ENV PASSWORD supersecretpassword
ENV ADDRESS dms.local
ENV DN DC=dms,DC=local
ENV GROUPNAME 3D Printing Basics
ENV PORT 80

WORKDIR /adcache
COPY requirements.txt requirements.txt
RUN pip3 install -r requirements.txt

COPY . .

#RUN apt-get update \
#  && pip3 install flask waitress dotenv

#CMD [ "python3", "-m" , "flask", "run", "--host=0.0.0.0"]

ENTRYPOINT ["python3 adcache.py"]