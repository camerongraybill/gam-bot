from .aiohttp_fixes import patch_gather
patch_gather()

from aiohttp import web

routes = web.RouteTableDef()


# pylint: disable=unused-argument
@routes.get("/healthz")
async def healthcheck(request: web.Request) -> web.Response:
    return web.Response(text="Why hello there")


def get_app() -> web.Application:
    app = web.Application()
    app.add_routes(routes)
    return app
