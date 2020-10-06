from aiohttp import web

routes = web.RouteTableDef()


@routes.get('/status')
async def get_status(request: web.Request):
    return web.json_response({
        'status': 'OK'
    })


@routes.post('/signup')
async def signup(request: web.Request):
    data = await request.post()
    email = data['email']
    await request.app.signup(email)
    return web.HTTPOk


class Application(web.Application):
    """ Backend web application
    """
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.add_routes(routes)

    async def signup(self, email):
        raise NotImplementedError("Not implemented Application.signup")


async def app_factory():
    """ Async application factory
    """
    return Application()


if __name__ == '__main__':
    web.run_app(app_factory(), port=8000)
