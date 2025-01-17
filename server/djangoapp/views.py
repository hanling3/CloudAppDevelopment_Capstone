from django.shortcuts import render
from django.http import HttpResponseRedirect, HttpResponse
from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404, render, redirect
# from .models import related models
from .models import CarMake, CarModel
# from .restapis import related methods
from .restapis import get_dealers_from_cf, get_dealer_by_id_from_cf, get_request, get_dealer_reviews_from_cf, post_request
from django.contrib.auth import login, logout, authenticate
from django.contrib import messages
from datetime import datetime
from django.urls import reverse
import logging
import json

# Get an instance of a logger
logger = logging.getLogger(__name__)


# Create your views here.


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
            context['message'] = "Invalid username or password."
            return render(request, 'djangoapp/index.html', context)
    else:
        return render(request, 'djangoapp/index.html', context) 

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
        # Check if user exists
        username = request.POST['username']
        password = request.POST['psw']
        first_name = request.POST['firstname']
        last_name = request.POST['lastname']
        user_exist = False
        try:
            User.objects.get(username=username)
            user_exist = True
        except:
            logger.error("New user")
        if not user_exist:
            user = User.objects.create_user(username=username, first_name=first_name, last_name=last_name,
                                            password=password)
            login(request, user)
            return redirect('djangoapp:index')
        else:
            context['message'] = "User already exists."
            return render(request, 'djangoapp/registration.html', context)
            # messages.warning(request, "The user already exists.")
            # return redirect("djangoapp:registration")


# Update the `get_dealerships` view to render the index page with a list of dealerships
# def get_dealerships(request):
#     context = {}
#     if request.method == "GET":
#         return render(request, 'djangoapp/index.html', context)
def get_dealerships(request):
    context={}
    if request.method == "GET":
        url = "https://us-south.functions.appdomain.cloud/api/v1/web/350f381a-47f4-43b7-9b23-baf89c5620a3/dealership-package/get-dealership"
        # Get dealers from the URL
        dealerships = get_dealers_from_cf(url)
        context["dealerships"] = dealerships
        # Return a list of dealer short name
        return render(request, 'djangoapp/index.html', context)


# Create a `get_dealer_details` view to render the reviews of a dealer
def get_dealer_details(request, dealer_id):
    context ={}
    if request.method == "GET":
        dealer_url = "https://us-south.functions.appdomain.cloud/api/v1/web/350f381a-47f4-43b7-9b23-baf89c5620a3/dealership-package/get-dealership"
        # Get dealers from the URL
        dealer = get_dealer_by_id_from_cf(dealer_url, dealer_id)
        context["dealer"] = dealer
        review_url = "https://us-south.functions.appdomain.cloud/api/v1/web/350f381a-47f4-43b7-9b23-baf89c5620a3/dealership-package/get-review"
        reviews = get_dealer_reviews_from_cf(review_url, dealer_id)
        context["reviews"] = reviews
        return render(request, 'djangoapp/dealer_details.html', context)


# Create a `add_review` view to submit a review
def add_review(request, dealer_id):
    context= {}
    dealer_url = "https://us-south.functions.appdomain.cloud/api/v1/web/350f381a-47f4-43b7-9b23-baf89c5620a3/dealership-package/get-dealership"
    dealer = get_dealer_by_id_from_cf(dealer_url, dealer_id)
    context["dealer"] = dealer
    # print("debug dealer")
    # print(dealer)
    if request.method == "GET":
        # render the form
        cars = CarModel.objects.all()
        print(cars)
        for car in cars:
            print(car)
        context["cars"] = cars
        return render(request, 'djangoapp/add_review.html', context)

    elif request.method == "POST": 
        if request.user.is_authenticated:
            payload = {}
            car_id = request.POST["car_id"]
            car = CarModel.objects.get(pk=car_id)
            payload["time"] = datetime.utcnow().isoformat()
            payload["name"] = request.user.username
            payload["dealership"] = dealer_id
            payload["review"] = request.POST["content"]
            payload["purchase"] = False
            if "purchasecheck" in request.POST:
                if request.POST["purchasecheck"] == 'on':
                        payload["purchase"] = True
            payload["purchase_date"] = request.POST["purchasedate"]
            payload["car_make"] = car.car_make.name
            payload["car_model"] = car.name
            payload["car_year"] = car.year

            json_payload = {"review": payload}
            url = "https://us-south.functions.appdomain.cloud/api/v1/web/350f381a-47f4-43b7-9b23-baf89c5620a3/dealership-package/post-review"
            post_request(url, json_payload, dealer_id=dealer_id)
            # Fetch updated reviews for this dealer
            # updated_reviews = get_dealer_reviews_from_cf(url, id)
            return redirect('djangoapp:dealer_details', dealer_id=dealer_id)
        else:
            return HttpResponse("You must be logged in to post a review.")
    else:
        # Handle non-POST cases here
        return redirect('djangoapp:dealer_details', dealer_id=dealer_id)
    # no any leading or trailing spaces around 'dealer_details'


