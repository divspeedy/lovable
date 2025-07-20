# Lovable Spec Aggregator

This project is a web application that allows users to upload a folder of JSON files, specify a "spec name" to search for, and receive an aggregated JSON file with the results.

## Architecture

The application uses a decoupled architecture:
- **Frontend:** A static web page (HTML, CSS, JavaScript) that runs in the user's browser.
- **Backend:** A Python Flask server that handles file uploads, processing, and API requests.

---

## How to Run Locally

### 1. Backend Setup

First, set up and run the backend server.

- **Navigate to the backend directory:**
  ```bash
  cd backend