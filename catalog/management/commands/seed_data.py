from django.core.management.base import BaseCommand
from catalog.models import Category, Author, Book
from orders.models import Review


class Command(BaseCommand):
    help = 'Seeds sample data into MySQL (default) and PostgreSQL (orders_db)'

    def handle(self, *args, **options):
        self.stdout.write("Starting database seeding...")

        # Use stable natural keys so it is safe to run this command repeatedly.
        # Catalog and reviews are intentionally handled through separate databases.
        c1, _ = Category.objects.using('default').get_or_create(name="Computer Science & Engineering")
        c2, _ = Category.objects.using('default').get_or_create(name="Fiction & Literature")
        c3, _ = Category.objects.using('default').get_or_create(name="Data Science & Artificial Intelligence")

        # 3. Insert 2 Authors into MySQL (default)
        a1, _ = Author.objects.using('default').get_or_create(
            name="Robert C. Martin",
            bio="Renowned software engineer, author of Clean Code and agile software craftsman."
        )
        a2, _ = Author.objects.using('default').get_or_create(
            name="George Orwell",
            bio="English novelist, essayist, and critic famous for dystopian fiction masterpieces."
        )

        # 4. Insert 6 Books into MySQL (default)
        b1, _ = Book.objects.using('default').update_or_create(
            title="Clean Code: A Handbook of Agile Software Craftsmanship",
            author=a1,
            category=c1,
            price=44.99,
            description="A classic guide to writing readable, maintainable, and refactored software."
        )
        b2, _ = Book.objects.using('default').update_or_create(
            title="The Clean Coder: A Code of Conduct for Professional Programmers",
            author=a1,
            category=c1,
            price=39.99,
            description="Practical advice for professional software developers on discipline and engineering."
        )
        b3, _ = Book.objects.using('default').update_or_create(
            title="Clean Architecture: A Craftsman's Guide to Software Structure",
            author=a1,
            category=c1,
            price=49.99,
            description="Universal rules of software architecture, component design, and system boundaries."
        )
        b4, _ = Book.objects.using('default').update_or_create(
            title="1984",
            author=a2,
            category=c2,
            price=14.99,
            description="A chilling dystopian novel depicting totalitarian surveillance and government control."
        )
        b5, _ = Book.objects.using('default').update_or_create(
            title="Animal Farm",
            author=a2,
            category=c2,
            price=11.99,
            description="A satirical allegorical novella reflecting political power dynamics and revolution."
        )
        b6, _ = Book.objects.using('default').update_or_create(
            title="Homage to Catalonia",
            author=a2,
            category=c2,
            price=16.50,
            description="Personal account of fighting in the Spanish Civil War and political struggle."
        )

        # 5. Insert 5 Reviews into PostgreSQL (orders_db) using book_id integer references
        Review.objects.using('orders_db').update_or_create(
            book_id=b1.id,
            reviewer_name="Alice Johnson",
            defaults={'rating': 5, 'comment': "Transformed the way I write code every single day. Highly recommended!"},
        )
        Review.objects.using('orders_db').update_or_create(
            book_id=b1.id,
            reviewer_name="Bob Smith",
            defaults={'rating': 4, 'comment': "Solid principles, though some code samples feel slightly dated."},
        )
        Review.objects.using('orders_db').update_or_create(
            book_id=b4.id,
            reviewer_name="Charlie Brown",
            defaults={'rating': 5, 'comment': "A timeless masterpiece. More relevant today than ever before."},
        )
        Review.objects.using('orders_db').update_or_create(
            book_id=b2.id,
            reviewer_name="Diana Prince",
            defaults={'rating': 5, 'comment': "Essential reading for anyone looking to build a career as a professional developer."},
        )
        Review.objects.using('orders_db').update_or_create(
            book_id=b5.id,
            reviewer_name="Evan Wright",
            defaults={'rating': 4, 'comment': "Short, impactful, and brilliant political satire."},
        )

        self.stdout.write(self.style.SUCCESS(
            "Seeding Complete!\n"
            "- MySQL ('default'): 3 Categories, 2 Authors, 6 Books inserted.\n"
            "- PostgreSQL ('orders_db'): 5 Reviews inserted."
        ))
