import requests
import json
from .models import CarDealer, DealerReview
from requests.auth import HTTPBasicAuth
from ibm_cloud_sdk_core.authenticators import IAMAuthenticator
from ibm_watson import NaturalLanguageUnderstandingV1
from ibm_watson.natural_language_understanding_v1 import Features,SentimentOptions
import time


# Create a `get_request` to make HTTP GET requests
# e.g., response = requests.get(url, params=params, headers={'Content-Type': 'application/json'},
#                                     auth=HTTPBasicAuth('apikey', api_key))
def get_request(url, **kwargs):
    
    # If argument contain API KEY
    api_key = kwargs.get("api_key")
    print("GET from {} ".format(url))
    try:
        if api_key:
            params = dict()
            params["text"] = kwargs["text"]
            params["version"] = kwargs["version"]
            params["features"] = kwargs["features"]
            params["return_analyzed_text"] = kwargs["return_analyzed_text"]
            response = requests.get(url, params=params, headers={'Content-Type': 'application/json'},
                                    auth=HTTPBasicAuth('apikey', api_key))
        else:
            # Call get method of requests library with URL and parameters
            response = requests.get(url, headers={'Content-Type': 'application/json'},
                                    params=kwargs)
    except:
        # If any error occurs
        print("Network exception occurred")

    status_code = response.status_code
    print("With status {} ".format(status_code))
    json_data = json.loads(response.text)
    return json_data

# Create a `post_request` to make HTTP POST requests
# e.g., response = requests.post(url, params=kwargs, json=payload)
def post_request(url, json_payload, **kwargs):
    print(kwargs)
    print("POST to {} ".format(url))
    print(json_payload)
    response = requests.post(url, params=kwargs, json=json_payload)
    status_code = response.status_code
    print("With status {} ".format(status_code))
    json_data = json.loads(response.text)
    print(json_data)
    return response

# Create a get_dealers_from_cf method to get dealers from a cloud function
# def get_dealers_from_cf(url, **kwargs):
# - Call get_request() with specified arguments
# - Parse JSON results into a CarDealer object list
def get_dealers_from_cf(url, **kwargs):
    results = []
    # Call get_request with a URL parameter
    json_result = get_request(url)
    print(json_result)
    print("############################################")
    if json_result:
        # Get the row list in JSON as dealers
        dealers = json_result
        # For each dealer object
        for dealer in dealers:
            dealer_obj = CarDealer(address=dealer["address"], city=dealer["city"], full_name=dealer["full_name"],
                                   id=dealer["id"], lat=dealer["lat"], long=dealer["long"],
                                   short_name=dealer["short_name"],
                                   st=dealer["st"], zip=dealer["zip"])
            results.append(dealer_obj)
    print(results)
    print("############################################")
    return results

# Create a get_dealer_reviews_from_cf method to get reviews by dealer id from a cloud function
# def get_dealer_by_id_from_cf(url, dealerId):
# - Call get_request() with specified arguments
# - Parse JSON results into a DealerView object list
def get_dealer_by_id_from_cf(url, id):
    json_result = get_request(url, id=id)
    print('json_result from line 54',json_result)

    if json_result:
        dealers = json_result
        
    
        dealer_doc = dealers[2]
        dealer_obj = CarDealer(address=dealer_doc["address"], 
                                city=dealer_doc["city"],
                                id=dealer_doc["id"], 
                                lat=dealer_doc["lat"], 
                                long=dealer_doc["long"], 
                                full_name=dealer_doc["full_name"],
                                short_name=dealer_doc["short_name"],
                                st=dealer_doc["st"], 
                                zip=dealer_doc["zip"])
    return dealer_obj

def get_dealer_reviews_from_cf(url, **kwargs):
    results = []
    json_result = get_request(url, id=kwargs['id'])
    if(json_result):
        dealer_reviews = json_result;
        for dealer_review in dealer_reviews:
            sentiment = analyze_review_sentiments(dealer_review['review'])
            dealer_review_obj = DealerReview(dealership=dealer_review['dealership'], 
                            name=dealer_review['name'],
                            purchase=dealer_review['purchase'], 
                            review=dealer_review['review'], 
                            purchase_date=dealer_review['purchase_date'],
                            car_make=dealer_review['car_make'], 
                            car_model=dealer_review['car_model'], 
                            car_year=dealer_review['car_year'],
                            id=dealer_review['id'], 
                            sentiment=sentiment)
            results.append(dealer_review_obj)
    return results


# Create an `analyze_review_sentiments` method to call Watson NLU and analyze text
# def analyze_review_sentiments(text):
# - Call get_request() with specified arguments
# - Get the returned sentiment label such as Positive or Negative
def analyze_review_sentiments(text):
    url = "https://api.us-south.natural-language-understanding.watson.cloud.ibm.com/instances/bb3023b7-ff44-45bb-938a-1373a05af3ae"
    api_key = "tsR0cp-DXyEHAKC8PMhfYtbM8Ek8q-LTqvpAjoAkNohx"
    authenticator = IAMAuthenticator(api_key)
    natural_language_understanding = NaturalLanguageUnderstandingV1(version='2021-08-01',authenticator=authenticator)
    natural_language_understanding.set_service_url(url)
    
    try:
        response = natural_language_understanding.analyze(
            text=text,
            features=Features(sentiment=SentimentOptions(targets=[text]))
        ).get_result()
        label = response['sentiment']['document']['label']
    except Exception as e:
        print("Exception occurred during sentiment analysis:", str(e))
        label = "unknown"
    
    return label


