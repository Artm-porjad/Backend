import aiohttp
import logging
from aiohttp import web

routes = web.RouteTableDef()


@routes.get('/status')
async def get_status(request: web.Request):
    return web.json_response({
        'status': 'OK'
    })


@routes.get('')
async def websocket_handler(request: web.Request):
    ws = web.WebSocketResponse()
    await ws.prepare(request)
    session = aiohttp.ClientSession()
    try:
        async with session.ws_connect(request.app['next_url'], protocols=['janus-protocol']) as next_ws:
            if request.app.logger.isEnabledFor(logging.DEBUG):
                request.app.logger.debug(f'WS_PROXY(${id(request)}) established!')
            async for msg in ws:
                if msg.type == aiohttp.WSMsgType.TEXT and msg.data == 'close':
                    await ws.close()
                else:
                    if request.app.logger.isEnabledFor(logging.DEBUG):
                        request.app.logger.debug(f'WS_PROXY(${id(request)}) << ${msg.data}')
                    if msg.type == aiohttp.WSMsgType.TEXT:
                        await next_ws.send_str(msg.data)
                        data = await next_ws.receive_str()
                        await ws.send_str(data)
                    elif msg.type == aiohttp.WSMsgType.BINARY:
                        await next_ws.send_bytes(msg.data)
                        data = await  next_ws.receive_bytes()
                        await ws.send_bytes(data)
                    elif msg.type == aiohttp.WSMsgType.ERROR:
                        request.app.logger.warning(f'WS_PROXY(${id(request)}) closed with exception ${ws.exception()}')
                    if request.app.logger.isEnabledFor(logging.DEBUG):
                        request.app.logger.debug(f'WS_PROXY(${id(request)}) >> ${data}')
    finally:
        await session.close()
    if request.app.logger.isEnabledFor(logging.DEBUG):
        request.app.logger.debug(f'WS_PROXY(${id(request)}) closed!')
    return ws

class WebApplication(web.Application):
    """ Backend websocket
    """

    def __init__(self, next_url):
        super().__init__()
        self['next_url'] = next_url
        self.add_routes(routes)
