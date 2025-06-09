from pathlib import Path
from random   import randint

from miniweb.orm.models import Model
from miniweb.orm.fields import StringField, IntegerField, ForeignKey

DB_FILE = "big_demo.db"
Path(DB_FILE).unlink(missing_ok=True)
Model.connect(DB_FILE)

class Author(Model):
    name = StringField()

class Book(Model):
    title  = StringField()
    pages  = IntegerField(default=0)
    author = ForeignKey(Author)

    def __str__(self) -> str:
        return f"{self.title} — {self.pages} стр. (автор: {self.author.name})"

Model.create_all()
author_objs: list[Author] = []
for idx in range(1, 6):
    a = Author(name=f"Author #{idx}")
    a.save()
    author_objs.append(a)
    for k in range(1, 4):
        Book(
            title = f"Book {k}-of-{idx}",
            pages = randint(90, 400),
            author = a,
        ).save()

header = f"{'ID':>2}  {'BOOK TITLE':15} {'PAGES':>5}  {'AUTHOR'}"
print(header)
print("-" * len(header))

for b in Book.all():
    print(f"{b.id:>2}  {b.title:15} {b.pages:>5}  {b.author.name}")

print("\nВсего авторов:", len(Author.all()))
print("Всего книг   :", len(Book.all()))
