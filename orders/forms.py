from django import forms

from catalog.models import Book
from .models import Order, Review


class OrderForm(forms.ModelForm):
    """Creates a PostgreSQL order while accepting a MySQL catalog book."""

    book = forms.ModelChoiceField(
        queryset=Book.objects.using('default').order_by('title'),
        empty_label=None,
        label='Book',
    )

    class Meta:
        model = Order
        fields = ('book', 'quantity')
        widgets = {
            'quantity': forms.NumberInput(attrs={'min': 1}),
        }

    def save(self, commit=True):
        order = super().save(commit=False)
        order.book_id = self.cleaned_data['book'].id
        if commit:
            order.save(using='orders_db')
        return order


class ReviewForm(forms.ModelForm):
    rating = forms.TypedChoiceField(
        choices=[(rating, f'{rating} / 5') for rating in range(1, 6)],
        coerce=int,
        empty_value=None,
    )
    comment = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={'rows': 3, 'placeholder': 'Share your thoughts about this book'}),
    )

    class Meta:
        model = Review
        fields = ('rating', 'comment')

    def clean_comment(self):
        comment = self.cleaned_data['comment'].strip()
        if not comment:
            raise forms.ValidationError('Please enter a review comment.')
        return comment
