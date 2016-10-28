FROM python:3.5

WORKDIR /root

COPY requirements.txt /root/requirements.txt

RUN pip install -r requirements.txt

COPY src /root

RUN python setup.py install

COPY docker-entrypoint.sh /root/docker-entrypoint.sh

ENTRYPOINT ["./docker-entrypoint.sh"]

EXPOSE 80

CMD ["start-server"]
