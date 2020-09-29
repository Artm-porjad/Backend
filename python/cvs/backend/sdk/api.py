from aiohttp import web

routes = web.RouteTableDef()


@routes.get('/status')
async def get_status(request: web.Request):
    return web.json_response({
        'status': 'OK'
    })


class WebApplication(web.Application):
    """ Backend API
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.add_routes(routes)
