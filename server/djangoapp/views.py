from django.shortcuts import render
from django.http import HttpResponseRedirect, HttpResponse
from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404, render, redirect
from .models import CarModel
from .restapis import get_dealers_from_cf, get_dealer_reviews_from_cf, post_request, get_dealers_by_id
from django.contrib.auth import login, logout, authenticate
from django.contrib import messages
from datetime import datetime
import logging
import json
import uuid

# Get an instance of a logger
logger = logging.getLogger(__name__)


# Create your views here.
def static_template(request):
    return render(request, "static_template.html")

# Create an `about` view to render a static about page
def about(request):
    return render(request, 'djangoapp/about.html')


# Create a `contact` view to return a static contact page
def contact(request):
    return render(request, 'djangoapp/contact.html')

# Create a `login_request` view to handle sign in request
def login_request(request):
    context = {}

    if request.method == "POST":
        username = request.POST['username']
        password = request.POST['psw']
        
        user = authenticate(username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('djangoapp:index')
        else:
            return redirect('djangoapp:index')
    else:
        return redirect('djangoapp:index')

# Create a `logout_request` view to handle sign out request
def logout_request(request):
    logout(request)
    return redirect('djangoapp:index')

# Create a `registration_request` view to handle sign up request
def registration_request(request):
    context = {}
    
    if request.method == 'GET':
        return render(request, 'djangoapp/registration.html', context)
    
    elif request.method == 'POST':
        username = request.POST['username']
        password = request.POST['psw']
        first_name = request.POST['firstname']
        last_name = request.POST['lastname']
        user_exist = False
        try:
            User.objects.get(username=username)
            user_exist = True
        except:
            logger.debug("{} is new user".format(username))
        
        if not user_exist:
            user = User.objects.create_user(username=username, first_name=first_name, last_name=last_name,
                                            password=password)
            login(request, user)
            return redirect("djangoapp:index")
        else:
            return render(request, 'djangoapp/registration.html', context)

# Update the `get_dealerships` view to render the index page with a list of dealerships
def get_dealerships(request):
    
    if request.method == "GET":
        url = r"https://prox87-3000.theiadocker-2-labs-prod-theiak8s-4-tor01.proxy.cognitiveclass.ai/api/dealership"
        
        dealerships = get_dealers_from_cf(url)
        context = dict()
        context["dealership_list"] = dealerships
        
        return render(request, 'djangoapp/index.html', context)


# Create a `get_dealer_details` view to render the reviews of a dealer
def get_dealer_details(request, dealer_id):
    
    if request.method == "GET":
        url = r"https://prox87-3000.theiadocker-2-labs-prod-theiak8s-4-tor01.proxy.cognitiveclass.ai/api/dealership"
        dealer = get_dealers_by_id(url=url, dealer_id = dealer_id)

        url = r"https://prox87-5000.theiadocker-2-labs-prod-theiak8s-4-tor01.proxy.cognitiveclass.ai/api/review"
        reviews = get_dealer_reviews_from_cf(url, dealerId=dealer_id)
        
        context = dict()
        context["dealer_id"] = dealer_id
        context["dealer_name"] = dealer[0].full_name
        context["reviews_list"] = reviews
        
        return render(request, 'djangoapp/dealer_details.html', context)

# Create a `add_review` view to submit a review
# def add_review(request, dealer_id):
def add_review(request, dealer_id):

    if request.method == "GET":
        url = r"https://prox87-3000.theiadocker-2-labs-prod-theiak8s-4-tor01.proxy.cognitiveclass.ai/api/dealership"
        dealer = get_dealers_by_id(url=url, dealer_id = dealer_id)

        context = dict()
        context["dealer_id"] = dealer_id
        context["dealer_name"] = dealer[0].full_name

        cars = CarModel.objects.filter(dealerId=dealer_id)
        context["dealer_cars"] = cars

        return render(request, 'djangoapp/add_review.html', context)

    elif request.method == "POST":
        if request.user.is_authenticated:
            car_id = request.POST["car"]
            car = CarModel.objects.get(pk=car_id)

            review = dict()
            review["id"] = str(uuid.uuid4())
            review["dealership"] = dealer_id
            review["name"] = request.user.username
            review["review"] = request.POST["content"]
            review["purchase"] = True if request.POST["purchasecheck"] == "on" else False
            review["purchase_date"] = datetime.utcnow().isoformat()
            review["car_make"] = car.make.name
            review["car_model"] = car.name
            review["car_year"] = car.year.strftime("%Y")

            url = r"https://prox87-5000.theiadocker-2-labs-prod-theiak8s-4-tor01.proxy.cognitiveclass.ai/api/review"
            
            json_payload = dict()
            json_payload["review"] = review

            print(json_payload)

            response = post_request(url, json_payload)

            print(response)

            return redirect("djangoapp:dealer_details", dealer_id=dealer_id)
    
    return HttpResponse("Authenticated required")