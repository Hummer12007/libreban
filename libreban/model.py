from libreban.app import db

class Board(db.Model):
    __tablename__ = 'boards'

    id = db.Column(db.BigInteger(), primary_key=True)
    initials = db.Column(db.Unicode())
    name = db.Column(db.Unicode())
    column_order = db.Column(db.ARRAY(db.Unicode()))

    def __init__(self, **kw):
        super().__init__(**kw)
        self._columns = dict()
        self._tickets = dict()

    @property
    def columns(self):
        return self._columns

    @columns.setter
    def add_column(self, column):
        self._columns[column.cid] = column

    @property
    def tickets(self):
        return self._tickets

    @tickets.setter
    def add_ticket(self, ticket):
        self._tickets[ticket.tid] = ticket


class Column(db.Model):
    __tablename__ = 'columns'

    id = db.Column(db.BigInteger(), primary_key=True)
    board_id = db.Column(db.BigInteger, db.ForeignKey('boards.id', ondelete='CASCADE'), index=True)
    cid = db.Column(db.Unicode())
    name = db.Column(db.Unicode())
    ticket_order = db.Column(db.ARRAY(db.BigInteger()))


class Ticket(db.Model):
    __tablename__ = 'tickets'

    id = db.Column(db.BigInteger(), primary_key=True)
    board_id = db.Column(db.BigInteger, db.ForeignKey('boards.id', ondelete='CASCADE'), index=True)
    tid = db.Column(db.BigInteger()) # TODO: autoincrement on per-board basis
    name = db.Column(db.Unicode())
    description = db.Column(db.Unicode())

    def __init__(self, **kw):
        super().__init__(**kw)
        self._comments = set()

    @property
    def comments(self):
        return self._comments

    @comments.setter
    def add_comment(self, comment):
        self._comments.add(comment)



class Comment(db.Model):
    __tablename__ = 'comments'

    id = db.Column(db.BigInteger(), primary_key=True)
    ticket_id = db.Column(db.BigInteger, db.ForeignKey('tickets.id', ondelete='CASCADE'), index=True)
    date = db.Column(db.DateTime())
    author = db.Column(db.Unicode())
    content = db.Column(db.Unicode())
