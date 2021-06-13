from django.db import models

class Product(models.Model):
    """
    The scrapped data will be saved in this model
    """
    manufacturer = models.TextField() # this stands for our crawled data
    brand = models.TextField()
    name = models.TextField()
    description = models.TextField()
    url = models.TextField()
