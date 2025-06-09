# tests/test_orm_basic.py

import pytest
from miniweb.orm.models import Model
from miniweb.orm.fields import StringField, IntegerField, ForeignKey

class User(Model):
    name = StringField()

class Post(Model):
    title = StringField()
    body  = StringField()
    user  = ForeignKey(User)

@pytest.fixture(scope="module", autouse=True)
def setup_db():
    Model.connect(":memory:")
    Model.create_all()
    yield

def test_insert_and_get():
    u = User(name="Alice").save()
    p = Post(title="Hi", body="Hello world", user=u).save()

    assert u.id == 1
    assert p.id == 1

    same_p = Post.get(1)
    assert same_p.title == "Hi"
    assert same_p.user.name == "Alice"

def test_update():
    bob  = User(name="Bob").save()
    note = Post(title="Draft", body="...", user=bob).save()

    note.title = "Published"
    note.save()          
    reread = Post.get(note.id)
    assert reread.title == "Published"

def test_all_and_counts():
    posts = Post.all()
    assert len(posts) == 2
    for post in posts:
        assert isinstance(post.__dict__["user_id"], int)
