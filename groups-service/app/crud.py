from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.models import Group, GroupMember, GroupInvitation
from typing import Optional
from datetime import datetime, timedelta
import uuid

async def create_group(db: AsyncSession, group_data, teacher_telegram_id: int):
    db_group = Group(
        name=group_data.name,
        description=group_data.description,
        teacher_telegram_id=teacher_telegram_id,
        group_type=group_data.group_type,
        max_students=group_data.max_students,
        language=group_data.language,
        level=group_data.level,
        start_date=group_data.start_date,
        end_date=group_data.end_date,
    )
    db.add(db_group)
    await db.commit()
    await db.refresh(db_group)
    return db_group

async def get_groups(db: AsyncSession):
    result = await db.execute(select(Group).filter(Group.is_active == True))
    return result.scalars().all()

async def get_groups_by_teacher(db: AsyncSession, teacher_telegram_id: int):
    result = await db.execute(
        select(Group)
        .filter(
            Group.teacher_telegram_id == teacher_telegram_id,
            Group.is_active == True
        )
    )
    return result.scalars().all()

async def get_groups_by_student(db: AsyncSession, student_telegram_id: int):
    result = await db.execute(
        select(Group)
        .join(GroupMember, Group.id == GroupMember.group_id)
        .filter(
            GroupMember.student_telegram_id == student_telegram_id,
            Group.is_active == True,
            GroupMember.status == "active"
        )
    )
    return result.scalars().all()

async def get_group(db: AsyncSession, group_id: int) -> Optional[Group]:
    result = await db.execute(select(Group).filter(Group.id == group_id))
    return result.scalars().first()

async def add_member(db: AsyncSession, group: Group, student_telegram_id: int):
    existing_member = await db.execute(
        select(GroupMember).filter(
            GroupMember.group_id == group.id,
            GroupMember.student_telegram_id == student_telegram_id
        )
    )
    if existing_member.scalars().first():
        raise Exception("Already a member")

    if group.current_students >= group.max_students:
        raise Exception("Group is full")

    member = GroupMember(
        group_id=group.id,
        student_telegram_id=student_telegram_id,
        status="active",
        role="student"
    )
    group.current_students += 1
    db.add(member)
    await db.commit()
    return member

async def deactivate_group(db: AsyncSession, group: Group):
    group.is_active = False
    await db.commit()
    return group

async def remove_member(db: AsyncSession, group_id: int, student_telegram_id: int) -> Optional[GroupMember]:
    # Находим участника в группе
    result = await db.execute(
        select(GroupMember).filter(
            GroupMember.group_id == group_id,
            GroupMember.student_telegram_id == student_telegram_id
        )
    )
    member = result.scalars().first()
    if not member:
        return None  # участник не найден

    # Уменьшаем количество студентов в группе
    group = await db.get(Group, group_id)
    if group and group.current_students > 0:
        group.current_students -= 1

    # Удаляем участника
    await db.delete(member)
    await db.commit()
    return member

async def leave_group(db: AsyncSession, group_id: int, student_telegram_id: int) -> Optional[GroupMember]:
    return await remove_member(db, group_id, student_telegram_id)

async def update_group(db: AsyncSession, group: Group, update_data):
    for key, value in update_data.dict(exclude_unset=True).items():
        setattr(group, key, value)
    await db.commit()
    await db.refresh(group)
    return group

async def create_invitation(
    db: AsyncSession,
    group: Group,
    message: Optional[str],
    expires_in_hours: int,
    student_telegram_id: int
):
    invite_token = str(uuid.uuid4())
    expires_at = datetime.utcnow() + timedelta(hours=expires_in_hours)

    invitation = GroupInvitation(
        group_id=group.id,
        student_telegram_id=student_telegram_id,  # будет заполнен при принятии
        status="pending",
        sent_at=datetime.utcnow(),
        expires_at=expires_at,
        message=message,
        invite_token=invite_token  # добавь поле invite_token в модель!
    )
    db.add(invitation)
    await db.commit()
    await db.refresh(invitation)
    return invitation

async def get_invitation_by_token(db: AsyncSession, invite_token: str):
    result = await db.execute(
        select(GroupInvitation).filter(
            GroupInvitation.invite_token == invite_token,
            GroupInvitation.status == "pending",
            GroupInvitation.expires_at > datetime.utcnow()
        )
    )
    return result.scalars().first()

async def accept_invitation(db: AsyncSession, invitation: GroupInvitation, group: Group):
    student_telegram_id = invitation.student_telegram_id

    existing_member = await db.execute(
        select(GroupMember).filter(
            GroupMember.group_id == group.id,
            GroupMember.student_telegram_id == student_telegram_id
        )
    )
    if existing_member.scalars().first():
        raise Exception("Already a member")

    if group.current_students >= group.max_students:
        raise Exception("Group is full")

    member = GroupMember(
        group_id=group.id,
        student_telegram_id=student_telegram_id,
        status="active",
        role="student"
    )
    group.current_students += 1

    invitation.student_telegram_id = student_telegram_id
    invitation.status = "accepted"
    invitation.responded_at = datetime.utcnow()

    db.add(member)
    await db.commit()
    return member
