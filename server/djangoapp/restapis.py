import requests
import json
# import related models here
from requests.auth import HTTPBasicAuth
from .models import CarDealer, DealerReview
from ibm_cloud_sdk_core.authenticators import IAMAuthenticator
from ibm_watson import NaturalLanguageUnderstandingV1
from ibm_watson.natural_language_understanding_v1 import Features,SentimentOptions


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
    result = []
    response = requests.post(url, params=kwargs, json=json_payload)

# Create a get_dealers_from_cf method to get dealers from a cloud function
# def get_dealers_from_cf(url, **kwargs):
# - Call get_request() with specified arguments
# - Parse JSON results into a CarDealer object list
def get_dealers_from_cf(url, **kwargs):
    results = []
    # Call get_request with a URL parameter
    json_result = get_request(url)
    if json_result:
        # Get the row list in JSON as dealers
        # print("DEBUG")
        # print(json_result)
        dealers = json_result
        # For each dealer object
        for dealer in dealers:
            # Get its content in `doc` object
            dealer_doc = dealer["doc"]
            # Create a CarDealer object with values in `doc` object
            dealer_obj = CarDealer(address=dealer_doc["address"], city=dealer_doc["city"], full_name=dealer_doc["full_name"],
                                   dealer_id=dealer_doc["id"], lat=dealer_doc["lat"], long=dealer_doc["long"],
                                   short_name=dealer_doc["short_name"],
                                   state=dealer_doc["st"], zip=dealer_doc["zip"])
            results.append(dealer_obj)

    return results

def get_dealer_by_id_from_cf(url, dealer_id):
    json = get_request(url)
    if json:
        for dealer in json:
            if(dealer["doc"]["id"] == dealer_id):
                dealer_doc = dealer["doc"]
                dealer_obj = CarDealer(address=dealer_doc["address"], 
                                   city=dealer_doc["city"], 
                                   full_name=dealer_doc["full_name"],
                                   dealer_id=dealer_doc["id"], 
                                   lat=dealer_doc["lat"],
                                   long=dealer_doc["long"],
                                   short_name=dealer_doc["short_name"],
                                   state=dealer_doc["st"], 
                                   zip=dealer_doc["zip"])
                return dealer_obj

# Create a get_dealer_reviews_from_cf method to get reviews by dealer id from a cloud function
def get_dealer_reviews_from_cf(url, dealer_id):
# - Call get_request() with specified arguments
# - Parse JSON results into a DealerView object list
    result = []
    json_result = get_request(url)
    if json_result:
        for dealer in json_result:
            # print("AAA")
            # print(dealer)
            if(dealer["doc"]["id"] == dealer_id):
                dealer_review  = dealer["doc"]
                # print("dealer_review")
                # print(dealer_review )
                review_obj = DealerReview(dealership=dealer_review["dealership"],
                                        name=dealer_review["name"],
                                        purchase=dealer_review["purchase"],
                                        review=dealer_review["review"])
                # .get() returns None if the key is not found
                # .get("key", "") will return an empty string if the key is not found
                review_obj.purchase_date = dealer_review.get("purchase_date", "")
                review_obj.car_make = dealer_review.get("car_make", "")
                review_obj.car_model = dealer_review.get("car_model", "")
                review_obj.car_year = dealer_review.get("car_year", "")
                review_obj.dealer_id = dealer_review.get("dealer_id", "")
                                        
                review_obj.sentiment = analyze_review_sentiments(review_obj.review)
                result.append(review_obj)
    return result


# Create an `analyze_review_sentiments` method to call Watson NLU and analyze text
def analyze_review_sentiments(text):
# - Call get_request() with specified arguments
# - Get the returned sentiment label such as Positive or Negative
    url = 'https://api.us-east.natural-language-understanding.watson.cloud.ibm.com/instances/19048b08-ca16-4978-ab75-e21ea618d7d7'
    api_key = 'UqqoRC_29l6JFjyqwhUvkxFnYlW1Sy6gUyudktKujNii'
    authenticator = IAMAuthenticator(api_key) 
    natural_language_understanding = NaturalLanguageUnderstandingV1(version='2021-08-01',authenticator=authenticator) 
    natural_language_understanding.set_service_url(url) 
    response = natural_language_understanding.analyze( text=text ,features=Features(sentiment=SentimentOptions(targets=[text]))).get_result() 
    label=json.dumps(response, indent=2) 
    label = response['sentiment']['document']['label'] 
    return(label) 