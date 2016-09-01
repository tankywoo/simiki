FROM python:2.7.11

WORKDIR /src

COPY . /src
RUN pip install simiki
RUN simiki g

CMD ["simiki", "p", "-w", "--host", "0.0.0.0", "--port", "8000"]

EXPOSE 8000
