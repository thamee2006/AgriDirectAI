from django.db import models
from django.contrib.auth.models import User


class Crop(models.Model):

    farmer = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        null=True,
        blank=True
    )

    farmer_name = models.CharField(max_length=100)

    crop_name = models.CharField(max_length=100)

    quantity = models.FloatField()

    price = models.FloatField()

    location = models.CharField(max_length=100)

    description = models.TextField(blank=True)

    created_at = models.DateTimeField(auto_now_add=True)


    @property
    def image_filename(self):

        image_map = {
            "tomato": "tomato.jpg",
            "onion": "onion.jpg",
            "carrot": "carrot.jpg",
            "beetroot": "beetroot.jpg",
            "cabbage": "cabbage.jpg",
            "cauliflower": "cauliflower.jpg",
            "corn": "corn.jpg",
            "drumstick": "drumstick.jpg",
            "lady finger": "lady finger.jpg",
            "potato": "potato.jpg",
        }

        return image_map.get(
            self.crop_name.lower().strip(),
            "tomato.jpg"
        )


    def __str__(self):
        return self.crop_name


class Order(models.Model):

    STATUS_CHOICES = [
        ('Pending', 'Pending'),
        ('Confirmed', 'Confirmed'),
        ('Shipped', 'Shipped'),
        ('Delivered', 'Delivered'),
    ]

    crop = models.ForeignKey(
        Crop,
        on_delete=models.CASCADE
    )

    buyer = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        null=True,
        blank=True
    )

    buyer_name = models.CharField(max_length=100)

    quantity = models.FloatField()

    total_price = models.FloatField()

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='Pending'
    )

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.buyer_name} - {self.crop.crop_name}"