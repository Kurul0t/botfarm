from sqlalchemy import select,and_,update
from sqlalchemy.ext.asyncio import AsyncSession

from database.models.incubator import Incubator,IncubatorState,IncubationState

class IncubatorRepository:
    async def get_all(
        self,
        session: AsyncSession,
        company_id: int,
    ) -> list[Incubator]:
        result = await session.execute(
            select(Incubator)
            .where(Incubator.company_id == company_id)
            .order_by(Incubator.number)
        )

        return list(result.scalars().all())
    
    async def get_all_available(
        self,
        session: AsyncSession,
        company_id: int,
    ) -> list[Incubator]:
        result = await session.execute(select(Incubator).where(and_(Incubator.company_id == company_id, Incubator.state == IncubatorState.AVAILABLE,)))
        return result.scalars().all()
     
    async def get_all_unavailable(
        self,
        session: AsyncSession,
        company_id: int,
    ) -> list[Incubator]:    
        result = await session.execute(select(Incubator).where(and_(Incubator.company_id==company_id,Incubator.state ==IncubatorState.INCUBATING)))
        return result.scalars().all()
    
    async def get_by_id(
        self,
        session: AsyncSession,
        company_id: int,
        incubator_id: int,
    ) -> Incubator | None:
        result = await session.execute(
            select(Incubator).where(
                Incubator.id == incubator_id,
                Incubator.company_id == company_id,
            )
        )
        return result.scalar_one_or_none()

    async def get_instruction_id(
        self,
        session:AsyncSession,
        company_id: int,
        number: int,
    ):
        result = await session.execute(select(Incubator.instruction_id).where(and_(Incubator.company_id == company_id, Incubator.number == number)))
        return result.scalar()

    async def change_state(
        self,
        session:AsyncSession,
        company_id: int,
        number: int,
        value_:str,
    ):
        target_state = IncubatorState[value_].value
        await session.execute(update(Incubator).where(Incubator.company_id == company_id,Incubator.number == number).values(state=target_state))
        
        await session.commit()
        
    async def change_parameters(
            self,
            session: AsyncSession,
            company_id: int,
            number: int,
            parameters: dict,
        ):
            result = await session.execute(
                select(Incubator.id).where(
                    Incubator.company_id == company_id,
                    Incubator.number == number
                )
            )
    
            incubator_id = result.scalar_one_or_none()
    
            if incubator_id is None:
                raise ValueError("Інкубатор не знайдено")
    
            result = await session.execute(
                select(IncubationState).where(
                    IncubationState.incubator_id == incubator_id
                )
            )
    
            state = result.scalar_one_or_none()
    
            if state is None:
                state = IncubationState(
                    incubator_id=incubator_id,
                    parameters={}
                )
                session.add(state)
    
            state.parameters = {
                **(state.parameters or {}),
                **parameters
            }
    
            await session.commit()
    
    async def get_parameters(
        self,
        session: AsyncSession,
        company_id: int,
        number: int,
    ):
        result = await session.execute(
            select(IncubationState.parameters)
            .join(
                Incubator,
                IncubationState.incubator_id == Incubator.id
            )
            .where(
                Incubator.company_id == company_id,
                Incubator.number == number
            )
        )

        return result.scalar_one_or_none() or {}
    
    
    async def get_parameters_by_id(
        self,
        session: AsyncSession,
        company_id: int,
        incubator_id: int,
    ) -> dict | None:

        result = await session.execute(
            select(
                Incubator.id,
                IncubationState.parameters
            )
            .outerjoin(
                IncubationState,
                IncubationState.incubator_id == Incubator.id
            )
            .where(
                Incubator.company_id == company_id,
                Incubator.id == incubator_id
            )
        )

        row = result.one_or_none()

        if row is None:
            return None

        return row[1] or {}
    
    async def change_incubators_info(
        self,
        session: AsyncSession,
        company_id: int,
        number: int,
        info: dict
    ):
        await session.execute(
            update(Incubator)
            .where(
                Incubator.company_id == company_id,
                Incubator.number == number
            )
            .values(**info)
        )

        await session.commit()
        