from miniweb.utils.config import load_config_from_args
from miniweb.templates.engine import init_template_engine, render_template
from miniweb.orm.models import Model
from miniweb.core.server import App
from demo import Book, Author

def main():
    config = load_config_from_args()

    Model.connect(config["DB_PATH"])
    Model.create_all()

    init_template_engine(
        enabled=config["TEMPLATES_ENABLED"],
        templates_dir="templates"
    )

    app = App()

    @app.route("/")
    def index(request):
        if config["TEMPLATES_ENABLED"]:
            return render_template("index.html", {})
        return (
            "Hello, world!<br>"
            '<a href="/items">List of books</a>'
        )


    @app.route("/items")
    async def list_items(request):
        items = Book.all()
        if config["TEMPLATES_ENABLED"]:
            return render_template("items.html", {"items": items})
        return "\n".join(f"{i:>2}. {b}" for i, b in enumerate(items, 1)) or "Книг нет."

    def _books_by_author(author):
        aid = author.id
        return [
            b for b in Book.all()
            if getattr(b.author, "id", b.author) == aid
        ]

    @app.route("/authors/<int:author_id>")
    def author_detail(req, author_id: int):
        author = Author.get(author_id)
        if author is None:
            return "Автор не найден", 404

        books = _books_by_author(author)

        if config["TEMPLATES_ENABLED"]:
            return render_template("author.html",
                                {"author": author, "books": books})

        titles = ", ".join(b.title for b in books) or "нет книг"
        return f"{author.name}: {titles}"

    app.run(
        host=config["HOST"],
        port=config["PORT"],
        debug=config["DEBUG"]
    )

if __name__ == "__main__":
    main()