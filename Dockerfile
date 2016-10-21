FROM python:3.5

COPY ./ /root
WORKDIR /root

RUN pip install -r requirements.txt
RUN python setup.py install

EXPOSE 8000

CMD ["./docker-entrypoint.sh"]
