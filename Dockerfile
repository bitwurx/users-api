FROM python:3.5

ADD ./ /root
WORKDIR /root

RUN pip install -r requirements.txt
RUN python setup.py install

RUN chmod +x docker-entrypoint.sh

ENTRYPOINT ["./docker-entrypoint.sh"]

EXPOSE 5000
