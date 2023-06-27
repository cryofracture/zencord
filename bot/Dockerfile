FROM python:3.9.5

RUN apt-get update
RUN apt-get upgrade -y

# Set the working directory
WORKDIR /zencord_bot

# Copy the requirements file and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY *.py .
COPY .env .

CMD ["python", "zencord_bot.py"]