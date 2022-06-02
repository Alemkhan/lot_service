from rest_framework import status
from rest_framework.exceptions import APIException


class AuthenticationRequiredException(APIException):
    status_code = status.HTTP_403_FORBIDDEN
    default_code = "auth_required"
    default_detail = "Please, login!"


class LotAlreadyExistsException(APIException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_code = "lot_already_exists"
    default_detail = "You already have an existing lot"


class NotEnoughBalanceException(APIException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_code = "not_enough_money"
    default_detail = "You do not have enough supply count in your p2p wallet"


class NotFoundException(APIException):
    status_code = status.HTTP_404_NOT_FOUND
    default_code = "not_found"
    default_detail = "Not found!"


class PermissionDeniedException(APIException):
    status_code = status.HTTP_403_FORBIDDEN
    default_code = "permission_denied"
    default_detail = "You don't have such permissions"
