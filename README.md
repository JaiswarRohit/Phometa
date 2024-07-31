# Phometa

Phometa is a secure phone book application built with Flask, SQLAlchemy, and PostgreSQL. It includes features such as user registration, login, contact management, spam number marking, and user search. The application uses JWT for user authentication and Flask-Migrate for database migrations.

## Prerequisites

- Python version >= 3.10
- PostgreSQL database

## Installation

1. **Clone the repository:**

   ```sh
   git clone https://github.com/yourusername/phometa.git
   cd phometa
   ```

2. **Create a virtual environment and activate it:**

   ```sh
   python -m venv venv
   source venv/bin/activate  # On Windows use `venv\Scripts\activate`
   ```

3. **Install the required packages:**

   ```sh
   pip install -r requirements.txt
   ```

## Configuration

1. **Set up the PostgreSQL database:**
   Create a new database in PostgreSQL.

   ```sql
   CREATE DATABASE phometa;
   ```

2. **Update the `SQLALCHEMY_DATABASE_URI` variable in `app.py`:**
   Open `app.py` and update the `SQLALCHEMY_DATABASE_URI` with your local database URL.

   ```python
   phometa.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://username:password@localhost:5432/Phometa'
   ```

## Database Migration

1. **Initialize the migration folder:**

   ```sh
   flask db init
   ```

2. **Generate the migration scripts:**

   ```sh
   flask db migrate -m "Initial migration."
   ```

3. **Apply the migrations to the database:**

   ```sh
   flask db upgrade
   ```

## Running the Application

1. **Start the Flask application:**

   ```sh
   python app.py
   ```

2. The application will be accessible at `http://127.0.0.1:5000/`.

## API Endpoints

### User Registration

- **URL:** `/register`
- **Method:** `POST`
- **Payload:**

  ```json
  {
    "name": "John Doe",
    "phone": "1234567890",
    "email": "john.doe@example.com",
    "password": "password123"
  }
  ```

- **Response:**

  ```json
  {
    "message": "User created successfully."
  }
  ```

### User Login

- **URL:** `/login`
- **Method:** `POST`
- **Payload:**

  ```json
  {
    "phone": "1234567890",
    "password": "password123"
  }
  ```

- **Response:**

  ```json
  {
    "access_token": "your_access_token"
  }
  ```

### Add Contact

- **URL:** `/add-contact`
- **Method:** `POST`
- **Headers:**

  ```json
  {
    "Authorization": "Bearer your_access_token"
  }
  ```

- **Payload:**

  ```json
  {
    "name": "Jane Doe",
    "phone": "0987654321"
  }
  ```

- **Response:**

  ```json
  {
    "message": "Contact added successfully."
  }
  ```

### Mark Spam

- **URL:** `/mark-spam`
- **Method:** `POST`
- **Headers:**

  ```json
  {
    "Authorization": "Bearer your_access_token"
  }
  ```

- **Payload:**

  ```json
  {
    "phone": "0987654321"
  }
  ```

- **Response:**

  ```json
  {
    "message": "Number marked as spam."
  }
  ```

### Search User

- **URL:** `/search`
- **Method:** `POST`
- **Headers:**

  ```json
  {
    "Authorization": "Bearer your_access_token"
  }
  ```

- **Payload:**

  ```json
  {
    "name": "Jane Doe",
    "phone": "0987654321"
  }
  ```

- **Response:**

  ```json
  {
    "message": "User(s) Found",
    "data": [
      {
        "name": "Jane Doe",
        "phone": "0987654321",
        "spam_reports": 0,
        "contact_name": "Jane",
        "email": "jane.doe@example.com"
      }
    ]
  }
  ```

### Logout

- **URL:** `/logout`
- **Method:** `POST`
- **Headers:**

  ```json
  {
    "Authorization": "Bearer your_access_token"
  }
  ```

- **Response:**

  ```json
  {
    "message": "User logged out successfully. Token Expired."
  }
  ```

## Data Generation Script

The `data.py` script can be used to generate random data and test the API endpoints.

1. **Update the API endpoint in `data.py`:**

   ```python
   api_endpoint = "http://127.0.0.1:5000/"
   ```

2. **Run the script:**

   ```sh
   python data.py
   ```

This script will register random users, log them in, add contacts, mark numbers as spam, and log out.
