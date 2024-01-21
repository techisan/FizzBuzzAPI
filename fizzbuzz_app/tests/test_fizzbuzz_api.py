from django.test import TestCase
from rest_framework.test import APIClient
from rest_framework import status

from fizzbuzz_app.models import FizzBuzzRequest
from fizzbuzz_app.tests import test_statistics_api
import json
import os
from pathlib import Path
from django.conf import settings
import filecmp

class TestFizzBuzzAPI(TestCase):
    def read_test_data(self, filename):
        test_path = settings.TEST_DIRS[0]
        file_path = os.path.join(test_path, 'test_data',filename)
        
        with open(file_path, 'r') as file:
            return json.load(file)
        
    def compare_output_with_expected(self, response_get, expected_output_file):
        # File path for the streaming chunk
        last_streaming_chunk_file = 'last_streaming_chunk1.txt'

        # Read the expected output file
        with open(expected_output_file, 'r') as file:
            expected_output_str = file.read()

        # Initialize a list to store streaming chunks
        response_chunks = []

        try:
            # Open the file to write streaming chunks
            with open(last_streaming_chunk_file, 'w') as response_file:
                # Iterate over the streaming content and decode chunks
                for chunk in response_get.streaming_content:
                    chunk_str = chunk.decode('utf-8', 'replace')
                    response_chunks.append(chunk_str)

                    # Write each chunk to the file immediately
                    response_file.write(chunk_str)

                    try:
                        # Try loading the chunk as a JSON object
                        response_json = json.loads(chunk_str)

                        # Check if the response_json matches any of the expected outputs
                        if json.dumps(response_json, indent=2) in expected_output_str:
                            print("Match found!")
                            break
                    except json.JSONDecodeError:
                        # If parsing fails for an individual JSON chunk, continue to the next one
                        continue

            # Compare the contents of the two files
            files_match = filecmp.cmp(last_streaming_chunk_file, expected_output_file)

            # Check if files match
            return files_match

        except Exception as e:
            print(f"An error occurred: {e}")
            return False

        finally:
            # Remove the files after the comparison
            if os.path.exists(last_streaming_chunk_file):
                os.remove(last_streaming_chunk_file)

    def send_request(self, test_case):
        url = 'http://127.0.0.1:8000/api/fizzbuzz/'

        if test_case["input_type"] == "GET":
            response = self.client.get(url, data=test_case["params"])

        elif test_case["input_type"] == "POST form-data":
            response = self.client.post(url, data=test_case["data"], format='multipart')

        elif test_case["input_type"] == "POST urlencoded":
            response = self.client.post(url, data=test_case["data"], content_type='application/x-www-form-urlencoded')

        elif test_case["input_type"] == "POST raw_data":
            response = self.client.post(url, data=test_case["data"], content_type='application/json')

        return response
    def test_basecase_api(self):
        client = APIClient()

        # Test Case 1: Valid base case input for GET using params
        url = '/api/fizzbuzz/?int1=3&int2=5&limit=100&str1=fizz&str2=buzz'
        data = None  # No data for GET request
        response_get = client.get(url, data)
        expected_output = self.read_test_data('basecase_get_output.json')

        self.assertEqual(response_get.status_code, status.HTTP_200_OK)
        self.assertEqual(response_get.data, expected_output)

        # Test Case 2: Valid base case input for POST using params
        response_post = client.post(url, data)
        expected_output = self.read_test_data('noinput_case_output.json')

        self.assertEqual(response_post.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response_post.data, expected_output)

    def test_noinput_api(self):
        client = APIClient()
        # Test Case 2: Invalid input (no input parameters) for GET
        url = '/api/fizzbuzz/'
        data = None
        response_get = client.get(url,data)
        expected_output = self.read_test_data('noinput_case_output.json')
        self.assertEqual(response_get.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response_get.data, expected_output)

        # Test Case 2: Invalid input (no input parameters) for POST
        response_post = client.post(url,data)
        expected_output = self.read_test_data('noinput_case_output.json')
        self.assertEqual(response_post.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response_post.data, expected_output)

    def test_lessthan1Mform_api(self):
            client = APIClient()

            # Test Case 1: Valid base case input for GET using body form-data
            url = '/api/fizzbuzz/'
            data = None  # No data for GET request
            
            response_get = client.get(url, data)
            expected_output = self.read_test_data('noinput_case_output.json')

            self.assertEqual(response_get.status_code, status.HTTP_400_BAD_REQUEST)
            self.assertEqual(response_get.data, expected_output)

            # Test Case 2: Valid base case input for POST using body form-data
            post_data = {
            'int1': '5',
            'int2': '7',
            'limit': '100',
            'str1': 'north',
            'str2': 'south'
            }
            response_post = client.post(url, post_data)
            expected_output = self.read_test_data('lessthan1Mform_post_output.json')

            self.assertEqual(response_post.status_code, status.HTTP_200_OK)
            self.assertEqual(response_post.data, expected_output)

    def test_lessthan1Murlencoded_api(self):
            client = APIClient()

            # Test Case 1: Valid base case input for GET using body x_www_form_urlencoded
            url = '/api/fizzbuzz/'
            data = None  # No data for GET request
            
            response_get = client.get(url, data)
            expected_output = self.read_test_data('noinput_case_output.json')

            self.assertEqual(response_get.status_code, status.HTTP_400_BAD_REQUEST)
            self.assertEqual(response_get.data, expected_output)

            # Test Case 2: Valid base case input for POST using body x_www_form_urlencoded
            x_www_form_urlencoded_data = 'int1=2&int2=3&limit=50&str1=east&str2=west'

            response_post = client.post(url, x_www_form_urlencoded_data, content_type='application/x-www-form-urlencoded')
            expected_output = self.read_test_data('lessthan1Murlencoded_post_output.json')

            self.assertEqual(response_post.status_code, status.HTTP_200_OK)
            self.assertEqual(response_post.data, expected_output)
    
    def test_lessthan1Mrawdata_api(self):
            client = APIClient()

            # Test Case 1: Valid base case input for GET using body application/json
            url = '/api/fizzbuzz/'
            data = None  # No data for GET request
            
            response_get = client.get(url, data)
            expected_output = self.read_test_data('noinput_case_output.json')

            self.assertEqual(response_get.status_code, status.HTTP_400_BAD_REQUEST)
            self.assertEqual(response_get.data, expected_output)

            # Test Case 2: Valid base case input for POST using body application/json
            raw_json_data = '{"int1": "2", "int2": "5", "limit": "70", "str1": "tri", "str2":"ram"}'

            response_post = client.post(url, raw_json_data, content_type='application/json')
            expected_output = self.read_test_data('lessthan1Mrawjson_post_output.json')

            self.assertEqual(response_post.status_code, status.HTTP_200_OK)
            self.assertEqual(response_post.data, expected_output)

    def test_1Mbasecase_api(self):
        client = APIClient()

        # Test Case 1: Valid base case input for GET using params; increase output size in POSTMAN to 100MB
        url = '/api/fizzbuzz/?int1=3&int2=5&limit=1000000&str1=fizz&str2=buzz'
        data = None  # No data for GET request
        response_get = client.get(url, data)

        # File paths
        expected_output_file = os.path.join(settings.TEST_DIRS[0], 'test_data', 'basecase1Mparam_output.txt')
        # Call the comparison function
        result = self.compare_output_with_expected(response_get, expected_output_file)

        # Assertion based on the comparison result
        self.assertTrue(result, "Files match.")

        # Test Case 2: Valid base case input for POST using params;increase output size in POSTMAN to 100MB
        response_post = client.post(url, data)
        expected_output = self.read_test_data('noinput_case_output.json')

        self.assertEqual(response_post.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response_post.data, expected_output)
    
    def test_10Mform_api(self):
        client = APIClient()

        # Test Case 1: Valid base case input for GET using form-data; increase output size in POSTMAN to 100MB
        url = '/api/fizzbuzz/'
        data = None  # No data for GET request
        response_get = client.get(url, data)

        expected_output = self.read_test_data('noinput_case_output.json')

        self.assertEqual(response_get.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response_get.data, expected_output)

        # Test Case 2: Valid base case input for POST using form-data;increase output size in POSTMAN to 100MB
        post_data = {
            'int1': '5',
            'int2': '7',
            'limit': '10000000',
            'str1': 'north',
            'str2': 'south'
            }
        response_post = client.post(url, post_data)
        
        # File paths
        expected_output_file = os.path.join(settings.TEST_DIRS[0], 'test_data', 'anothercase10Mform_output.txt')
        # Call the comparison function
        result = self.compare_output_with_expected(response_post, expected_output_file)

        # Assertion based on the comparison result
        self.assertTrue(result, "Files match.")

    def test_1Murlencoded_api(self):
        client = APIClient()

        # Test Case 1: Valid base case input for GET using form-data; increase output size in POSTMAN to 100MB
        url = '/api/fizzbuzz/'
        data = None  # No data for GET request
        response_get = client.get(url, data)

        expected_output = self.read_test_data('noinput_case_output.json')

        self.assertEqual(response_get.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response_get.data, expected_output)

        # Test Case 2: Valid base case input for POST using form-data;increase output size in POSTMAN to 100MB
        x_www_form_urlencoded_data = 'int1=2&int2=3&limit=1000000&str1=east&str2=west'
        response_post = client.post(url, x_www_form_urlencoded_data, content_type='application/x-www-form-urlencoded')
        
        # File paths
        expected_output_file = os.path.join(settings.TEST_DIRS[0], 'test_data', '1Murlencoded_output.txt')
        # Call the comparison function
        result = self.compare_output_with_expected(response_post, expected_output_file)

        # Assertion based on the comparison result
        self.assertTrue(result, "Files match.")

    def test_1Mrawdata_api(self):
        client = APIClient()

        # Test Case 1: Valid base case input for GET using form-data; increase output size in POSTMAN to 100MB
        url = '/api/fizzbuzz/'
        data = None  # No data for GET request
        response_get = client.get(url, data)

        expected_output = self.read_test_data('noinput_case_output.json')

        self.assertEqual(response_get.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response_get.data, expected_output)

        # Test Case 2: Valid base case input for POST using form-data;increase output size in POSTMAN to 100MB
        raw_json_data = '{"int1": "2", "int2": "5", "limit": "1000000", "str1": "tri", "str2":"ram"}'
        response_post = client.post(url, raw_json_data, content_type='application/json')
        
        # File paths
        expected_output_file = os.path.join(settings.TEST_DIRS[0], 'test_data', '1Mrawdata_output.txt')
        # Call the comparison function
        result = self.compare_output_with_expected(response_post, expected_output_file)

        # Assertion based on the comparison result
        self.assertTrue(result, "Files match.")

    def test_int1_empty_input_types(self):

        test_cases = [
            {"input_type": "GET", "params": {"int1": '', "int2": 3, "limit": 100, "str1": "res", "str2": "szu"}},
            {"input_type": "POST form-data", "data": {"int1": '', "int2": 3, "limit": 100, "str1": "res", "str2": "szu"}},
            {"input_type": "POST urlencoded", "data": "int1=&int2=3&limit=100&str1=res&str2=szu"},
            {"input_type": "POST raw_data", "data": json.dumps({"int1": '', "int2": 3, "limit": 100, "str1": "res", "str2": "szu"})}
        ]

        for test_case in test_cases:
            with self.subTest(test_case=test_case):
                response = self.send_request(test_case)
                expected_output = self.read_test_data('int1empty_output.json')

                self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
                self.assertEqual(response.data, expected_output)

    def test_int2_empty_input_types(self):

        test_cases = [
            {"input_type": "GET", "params": {"int1": 3, "int2": '', "limit": 100, "str1": "res", "str2": "szu"}},
            {"input_type": "POST form-data", "data": {"int1": 3, "int2": "", "limit": 100, "str1": "res", "str2": "szu"}},
            {"input_type": "POST urlencoded", "data": "int1=3&int2=&limit=100&str1=res&str2=szu"},
            {"input_type": "POST raw_data", "data": json.dumps({"int1": 3, "int2": "", "limit": 100, "str1": "res", "str2": "szu"})}
        ]

        for test_case in test_cases:
            with self.subTest(test_case=test_case):
                response = self.send_request(test_case)
                expected_output = self.read_test_data('int2empty_output.json')

                self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
                self.assertEqual(response.data, expected_output)

    def test_limit_empty_input_types(self):

        test_cases = [
            {"input_type": "GET", "params": {"int1": 3, "int2": 5, "limit": '', "str1": "res", "str2": "szu"}},
            {"input_type": "POST form-data", "data": {"int1": 3, "int2": 5, "limit": "", "str1": "res", "str2": "szu"}},
            {"input_type": "POST urlencoded", "data": "int1=3&int2=5&limit=&str1=res&str2=szu"},
            {"input_type": "POST raw_data", "data": json.dumps({"int1": 3, "int2": 5, "limit": "", "str1": "res", "str2": "szu"})}
        ]

        for test_case in test_cases:
            with self.subTest(test_case=test_case):
                response = self.send_request(test_case)
                expected_output = self.read_test_data('limitempty_output.json')

                self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
                self.assertEqual(response.data, expected_output)

    def test_str1_empty_input_types(self):

        test_cases = [
            {"input_type": "GET", "params": {"int1": 3, "int2": 5, "limit": 100, "str1": "", "str2": "szu"}},
            {"input_type": "POST form-data", "data": {"int1": 3, "int2": 5, "limit": 100, "str1": "", "str2": "szu"}},
            {"input_type": "POST urlencoded", "data": "int1=3&int2=5&limit=100&str1=&str2=szu"},
            {"input_type": "POST raw_data", "data": json.dumps({"int1": 3, "int2": 5, "limit": 100, "str1": "", "str2": "szu"})}
        ]

        for test_case in test_cases:
            with self.subTest(test_case=test_case):
                response = self.send_request(test_case)
                expected_output = self.read_test_data('str1empty_output.json')

                self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
                self.assertEqual(response.data, expected_output)

    def test_str2_empty_input_types(self):

        test_cases = [
            {"input_type": "GET", "params": {"int1": 3, "int2": 5, "limit": 100, "str1": "res", "str2": ""}},
            {"input_type": "POST form-data", "data": {"int1": 3, "int2": 5, "limit": 100, "str1": "res", "str2": ""}},
            {"input_type": "POST urlencoded", "data": "int1=3&int2=5&limit=100&str1=res&str2="},
            {"input_type": "POST raw_data", "data": json.dumps({"int1": 3, "int2": 5, "limit": 100, "str1": "res", "str2": ""})}
        ]

        for test_case in test_cases:
            with self.subTest(test_case=test_case):
                response = self.send_request(test_case)
                expected_output = self.read_test_data('str2empty_output.json')

                self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
                self.assertEqual(response.data, expected_output)

    def test_no_int1_input_types(self):

        test_cases = [
            {"input_type": "GET", "params": {"int2": 5, "limit": 100, "str1": "res", "str2": "szu"}},
            {"input_type": "POST form-data", "data": {"int2": 5, "limit": 100, "str1": "res", "str2": "szu"}},
            {"input_type": "POST urlencoded", "data": "int2=5&limit=100&str1=res&str2=szu"},
            {"input_type": "POST raw_data", "data": json.dumps({"int2": 5, "limit": 100, "str1": "res", "str2": "szu"})}
        ]

        for test_case in test_cases:
            with self.subTest(test_case=test_case):
                response = self.send_request(test_case)
                expected_output = self.read_test_data('noint1_output.json')

                self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
                self.assertEqual(response.data, expected_output)
    
    def test_no_int2_input_types(self):

        test_cases = [
            {"input_type": "GET", "params": {"int1": 3, "limit": 100, "str1": "res", "str2": "szu"}},
            {"input_type": "POST form-data", "data": {"int1": 3, "limit": 100, "str1": "res", "str2": "szu"}},
            {"input_type": "POST urlencoded", "data": "int1=3&limit=100&str1=res&str2=szu"},
            {"input_type": "POST raw_data", "data": json.dumps({"int1": 3, "limit": 100, "str1": "res", "str2": "szu"})}
        ]

        for test_case in test_cases:
            with self.subTest(test_case=test_case):
                response = self.send_request(test_case)
                expected_output = self.read_test_data('noint2_output.json')

                self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
                self.assertEqual(response.data, expected_output)
    
    def test_no_limit_input_types(self):

        test_cases = [
            {"input_type": "GET", "params": {"int1": 3, "int2": 5, "str1": "res", "str2": "szu"}},
            {"input_type": "POST form-data", "data": {"int1": 3, "int2": 5, "str1": "res", "str2": "szu"}},
            {"input_type": "POST urlencoded", "data": "int1=3&int2=5&str1=res&str2=szu"},
            {"input_type": "POST raw_data", "data": json.dumps({"int1": 3, "int2": 5, "str1": "res", "str2": "szu"})}
        ]

        for test_case in test_cases:
            with self.subTest(test_case=test_case):
                response = self.send_request(test_case)
                expected_output = self.read_test_data('nolimit_output.json')

                self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
                self.assertEqual(response.data, expected_output)
    
    def test_no_str1_input_types(self):

        test_cases = [
            {"input_type": "GET", "params": {"int1": 3, "int2": 5, "limit": 100, "str2": "szu"}},
            {"input_type": "POST form-data", "data": {"int1": 3, "int2": 5, "limit": 100, "str2": "szu"}},
            {"input_type": "POST urlencoded", "data": "int1=3&int2=5&limit=100&str2=szu"},
            {"input_type": "POST raw_data", "data": json.dumps({"int1": 3, "int2": 5, "limit": 100, "str2": "szu"})}
        ]

        for test_case in test_cases:
            with self.subTest(test_case=test_case):
                response = self.send_request(test_case)
                expected_output = self.read_test_data('nostr1_output.json')

                self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
                self.assertEqual(response.data, expected_output)

    def test_no_str2_input_types(self):

        test_cases = [
            {"input_type": "GET", "params": {"int1": 3, "int2": 5, "limit": 100, "str1": "res"}},
            {"input_type": "POST form-data", "data": {"int1": 3, "int2": 5, "limit": 100, "str1": "res"}},
            {"input_type": "POST urlencoded", "data": "int1=3&int2=5&limit=100&str1=res"},
            {"input_type": "POST raw_data", "data": json.dumps({"int1": 3, "int2": 5, "limit": 100, "str1": "res"})}
        ]

        for test_case in test_cases:
            with self.subTest(test_case=test_case):
                response = self.send_request(test_case)
                expected_output = self.read_test_data('nostr2_output.json')

                self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
                self.assertEqual(response.data, expected_output)
    
    def test_str1str2_empty_input_types(self):

        test_cases = [
            {"input_type": "GET", "params": {"int1": 3, "int2": 5, "limit": 100, "str1": "", "str2": ""}},
            {"input_type": "POST form-data", "data": {"int1": 3, "int2": 5, "limit": 100, "str1": "", "str2": ""}},
            {"input_type": "POST urlencoded", "data": "int1=3&int2=5&limit=100&str1=&str2="},
            {"input_type": "POST raw_data", "data": json.dumps({"int1": 3, "int2": 5, "limit": 100, "str1": "", "str2": ""})}
        ]

        for test_case in test_cases:
            with self.subTest(test_case=test_case):
                response = self.send_request(test_case)
                expected_output = self.read_test_data('str1str2empty_output.json')

                self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
                self.assertEqual(response.data, expected_output)
    
    def test_no_int1int2_input_types(self):

        test_cases = [
            {"input_type": "GET", "params": {"limit": 100, "str1": "res", "str2": "szu"}},
            {"input_type": "POST form-data", "data": {"limit": 100, "str1": "res", "str2": "szu"}},
            {"input_type": "POST urlencoded", "data": "limit=100&str1=res&str2=szu"},
            {"input_type": "POST raw_data", "data": json.dumps({"limit": 100, "str1": "res", "str2": "szu"})}
        ]

        for test_case in test_cases:
            with self.subTest(test_case=test_case):
                response = self.send_request(test_case)
                expected_output = self.read_test_data('noint1int2_output.json')

                self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
                self.assertEqual(response.data, expected_output)
    
    def test_bothints_bothstrs_bothintsandstrs_are_equal_input_types(self):

        test_cases = [
            {"input_type": "GET", "params": {"int1": 3, "int2": 3, "limit": 100, "str1": "res", "str2": "szu"}},
            {"input_type": "POST form-data", "data": {"int1": 3, "int2": 3, "limit": 100, "str1": "res", "str2": "szu"}},
            {"input_type": "POST urlencoded", "data": "int1=3&int2=3&limit=100&str1=res&str2=szu"},
            {"input_type": "POST raw_data", "data": json.dumps({"int1": 3, "int2": 3, "limit": 100, "str1": "res", "str2": "szu"})},
            {"input_type": "GET", "params": {"int1": 3, "int2": 5, "limit": 100, "str1": "res", "str2": "res"}},
            {"input_type": "POST form-data", "data": {"int1": 3, "int2": 5, "limit": 100, "str1": "res", "str2": "res"}},
            {"input_type": "POST urlencoded", "data": "int1=3&int2=5&limit=100&str1=res&str2=res"},
            {"input_type": "POST raw_data", "data": json.dumps({"int1": 3, "int2": 5, "limit": 100, "str1": "res", "str2": "res"})},
            {"input_type": "GET", "params": {"int1": 3, "int2": 3, "limit": 100, "str1": "res", "str2": "res"}},
            {"input_type": "POST form-data", "data": {"int1": 3, "int2": 3, "limit": 100, "str1": "res", "str2": "res"}},
            {"input_type": "POST urlencoded", "data": "int1=3&int2=3&limit=100&str1=res&str2=res"},
            {"input_type": "POST raw_data", "data": json.dumps({"int1": 3, "int2": 3, "limit": 100, "str1": "res", "str2": "res"})}
        ]

        for test_case in test_cases:
            with self.subTest(test_case=test_case):
                response = self.send_request(test_case)
                expected_output = self.read_test_data('equalintsandstrs_output.json')

                self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
                self.assertEqual(response.data, expected_output)

    def test_sevenparams_input_types(self):

        test_cases = [
            {"input_type": "GET", "params": {"int1": 3, "int2": 5, "int3": 8, "limit": 100, "str1": "res", "str2": "szu", "str3": "hello"}},
            {"input_type": "POST form-data", "data": {"int1": 3, "int2": 5, "int3": 8, "limit": 100, "str1": "res", "str2": "szu", "str3": "hello"}},
            {"input_type": "POST urlencoded", "data": "int1=3&int2=5&int3=8&limit=100&str1=res&str2=szu&str3=hello"},
            {"input_type": "POST raw_data", "data": json.dumps({"int1": 3, "int2": 5, "int3": 8, "limit": 100, "str1": "res", "str2": "szu", "str3": "hello"})}
        ]

        for test_case in test_cases:
            with self.subTest(test_case=test_case):
                response = self.send_request(test_case)
                
                self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
                # Check if both "int3" and "str3" are present in the error message
                self.assertIn("int3", response.data.get("error", ""))
                self.assertIn("str3", response.data.get("error", ""))
    
    def test_int1_notint_input_types(self):

        test_cases = [
            {"input_type": "GET", "params": {"int1": "pre", "int2": 3, "limit": 100, "str1": "res", "str2": "szu"}},
            {"input_type": "POST form-data", "data": {"int1": "pre", "int2": 3, "limit": 100, "str1": "res", "str2": "szu"}},
            {"input_type": "POST urlencoded", "data": "int1=pre&int2=3&limit=100&str1=res&str2=szu"},
            {"input_type": "POST raw_data", "data": json.dumps({"int1": "pre", "int2": 3, "limit": 100, "str1": "res", "str2": "szu"})}
        ]

        for test_case in test_cases:
            with self.subTest(test_case=test_case):
                response = self.send_request(test_case)
                expected_output = self.read_test_data('int1notint_output.json')

                self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
                self.assertEqual(response.data, expected_output)
    
    def test_int2_notint_input_types(self):

        test_cases = [
            {"input_type": "GET", "params": {"int1": 3, "int2": "pre", "limit": 100, "str1": "res", "str2": "szu"}},
            {"input_type": "POST form-data", "data": {"int1": 3, "int2": "pre", "limit": 100, "str1": "res", "str2": "szu"}},
            {"input_type": "POST urlencoded", "data": "int1=3&int2=pre&limit=100&str1=res&str2=szu"},
            {"input_type": "POST raw_data", "data": json.dumps({"int1": 3, "int2": "pre", "limit": 100, "str1": "res", "str2": "szu"})}
        ]

        for test_case in test_cases:
            with self.subTest(test_case=test_case):
                response = self.send_request(test_case)
                expected_output = self.read_test_data('int2notint_output.json')

                self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
                self.assertEqual(response.data, expected_output)

    def test_limit_notint_input_types(self):

        test_cases = [
            {"input_type": "GET", "params": {"int1": 3, "int2": 5, "limit": "pre", "str1": "res", "str2": "szu"}},
            {"input_type": "POST form-data", "data": {"int1": 3, "int2": 5, "limit": "pre", "str1": "res", "str2": "szu"}},
            {"input_type": "POST urlencoded", "data": "int1=3&int2=5&limit=pre&str1=res&str2=szu"},
            {"input_type": "POST raw_data", "data": json.dumps({"int1": 3, "int2": 5, "limit": "pre", "str1": "res", "str2": "szu"})}
        ]

        for test_case in test_cases:
            with self.subTest(test_case=test_case):
                response = self.send_request(test_case)
                expected_output = self.read_test_data('limitnotint_output.json')

                self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
                self.assertEqual(response.data, expected_output)

    def test_str1_notstr_input_types(self):

        test_cases = [
            {"input_type": "GET", "params": {"int1": 3, "int2": 5, "limit": 100, "str1": 7, "str2": "szu"}},
            {"input_type": "POST form-data", "data": {"int1": 3, "int2": 5, "limit": 100, "str1": 7, "str2": "szu"}},
            {"input_type": "POST urlencoded", "data": "int1=3&int2=5&limit=100&str1=7&str2=szu"},
            {"input_type": "POST raw_data", "data": json.dumps({"int1": 3, "int2": 5, "limit": 100, "str1": 7, "str2": "szu"})}
        ]

        for test_case in test_cases:
            with self.subTest(test_case=test_case):
                response = self.send_request(test_case)
                expected_output = self.read_test_data('str1notstr_output.json')

                self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
                self.assertEqual(response.data, expected_output)
    
    def test_str2_notstr_input_types(self):

        test_cases = [
            {"input_type": "GET", "params": {"int1": 3, "int2": 5, "limit": 100, "str1": "res", "str2": 7}},
            {"input_type": "POST form-data", "data": {"int1": 3, "int2": 5, "limit": 100, "str1": "res", "str2": 7}},
            {"input_type": "POST urlencoded", "data": "int1=3&int2=5&limit=100&str1=res&str2=7"},
            {"input_type": "POST raw_data", "data": json.dumps({"int1": 3, "int2": 5, "limit": 100, "str1": "res", "str2": 7})}
        ]

        for test_case in test_cases:
            with self.subTest(test_case=test_case):
                response = self.send_request(test_case)
                expected_output = self.read_test_data('str2notstr_output.json')

                self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
                self.assertEqual(response.data, expected_output)