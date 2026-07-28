from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator


class Order(models.Model):
    # This is a logical reference to catalog.Book, which is stored in MySQL.
    # It intentionally is not a Django relation because this model is stored
    # in PostgreSQL and cross-database foreign keys are unsupported.
    book_id = models.PositiveBigIntegerField()
    # Authentication data is in auth_db, so this is a logical user reference
    # rather than a cross-database foreign key.
    user_name = models.CharField(max_length=150, db_index=True)
    quantity = models.PositiveIntegerField(default=1)
    total = models.DecimalField(max_digits=10, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        app_label = 'orders'

    def __str__(self):
        return f"Order #{self.id} - book #{self.book_id} ({self.quantity})"


class Review(models.Model):
    # Logical MySQL catalog.Book identifier; see Order.book_id above.
    book_id = models.PositiveBigIntegerField()
    reviewer_name = models.CharField(max_length=255)
    rating = models.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        help_text="Rating must be between 1 and 5"
    )
    comment = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        app_label = 'orders'

    def __str__(self):
        return f"Review by {self.reviewer_name} for book #{self.book_id} ({self.rating}/5)"
