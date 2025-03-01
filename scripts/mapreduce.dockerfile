FROM python:3.8-slim  

WORKDIR /app

COPY . .

RUN pip install --upgrade pip
RUN  pip install pandas

RUN chmod +x mapper.py

CMD ["bash"]
