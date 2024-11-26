import asyncio
import uuid

from sqlalchemy import select

from api.auth.models import Permission
from api.database import AsyncSessionLocal

permissions = [
    {
        "id": uuid.uuid4(),
        "name": "create group",
        "description": "create group",
        "action": "CREATE",
        "object": "group",
    },
    {
        "id": uuid.uuid4(),
        "name": "read group",
        "description": "read group",
        "action": "READ",
        "object": "group",
    },
    {
        "id": uuid.uuid4(),
        "name": "update group",
        "description": "update group",
        "action": "UPDATE",
        "object": "group",
    },
    {
        "id": uuid.uuid4(),
        "name": "delete group",
        "description": "delete group",
        "action": "DELETE",
        "object": "group",
    },
    {
        "id": uuid.uuid4(),
        "name": "create user",
        "description": "create user",
        "action": "CREATE",
        "object": "user",
    },
    {
        "id": uuid.uuid4(),
        "name": "read user",
        "description": "read user",
        "action": "READ",
        "object": "user",
    },
    {
        "id": uuid.uuid4(),
        "name": "update user",
        "description": "update user",
        "action": "UPDATE",
        "object": "user",
    },
    {
        "id": uuid.uuid4(),
        "name": "delete user",
        "description": "delete user",
        "action": "DELETE",
        "object": "user",
    },
]


def main():
    async def run():
        async with AsyncSessionLocal() as db_session:
            try:
                for permission_data in permissions:
                    result = await db_session.execute(
                        select(Permission).where(
                            Permission.name == permission_data["name"]
                        )
                    )
                    existing_permission = result.scalar_one_or_none()

                    if not existing_permission:
                        permission = Permission(
                            id=permission_data["id"],
                            name=permission_data["name"],
                            description=permission_data["description"],
                            action=permission_data["action"],
                            object=permission_data["object"],
                        )
                        db_session.add(permission)

                await db_session.commit()
            except Exception as e:
                await db_session.rollback()
                raise e

    asyncio.run(run())


if __name__ == "__main__":
    main()
