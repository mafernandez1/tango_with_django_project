# Chapter 3
from django.test import TestCase
from django.contrib.staticfiles.testing import StaticLiveServerTestCase
from django.core.urlresolvers import reverse
import os

#Chapter 4
from django.contrib.staticfiles import finders

#Chapter 5
from rango.models import Page, Category
import populate_rango
import rango.test_utils as test_utils

#Chapter 6
from rango.decorators import chapter6


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

#Chapter 6
from rango.decorators import chapter6

# ===== Chapter 6
class Chapter6ModelTests(TestCase):
    def test_category_contains_slug_field(self):
        #Create a new category
        new_category = Category(name="Test Category")
        new_category.save()

        #Check slug was generated
        self.assertEquals(new_category.slug, "test-category")

        #Check there is only one category
        categories = Category.objects.all()
        self.assertEquals(len(categories), 1)

        #Check attributes were saved correctly
        categories[0].slug = new_category.slug


class Chapter6ViewTests(TestCase):
    def test_index_context(self):
        # Access index with empty database
        response = self.client.get(reverse('index'))

        # Context dictionary is then empty
        self.assertCountEqual(response.context['categories'], [])
        self.assertCountEqual(response.context['pages'], [])

        categories = test_utils.create_categories()
        test_utils.create_pages(categories)

        #Access index with database filled
        response = self.client.get(reverse('index'))

        #Retrieve categories and pages from database
        categories = Category.objects.order_by('-likes')[:5]
        pages = Page.objects.order_by('-views')[:5]

        # Check context dictionary filled
        self.assertCountEqual(response.context['categories'], categories)
        self.assertCountEqual(response.context['pages'], pages)

    def test_index_displays_five_most_liked_categories(self):
        #Create categories
        test_utils.create_categories()

        # Access index
        response = self.client.get(reverse('index'))

        # Check if the 5 pages with most likes are displayed
        for i in range(10, 5, -1):
            self.assertIn("Category " + str(i), response.content.decode('ascii'))

    def test_index_displays_no_categories_message(self):
        # Access index with empty database
        response = self.client.get(reverse('index'))

        # Check if no categories message is displayed
        self.assertIn("There are no categories present.".lower(), response.content.decode('ascii').lower())

    def test_index_displays_five_most_viewed_pages(self):
        #Create categories
        categories = test_utils.create_categories()

        #Create pages for categories
        test_utils.create_pages(categories)

        # Access index
        response = self.client.get(reverse('index'))

        # Check if the 5 pages with most views are displayed
        for i in range(20, 15, -1):
            self.assertIn("Page " + str(i), response.content.decode('ascii'))

    def test_index_contains_link_to_categories(self):
        #Create categories
        categories = test_utils.create_categories()

        # Access index
        response = self.client.get(reverse('index'))

        # Check if the 5 pages with most likes are displayed
        for i in range(10, 5, -1):
            category = categories[i - 1]
            self.assertIn(reverse('show_category', args=[category.slug])[:-1], response.content.decode('ascii'))

    def test_category_context(self):
        #Create categories and pages for categories
        categories = test_utils.create_categories()
        pages = test_utils.create_pages(categories)

        # For each category check the context dictionary passed via render() function
        for category in categories:
            response = self.client.get(reverse('show_category', args=[category.slug]))
            pages = Page.objects.filter(category=category)
            self.assertCountEqual(response.context['pages'], pages)
            self.assertEquals(response.context['category'], category)

    def test_category_page_using_template(self):
        #Create categories in database
        test_utils.create_categories()

        # Access category page
        response = self.client.get(reverse('show_category', args=['category-1']))

        # check was used the right template
        self.assertTemplateUsed(response, 'rango/category.html')

    @chapter6
    def test_category_page_displays_pages(self):
        #Create categories in database
        categories = test_utils.create_categories()

        # Create pages for categories
        test_utils.create_pages(categories)

        # For each category, access its page and check for the pages associated with it
        for category in categories:
            # Access category page
            response = self.client.get(reverse('show_category', args=[category.slug]))

            # Retrieve pages for that category
            pages = Page.objects.filter(category=category)

            # Check pages are displayed and they have a link
            for page in pages:
                self.assertIn(page.title, response.content.decode('ascii'))
                self.assertIn(page.url, response.content.decode('ascii'))

    def test_category_page_displays_empty_message(self):
        #Create categories in database
        categories = test_utils.create_categories()

        # For each category, access its page and check there are no pages associated with it
        for category in categories:
            # Access category page
            response = self.client.get(reverse('show_category', args=[category.slug]))
            self.assertIn("No pages currently in category.".lower(), response.content.decode('ascii').lower())

    def test_category_page_displays_category_does_not_exist_message(self):
        # Try to access categories not saved to database and check the message
        response = self.client.get(reverse('show_category', args=['Python']))
        self.assertIn("does not exist!".lower(), response.content.decode('ascii').lower())

        response = self.client.get(reverse('show_category', args=['Django']))
        self.assertIn("does not exist!".lower(), response.content.decode('ascii').lower())
