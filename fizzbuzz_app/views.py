from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.http import StreamingHttpResponse
from .serializers import FizzBuzzRequestSerializer
from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.db.models import F, Max
from rest_framework.pagination import PageNumberPagination
from .models import FizzBuzzRequest
from django.http import HttpResponseBadRequest


# Used to adjust the page size for processing fizzbuzz for large values of limit
class CustomPageNumberPagination(PageNumberPagination):
    page_size = 10  # Adjust the page size as needed
    page_size_query_param = 'page_size'
    max_page_size = 1000

# Handles the fizzbuzz request
def handle_fizzbuzz_request(method):
    def wrapper(self, request, *args, **kwargs):
        try:
            if request.method == 'GET':
                # For GET requests, use query_params for form data
                params_source = request.query_params
            else:
                # For other methods, use data attribute
                params_source = request.data

            serializer = FizzBuzzRequestSerializer(data=params_source)
            extra_params = set(params_source.keys()) - set(serializer.fields.keys())

            #Send errors if extra parameters are sent
            if extra_params:
                return Response({'error': f"Extra parameters found: {', '.join(extra_params)}"},
                                status=status.HTTP_400_BAD_REQUEST)

            if serializer.is_valid():
                int1 = serializer.validated_data.get('int1')
                int2 = serializer.validated_data.get('int2')
                limit = serializer.validated_data.get('limit')
                str1 = serializer.validated_data.get('str1')
                str2 = serializer.validated_data.get('str2')

                # Logic if the integers or strings are equal, return bad request
                if int1 == int2 or str1 == str2:
                    return Response({'Error': 'int1 must be different from int2 and str1 must be different from str2'},
                                    status=status.HTTP_400_BAD_REQUEST)

                #Update the values of the inputs by calling the udate function which handles the statistics
                self.update_statistics(int1, int2, limit, str1, str2)

                # Based on the value of limit we check if we can have a blocking call or use a non-blocking call to perform the FizzBuzz logic
                if limit <= 100000:
                    result = self.perform_fizzbuzz_logic(int1, int2, limit, str1, str2)
                    return Response({"result": result}, status=status.HTTP_200_OK)
                else:
                    response = StreamingHttpResponse(
                        self.generate_fizzbuzz(int1, int2, limit, str1, str2),
                        content_type='application/json'
                    )
                    response['Accept-Encoding'] = 'gzip'
                    return response
            else:
                return Response({'error': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    return wrapper

class FizzBuzzView(APIView):
    # Class variable to store statistics
    statistics = {}

    @api_view(['GET'])
    def statistics_endpoint(request):
        try:
            if request.GET or request.POST:
                return HttpResponseBadRequest("Invalid request. No parameters should be sent.")

            # Find the maximum hit count using a database query
            max_hits = FizzBuzzRequest.objects.aggregate(max_hits=Max('hits'))['max_hits']

            # Find all requests with the maximum hit count
            tied_requests = FizzBuzzRequest.objects.filter(hits=max_hits).values('int1', 'int2', 'limit', 'str1', 'str2')

            # Check if there is a tie in hits
            if tied_requests.count() > 1:
                response_data = {
                    'tied_requests': list(tied_requests),
                    'max_hits': max_hits,
                }
            else:
                # If no tie, create a single set of parameters and hits
                single_request = tied_requests.first()
                response_data = {
                    'single_request': single_request,
                    'max_hits': max_hits,
                }

            # Return the response data
            return Response(response_data)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


    def update_statistics(self, int1, int2, limit, str1, str2):

        #For special scenarios where limit = 100 {[int1= 3, int=5, str1= fizz, str2= buzz] & 
        #[int1= 5, int=3, str1= buzz, str2= fizz]}
        #treating them as equal and considering the strings and integers simply interchanged
        if int1 > int2:
            int1, int2 = int2, int1
            str1, str2 = str2, str1

        parameters = (int1, int2, limit, str1, str2)

        # Update in-memory statistics
        if parameters in FizzBuzzView.statistics:
            FizzBuzzView.statistics[parameters] += 1
        else:
            FizzBuzzView.statistics[parameters] = 1

        # Update database statistics or create a new one 
        fizzbuzz_request, created = FizzBuzzRequest.objects.get_or_create(
            int1=int1,
            int2=int2,
            limit=limit,
            str1=str1,
            str2=str2,
        )
        fizzbuzz_request.hits = F('hits') + 1
        fizzbuzz_request.save()

    @handle_fizzbuzz_request
    def fizzbuzz_handler(self, request, *args, **kwargs):
        print(request.method)

    def perform_fizzbuzz_logic(self, int1, int2, limit, str1, str2):
        try:
            result = []
            for num in range(1, limit + 1):
                if num % int1 == 0 and num % int2 == 0:
                    result.append(str1 + str2)
                elif num % int1 == 0:
                    result.append(str1)
                elif num % int2 == 0:
                    result.append(str2)
                else:
                    result.append(str(num))
            return result
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def generate_fizzbuzz(self, int1, int2, limit, str1, str2, batch_size=100):
        try:
            # Stream the Fizz-Buzz response line by line in batches
            for start in range(1, limit + 1, batch_size):
                end = min(start + batch_size, limit + 1)
                batch_result = [
                    self.compute_fizzbuzz(num, int1, int2, str1, str2) for num in range(start, end)
                ]
                yield '\n'.join(batch_result) + '\n'
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def compute_fizzbuzz(self, num, int1, int2, str1, str2):
        try:
            # Perform the Fizz-Buzz computation for a single number
            if num % int1 == 0 and num % int2 == 0:
                return f'{str1}{str2}'
            elif num % int1 == 0:
                return str1
            elif num % int2 == 0:
                return str2
            else:
                return str(num)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# Map the fizzbuzz_handler to both GET and POST methods
FizzBuzzView.get = FizzBuzzView.fizzbuzz_handler
FizzBuzzView.post = FizzBuzzView.fizzbuzz_handler