from sqlalchemy import (
    Column,
    DateTime,
    ForeignKey,
    Integer,
    String,
    create_engine,
    event,
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import Session, backref, relationship
from sqlalchemy.sql import func

Base = declarative_base()


class Vote(Base):
    __tablename__ = "vote"
    bet_id = Column(
        Integer,
        ForeignKey("bet.id"),
        primary_key=True,
    )
    author_id = Column(
        Integer,
        ForeignKey("author.id"),
        primary_key=True,
    )
    value = Column(
        String,
        nullable=False,
    )
    created_at = Column(
        DateTime,
        nullable=False,
        server_default=func.now(),
    )

    @staticmethod
    def create(bet_id, author_id, value):
        bet = Bet.read(bet_id)
        if bet.winner_id is not None:
            raise Exception(f"Author with ID {bet.winner_id} won Bet with ID {bet.id}.")
        vote = vote = Vote(
            bet_id=bet_id,
            author_id=author_id,
            value=value,
        )
        session.add(vote)
        try:
            session.commit()
        except Exception as exception:
            session.rollback()
            raise exception
        return vote


class Bet(Base):
    __tablename__ = "bet"
    id = Column(
        Integer,
        primary_key=True,
    )
    author_id = Column(
        Integer,
        ForeignKey("author.id"),
        nullable=False,
    )
    winner_id = Column(
        Integer,
        ForeignKey("author.id"),
    )
    value = Column(
        String,
        nullable=False,
    )
    created_at = Column(
        DateTime,
        nullable=False,
        server_default=func.now(),
    )

    votes = relationship(
        "Vote",
        foreign_keys=[Vote.bet_id],
        backref=backref("bet"),
    )

    @staticmethod
    def create(author_id, value):
        bet = Bet(
            author_id=author_id,
            value=value,
        )
        session.add(bet)
        try:
            session.commit()
        except Exception as exception:
            session.rollback()
            raise exception
        return bet

    @staticmethod
    def read(bet_id=None, exclude_closed=True):
        query = session.query(Bet)
        if exclude_closed:
            query = query.filter_by(winner_id=None)
        return (
            query.all()
            if bet_id is None
            else session.query(Bet).filter_by(id=bet_id).first()
        )

    def update_winner(self, winner_id):
        if winner_id and all(vote.author.id != winner_id for vote in self.votes):
            raise Exception(
                f"Author with ID {winner_id} did not vote in Bet with ID {self.id}."
            )
        self.winner_id = winner_id
        try:
            session.commit()
        except Exception as exception:
            session.rollback()
            raise exception


class Author(Base):
    __tablename__ = "author"
    id = Column(
        Integer,
        primary_key=True,
    )
    discord_id = Column(
        Integer,
        nullable=False,
        unique=True,
    )
    created_at = Column(
        DateTime,
        nullable=False,
        server_default=func.now(),
    )

    bets = relationship(
        "Bet",
        foreign_keys=[Bet.author_id],
        backref=backref("author"),
    )
    won = relationship(
        "Bet",
        foreign_keys=[Bet.winner_id],
        backref=backref("winner"),
    )
    votes = relationship(
        "Vote",
        foreign_keys=[Vote.author_id],
        backref=backref("author"),
    )

    @staticmethod
    def create(discord_id):
        author = Author(discord_id=discord_id)
        session.add(author)
        try:
            session.commit()
        except Exception as exception:
            session.rollback()
            raise exception
        return author

    @staticmethod
    def create_or_read_by_discord_id(discord_id):
        return session.query(Author).filter_by(
            discord_id=discord_id
        ).first() or Author.create(discord_id)


engine = create_engine("sqlite:///db.sqlite")

Base.metadata.create_all(engine)

event.listen(
    engine,
    "connect",
    lambda dbapi_con, _: dbapi_con.execute(
        "PRAGMA foreign_keys=ON"  # SQLite FK are off by default.
    ),
)

session = Session(engine)
