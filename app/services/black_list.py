from fastapi import HTTPException, status

from app.models import BlackList, Comment
from app.utils.unitofwork import UnitOfWork
from app.schemas.black_list import BlackListResponse, BlackListSchemaAdd, BlackListSchema


class BlackListService:
    """
    Service class for managing blacklist operations, including adding, retrieving, and deleting blacklisted cars.
    """

    @staticmethod
    async def get_blacklisted_words(uow: UnitOfWork):
        """
        Retrieves a list of blacklisted words from the database.

        Args:
            uow (UnitOfWork): The unit of work instance for database transactions.

        Returns:
            list[str]: A list of blacklisted words.
        """
        async with uow:
            return await uow.black_list.get_blacklisted_words()

    @staticmethod
    async def add_black_list(uow: UnitOfWork, black_list_data: BlackListSchemaAdd) -> BlackListResponse:
        """
        Adds a car to the blacklist.

        Args:
            uow (UnitOfWork): The unit of work instance for database transactions.
            black_list_data (BlackListSchemaAdd): The data required to blacklist a car.

        Returns:
            BlackListResponse: The response object containing details of the blacklisted car.

        Raises:
            HTTPException: If the car is not found or is already blacklisted, or if the comment contains blacklisted words.
        """
        async with uow:
            
            blacklisted_words = await BlackListService.get_blacklisted_words(uow)

           
            if any(word in black_list_data.reason for word in blacklisted_words):
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Comment contains blacklisted words")

            comment = await uow.comments.find_one_or_none(license_plate=black_list_data.license_plate)
            if comment is None:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Comment not found")

            black_record = await uow.black_list.find_one_or_none(comment_id=comment.id)
            if black_record:
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Comment already blacklisted")

            black_data = BlackList(comment_id=comment.id, reason=black_list_data.reason)
            uow.session.add(black_data)
            await uow.commit()
            await uow.session.refresh(black_data)

            black_response = BlackListResponse(
                id=black_data.id,
                car_id=black_data.car_id,
                license_plate=black_list_data.license_plate,
                reason=black_data.reason,
            )

            return black_response

    @staticmethod
    async def get_black_list(uow: UnitOfWork):
        """
        Retrieves the list of all blacklisted cars.

        Args:
            uow (UnitOfWork): The unit of work instance for database transactions.

        Returns:
            list[BlackListResponse]: A list of blacklisted car details.
        """
        async with uow:
            output_data = []
            black_list = await uow.black_list.find_all()
            for record in black_list:
                comment = await uow.comments.find_one(id=record.comment_id)
                output_data.append(BlackListResponse(
                    id=record.id,
                    comment_id=record.comment_id,
                    license_plate=comment.license_plate,
                    reason=record.reason,
                ))
            return output_data

    @staticmethod
    async def delete_black_list(uow: UnitOfWork, license_plate: str):
        """
        Removes a car from the blacklist.

        Args:
            uow (UnitOfWork): The unit of work instance for database transactions.
            license_plate (str): The license plate of the car to remove from the blacklist.

        Raises:
            HTTPException: If the car is not found or is not blacklisted.
        """
        async with uow:
            comment = await uow.comments.find_one_or_none(license_plate=license_plate)
            if comment is None:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Comment not found")
            black_record = await uow.black_list.find_one_or_none(comment_id=comment.id)
            if black_record is None:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Comment not blacklisted")
            await uow.black_list.delete_one(id=black_record.id)
  

    
    

 
