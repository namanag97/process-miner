#!/usr/bin/env python3
"""Seed MVP data for development."""
import asyncio
from datetime import datetime

async def seed_mvp():
    from sqlalchemy import select
    from src.models.database import async_session_maker, init_database
    from src.models.orm import User, Workspace, WorkspaceMember, Organization

    await init_database()
    async with async_session_maker() as db:
        # Check if MVP user already exists
        result = await db.execute(select(User).filter(User.email == 'analyst@company.local'))
        if result.scalar_one_or_none():
            print('MVP user already exists!')
            return

        # Check/create MVP org (use different slug to avoid conflict)
        org_result = await db.execute(select(Organization).filter(Organization.id == 'mvp-org-001'))
        org = org_result.scalar_one_or_none()
        if not org:
            org = Organization(
                id='mvp-org-001',
                name='MVP Organization',
                slug='mvp-org',  # Different slug to avoid conflict
                plan='free',
                created_at=datetime.utcnow(),
            )
            db.add(org)
            await db.flush()
        
        # Check/create MVP workspace
        ws_result = await db.execute(select(Workspace).filter(Workspace.id == 'mvp-ws-001'))
        workspace = ws_result.scalar_one_or_none()
        if not workspace:
            workspace = Workspace(
                id='mvp-ws-001',
                org_id='mvp-org-001',
                name='Default Workspace',
                description='Your default process mining workspace',
                created_at=datetime.utcnow(),
            )
            db.add(workspace)
            await db.flush()
        
        # Create MVP user
        user = User(
            id='mvp-user-001',
            org_id='mvp-org-001',
            email='analyst@company.local',
            name='Process Analyst',
            auth_provider='local',
            role='admin',
            created_at=datetime.utcnow(),
            last_login_at=datetime.utcnow(),
        )
        db.add(user)
        
        # Add workspace membership
        membership = WorkspaceMember(
            id='mvp-member-001',
            workspace_id='mvp-ws-001',
            user_id='mvp-user-001',
            role='owner',
            joined_at=datetime.utcnow(),
        )
        db.add(membership)
        
        await db.commit()
        print('MVP data seeded successfully!')
        print(f'  User: analyst@company.local (mvp-user-001)')
        print(f'  Workspace: mvp-ws-001')
        print(f'  Org: mvp-org-001')

if __name__ == '__main__':
    asyncio.run(seed_mvp())
