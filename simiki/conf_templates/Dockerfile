FROM python:2.7.11

WORKDIR /src

COPY . /src
RUN pip install simiki
RUN simiki g

WORKDIR /src/output
CMD ["python", "-m", "SimpleHTTPServer", "8000"]

EXPOSE 8000
