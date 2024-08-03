from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, timezone
from typing import Optional
from flask_login import UserMixin
import sqlalchemy as sa
import sqlalchemy.orm as so
from app import db, login


@login.user_loader
def load_user(id):
    return db.session.get(User, int(id))


class User(UserMixin, db.Model):
    id: so.Mapped[int] = so.mapped_column(primary_key=True)
    username: so.Mapped[str] = so.mapped_column(sa.String(64), index=True,
                                                unique=True)
    email: so.Mapped[str] = so.mapped_column(sa.String(120), index=True,
                                             unique=True)
    password_hash: so.Mapped[Optional[str]] = so.mapped_column(sa.String(256))

    ads: so.WriteOnlyMapped['Ad'] = so.relationship(
        back_populates='author')

    def __repr__(self):
        return f"<User {self.username}>"
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)


class Category(db.Model):
    id: so.Mapped[int] = so.mapped_column(primary_key=True)
    name: so.Mapped[str] = so.mapped_column(sa.String(50))

    cat: so.WriteOnlyMapped['Ad'] = so.relationship(
        back_populates='category')


class Ad(db.Model):
    id: so.Mapped[int] = so.mapped_column(primary_key=True)
    title: so.Mapped[str] = so.mapped_column(sa.String(40))
    text: so.Mapped[str] = so.mapped_column(sa.String(140))
    timestamp: so.Mapped[datetime] = so.mapped_column(
        index=True, default=lambda: datetime.now(timezone.utc))
    price: so.Mapped[int] = so.mapped_column(sa.Integer())
    user_id: so.Mapped[int] = so.mapped_column(sa.ForeignKey(User.id),
                                               index=True)
    category_id: so.Mapped[int] = so.mapped_column(sa.ForeignKey(Category.id),
                                               index=True)
    
    author: so.Mapped[User] = so.relationship(back_populates='ads')
    category: so.Mapped[Category] = so.relationship(back_populates='cat')

    def __repr__(self):
        return f"<Title {self.title}>"
    
    def ad_photo(self):
        pass
    

