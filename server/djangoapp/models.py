from django.db import models
from datetime import datetime
import json

# Create your models here.

# <HINT> Create a Car Make model `class CarMake(models.Model)`:
# - Name
# - Description
# - Any other fields you would like to include in car make model
# - __str__ method to print a car make object
class CarMake(models.Model):
    name = models.CharField(max_length=50, null = False, default='car make')
    description = models.CharField(max_length=100, null = False, default = 'car make description')

    def __str__(self):
        return "Name: " + self.name + ", " + "\nDescription: " + self.description


# <HINT> Create a Car Model model `class CarModel(models.Model):`:
# - Many-To-One relationship to Car Make model (One Car Make has many Car Models, using ForeignKey field)
# - Name
# - Dealer id, used to refer a dealer created in cloudant database
# - Type (CharField with a choices argument to provide limited choices such as Sedan, SUV, WAGON, etc.)
# - Year (DateField)
# - Any other fields you would like to include in car model
# - __str__ method to print a car make object
class CarModel(models.Model):
    car_id = models.IntegerField(default=1,primary_key=True)
    SEDAN = "Sedan"
    SUV = "SUV"
    WAGON = "Wagon"
    CAR_TYPES = [
        (SEDAN, "Sedan"), (SUV, "SUV"), (WAGON, "Wagon")
    ]
    car_make = models.ForeignKey(CarMake, null=False, on_delete=models.CASCADE)
    name = models.CharField(max_length= 50, null=False)
    model_type = models.CharField(max_length=50, choices=CAR_TYPES, default=SUV)
    YEAR_CHOICES = []
    current_year = datetime.now().year
    for r in range(1969, (current_year+1)):
        YEAR_CHOICES.append((r, r))
    year = models.IntegerField(
        ('year'), choices=YEAR_CHOICES, default=current_year)
    
    def __str__(self):
        return "Name: " + self.name + "," + \
                "\n Type: " + self.model_type + "," + \
                "\n Year: " + str(self.year)

# <HINT> Create a plain Python class `CarDealer` to hold dealer data
class CarDealer:
    def __init__(self, address, city, full_name, dealer_id, lat, long, short_name, state, zip):
        # Dealer address
        self.address = address
        # Dealer city
        self.city = city
        # Dealer Full Name
        self.full_name = full_name
        # Dealer id
        self.dealer_id = dealer_id
        # Location lat
        self.lat = lat
        # Location long
        self.long = long
        # Dealer short name
        self.short_name = short_name
        # Dealer state
        self.state = state
        # Dealer zip
        self.zip = zip

    def __str__(self):
        return "Dealer name: " + self.full_name

# <HINT> Create a plain Python class `DealerReview` to hold review data
class DealerReview:
    def __init__(self, dealership, name, purchase, review):
        self.dealership = dealership
        self.name = name
        self.purchase = purchase
        self.review = review
        # optional attributes
        self.purchase_date = ""            
        self.car_make = ""
        self.car_model = ""
        self.car_year = ""
        self.sentiment = ""
        # dealer id
        self.dealer_id = ""
        
    def __str__(self):
        return "Review: " + self.review

    def to_json(self):
        return json.dumps(self, default=lambda o: o.__dict__,
                            sort_keys=True, indent=4)
