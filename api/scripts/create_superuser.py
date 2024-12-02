import asyncio
from datetime import datetime
from typing import Optional

import typer
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from api.auth.security import get_password_hash
from api.database import AsyncSessionLocal
from api.user.models import User

cli = typer.Typer()


async def create_superuser(
    db_session: AsyncSession,
    username: str,
    email: str,
    password: str,
    first_name: Optional[str] = None,
    last_name: Optional[str] = None,
) -> User:
    result = await db_session.execute(
        select(User).where((User.username == username) | (User.email == email))
    )
    existing_user = result.scalar_one_or_none()

    if existing_user:
        raise ValueError("User with this username or email already exists")

    hashed_password = get_password_hash(password)

    superuser = User(
        username=username,
        email=email,
        password=hashed_password,
        first_name=first_name,
        last_name=last_name,
        is_superuser=True,
        is_active=True,
        last_login=datetime.now(),
    )

    db_session.add(superuser)
    await db_session.commit()
    await db_session.refresh(superuser)

    return superuser


@cli.command()
def createsuperuser(
    username: str = typer.Option(..., prompt=True),
    email: str = typer.Option(..., prompt=True),
    password: str = typer.Option(
        ..., prompt=True, hide_input=True, confirmation_prompt=True
    ),
):
    """Create a superuser."""

    async def run():
        async with AsyncSessionLocal() as db_session:
            try:
                user = await create_superuser(
                    db_session=db_session,
                    username=username,
                    email=email,
                    password=password,
                )
                typer.echo(f"Superuser '{user.username}' created successfully!")
            except ValueError as e:
                typer.echo(f"Error: {str(e)}", err=True)
            except Exception as e:
                typer.echo(f"An error occurred: {str(e)}", err=True)

    asyncio.run(run())


if __name__ == "__main__":
    cli()
