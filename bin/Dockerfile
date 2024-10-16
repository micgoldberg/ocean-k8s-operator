# Start from a base image with Python installed
FROM python:3.10-slim

# Set the working directory
WORKDIR /usr/src/app

# Copy the requirements file and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Install Terraform
RUN apt-get update && \
    apt-get install -y wget unzip git && \
    wget -O /tmp/terraform.zip https://releases.hashicorp.com/terraform/1.5.4/terraform_1.5.4_linux_amd64.zip && \
    unzip /tmp/terraform.zip -d /usr/local/bin/ && \
    chmod +x /usr/local/bin/terraform && \
    rm /tmp/terraform.zip

# Copy the operator code and Terraform configuration files into the image
COPY ocean_operator.py .
COPY terraform/ ./terraform/

# Set the entrypoint for the container
ENTRYPOINT ["python", "./ocean_operator.py"]
