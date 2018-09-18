from libreban.model import *

async def load_board(id):
    q1 = Board.outerjoin(Column).select().where(Board.id == id)
    b1 = await q1.gino.load(
        Board.distinct(Board.id).load(add_column=Column)).all()

    q2 = Board.outerjoin(Ticket).select().where(Board.id == id)
    b2 = await q2.gino.load(
        Board.distinct(Board.id).load(add_ticket=Ticket)).all()

    if len(b1) < 1 or len(b2) < 1:
        return None
    board = b1[0]
    board._tickets = b2[0]._tickets
    return board

async def gen_board():
    async with db.transaction():
        cols = ['todo', 'inprogress', 'taskreview', 'codereview', 'done']
        b = await Board.create(name='BC Board', initials='BC', column_order=cols)
        await Column.create(board_id=b.id, cid='todo', name='To Do', ticket_order=[1, 2])
        await Column.create(board_id=b.id, cid='inprogress', name='In Progress', ticket_order=[])
        await Column.create(board_id=b.id, cid='taskreview', name='Task Review', ticket_order=[])
        await Column.create(board_id=b.id, cid='codereview', name='Code Review', ticket_order=[])
        await Column.create(board_id=b.id, cid='done', name='Done', ticket_order=[])
        await Ticket.create(board_id=b.id, tid=1, name='Implement ticket addition',
                description='As a user I would like to be able to add tickets to the board')
        await Ticket.create(board_id=b.id, tid=2, name='Implement ticket removal',
                description='As a user I would like to be able to remove tickets from the board')
