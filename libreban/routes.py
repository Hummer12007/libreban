import json
import react
from sanic import response
from sanic.exceptions import abort

from sqlalchemy import and_

from libreban.app import *
from libreban.misc import *
from libreban.model import *
from libreban.socket import dispatch

react.set_up()
react.utils.load_libs([f'{app.config.FRONTEND_PATH}/prerender.js'])


@app.route('/board/<id:int>')
@jinja.template('board.html')
async def board(request, id):
    board = await load_board(id)
    if not board:
        abort(404, "Board not found")
    print(board.initials, board.name, board.column_order)
    for cid, col in board.columns.items():
        print('\t', col.name, col.cid, col.ticket_order)
    for tid, tkt in board.tickets.items():
        print('\tTICKET ', tkt.tid, tkt.name, tkt.description)
    state = {
        'order': board.column_order,
        'columns': {},
        'tickets': {}
    }
    for cid, col in board.columns.items():
        state['columns'][col.cid] = {'name': col.name, 'tickets': col.ticket_order}
    for tid, tkt in board.tickets.items():
        state['tickets'][tkt.tid] = {'name': tkt.name, 'description': tkt.description}
    print(json.dumps(state))
    return {
        'name': board.name,
        'markup': react.React(state).render(),
        'bid': id,
        'state': json.dumps(state)
    }

@app.route('/board/new')
async def create_board(request):
    await gen_board()
    return response.redirect('/board/1')

@app.route('/board/<id:int>/move-ticket', methods=['POST'])
async def moveTicket(request, id):
    print(request.json)
    board = await load_board(id)
    if (not board
            or not request.json['ticket'] in board.tickets
            or not request.json['dest'] in board.columns
            or request.json['destIdx'] > len(board.columns[request.json['dest']].ticket_order)):
        abort(404, "Board not found")
    async with db.transaction():
        for cid, col in board.columns.items():
            if request.json['ticket'] in col.ticket_order:
                col.ticket_order.remove(request.json['ticket'])
                await col.update(ticket_order=col.ticket_order).apply()
        dest = board.columns[request.json['dest']]
        dest.ticket_order.insert(request.json['destIdx'], request.json['ticket'])
        await dest.update(ticket_order=dest.ticket_order).apply()
    await dispatch(id, json.dumps({ 'type': 'move-ticket', **request.json }))
    return response.json({'ca': 'OK'})

@app.route('/board/<id:int>/move-container', methods=['POST'])
async def moveContainer(request, id):
    print(request.json)
    b = await Board.get(id)
    if not board:
        abort(404, "Board not found")
    order = list(b.column_order)
    idx = order.index(request.json['column'])
    if idx < 0 or request.json['dest'] >= len(order):
        abort(404, "Wrong column or index")
    order.insert(request.json['dest'], order.pop(idx))
    await b.update(column_order=order).apply() 
    await dispatch(id, json.dumps({ 'type': 'move-container', **request.json }))
    return response.text('OK')

@app.route('/')
async def root(request):
    return response.text('')

@app.route('/board/<id:int>/add-ticket', methods=['POST'])
async def test(request, id):
    print(request.json)
    j = request.json
    board = await load_board(id)
    column = await Column.query.where(and_(Column.board_id == id, Column.cid == j['column'])).gino.first()
    tkt = await Ticket.create(board_id=id, name=j['name'], description=j['description'])
    await tkt.update(tid=tkt.id).apply()
    order = list(column.ticket_order)
    order.append(tkt.id)
    await column.update(ticket_order=order).apply()
    await dispatch(id, json.dumps({ 'type': 'add-ticket', 'tid': tkt.tid, 'idx': len(order) - 1, **request.json }))
    return response.text('OK')
