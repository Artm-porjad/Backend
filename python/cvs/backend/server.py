from aiohttp import web
import cvs.backend.sdk.api
import cvs.backend.sdk.ws


class WebApplication(web.Application):
    """ Backend server
    """

    def __init__(self, options):
        super().__init__(logger=logging.root)
        self.add_subapp(f"/v1{options.api_uri}", cvs.backend.sdk.api.WebApplication())
        self.add_subapp(f"/v1{options.ws_uri}", cvs.backend.sdk.ws.WebApplication(next_url=options.janus))


if __name__ == '__main__':
    import logging
    import configargparse

    parser = configargparse.ArgumentParser("CVS Backend Server")
    parser.add_argument('-c', '--config', is_config_file=True, help='config file path')
    parser.add_argument('-j', '--janus', required=True, help='URL of Janus websocket', env_var='JANUS_WS')
    parser.add_argument('--api-uri', default='/api', help='URI to backend API', env_var='BACKEND_API_URI')
    parser.add_argument('--ws-uri', default='/ws', help='URI to websocket', env_var='BACKEND_WS_URI')
    parser.add_argument('-p', '--port', default=5000, help='service port', env_var='BACKEND_PORT')
    parser.add_argument('-d', '--debug', default=False, action='store_true', help='debug mode', env_var='DEBUG')

    options, _ = parser.parse_known_args()


    async def app_factory():
        return WebApplication(options)


    logging.basicConfig(level=(logging.DEBUG if options.debug else logging.WARNING))
    web.run_app(app_factory(), port=options.port)
