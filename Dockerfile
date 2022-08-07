FROM python:3.8.5-alpine
WORKDIR /dir
COPY get.py ./
RUN apk add --no-cache gcc libc-dev
RUN pip3 install --no-cache-dir --upgrade pyrebase pytz beautifulsoup4 requests
CMD [ "python", "-u", "get.py"]
