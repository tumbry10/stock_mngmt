from django.db import models
from django.core.exceptions import ValidationError
from django.db import transaction


# Create your models here.
class Brand(models.Model):
    name = models.CharField(max_length=255, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'brand'

    def save(self, *args, **kwargs):
        # Convert name to title before saving
        if self.name:
            self.name = self.name.title()
        super().save(*args, **kwargs)
    
    def __str__(self):
        return self.name
    
class Product(models.Model):
    name = models.CharField(max_length=255, unique=True)
    brand = models.ForeignKey(Brand, on_delete=models.CASCADE)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    quantity = models.PositiveIntegerField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'product'
        ordering = ['name']
    
    def save(self, *args, **kwargs):
        # Convert name to title before saving
        if self.name:
            self.name = self.name.title()
        super().save(*args, **kwargs)
    
    def __str__(self):
        return self.name

class Stock(models.Model):
    STOCK_TYPE_CHOICES = [
        ('in_stock', 'In Stock'),
        ('out_of_stock', 'Out of Stock'),
    ]
    reference_no = models.CharField(max_length=50, unique=True)
    stock_type = models.CharField(max_length=20, choices=STOCK_TYPE_CHOICES, default='in_stock')
    date = models.DateTimeField(auto_now_add=True)
    notes = models.TextField(blank=True, null=True)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)

    def __str__(self):
        return f"{self.reference_number} - {self.get_stock_type_display()}"

    def calculate_total(self):
        total = sum(item.quantity * item.unit_price for item in self.stockitem_set.all())
        self.total_amount = total
        self.save()

    class Meta:
        ordering = ['-date']
        db_table = 'stock'

class StockItem(models.Model):
    stock = models.ForeignKey(Stock, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField()
    unit_price = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"{self.product.name} - {self.quantity}"

    def clean(self):
        if self.stock.stock_type == 'out_of_stock' and self.quantity > self.product.quantity:
            raise ValidationError(f'Insufficient stock for {self.product.name}. Available: {self.product.quantity}')

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)
    
    class Meta:
        db_table = 'stock_item'

class Sale(models.Model):
    invoice_number = models.CharField(max_length=50, unique=True)
    customer_name = models.CharField(max_length=100, blank=True)
    date = models.DateTimeField(auto_now_add=True)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    notes = models.TextField(blank=True)

    def __str__(self):
        return f"{self.invoice_number} - {self.customer_name}"

    def calculate_total(self):
        total = sum(item.quantity * item.unit_price for item in self.saleitem_set.all())
        self.total_amount = total
        self.save()

    class Meta:
        ordering = ['-date']
        db_table = 'sale'

class SaleItem(models.Model):
    sale = models.ForeignKey(Sale, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.IntegerField()
    unit_price = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"{self.product.name} - {self.quantity}"

    def clean(self):
        if self.quantity > self.product.quantity:
            raise ValidationError(f'Insufficient stock for {self.product.name}. Available: {self.product.quantity}')

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)

    class Meta:
        db_table = 'sale_item'