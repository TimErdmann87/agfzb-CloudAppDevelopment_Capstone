from django.db import models
from django.utils.timezone import now


class CarMake(models.Model):
    name = models.CharField(max_length=50)
    description = models.TextField()
    headquarters = models.CharField(max_length=50)

    def __str__(self):
        CarMakeObjectString = f"name: {self.name},\
            \ndescription: {self.description},\
            \nheadquarters: {self.headquarters}"
        return CarMakeObjectString


class CarModel(models.Model):
    TYPE_CHOICES = [
        ("SEDAN", "Sedan"),
        ("SUV", "SUV"),
        ("WAGON", "Wagon"),
    ]

    make = models.ForeignKey(CarMake, on_delete=models.CASCADE)
    dealerId = models.IntegerField()
    name = models.CharField(max_length=50)
    type = models.CharField(max_length=50, choices=TYPE_CHOICES)
    year = models.DateField()

    def __str__(self):
        CarModelObjectString = f"make: {self.make},\
            \ndealerId: {str(self.dealerId)},\
            \nname: {self.name},\
            \ntype: {self.type},\
            \nyear: {str(self.year)}"

        return CarModelObjectString


# <HINT> Create a Car Model model `class CarModel(models.Model):`:
# - Many-To-One relationship to Car Make model (One Car Make has many Car Models, using ForeignKey field)
# - Name
# - Dealer id, used to refer a dealer created in cloudant database
# - Type (CharField with a choices argument to provide limited choices such as Sedan, SUV, WAGON, etc.)
# - Year (DateField)
# - Any other fields you would like to include in car model
# - __str__ method to print a car make object


# <HINT> Create a plain Python class `CarDealer` to hold dealer data


# <HINT> Create a plain Python class `DealerReview` to hold review data
