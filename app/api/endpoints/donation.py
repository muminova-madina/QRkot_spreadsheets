from typing import List

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.db import get_async_session
from app.core.user import current_user, current_superuser
from app.crud.donation import donation_crud
from app.models import CharityProject, User
from app.schemas.donation import DonationCreate, DonationDB, DonationDBFull
from app.services.investment import donation_process

router = APIRouter()


@router.post(
    '/',
    response_model=DonationDB,
    response_model_exclude_none=True,
    response_model_exclude={'user_id'}
)
async def create_new_donation(
    donation: DonationCreate,
    session: AsyncSession = Depends(get_async_session),
    user: User = Depends(current_user),
):
    """Сделать пожертвование."""
    new_donation = await donation_crud.create_donation(donation, session, user)
    return await donation_process(new_donation, CharityProject, session)


@router.get(
    '/',
    response_model=List[DonationDBFull],
    response_model_exclude_none=True,
    dependencies=[Depends(current_superuser)],
)
async def get_all_donations(session: AsyncSession = Depends(get_async_session)):
    """Только для суперюзеров.

    Возвращает список всех пожертвований."""
    return await donation_crud.get_multi(session)


@router.get(
    '/my',
    response_model=List[DonationDB],
    response_model_exclude={'user_id'}
)
async def get_my_donations(
    session: AsyncSession = Depends(get_async_session),
    user: User = Depends(current_user)
):
    """Вернуть список пожертвований пользователя, выполняющего запрос."""
    return await donation_crud.get_by_user(session=session, user=user)
