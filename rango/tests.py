# Chapter 3
from django.contrib.staticfiles import finders
from django.test import TestCase
from django.contrib.staticfiles.testing import StaticLiveServerTestCase

from django.core.urlresolvers import reverse
import os

# ===== CHAPTER 3

# Chapter 5
from rango.models import Page, Category
import populate_rango


class Chapter3ViewTests(TestCase):
    def test_index_contains_hello_message(self):
        # Check if there is the message 'hello world!'
        response = self.client.get(reverse('index'))
        self.assertIn('Rango says'.lower(),
                      response.content.decode('ascii').lower())

        # file.write('test_index_contains_hello_message\n')

    def test_about_contains_create_message(self):
        # Check if in the about page is there a message
        self.client.get(reverse('index'))
        response = self.client.get(reverse('about'))
        self.assertIn('Rango says here is the about page'.lower(),
                      response.content.decode('ascii').lower())


# Chapter 4

# ===== CHAPTER 4

class Chapter4ViewTest(TestCase):

    def test_view_has_title(self):
        response = self.client.get(reverse('index'))

        # Check title used correctly
        self.assertIn('<title>', response.content.decode('ascii'))
        self.assertIn('</title>', response.content.decode('ascii'))

    def test_index_using_template(self):
        response = self.client.get(reverse('index'))

        # Check the template used to render index page
        self.assertTemplateUsed(response, 'rango/index.html')

    def test_about_using_template(self):
        self.client.get(reverse('index'))
        response = self.client.get(reverse('about'))

        # Check the template used to render about page
        self.assertTemplateUsed(response, 'rango/about.html')

    def test_rango_picture_displayed(self):
        response = self.client.get(reverse('index'))

        # Check if is there an image in index page
        self.assertIn('img src="/static/images/rango.jpg'.lower(),
                      response.content.decode('ascii').lower())

    # New media test
    def test_cat_picture_displayed(self):
        response = self.client.get(reverse('about'))

        # Check if is there an image in index page
        self.assertIn('img src="/media/cat.jpg'.lower(),
                      response.content.decode('ascii').lower())

    def test_about_contain_image(self):
        self.client.get(reverse('index'))
        response = self.client.get(reverse('about'))

        # Check if is there an image in index page
        self.assertIn('img src="/static/images/',
                      response.content.decode('ascii'))

    def test_serving_static_files(self):
        # If using static media properly result is not NONE once it finds rango.jpg
        result = finders.find('images/rango.jpg')
        self.assertIsNotNone(result)


# Chapter 5

# ===== CHAPTER 5

class Chapter5ModelTests(TestCase):

    def test_create_a_new_category(self):
        cat = Category(name="Python")
        cat.save()

        # Check category is in database
        categories_in_database = Category.objects.all()
        self.assertEquals(len(categories_in_database), 1)
        only_poll_in_database = categories_in_database[0]
        self.assertEquals(only_poll_in_database, cat)

    def test_create_pages_for_categories(self):
        cat = Category(name="Python")
        cat.save()

        # create 2 pages for category python
        python_page = Page()
        python_page.category = cat
        python_page.title = "Official Python Tutorial"
        python_page.url = "http://docs.python.org/2/tutorial/"
        python_page.save()

        django_page = Page()
        django_page.category = cat
        django_page.title = "Django"
        django_page.url = "https://docs.djangoproject.com/en/1.5/intro/tutorial01/"
        django_page.save()

        # Check if they both were saved
        python_pages = cat.page_set.all()
        self.assertEquals(python_pages.count(), 2)

        # Check if they were saved properly
        first_page = python_pages[0]
        self.assertEquals(first_page, python_page)
        self.assertEquals(first_page.title, "Official Python Tutorial")
        self.assertEquals(first_page.url, "http://docs.python.org/2/tutorial/")

    def test_population_script_changes(self):
        # Populate database
        populate_rango.populate()

        # Check if the category has correct number of views and likes
        cat = Category.objects.get(name='Python')
        self.assertEquals(cat.views, 128)
        self.assertEquals(cat.likes, 64)

        # Check if the category has correct number of views and likes
        cat = Category.objects.get(name='Django')
        self.assertEquals(cat.views, 64)
        self.assertEquals(cat.likes, 32)

        # Check if the category has correct number of views and likes
        cat = Category.objects.get(name='Other Frameworks')
        self.assertEquals(cat.views, 32)
        self.assertEquals(cat.likes, 16)
