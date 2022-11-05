FROM python:3.11

COPY requirements.txt .

RUN python -mpip install --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt

# `/app` is mounted to the `src` dir in the
# `docker run` command.
WORKDIR /app
COPY ./src .

# You will still probably have to source this
# manually from inside the container
COPY ./bash.bashrc /root/.bashrc

RUN mkdir /data
RUN mkdir /ctdata

CMD ["python", "app.py"]
