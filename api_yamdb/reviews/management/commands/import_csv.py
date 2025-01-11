import csv
import os

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand, CommandError

from reviews.models import Category, Comment, Genre, Review, Title

User = get_user_model()

IMPORT_CONFIG = [
    {"file": "users.csv", "model": User},
    {"file": "category.csv", "model": Category},
    {"file": "genre.csv", "model": Genre},
    {"file": "titles.csv", "model": Title},
    {"file": "genre_title.csv", "model": None},
    {"file": "review.csv", "model": Review},
    {"file": "comments.csv", "model": Comment},
]


class Command(BaseCommand):
    help = "Импортирует данные из CSV файлов в БД."

    def add_arguments(self, parser):
        parser.add_argument(
            "--path",
            type=str,
            default="static/data/",
            help="Directory path containing CSV files.",
        )

    def handle(self, *args, **options):
        path = options["path"]

        if not os.path.exists(path):
            raise CommandError(f"The directory {path} does not exist.")

        for config in IMPORT_CONFIG:
            filename = config["file"]
            model = config["model"]
            file_path = os.path.join(path, filename)

            if not os.path.exists(file_path):
                self.stdout.write(
                    self.style.WARNING(
                        f"File {filename} not found. Skipping..."
                    )
                )
                continue

            if filename == "genre_title.csv":
                self.stdout.write(
                    self.style.SUCCESS(f"Importing data from {filename}...")
                )
                self.import_genre_title(file_path)
            else:
                self.stdout.write(
                    self.style.SUCCESS(f"Importing data from {filename}...")
                )
                self.import_csv(file_path, model)

    def import_csv(self, file_path, model):
        with open(file_path, encoding="utf-8") as csvfile:
            reader = csv.DictReader(csvfile)
            count = 0
            for row in reader:
                try:
                    # Обрабатываем FK
                    if model == Title and "category" in row:
                        category_id = row.pop("category")
                        row["category"] = Category.objects.get(id=category_id)

                    if model == Review and "author" in row:
                        user_id = row.pop("author")
                        row["author"] = User.objects.get(id=user_id)

                    if model == Review and "title" in row:
                        title_id = row.pop("title")
                        row["title"] = Title.objects.get(id=title_id)

                    if model == Comment and "author" in row:
                        user_id = row.pop("author")
                        row["author"] = User.objects.get(id=user_id)

                    if model == Comment and "review" in row:
                        review_id = row.pop("review")
                        row["review"] = Review.objects.get(id=review_id)

                    model.objects.update_or_create(**row)
                    count += 1
                except Exception as e:
                    self.stdout.write(
                        self.style.ERROR(f"Error importing row {row}: {e}")
                    )

            self.stdout.write(
                self.style.SUCCESS(
                    f"Successfully imported {count} rows "
                    f"into {model.__name__}."
                )
            )

    def import_genre_title(self, file_path):
        """Специальный обработчик genre_title.csv. Работает с М2М связью."""

        with open(file_path, encoding="utf-8") as csvfile:
            reader = csv.DictReader(csvfile)
            count = 0
            for row in reader:
                try:
                    title = Title.objects.get(id=row["title_id"])
                    genre = Genre.objects.get(id=row["genre_id"])
                    title.genre.add(genre)
                    count += 1
                except Exception as e:
                    self.stdout.write(
                        self.style.ERROR(f"Error importing row {row}: {e}")
                    )
