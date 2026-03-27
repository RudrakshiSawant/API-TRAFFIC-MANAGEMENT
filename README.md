# Containerized API Traffic Management System with CI/CD Deployment

## Project Overview
This project is a simple backend application developed using Flask to manage and regulate API traffic.

## Features
- API request handling
- Request validation
- Rate limiting
- Request logging
- Health check endpoint
- Docker containerization
- CI/CD pipeline using GitHub Actions

## API Endpoints

### `/api/data`
Returns sample API response.

### `/health`
Returns application health status.

## Technologies Used
- Python
- Flask
- Docker
- GitHub Actions
- Docker Compose

## Run Locally
```bash
pip install -r requirements.txt
python app.py
```

## Run with Docker
```bash
docker build -t api-traffic-management .
docker run -p 5000:5000 api-traffic-management
```

## Run with Docker Compose
```bash
docker-compose up --build
```
