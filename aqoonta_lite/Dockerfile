# Use an official Python runtime as a parent image
FROM python:3.9-slim-buster

# Set the working directory in the container
WORKDIR /app

# Copy the requirements.txt first to leverage Docker cache
# If requirements.txt doesn't change, this layer won't rebuild
COPY requirements.txt .

# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of your application code into the container
COPY . .

# Make port 5000 available to the world outside this container
EXPOSE 5000

# Run Flask app using 'flask run' and bind to 0.0.0.0
# This is the crucial change to make Flask accessible from outside the container
CMD ["flask", "run", "--host=0.0.0.0", "--port=5000"]