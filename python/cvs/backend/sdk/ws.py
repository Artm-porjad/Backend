import asyncio
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
    app = request.app  # type: WebApplication
    frontend = web.WebSocketResponse()
    await frontend.prepare(request)
    session = aiohttp.ClientSession()
    try:
        if app.logger.isEnabledFor(logging.DEBUG):
            request.app.logger.debug(f'WS_PROXY(${id(request)}) establishing...')
        async with session.ws_connect(app['next_url'], protocols=['janus-protocol']) as backend:

            async def backend2frontend():
                async for msg in backend:
                    if request.app.logger.isEnabledFor(logging.DEBUG):
                        request.app.logger.debug(f'WS_PROXY(${id(request)}) << ${msg.data}')
                    if msg.type == aiohttp.WSMsgType.TEXT:
                        await frontend.send_str(msg.data)
                    elif msg.type == aiohttp.WSMsgType.ERROR:
                        exc = backend.exception()
                        await frontend.close(message=f'Remote exception: ${exc}')
                        raise exc

            async def frontend2backend():
                async for msg in frontend:
                    if request.app.logger.isEnabledFor(logging.DEBUG):
                        request.app.logger.debug(f'WS_PROXY(${id(request)}) >> ${msg.data}')
                    if msg.type == aiohttp.WSMsgType.TEXT:
                        await backend.send_str(msg.data)
                    elif msg.type == aiohttp.WSMsgType.ERROR:
                        exc = frontend.exception()
                        await backend.close(message=f'Remote exception: ${exc}')
                        raise exc


            await asyncio.gather(backend2frontend(), frontend2backend())
    except Exception:
        app.logger.exception(f'WS_PROXY(${id(request)}) fail')
    finally:
        await session.close()
        if app.logger.isEnabledFor(logging.DEBUG):
            app.logger.debug(f'WS_PROXY(${id(request)}) done')
    return frontend


class WebApplication(web.Application):
    """ Backend websocket
    """

    def __init__(self, next_url):
        super().__init__()
        self['next_url'] = next_url
        self.add_routes(routes)

    async def _proxy(self, tx, rx):
        pass

    async def do_proxying(self, frontend):
        session = aiohttp.ClientSession()
        try:
            async with session.ws_connect(self['next_url'], protocols=['janus-protocol']) as backend:
                await asyncio.gather(self._proxy(backend, frontend), self._proxy(frontend, backend))
        finally:
            await session.close()
        return frontend
