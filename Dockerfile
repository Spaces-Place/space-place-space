FROM python:3.9.20-alpine3.19

WORKDIR /code

COPY ./requirements.txt /code/requirements.txt

RUN pip install --no-cache-dir --upgrade -r /code/requirements.txt

COPY ./entry_point.sh /code/entry_point.sh
RUN chmod +x /code/entry_point.sh

COPY ./ ./

EXPOSE 80

CMD ["sh", "/code/entry_point.sh"]
