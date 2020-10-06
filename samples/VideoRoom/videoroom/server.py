from aiohttp import web
from aiopg.sa import create_engine
from uuid import uuid4
from sqlalchemy import insert, select
from videoroom.models import RegToken
from datetime import datetime, timedelta

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
    return web.HTTPOk()


@routes.get('/signup_check/{token}')
async def signup_check(request: web.Request):
    token = request.match_info['token']
    if await request.app.signup_check(token):
        return  web.HTTPOk()
    return web.HTTPNotFound()


class Application(web.Application):
    """ Backend web application
    """
    REG_TOKEN_EXP = 900

    def __init__(self, engine, **kwargs):
        super().__init__(**kwargs)
        self.add_routes(routes)
        self.engine = engine

    async def signup(self, email):
        token = str(uuid4())
        expired_at = datetime.now() + timedelta(seconds=Application.REG_TOKEN_EXP)
        async with self.engine.acquire() as connection:
            sql = insert(RegToken).values(email=email, token=token, expired_at=expired_at)
            await connection.execute(sql)
            # ToDo: send mail with reg token

    async def signup_check(self, token):
        async with self.engine.acquire() as connection:
            sql = select([RegToken]).where(RegToken.token==token)
            async for row in connection.execute(sql):
                if row['expired_at'] >= datetime.now():
                    return await self.signup_final(row['id'])
            return False

    async def signup_final(self, id):
        # ToDo:  Complete registration.
        return True



async def app_factory(database_url):
    """ Async application factory
    """
    engine = await create_engine(database_url)
    return Application(engine)


if __name__ == '__main__':
    url = 'postgresql://postgres:123456@localhost:54321/videoroom'
    web.run_app(app_factory(url), port=8000)
