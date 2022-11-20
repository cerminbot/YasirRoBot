# Base Docker
FROM ubuntu:22.10

# Setup Working Directory
WORKDIR /YasirRoBot
RUN chmod 777 /YasirRoBot

# Installing basic packages
RUN apt-get update -y && apt install python3-pip apt-utils -y

# Install Requirements
COPY requirements.txt .
RUN pip3 install --no-cache-dir -r requirements.txt

COPY . .
# Set CMD Bot
CMD ["python3", "-m", "YasirRoBot"]
