import asyncio
import importlib
import os
import sys
import traceback
import csv
import aiohttp
from aiohttp import web
from gidgetlab.aiohttp import GitLabBot
from gidgetlab import sansio
from gidgetlab import aiohttp as gl_aiohttp
from gidgetlab import routing
import joblib

routes = web.RouteTableDef()
router = routing.Router()

model = joblib.load('./notebooks/model1.sav')

model =joblib.load('./notebooks/model1.sav')
def pred_label( title , description):
    X = [title +' '+ description]
    print(X)
    label = model.predict(X)
    print(label)
    return label[0]

@router.register("Issue Hook", action  ="open")
async def issue_opened_event(event, gl, *args, **kwargs):
    data =event.data
    title = data["object_attributes"]["title"]
    description = data["object_attributes"]["description"]
    label = pred_label(title,description)
    url = f'https://gitlab.tu-clausthal.de/api/v4/projects/{data["project"]["id"]}/issues/{data["object_attributes"]["iid"]}/notes'
    url1 =f'https://gitlab.tu-clausthal.de/api/v4/projects/{data["project"]["id"]}/issues/{data["object_attributes"]["iid"]}?labels= {label}'
    print (url1)
    message = f'hello im label_bot_1.1 🤙 i predicted label **{label}** for your issue'
    label1 = f'{label}'
    await gl.post(url, data ={'body': message})
    await gl.put(url1)

@routes.post("/")
async def main(request):

    body = await request.read()
    secret = os.environ.get("GH_SECRET")
    oauth_token = os.environ.get("GH_AUTH")

    event = sansio.Event.from_http(request.headers, body, secret=secret)
    async with aiohttp.ClientSession() as session:
        gl = gl_aiohttp.GitLabAPI(session, "sk65",
                                  access_token=oauth_token)
        await router.dispatch(event, gl)
    return web.Response(status=200)


if __name__ == "__main__":
    app = web.Application()
    app.add_routes(routes)
    port = os.environ.get("PORT")
    if port is not None:
        port = int(port)

    web.run_app(app, port=port)
