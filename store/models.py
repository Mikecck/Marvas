from django.db import models

from django.dispatch import receiver

from django.db.models.signals import post_save

from django.contrib.auth.models import User

from django.contrib.staticfiles.templatetags.staticfiles import static

# Create your models here.

class Customer(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, null=True, blank=True)
    name = models.CharField(max_length=200, null=True)
    email = models.CharField(max_length=200, null=True)

    def __str__(self):
        return self.name

@receiver(post_save, sender=User)
def create_customer(sender, instance, created, **kwargs):
    if created:
        Customer.objects.get_or_create(
            user=instance,
            name=instance.username,
            email=instance.email
        )

class Category(models.Model):
    name = models.CharField(max_length=200, unique=True)

    # image
    image = models.ImageField(upload_to='category_images', blank=True)

    def __str__(self):
        return self.name

    @property
    def imageURL(self):
        try:
            url = self.image.url
        except:
            url = static('images/other.png')

        return url

    class Meta:
        verbose_name_plural = "Categories"


class Product(models.Model):
    name = models.CharField(max_length=200)
    price = models.DecimalField(max_digits=7, decimal_places=2)
    condition = models.BooleanField(default=False, null=True, blank=False)
    date_create = models.DateTimeField('date_create')

    # Image
    image = models.ImageField(upload_to='product_images', blank=True)

    # categories
    categories = models.ManyToManyField(Category)

    def __str__(self):
        return self.name

    @property
    def imageURL(self):
        try:
            url = self.image.url
        except:
            url = static('images/placeholder.png')

        return url



# represents cart
class Order(models.Model):
    customer = models.ForeignKey(Customer, on_delete=models.SET_NULL, null=True, blank=True)
    date_ordered = models.DateTimeField(auto_now_add=True)
    complete = models.BooleanField(default=False, null=True, blank=True)
    transaction_id = models.CharField(max_length=200, null=True)

    def __str__(self):
        return str(self.id)

    # get total price
    # of all items
    # in the order or cart
    @property
    def total_price(self):
        orderitems = self.orderitem_set.all()
        total_price = sum([orderitem.total for orderitem in orderitems])
        return float(total_price)

    # get total amount
    # of all items
    # in the order or cart
    @property
    def total_quantity(self):
        orderitems = self.orderitem_set.all()
        total_quantity = sum([orderitem.quantity for orderitem in orderitems])
        return total_quantity

    @property
    def shipping(self):
        shipping = False
        orderitems = self.orderitem_set.all()
        for orderitem in orderitems:
            if orderitem.product.condition == False:
                shipping = True
        return shipping

class OrderItem(models.Model):
    product = models.ForeignKey(Product, on_delete=models.SET_NULL, null=True)
    order = models.ForeignKey(Order, on_delete=models.SET_NULL, null=True)
    quantity = models.IntegerField(default=0, null=True, blank=True)
    date_added = models.DateTimeField(auto_now_add=True)

    @property
    def total(self):
        price_per_item = self.product.price
        total = price_per_item * self.quantity
        return total

class ShippingAddress(models.Model):
    customer = models.ForeignKey(Customer, on_delete=models.SET_NULL, null=True, blank=True)
    order = models.ForeignKey(Order, on_delete=models.SET_NULL, null=True, blank=True)
    address = models.CharField(max_length=200)
    city = models.CharField(max_length=200)
    zipcode = models.CharField(max_length=200, null=True)
    date_added = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.address