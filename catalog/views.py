import logging

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render

from catalog.models import Book
from orders.forms import OrderForm, ReviewForm
from orders.models import Order, Review
from activity.mongo import recent_views, log_view

logger = logging.getLogger(__name__)


def _home_context(request, review_forms=None):
    books = list(Book.objects.using('default').select_related('author', 'category').all())
    book_ids = [book.id for book in books]

    reviews_qs = Review.objects.using('orders_db').filter(book_id__in=book_ids).order_by('-created_at')
    reviews_by_book = {}
    books_by_id = {}
    for book in books:
        books_by_id[book.id] = book
    for review in reviews_qs:
        reviews_by_book.setdefault(review.book_id, []).append(review)

    activity_documents = recent_views(user_id=request.user.id, limit=10)
    recent_ids = [document['book_id'] for document in activity_documents]
    logger.warning("Mongo ordered book IDs: %s", recent_ids)
    mysql_books = Book.objects.using('default').select_related('author').filter(id__in=recent_ids)
    logger.warning(
        "MySQL books resolved from Mongo IDs: %s",
        list(mysql_books.values_list('id', 'title')),
    )
    recent_books_by_id = {
        book.id: book
        for book in mysql_books
    }
    recently_viewed = [
        recent_books_by_id[book_id]
        for book_id in recent_ids
        if book_id in recent_books_by_id
    ]

    return {
        'books': books,
        'reviews': reviews_qs,
        'reviews_by_book': reviews_by_book,
        'books_by_id': books_by_id,
        'recently_viewed': recently_viewed,
        'review_forms': review_forms or {book.id: ReviewForm() for book in books},
    }


@login_required(login_url='accounts:login')
def home(request):
    return render(request, 'catalog/home.html', _home_context(request))


@login_required(login_url='accounts:login')
def book_detail(request, book_id):
    logger.warning(
        "BOOK DETAIL VIEW ENTERED: book_id=%s user_id=%s path=%s",
        book_id,
        request.user.id if request.user.is_authenticated else None,
        request.path,
    )
    book = get_object_or_404(
        Book.objects.using('default').select_related('author', 'category'), pk=book_id
    )
    logger.warning(
        "CALLING MONGODB log_view: book_id=%s user_id=%s",
        book.id,
        request.user.id if request.user.is_authenticated else None,
    )
    inserted_id = log_view(
        book_id=book.id,
        user_id=request.user.id,
        request_path=request.path,
        debug_marker="REAL_CLICK_TEST",
    )
    logger.warning("MONGODB log_view RESULT: inserted_id=%s", inserted_id)
    if inserted_id is None:
        logger.warning(
            "Book detail loaded, but MongoDB activity logging failed. "
            "book_id=%s user_id=%s",
            book.id,
            request.user.id,
        )
    reviews = Review.objects.using('orders_db').filter(book_id=book.id).order_by('-created_at')
    return render(request, 'catalog/book_detail.html', {
        'book': book,
        'reviews': reviews,
        'review_form': ReviewForm(),
    })


@login_required(login_url='accounts:login')
def place_order(request, book_id):
    book = get_object_or_404(Book.objects.using('default'), pk=book_id)
    form = OrderForm(request.POST or None, initial={'book': book})
    if request.method == 'POST' and form.is_valid():
        order = form.save(commit=False)
        order.user_name = request.user.username
        order.total = form.cleaned_data['book'].price * order.quantity
        order.save(using='orders_db')
        messages.success(request, 'Your order has been placed.')
        return redirect('catalog:book_detail', book_id=form.cleaned_data['book'].id)
    return render(request, 'catalog/order_form.html', {'book': book, 'form': form})


@login_required(login_url='accounts:login')
def submit_review(request, book_id):
    book = get_object_or_404(Book.objects.using('default'), pk=book_id)
    if request.method != 'POST':
        return redirect('catalog:book_detail', book_id=book.id)

    form = ReviewForm(request.POST)
    if form.is_valid():
        review = form.save(commit=False)
        review.book_id = book.id
        review.reviewer_name = request.user.username
        review.save(using='orders_db')
        messages.success(request, 'Thanks—your review has been published.')
        return redirect('catalog:book_detail', book_id=book.id)

    if request.POST.get('next') == 'home':
        review_forms = {item.id: ReviewForm() for item in Book.objects.using('default').all()}
        review_forms[book.id] = form
        return render(request, 'catalog/home.html', _home_context(request, review_forms), status=400)

    reviews = Review.objects.using('orders_db').filter(book_id=book.id).order_by('-created_at')
    return render(request, 'catalog/book_detail.html', {
        'book': book,
        'reviews': reviews,
        'review_form': form,
    }, status=400)


@login_required(login_url='accounts:login')
def my_orders(request):
    orders = Order.objects.using('orders_db').filter(user_name=request.user.username).order_by('-created_at')
    books_by_id = {
        book.id: book
        for book in Book.objects.using('default').filter(id__in=[order.book_id for order in orders])
    }
    return render(request, 'catalog/my_orders.html', {'orders': orders, 'books_by_id': books_by_id})
