FROM python

WORKDIR /app

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY ./app /app

CMD ["/bin/bash", "-c", "python main.py"]