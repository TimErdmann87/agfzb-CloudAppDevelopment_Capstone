import requests
import json
from .models import CarDealer, DealerReview
from requests.auth import HTTPBasicAuth

from ibm_watson import NaturalLanguageUnderstandingV1, ApiException
from ibm_cloud_sdk_core.authenticators import IAMAuthenticator
from ibm_watson.natural_language_understanding_v1 import Features, SentimentOptions


# Create a `get_request` to make HTTP GET requests
# e.g., response = requests.get(url, params=params, headers={'Content-Type': 'application/json'},
#                                     auth=HTTPBasicAuth('apikey', api_key))
def get_request(url, **kwargs):
    # Watson NLU Sentiment Analysis code in instructions outdated
    # official documentation IBM CLoud NLU > Sentiment don't perform GET requests
    # and Python example involves respective libraries
    # => code simplified and Watson NLU simply moved to respective function
    print("GET from {}".format(url))
    try:
        # Call get method of requests library with URL and parameters
        response = requests.get(
            url, 
            headers={'Content-Type': 'application/json'}, 
            params=kwargs
        )
    except:
        # If any error occurs
        print("Network exception occurred")

    status_code = response.status_code
    print("With status {}".format(status_code))
    
    if status_code != 200:
        return None
    
    json_data = json.loads(response.text)
    return json_data

# Create a `post_request` to make HTTP POST requests
# e.g., response = requests.post(url, params=kwargs, json=payload)
def post_request(url, json_payload, **kwargs):
    print("POST to {}".format(url))
    try:
        response = requests.post(
            url, 
            headers={'Content-Type': 'application/json'},
            json=json_payload,
            params=kwargs
        )
    except Exception as err:
        print(err)
        print("Network exception occurred")

    status_code = response.status_code
    print("With status {} ".format(status_code))

    json_data = json.loads(response.text)
    return json_data

# Create a get_dealers_from_cf method to get dealers from a cloud function
# def get_dealers_from_cf(url, **kwargs):
# - Call get_request() with specified arguments
# - Parse JSON results into a CarDealer object list
def get_dealers_from_cf(url, **kwargs):
    results = []
    json_result = get_request(url)
    
    if json_result:
        for dealer in json_result:
            dealer_obj = CarDealer(
                address=dealer["address"], 
                city=dealer["city"], 
                full_name=dealer["full_name"],
                id=dealer["id"], 
                lat=dealer["lat"], 
                long=dealer["long"],
                short_name=dealer["short_name"],
                state=dealer["state"],
                st=dealer["st"],
                zip=dealer["zip"])
            results.append(dealer_obj)

    return results

def get_dealers_by_id(url, **kwargs):
    results = []
    json_result = get_request(url, id=kwargs["dealer_id"])

    if json_result:
        for dealer_doc in json_result:
            dealer_obj = CarDealer(address=dealer_doc["address"], city=dealer_doc["city"], full_name=dealer_doc["full_name"],
                                   id=dealer_doc["id"], lat=dealer_doc["lat"], long=dealer_doc["long"],
                                   short_name=dealer_doc["short_name"],
                                   state=dealer_doc["state"],st=dealer_doc["st"], zip=dealer_doc["zip"])
            results.append(dealer_obj)

    return results

def get_dealers_by_state(url, **kwargs):
    results = []
    json_result = get_request(url, state=kwargs["state"])

    if json_result:
        for dealer_doc in json_result:
            dealer_obj = CarDealer(address=dealer_doc["address"], city=dealer_doc["city"], full_name=dealer_doc["full_name"],
                                   id=dealer_doc["id"], lat=dealer_doc["lat"], long=dealer_doc["long"],
                                   short_name=dealer_doc["short_name"],
                                   state=dealer_doc["state"],st=dealer_doc["st"], zip=dealer_doc["zip"])
            results.append(dealer_obj)

    return results

# Create a get_dealer_reviews_from_cf method to get reviews by dealer id from a cloud function
# def get_dealer_reviews_from_cf(url, dealerId):
# - Call get_request() with specified arguments
# - Parse JSON results into a DealerView object list
def get_dealer_reviews_from_cf(url, dealerId):
    results = []
    json_result = get_request(url, dealerId=dealerId)
    
    if json_result:
        print(json_result)
        for d in json_result:
            review_obj = DealerReview(
                dealership=d["dealership"],
                name=d["name"],
                purchase=d["purchase"],
                review=d["review"],
                purchase_date=d["purchase_date"],
                car_make=d["car_make"],
                car_model=d["car_model"],
                car_year=d["car_year"],
                sentiment=analyze_review_sentiments(d["review"]),
                id=d["id"]
            )
            results.append(review_obj)

    return results

# Create an `analyze_review_sentiments` method to call Watson NLU and analyze text
# def analyze_review_sentiments(text):
# - Call get_request() with specified arguments
# - Get the returned sentiment label such as Positive or Negative
def analyze_review_sentiments(text):
    
    url = r"https://api.us-south.natural-language-understanding.watson.cloud.ibm.com/instances/0f934e27-2517-405a-9f00-ca6823916ce3"
    api_key = "K3h5pKTD2uAI4mwIyyfsxq4DsvrjT2IezMTsonyW-EWy"

    version="2022-04-07"
    features="sentiment"
    return_analyzed_text=True

    authenticator = IAMAuthenticator(api_key)
    
    natural_language_understanding = NaturalLanguageUnderstandingV1(
        version=version,
        authenticator=authenticator
    )
    natural_language_understanding.set_service_url(url)
    
    try:
        response = natural_language_understanding.analyze(
            text=text,
            features=Features(sentiment=SentimentOptions(document=True))
        ).get_result()

        sentiment_label = response["sentiment"]["document"]["label"]

    except ApiException as err:
        if err.http_response.status_code == 422:
            sentiment_label = "n/a, text too short"
    except:
        sentiment_label = "error"

    return sentiment_label