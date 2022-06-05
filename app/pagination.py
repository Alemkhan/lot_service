import os

from rest_framework.pagination import PageNumberPagination


class SmallPagesPagination(PageNumberPagination):
    page_size = int(os.environ.get("PAGE_COUNT", 10))
