from models import User, Base
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from nicegui import ui
from sqlalchemy import delete, select
from sqlalchemy.exc import SQLAlchemyError
import asyncio
port = 8080
DATABASE_URL = 'sqlite+aiosqlite:///blog.db'  # Update with your DB URL
async_engine = create_async_engine(DATABASE_URL, echo=True)
# Asynchronous session maker
async_session = async_sessionmaker(async_engine, expire_on_commit=False, class_=AsyncSession)


async def init_db() -> None:
    # Create the database tables
    async with async_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


async def close_db() -> None:
    # Close the database
    await async_engine.dispose()


@ui.refreshable
async def list_of_users() -> None:
    async def delete_user(user_id: int) -> None:
        async with async_session() as session:
            await session.execute(delete(User).where(User.id == user_id))
            await session.commit()
            await close_db()
        list_of_users.refresh()

    async with async_session() as session:
        result = await session.execute(select(User))
        users = result.scalars().all()

    for user in reversed(users):
        with ui.card().classes('m-4'):
            with ui.row().classes('items-center'):
                ui.label('Name:')
                ui.html(f"<h3>{user.name}</h3>")
                ui.label('Email:')
                ui.html(f"<h3>{user.email}</h3>")
                ui.label('Admin:')
                ui.html(f"<h3>{user.is_admin}</h3>")
                ui.button(icon='delete', on_click=lambda u=user: delete_user(u.id)).props('flat')
                print(user.id)


def create_dashboard() -> None:
    @ui.page(path='/')
    async def dash():
        async def create_user(n, e, p, a) -> None:
            new_user = User()
            new_user.create_user(name=n, email=e, password=p, is_admin=a)
            async with async_session() as session:
                session.add(new_user)
                try:
                    await session.commit()
                    list_of_users.refresh()
                except SQLAlchemyError as e:
                    ui.notify(f'Error creating user: {str(e)}', level='error')
                    await session.rollback()
            await close_db()

        container = ui.column().classes('mx-auto p-4')
        with container:
            ui.label('Create User').classes('text-4xl m-4')
            with ui.row().classes('w-full items-center px-4'):
                name = ui.input(label='Name')
                email = ui.input(label='Email')
                password = ui.input(label='Password', password=True)
                admin = ui.checkbox('Is Admin')
                ui.button('Create User',
                          on_click=lambda: create_user(name.value, email.value, password.value,
                                                       admin.value))

            await list_of_users()
            list_of_users.refresh()


create_dashboard()
asyncio.run(init_db())

if __name__ in {"__main__", "__mp_main__"}:
    ui.run(storage_secret='secret_key', port=port)
