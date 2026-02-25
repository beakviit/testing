from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from .models import Product, Category, Cart, CartItem, Order
from tabulate import tabulate

class ShopTests(TestCase):
    results = []

    @classmethod
    def setUpTestData(cls):
        cls.category = Category.objects.create(name='Electronics', slug='electronics')
        cls.product = Product.objects.create(
            category=cls.category,
            name='Smartphone',
            slug='smartphone',
            price=100.00,
            available=True
        )
        cls.user = User.objects.create_user(username='testuser', password='password123')

    def setUp(self):
        self.client = Client()

    def test_product_list_view(self):
        response = self.client.get(reverse('shop:product_list'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.product.name)
        self.__class__.results.append(['Product List', 'GET', 'Успешно: список товаров отображен'])

    def test_product_detail_view(self):
        response = self.client.get(reverse('shop:product_detail', args=[self.product.id, self.product.slug]))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.product.name)
        self.__class__.results.append(['Product Detail', 'GET', 'Успешно: страница товара доступна'])

    def test_add_to_cart(self):
        self.client.login(username='testuser', password='password123')
        
        response = self.client.post(reverse('shop:cart_add', args=[self.product.id]), {
            'quantity': 2,
            'update': False
        })
        
        cart_item_exists = CartItem.objects.filter(product=self.product).exists()
        self.assertTrue(cart_item_exists)
        
        self.__class__.results.append(['Add to Cart', 'POST', 'Успешно: товар добавлен в БД'])

    def test_order_creation_logic(self):
        self.client.login(username='testuser', password='password123')
        
        self.client.post(reverse('shop:cart_add', args=[self.product.id]), {'quantity': 1})
        
        order_data = {
            'first_name': 'Ivan',
            'last_name': 'Ivanov',
            'email': 'ivan@example.com',
            'address': 'Some Street 1',
            'postal_code': '123456',
            'city': 'Moscow'
        }
        response = self.client.post(reverse('shop:order_create'), data=order_data)
        
        self.assertIn(response.status_code, [200, 302])
        
        order_exists = Order.objects.filter(user=self.user, first_name='Ivan').exists()
        self.assertTrue(order_exists)
        
        cart_count = CartItem.objects.filter(product=self.product).count()
        self.assertEqual(cart_count, 0)
        
        self.__class__.results.append(['Order Creation', 'POST', 'Успешно: заказ создан, корзина пуста'])

    def test_search_functionality(self):
        response = self.client.get(reverse('shop:product_list'), {'q': 'Smart'})
        self.assertContains(response, 'Smartphone')
        
        response = self.client.get(reverse('shop:product_list'), {'q': 'Laptop'})
        self.assertNotContains(response, 'Smartphone')
        
        self.__class__.results.append(['Search', 'GET', 'Успешно: фильтрация работает'])

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        
        headers = ['Тест', 'Метод', 'Результат/Описание']
        markdown_table = tabulate(cls.results, headers=headers, tablefmt='github')
        
        report_content = f"# Отчет о тестировании магазина\n\n{markdown_table}\n"
        
        file_path = 'test_report.md'
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(report_content)
        
        print(f"\n[INFO] Отчет успешно экспортирован в файл: {os.path.abspath(file_path)}")