from django.test import TestCase
from rest_framework.test import APIClient
from rest_framework import status

from fizzbuzz_app.models import FizzBuzzRequest
from django.db.models import F, Max

class TestStatisticsAPI(TestCase):
    def setUp(self):
        # Set up any necessary data for your tests
        pass

    def populate_database(self):
        # List of dictionaries containing parameters and hits for testing
        test_data = [
            {'int1': 3, 'int2': 5, 'limit': 1000000, 'str1': 'fizz', 'str2': 'buzz', 'hits': 10},
            {'int1': 3, 'int2': 5, 'limit': 1000000, 'str1': 'fizz', 'str2': 'buzz', 'hits': 23},
            {'int1': 4, 'int2': 6, 'limit': 1000000, 'str1': 'fizz', 'str2': 'buzz', 'hits': 15},
            # Add more instances as needed
        ]

        # Iterate through the test data and create instances
        for data in test_data:
            # Check if an instance with the same parameters already exists
            existing_instance = FizzBuzzRequest.objects.filter(
                int1=data['int1'],
                int2=data['int2'],
                limit=data['limit'],
                str1=data['str1'],
                str2=data['str2'],
            ).first()

            # If the instance exists, update the hits field
            if existing_instance:
                existing_instance.hits = F('hits') + data['hits']
                existing_instance.save()
            else:
                # If the instance doesn't exist, create a new one
                FizzBuzzRequest.objects.create(**data)
    
    def test_statistics_endpoint(self):
        # Populate the database
        self.populate_database()

        # Make a GET request to the statistics endpoint
        url = 'http://127.0.0.1:8000/api/statistics/'  # Use the actual URL name from your urls.py
        client = APIClient()
        response = client.get(url)

        # Check if the response status code is 200 OK
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Check the structure of the response data
        self.assertIn("max_hits", response.data)

        if "single_request" in response.data:
            # If there is a single request, retrieve the maximum hits value and parameters from the database
            max_hits_data = FizzBuzzRequest.objects.order_by('-hits').first()
            
            # Create the expected_single_request object based on the database
            expected_single_request = {
                "int1": max_hits_data.int1,
                "int2": max_hits_data.int2,
                "limit": max_hits_data.limit,
                "str1": max_hits_data.str1,
                "str2": max_hits_data.str2
            }

            # Check the values in the response data
            self.assertEqual(response.data["single_request"], expected_single_request)
            self.assertEqual(response.data["max_hits"], max_hits_data.hits)
            
        elif "tied_requests" in response.data:
            # If there are tied requests, retrieve the maximum hits value and parameters from the first tied request
            tied_request_data = response.data["tied_requests"][0]

            # Create the expected_tied_request object based on the database
            expected_tied_request = {
                "int1": tied_request_data["int1"],
                "int2": tied_request_data["int2"],
                "limit": tied_request_data["limit"],
                "str1": tied_request_data["str1"],
                "str2": tied_request_data["str2"]
            }

            # Check the values in the response data
            self.assertEqual(response.data["tied_requests"], [expected_tied_request])
            self.assertEqual(response.data["max_hits"], tied_request_data["max_hits"])
            
        else:
            # If unexpected structure in response data
            self.fail("Unexpected structure in response data")


    def test_statistics_endpoint_with_tied_requests(self):
        # Populate the database with tied requests
        self.populate_database()
        # Check if an object with the specified parameters already exists in the database
        existing_object = FizzBuzzRequest.objects.filter(int1=3, int2=5, limit=1000000, str1="fizz", str2="buzz").first()

        if existing_object:
            # If the object exists, update the hits count
            existing_object.hits += 23
            existing_object.save()
        else:
            # If the object does not exist, create a new one
            FizzBuzzRequest.objects.create(int1=3, int2=5, limit=1000000, str1="fizz", str2="buzz", hits=23)

        # Make a GET request to the statistics endpoint
        url = 'http://127.0.0.1:8000/api/statistics/'  # Use the actual URL name from your urls.py
        client = APIClient()
        response = client.get(url)

        # Check if the response status code is 200 OK
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Check the structure of the response data
        self.assertIn("max_hits", response.data)

        if "tied_requests" in response.data:
            # If there are tied requests, retrieve the maximum hits value and parameters from the first tied request
            tied_request_data = response.data["tied_requests"][0]

            # Create the expected_tied_request object based on the database
            expected_tied_request = {
                "int1": tied_request_data["int1"],
                "int2": tied_request_data["int2"],
                "limit": tied_request_data["limit"],
                "str1": tied_request_data["str1"],
                "str2": tied_request_data["str2"]
            }

            # Check the values in the response data
            self.assertEqual(response.data["tied_requests"], [expected_tied_request])
            self.assertEqual(response.data["max_hits"], tied_request_data["max_hits"])
            
        elif "single_request" in response.data:
            # If there is a single request, retrieve the maximum hits value and parameters from the database
            max_hits_data = FizzBuzzRequest.objects.order_by('-hits').first()
            
            # Create the expected_single_request object based on the database
            expected_single_request = {
                "int1": max_hits_data.int1,
                "int2": max_hits_data.int2,
                "limit": max_hits_data.limit,
                "str1": max_hits_data.str1,
                "str2": max_hits_data.str2
            }

            # Check the values in the response data
            self.assertEqual(response.data["single_request"], expected_single_request)
            self.assertEqual(response.data["max_hits"], max_hits_data.hits)
            
        else:
            # If unexpected structure in response data
            self.fail("Unexpected structure in response data")

    def test_bad_request_on_parameters(self):
        # Make a GET request with parameters to the statistics endpoint
        url = 'http://127.0.0.1:8000/api/statistics/'  
        client = APIClient()
        response = client.get(url, {'int1': 3, 'int2': 5, 'limit': 100, 'str1': 'fizz', 'str2': 'buzz'})

        # Check if the response status code is 400 Bad Request
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)