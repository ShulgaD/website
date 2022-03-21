from shulga_framework.templator import render
from patterns.patterns import Engine, Logger, MapperRegistry
from patterns.structural_patterns import AppRoute, Debug
from patterns.behavioral_patterns import EmailNotifier, SmsNotifier, CreateView, BaseSerializer, ListView
from patterns.unit_of_work import UnitOfWork


site = Engine()
logger = Logger('main')
email_notifier = EmailNotifier()
sms_notifier = SmsNotifier()
UnitOfWork.new_current()
UnitOfWork.get_current().set_mapper_registry(MapperRegistry)

routes = {}

# контроллер - главная страница
@AppRoute(routes=routes, url='/')
class Index:
    @Debug(name='Index')
    def __call__(self, request):
        return '200 OK', render('index.html', date=request.get('date', None), objects_list=site.categories)


# контроллер - Примеры
@AppRoute(routes=routes, url='/examples/')
class Examples:
    @Debug(name='Examples')
    def __call__(self, request):
        return '200 OK', render('examples.html', date=request.get('date', None))


# контроллер - Другая страница
@AppRoute(routes=routes, url='/another_page/')
class Another_page:
    @Debug(name='Another_page')
    def __call__(self, request):
        return '200 OK', render('another_page.html', date=request.get('date', None))


# контроллер - Страница
@AppRoute(routes=routes, url='/page/')
class Page:
    @Debug(name='Page')
    def __call__(self, request):
        return '200 OK', render('page.html', date=request.get('date', None))


# контроллер - Контакты
@AppRoute(routes=routes, url='/contact/')
class Contact:
    @Debug(name='Contact')
    def __call__(self, request):
        return '200 OK', render('contact.html', date=request.get('date', None))


# контроллер - список курсов
@AppRoute(routes=routes, url='/souvenir_list/')
class SouvenirList:
    def __call__(self, request):
        logger.log('Список Сувениров')
        try:
            category = site.find_category_by_id(
                int(request['request_params']['id']))
            return '200 OK', render('souvenir_list.html', date=request.get('date', None),
                                    objects_list=category.souvenirs,
                                    name=category.name, id=category.id)
        except KeyError:
            return '200 OK'


# контроллер - создать сувенир
@AppRoute(routes=routes, url='/create_souvenir/')
class CreateSouvenir:
    souvenir_id = -1

    def __call__(self, request):
        if request['method'] == 'POST':
            # метод пост
            data = request['data']

            name = data['name']
            name = site.decode_value(name)

            category = None
            if self.souvenir_id != -1:
                category = site.find_category_by_id(int(self.souvenir_id))

                souvenir = site.create_souvenir('wood', name, category)

                souvenir.observers.append(email_notifier)
                souvenir.observers.append(sms_notifier)

                site.souvenirs.append(souvenir)

            return '200 OK', render('souvenir_list.html', date=request.get('date', None),
                                    objects_list=category.souvenirs,
                                    name=category.name,
                                    id=category.id)

        else:
            try:
                self.souvenir_id = int(request['request_params']['id'])
                category = site.find_category_by_id(int(self.souvenir_id))

                return '200 OK', render('create_souvenir.html', date=request.get('date', None),
                                        name=category.name,
                                        id=category.id)
            except KeyError:
                return '200 OK'


# контроллер - создать категорию
@AppRoute(routes=routes, url='/create-category/')
class CreateCategory:
    def __call__(self, request):

        if request['method'] == 'POST':
            # метод пост

            data = request['data']

            name = data['name']
            name = site.decode_value(name)

            category_id = data.get('category_id')

            category = None
            if category_id:
                category = site.find_category_by_id(int(category_id))

            new_category = site.create_category(name, category)

            site.categories.append(new_category)

            return '200 OK', render('index.html', date=request.get('date', None), objects_list=site.categories)
        else:
            categories = site.categories
            return '200 OK', render('create_category.html', date=request.get('date', None),
                                    categories=categories)


# контроллер - список категорий
@AppRoute(routes=routes, url='/category-list/')
class CategoryList:
    def __call__(self, request):
        logger.log('Список категорий')
        return '200 OK', render('category_list.html', date=request.get('date', None),
                                objects_list=site.categories)


# контроллер - копировать сувенир
@AppRoute(routes=routes, url='/copy-souvenir/')
class CopySouvenir:
    def __call__(self, request):
        request_params = request['request_params']

        try:
            name = request_params['name']

            old_souvenir = site.get_souvenir(name)
            if old_souvenir:
                new_name = f'copy_{name}'
                new_souvenir = old_souvenir.clone()
                new_souvenir.name = new_name
                site.souvenirs.append(new_souvenir)

            return '200 OK', render('souvenir_list.html', date=request.get('date', None),
                                    objects_list=site.souvenirs,
                                    name=new_souvenir.category.name)
        except KeyError:
            return '200 OK'


@AppRoute(routes=routes, url='/buyer-list/')
class BuyertListView(ListView):
    template_name = 'buyer_list.html'

    def get_queryset(self):
        mapper = MapperRegistry.get_current_mapper('buyer')
        return mapper.all()


@AppRoute(routes=routes, url='/create-buyer/')
class BuyerCreateView(CreateView):
    template_name = 'create_buyer.html'

    def create_obj(self, data: dict):
        name = data['name']
        name = site.decode_value(name)
        new_obj = site.create_user('buyer', name)
        site.buyers.append(new_obj)
        new_obj.mark_new()
        UnitOfWork.get_current().commit()


@AppRoute(routes=routes, url='/add-buyer/')
class AddBuyerCreateView(CreateView):
    template_name = 'add_buyer.html'

    def get_context_data(self):
        context = super().get_context_data()
        context['souvenirs'] = site.souvenirs
        context['buyers'] = site.buyers
        return context

    def create_obj(self, data: dict):
        souvenir_name = data['souvenir_name']
        souvenir_name = site.decode_value(souvenir_name)
        souvenir = site.get_souvenir(souvenir_name)
        buyer_name = data['buyer_name']
        buyer_name = site.decode_value(buyer_name)
        buyer = site.get_buyer(buyer_name)
        souvenir.add_buyer(buyer)


@AppRoute(routes=routes, url='/api/')
class SouvenirApi:
    @Debug(name='SouvenirApi')
    def __call__(self, request):
        return '200 OK', BaseSerializer(site.souvenirs).save()