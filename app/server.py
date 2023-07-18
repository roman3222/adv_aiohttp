import json
from aiohttp import web
from models import engine, Base, User, Advertisement, Session
from schema import CreateUser, UpdateUser, VALIDATION_CLASS
from pydantic import ValidationError
from sqlalchemy.exc import IntegrityError
from auth import hash_password


async def orm_context(app):
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    await engine.dispose()


@web.middleware
async def session_middleware(request: web.Request, handler):
    async with Session() as session:
        request['session'] = session
        response = await handler(request)
        return response


async def get_user(user_id: int, session: Session) -> User:
    user = await session.get(User, user_id)
    if user is None:
        raise web.HTTPNotFound(
            text=json.dumps({"error": "user not found"}),
            content_type='application/json'
        )
    return user


async def get_adv(adv_id: int, session: Session) -> Advertisement:
    adv = await session.get(Advertisement, adv_id)
    if adv is None:
        raise web.HTTPNotFound(
            text=json.dumps({"error": "advertisement not found"}),
            content_type="application/json"
        )
    return adv


def get_json_user(user):
    return web.json_response({
        "id": user.id,
        "name": user.name,
        "creation_time": int(user.creation_time.timestamp()),
    })


def get_json_adv(adv):
    return web.json_response({
        "id": adv.id,
        "title": adv.title,
        "descriptions": adv.descriptions,
        "user": adv.user_id,
    })


def validate_json(json_data, validation_model: VALIDATION_CLASS):
    print("json_data:", json_data)
    try:
        model_obj = validation_model(**json_data)
        model_obj_dict = model_obj.dict()
    except ValidationError as error:
        raise web.HTTPConflict(
            text=json.dumps({"error": str(error)}),
            content_type="application/json"
        )
    return model_obj_dict


class UsersView(web.View):

    @property
    def session(self) -> Session:
        return self.request['session']

    @property
    def user_id(self) -> int:
        return int(self.request.match_info["user_id"])

    async def get(self):
        user = await get_user(self.user_id, self.session)
        return get_json_user(user)

    async def post(self):
        json_data = await self.request.json()
        try:
            json_data = validate_json(json_data, CreateUser)
        except ValidationError as error:
            raise web.HTTPBadRequest(
                text=json.dumps({"error": str(error)}),
                content_type="application/json"
            )
        json_data['password'] = hash_password(json_data['password'])
        user = User(**json_data)
        self.session.add(user)
        try:
            await self.session.commit()
        except IntegrityError:
            raise web.HTTPConflict(
                text=json.dumps({"error": "user already exists"}),
                content_type="application/json"
            )
        return web.json_response({
            "id": user.id,
            "name": user.name,
        })

    async def patch(self):
        json_data = await self.request.json()
        if "password" in json_data:
            json_data = validate_json(json_data, UpdateUser)
            json_data['password'] = hash_password(json_data['password'])
        user = await get_user(self.user_id, self.session)
        for field, value in json_data.items():
            setattr(user, field, value)
        self.session.add(user)
        try:
            await self.session.commit()
        except IntegrityError:
            raise web.HTTPConflict(
                text=json.dumps({"error": "user already exists"}),
                content_type="application/json"
            )
        return web.json_response({
            "id": user.id,
            "name": user.name
        })

    async def delete(self):
        user = await get_user(self.user_id, self.session)
        await self.session.delete(user)
        await self.session.commit()
        return web.json_response({
            "id": user.id,
            "name": user.name,
        })


class AdvView(web.View):

    @property
    def session(self) -> Session:
        return self.request['session']

    @property
    def adv_id(self) -> int:
        return int(self.request.match_info["adv_id"])

    async def get(self):
        adv = await get_adv(self.adv_id, self.session)
        return get_json_adv(adv)

    async def post(self):
        json_data = await self.request.json()
        adv = Advertisement(**json_data)
        self.session.add(adv)
        await self.session.commit()
        return get_json_adv(adv)

    async def patch(self):
        json_data = await self.request.json()
        print(type(self.adv_id))
        adv = await get_adv(self.adv_id, self.session)
        for field, value in json_data.items():
            setattr(adv, field, value)
        self.session.add(adv)
        await self.session.commit()
        return get_json_adv(adv)

    async def delete(self):
        adv = await get_adv(self.adv_id, self.session)
        await self.session.delete(adv)
        await self.session.commit()
        return web.json_response({
            "id": adv.id,
            "title": adv.title,
        })


async def get_app():
    app = web.Application()
    app.add_routes(
        [
            web.get("/users/{user_id:\d+}", UsersView),
            web.patch("/users/{user_id:\d+}", UsersView),
            web.delete("/users/{user_id:\d+}", UsersView),
            web.post("/users/", UsersView),
            web.get("/adv/{adv_id:\d+}", AdvView),
            web.patch("/adv/{adv_id:\d+}", AdvView),
            web.delete("/adv/{adv_id:\d+}", AdvView),
            web.post("/adv/", AdvView),
        ]
    )
    app.cleanup_ctx.append(orm_context)
    app.middlewares.append(session_middleware)
    return app

if __name__ == '__main__':
    app = get_app()
    web.run_app(app)

