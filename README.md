# FizzBuzz API

The FizzBuzz API provides two endpoints to perform FizzBuzz calculations and retrieve statistics.

## Endpoints

1. **FizzBuzz Calculation**
   - **Endpoint:** `/api/fizzbuzz`
   - **HTTP Methods:**
     - `GET` with query parameters
     - `POST` with form-data, urlencoded data, or raw data
   - **Parameters:**
     - `int1` (integer): First FizzBuzz divisor
     - `int2` (integer): Second FizzBuzz divisor
     - `limit` (integer): Upper limit for FizzBuzz sequence
     - `str1` (string): String replacement for multiples of `int1`
     - `str2` (string): String replacement for multiples of `int2`
   - **Response:**
     - Successful response returns FizzBuzz sequence in JSON format.
     - Possible errors: Bad Request (400) if parameters are missing or incorrect.

2. **Statistics**
   - **Endpoint:** `/api/statistics`
   - **HTTP Method:** `GET` with no parameters
   - **Response:**
     - Successful response returns statistics in JSON format.
     - Possible errors: Bad Request (400) or Internal Server Error (500).

## Getting Started

1. Clone the repository:

   ```bash
   git clone https://github.com/yourusername/fizzbuzz-api.git
   cd fizzbuzz-api
2. Build instructions
   
## Requirements
Python 3.x
Django
pip install django
djangorestframework
pip install djangorestframework

## List of Third-Party Libraries Used:
# Django:

Purpose: Django is a high-level Python web framework that encourages rapid development and clean, pragmatic design. It provides a robust set of tools for building web applications.
How Used: Our project is built on the Django framework, leveraging its ORM for database interactions, its views for handling HTTP requests, and its admin interface for managing data.

# Django REST Framework:

Purpose: Django REST Framework is a powerful and flexible toolkit for building Web APIs in Django. It provides serializers, authentication, and other utilities for building RESTful APIs.
How Used: We use Django REST Framework to build and expose our API endpoints, making it easy to handle HTTP methods, validate input, and serialize responses.

# Rest Framework Decorators:

Purpose: This library extends Django REST Framework with additional decorators for customizing the behavior of API views.
How Used: We utilize these decorators to enhance our API views, adding specific functionality or behavior to certain endpoints.

# Django Pagination:

Purpose: Django Pagination is used to handle paginated responses, making it easier to manage large sets of data.
How Used: We apply Django Pagination to ensure that responses from certain API endpoints are paginated, enhancing performance and user experience.

## Contributing
Feel free to contribute to the development of the FizzBuzz API. Create a pull request or open an issue if you find any bugs or have suggestions.

