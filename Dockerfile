# Base image on python 3.12.X
FROM python:3.12

# Prints python std outs directly to terminal
ENV PYTHONUNBUFFERED=1

# Set the directory to work from
WORKDIR /

# Copy our local server files into the server folder
COPY . .

# Install python requirements
RUN pip install -r requirements.txt

# Copy over files
COPY . /

# Expose port
EXPOSE 8000
