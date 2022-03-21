from datetime import date
from views import Index, Examples, Another_page, Page, Contact, \
    CreateSouvenir, CreateCategory, CategoryList, CopySouvenir, SouvenirList


# front controller
def secret_front(request):
    request['date'] = date.today()


def other_front(request):
    request['key'] = 'key'


fronts = [secret_front, other_front]
