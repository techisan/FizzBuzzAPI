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

## Requirements
Python 3.x
Django
djangorestframework

## Contributing
Feel free to contribute to the development of the FizzBuzz API. Create a pull request or open an issue if you find any bugs or have suggestions.

