# Chapter 3
from django.test import TestCase
from django.contrib.staticfiles.testing import StaticLiveServerTestCase
from selenium import webdriver
from django.core.urlresolvers import reverse
import os
import socket

#Chapter 4
from django.contrib.staticfiles import finders

#Chapter 5
from rango.models import Page, Category
import populate_rango
import rango.test_utils as test_utils

#Chapter 6
from rango.decorators import chapter6

#Chapter 7
from rango.decorators import chapter7
from rango.forms import CategoryForm, PageForm

#Chapter 8
from django.template import loader
from django.conf import settings
from rango.decorators import chapter8
import os.path

#Chapter 9
from rango.models import User, UserProfile
from rango.forms import UserForm, UserProfileForm
from selenium.webdriver.common.keys import Keys
from django.core.files.uploadedfile import SimpleUploadedFile
from django.core.files.storage import default_storage
from rango.decorators import chapter9

# ===== Chapter 7
class Chapter7LiveServerTestCase(StaticLiveServerTestCase):

    def setUp(self):
        from django.contrib.auth.models import User
        User.objects.create_superuser(username='admin', password='admin', email='admin@me.com')
        chrome_options = webdriver.ChromeOptions()
        chrome_options.add_argument('headless')
        self.browser = webdriver.Chrome(chrome_options = chrome_options)
        self.browser.implicitly_wait(3)

    @classmethod
    def setUpClass(cls):
        cls.host = socket.gethostbyname(socket.gethostname())
        super(Chapter7LiveServerTestCase, cls).setUpClass()

    def tearDown(self):
        self.browser.refresh()
        self.browser.quit()

    @chapter7
    def test_form_is_saving_new_category(self):
        # Access index page
        url = self.live_server_url
        url = url.replace('localhost', '127.0.0.1')
        self.browser.get(url + reverse('index'))

        # Check if is there link to add categories
        categories_link = self.browser.find_elements_by_partial_link_text('Add a New Category')
        if len(categories_link) == 0:
            categories_link = self.browser.find_elements_by_partial_link_text('Add New Category')

        categories_link[0].click()

        # Types new category name
        username_field = self.browser.find_element_by_name('name')
        username_field.send_keys('New Category')

        # Click on Create Category
        self.browser.find_element_by_css_selector(
            "input[type='submit']"
        ).click()

        body = self.browser.find_element_by_tag_name('body')

        # Check if New Category appears in the index page
        self.assertIn('New Category'.lower(), body.text.lower())

    @chapter7
    def test_form_error_when_category_field_empty(self):
        # Access index page
        url = self.live_server_url
        url = url.replace('localhost', '127.0.0.1')
        self.browser.get(url + reverse('index'))

        # Check if is there link to add categories
        categories_link = self.browser.find_elements_by_partial_link_text('Add a New Category')
        if len(categories_link) == 0:
            categories_link = self.browser.find_elements_by_partial_link_text('Add New Category')

        categories_link[0].click()

        url_path = self.browser.current_url
        response = self.client.get(url_path)

        self.assertIn('required'.lower(), response.content.lower())

    @chapter7
    def test_add_category_that_already_exists(self):
        # Create a category in database
        new_category = Category(name="New Category")
        new_category.save()

        # Access index page
        url = self.live_server_url
        url = url.replace('localhost', '127.0.0.1')
        self.browser.get(url + reverse('index'))

        # Check if is there link to add categories
        categories_link = self.browser.find_elements_by_partial_link_text('Add a New Category')
        if len(categories_link) == 0:
            categories_link = self.browser.find_elements_by_partial_link_text('Add New Category')

        categories_link[0].click()

        # Types new category name
        username_field = self.browser.find_element_by_name('name')
        username_field.send_keys('New Category')

        # Click on Create Category
        self.browser.find_element_by_css_selector(
            "input[type='submit']"
        ).click()

        body = self.browser.find_element_by_tag_name('body')

        # Check if there is an error message
        self.assertIn('Category with this Name already exists.'.lower(), body.text.lower())

    @chapter7
    def test_form_is_saving_new_page(self):
        #Create categories and pages
        categories = test_utils.create_categories()
        i = 0

        for category in categories:
            i = i + 1
            # Access link to add page for the category
            url = self.live_server_url
            url = url.replace('localhost', '127.0.0.1')
            self.browser.get(url + reverse('add_page', args=[category.slug]))

            # Types new page name
            username_field = self.browser.find_element_by_name('title')
            username_field.send_keys('New Page ' + str(i))

            # Types url for the page
            username_field = self.browser.find_element_by_name('url')
            username_field.send_keys('http://www.newpage1.com')

            # Click on Create Page
            self.browser.find_element_by_css_selector(
                "input[type='submit']"
            ).click()

            body = self.browser.find_element_by_tag_name('body')

            # Check if New Page appears in the category page
            self.assertIn('New Page'.lower(), body.text.lower())

    def test_cleaned_data_from_add_page(self):
        #Create categories and pages
        categories = test_utils.create_categories()
        i = 0

        for category in categories:
            i = i + 1
            # Access link to add page for the category
            url = self.live_server_url
            url = url.replace('localhost', '127.0.0.1')
            self.browser.get(url + '/rango/category/' + category.slug + '/add_page/')

            # Types new page name
            username_field = self.browser.find_element_by_name('title')
            username_field.send_keys('New Page ' + str(i))

            # Types url for the page
            username_field = self.browser.find_element_by_name('url')
            username_field.send_keys('http://www.newpage' + str(1) + '.com')

            # Click on Create Page
            self.browser.find_element_by_css_selector(
                "input[type='submit']"
            ).click()

            body = self.browser.find_element_by_tag_name('body')

            # Check if New Page appears in the category page
            self.assertIn('New Page'.lower(), body.text.lower())


class Chapter7ViewTests(TestCase):
    @chapter7
    def test_index_contains_link_to_add_category(self):
        # Access index
        try:
            response = self.client.get(reverse('index'))
        except:
            try:
                response = self.client.get(reverse('rango:index'))
            except:
                return False

        # Check if there is text and a link to add category
        self.assertIn('href="' + reverse('add_category') + '"', response.content.decode('ascii'))

    @chapter7
    def test_add_category_form_is_displayed_correctly(self):
        # Access add category page
        response = self.client.get(reverse('add_category'))

        # Check form in response context is instance of CategoryForm
        self.assertTrue(isinstance(response.context['form'], CategoryForm))

        # Check form is displayed correctly
        # Header
        self.assertIn('<h1>Add a Category</h1>'.lower(), response.content.decode('ascii').lower())

        # Label
        self.assertIn('Please enter the category name.'.lower(), response.content.decode('ascii').lower())

        # Text input
        self.assertIn('id="id_name"', response.content.decode('ascii'))
        self.assertIn('maxlength="128"', response.content.decode('ascii'))
        self.assertIn('name="name"', response.content.decode('ascii'))
        self.assertIn('type="text"', response.content.decode('ascii'))

        # Button
        self.assertIn('type="submit" name="submit" value="Create Category"'.lower(), response.content.decode('ascii').lower())

    @chapter7
    def test_add_page_form_is_displayed_correctly(self):
        # Create categories
        categories = test_utils.create_categories()

        for category in categories:
            # Access add category page
            try:
                response = self.client.get(reverse('index'))
                response = self.client.get(reverse('add_page', args=[category.slug]))
            except:
                try:
                    response = self.client.get(reverse('rango:index'))
                    response = self.client.get(reverse('rango:add_page', args=[category.slug]))
                except:
                    return False

            # Check form in response context is instance of CategoryForm
            self.assertTrue(isinstance(response.context['form'], PageForm))

            # Check form is displayed correctly

            # Label 1
            self.assertIn('Please enter the title of the page.'.lower(), response.content.decode('ascii').lower())

            # Label 2
            self.assertIn('Please enter the URL of the page.'.lower(), response.content.decode('ascii').lower())

            # Text input 1
            self.assertIn('id="id_title"'.lower(), response.content.decode('ascii').lower())
            self.assertIn('maxlength="128"'.lower(), response.content.decode('ascii').lower())
            self.assertIn('name="title"'.lower(), response.content.decode('ascii').lower())
            self.assertIn('type="text"'.lower(), response.content.decode('ascii').lower())

            # Text input 2
            self.assertIn('id="id_url"'.lower(), response.content.decode('ascii').lower())
            self.assertIn('maxlength="200"'.lower(), response.content.decode('ascii').lower())
            self.assertIn('name="url"'.lower(), response.content.decode('ascii').lower())
            self.assertIn('type="url"'.lower(), response.content.decode('ascii').lower())

            # Button
            self.assertIn('type="submit" name="submit" value="Add Page"'.lower(), response.content.decode('ascii').lower())

    def test_access_category_that_does_not_exists(self):
        # Access a category that does not exist
        response = self.client.get(reverse('show_category', args=['python']))

        # Check that it has a response as status code OK is 200
        self.assertEquals(response.status_code, 200)

        # Check the rendered page is not empty, thus it was customised (I suppose)
        self.assertNotEquals(response.content.decode('ascii'), '')

    def test_link_to_add_page_only_appears_in_valid_categories(self):
        # Access a category that does not exist
        response = self.client.get(reverse('show_category', args=['python']))

        # Check that there is not a link to add page
        try:
            self.assertNotIn(reverse('add_page', args=['python']), response.content.decode('ascii'))
            # Access a category that does not exist
            response = self.client.get(reverse('show_category', args=['other-frameworks']))
            # Check that there is not a link to add page
            self.assertNotIn(reverse('add_page', args=['other-frameworks']), response.content.decode('ascii'))
        except:
            try:
                self.assertNotIn(reverse('rango:add_page', args=['python']), response.content.decode('ascii'))
                # Access a category that does not exist
                response = self.client.get(reverse('rango:show_category', args=['other-frameworks']))
                # Check that there is not a link to add page
                self.assertNotIn(reverse('rango:add_page', args=['other-frameworks']), response.content.decode('ascii'))
            except:
                return False

    @chapter7
    def test_category_contains_link_to_add_page(self):
        # Crete categories
        categories = test_utils.create_categories()

        # For each category in the database check if contains link to add page
        for category in categories:
            try:
                response = self.client.get(reverse('show_category', args=[category.slug]))
                self.assertIn(reverse('add_page', args=[category.slug]), response.content.decode('ascii'))
            except:
                try:
                    response = self.client.get(reverse('rango:show_category', args=[category.slug]))
                    self.assertIn(reverse('rango:add_page', args=[
                                  category.slug]), response.content.decode('ascii'))
                except:
                    return False


#Chapter 8

# ====== Chapter 8

class Chapter8ViewTests(TestCase):

    def test_base_template_exists(self):
        # Check base.html exists inside template folder
        path_to_base = settings.TEMPLATE_DIR + '/rango/base.html'
        print(path_to_base)
        self.assertTrue(os.path.isfile(path_to_base))

    @chapter8
    def test_titles_displayed(self):
        # Create user and log in
        test_utils.create_user()
        self.client.login(username='testuser', password='test1234')

        # Create categories
        categories = test_utils.create_categories()

        # Access index and check the title displayed
        response = self.client.get(reverse('index'))
        self.assertIn('Rango -'.lower(),
                      response.content.decode('ascii').lower())

        # Access category page and check the title displayed
        response = self.client.get(
            reverse('show_category', args=[categories[0].slug]))
        self.assertIn(categories[0].name.lower(),
                      response.content.decode('ascii').lower())

        # Access about page and check the title displayed
        response = self.client.get(reverse('about'))
        self.assertIn('About'.lower(),
                      response.content.decode('ascii').lower())

        # Access login page and check the title displayed
        response = self.client.get(reverse('login'))
        self.assertIn('Login'.lower(),
                      response.content.decode('ascii').lower())

        # Access register page and check the title displayed
        response = self.client.get(reverse('register'))
        self.assertIn('Register'.lower(),
                      response.content.decode('ascii').lower())

        # Access restricted page and check the title displayed
        response = self.client.get(reverse('restricted'))
        self.assertIn("Since you're logged in".lower(),
                      response.content.decode('ascii').lower())

        # Access add page and check the title displayed
        response = self.client.get(
            reverse('add_page', args=[categories[0].slug]))
        self.assertIn('Add Page'.lower(),
                      response.content.decode('ascii').lower())

        # Access add new category page and check the title displayed
        response = self.client.get(reverse('add_category'))
        self.assertIn('Add Category'.lower(),
                      response.content.decode('ascii').lower())

    @chapter8
    def test_pages_using_templates(self):
        # Create user and log in
        test_utils.create_user()
        self.client.login(username='testuser', password='test1234')

        # Create categories
        categories = test_utils.create_categories()
        # Create a list of pages to access
        pages = [reverse('index'), reverse('about'), reverse('add_category'), reverse('register'), reverse('login'),
                 reverse('show_category', args=[categories[0].slug]), reverse('add_page', args=[categories[0].slug])]  # , reverse('restricted')]

        # Create a list of pages to access
        templates = ['rango/index.html', 'rango/about.html', 'rango/add_category.html', 'rango/register.html',
                     'rango/login.html', 'rango/category.html', 'rango/add_page.html']  # , 'rango/restricted.html']

        # For each page in the page list, check if it extends from base template
        for template, page in zip(templates, pages):
            response = self.client.get(page)
            self.assertTemplateUsed(response, template)

    @chapter8
    def test_url_reference_in_index_page_when_logged(self):
        # Create user and log in
        test_utils.create_user()
        self.client.login(username='testuser', password='test1234')

        # Access index page
        response = self.client.get(reverse('index'))

        # Check links that appear for logged person only
        self.assertIn(reverse('add_category'),
                      response.content.decode('ascii'))
        self.assertIn(reverse('restricted'), response.content.decode('ascii'))
        self.assertIn(reverse('logout'), response.content.decode('ascii'))
        self.assertIn(reverse('about'), response.content.decode('ascii'))

    @chapter8
    def test_url_reference_in_index_page_when_not_logged(self):
        #Access index page with user not logged
        response = self.client.get(reverse('index'))

        # Check links that appear for logged person only
        self.assertIn(reverse('register'), response.content.decode('ascii'))
        self.assertIn(reverse('login'), response.content.decode('ascii'))
        self.assertIn(reverse('about'), response.content.decode('ascii'))

    def test_link_to_index_in_base_template(self):
        # Access index
        response = self.client.get(reverse('index'))

        # Check for url referencing index
        self.assertIn(reverse('index'), response.content.decode('ascii'))

    @chapter8
    def test_url_reference_in_category_page(self):
        # Create user and log in
        test_utils.create_user()
        self.client.login(username='testuser', password='test1234')

        # Create categories
        test_utils.create_categories()

        # Check for add_page in category page
        response = self.client.get(
            reverse('show_category', args=['category-1']))
        self.assertIn(reverse('add_page', args=[
                      'category-1']), response.content.decode('ascii'))


#Chapter 9

# ===== Chapter 9

class Chapter9LiveServerTests(StaticLiveServerTestCase):

    def setUp(self):
        from django.contrib.auth.models import User
        User.objects.create_superuser(
            username='admin', password='admin', email='admin@me.com')
        chrome_options = webdriver.ChromeOptions()
        chrome_options.add_argument('headless')
        self.browser = webdriver.Chrome(chrome_options=chrome_options)
        self.browser.implicitly_wait(3)

    @classmethod
    def setUpClass(cls):
        cls.host = socket.gethostbyname(socket.gethostname())
        super(Chapter9LiveServerTests, cls).setUpClass()

    def tearDown(self):
        self.browser.refresh()
        self.browser.quit()

    @chapter9
    def test_register_user(self):
        #Access index page
        url = self.live_server_url
        url = url.replace('localhost', '127.0.0.1')

        try:
            self.browser.get(url + reverse('index'))
        except:
            try:
                self.browser.get(url + reverse('rango:index'))
            except:
                return False

        #Click in Register
        self.browser.find_elements_by_link_text('Sign Up')[0].click()

        # Fill registration form
        # username
        username_field = self.browser.find_element_by_name('username')
        username_field.send_keys('testuser')

        # email
        email_field = self.browser.find_element_by_name('email')
        email_field.send_keys('testuser@testuser.com')

        # password
        password_field = self.browser.find_element_by_name('password')
        password_field.send_keys('test1234')

        # website
        website_field = self.browser.find_element_by_name('website')
        website_field.send_keys('http://www.testuser.com')

        # Submit
        website_field.send_keys(Keys.RETURN)

        body = self.browser.find_element_by_tag_name('body')

        # Check for success message
        self.assertIn(
            'Rango says: thank you for registering!'.lower(), body.text.lower())
        self.browser.find_element_by_link_text('Return to the homepage.')

    def test_admin_contains_user_profile(self):
        # Access admin page
        url = self.live_server_url
        url = url.replace('localhost', '127.0.0.1')
        self.browser.get(url + reverse('admin:index'))

        # Log in the admin page
        test_utils.login(self)

        # Check exists a link to user profiles
        self.browser.find_element_by_link_text('User profiles').click()

        # Check it is empty
        body = self.browser.find_element_by_tag_name('body')
        self.assertIn('0 user profiles', body.text)

        # create a user
        user, user_profile = test_utils.create_user()

        self.browser.refresh()

        # Check there is one profile
        body = self.browser.find_element_by_tag_name('body')
        # self.assertIn(user.username, body.text)

    @chapter9
    def test_links_in_index_page_when_logged(self):
        # Access login page
        url = self.live_server_url
        url = url.replace('localhost', '127.0.0.1')
        try:
            self.browser.get(url + reverse('login'))
        except:
            try:
                self.browser.get(url + reverse('rango:login'))
            except:
                return False

        # Log in
        test_utils.user_login(self)

        #Check links that appear for logged person only
        self.browser.find_element_by_link_text('Add a New Category')
        self.browser.find_element_by_link_text('Restricted Page')
        self.browser.find_element_by_link_text('Logout')
        self.browser.find_element_by_link_text('About')

        # Check that links does not appears for logged users
        body = self.browser.find_element_by_tag_name('body')
        self.assertNotIn('Sign In', body.text)
        self.assertNotIn('Sign Up', body.text)

    def test_links_in_index_page_when_not_logged(self):
        #Access index page
        url = self.live_server_url
        url = url.replace('localhost', '127.0.0.1')
        try:
            self.browser.get(url + reverse('index'))
        except:
            try:
                self.browser.get(url + reverse('rango:index'))
            except:
                return False

        #Check links that appear for not logged person only
        self.browser.find_element_by_link_text('Sign Up')
        self.browser.find_element_by_link_text('Sign In')
        self.browser.find_element_by_link_text('About')

        # Check that links does not appears for not logged users
        body = self.browser.find_element_by_tag_name('body')
        self.assertNotIn('Add a New Category', body.text)
        self.assertNotIn('Restricted Page', body.text)
        self.assertNotIn('Logout', body.text)

    @chapter9
    def test_logout_link(self):
        # Access login page
        url = self.live_server_url
        url = url.replace('localhost', '127.0.0.1')
        try:
            self.browser.get(url + reverse('login'))
        except:
            try:
                self.browser.get(url + reverse('rango:login'))
            except:
                return False

        # Log in
        test_utils.user_login(self)

        #Clicks to logout
        self.browser.find_element_by_link_text('Logout').click()

        # Check if it see log in link, thus it is logged out
        self.browser.find_element_by_link_text('Sign In')

    @chapter9
    def test_add_category_when_logged(self):
        # Access login page
        url = self.live_server_url
        url = url.replace('localhost', '127.0.0.1')
        try:
            self.browser.get(url + reverse('login'))
        except:
            try:
                self.browser.get(url + reverse('rango:login'))
            except:
                return False

        # Log in
        test_utils.user_login(self)

        # Click category
        self.browser.find_element_by_partial_link_text(
            'Add a New Category').click()

        # Types new category name
        username_field = self.browser.find_element_by_name('name')
        username_field.send_keys('New Category')

        # Click on Create Category
        self.browser.find_element_by_css_selector(
            "input[type='submit']"
        ).click()

        body = self.browser.find_element_by_tag_name('body')

        # Check if New Category appears in the index page
        self.assertIn('New Category', body.text)

    @chapter9
    def test_add_page_when_logged(self):
        #Create categories
        test_utils.create_categories()

        # Access login page
        url = self.live_server_url
        url = url.replace('localhost', '127.0.0.1')
        try:
            self.browser.get(url + reverse('login'))
        except:
            try:
                self.browser.get(url + reverse('rango:login'))
            except:
                return False

        # Log in
        test_utils.user_login(self)

        # Click category
        self.browser.find_element_by_partial_link_text('Category').click()

        # Click add page
        try:
            self.browser.find_element_by_partial_link_text("Add").click()
        except:
            self.browser.find_element_by_partial_link_text("add").click()

        # Types new page name
        username_field = self.browser.find_element_by_name('title')
        username_field.send_keys('New Page')

        # Types url for the page
        username_field = self.browser.find_element_by_name('url')
        username_field.send_keys('http://www.newpage.com')

        # Click on Create Page
        self.browser.find_element_by_css_selector(
            "input[type='submit']"
        ).click()

        body = self.browser.find_element_by_tag_name('body')

        # Check if New Page appears in the category page
        self.assertIn('New Page', body.text)

    def test_add_page_when_not_logged(self):
        #Create categories
        test_utils.create_categories()

        # Access index
        url = self.live_server_url
        url = url.replace('localhost', '127.0.0.1')
        try:
            self.browser.get(url + reverse('index'))
        except:
            try:
                self.browser.get(url + reverse('rango:index'))
            except:
                return False

        # Click category
        self.browser.find_element_by_partial_link_text('Category').click()

        # Check it does not have a link to add page
        body = self.browser.find_element_by_tag_name('body')
        self.assertNotIn('Add a Page', body.text)

    @chapter9
    def test_access_restricted_page_when_logged(self):
        # Access login page
        url = self.live_server_url
        url = url.replace('localhost', '127.0.0.1')
        try:
            self.browser.get(url + reverse('login'))
        except:
            try:
                self.browser.get(url + reverse('rango:login'))
            except:
                return False

        # Log in
        test_utils.user_login(self)

        # Access restricted page
        self.browser.find_element_by_link_text('Restricted Page').click()

        # Check that a message is displayed
        body = self.browser.find_element_by_tag_name('body')
        self.assertIn(
            "Since you're logged in, you can see this text!".lower(), body.text.lower())

    def test_access_restricted_page_when_not_logged(self):
        # Access restricted page
        url = self.live_server_url
        url = url.replace('localhost', '127.0.0.1')
        try:
            self.browser.get(url + reverse('restricted'))
        except:
            try:
                self.browser.get(url + reverse('rango:restricted'))
            except:
                return False

        # Check login form is displayed
        # username
        self.browser.find_element_by_name('username')

        # password
        self.browser.find_element_by_name('password')

    @chapter9
    def test_logged_user_message_in_index(self):
        # Access login page
        url = self.live_server_url
        url = url.replace('localhost', '127.0.0.1')
        try:
            self.browser.get(url + reverse('login'))
        except:
            try:
                self.browser.get(url + reverse('rango:login'))
            except:
                return False

        # Log in
        test_utils.user_login(self)

        # Check for the username in the message
        body = self.browser.find_element_by_tag_name('body')
        self.assertIn('admin', body.text)


class Chapter9ModelTests(TestCase):
    def test_user_profile_model(self):
        # Create a user
        user, user_profile = test_utils.create_user()

        # Check there is only the saved user and its profile in the database
        all_users = User.objects.all()
        self.assertEquals(len(all_users), 1)

        all_profiles = UserProfile.objects.all()
        self.assertEquals(len(all_profiles), 1)

        # Check profile fields were saved correctly
        all_profiles[0].user = user
        all_profiles[0].website = user_profile.website


class Chapter9ViewTests(TestCase):

    @chapter9
    def test_registration_form_is_displayed_correctly(self):
        #Access registration page
        try:
            response = self.client.get(reverse('register'))
        except:
            try:
                response = self.client.get(reverse('rango:register'))
            except:
                return False

        # Check if form is rendered correctly
        # self.assertIn('<h1>Register with Rango</h1>', response.content.decode('ascii'))
        self.assertIn('<strong>register here!</strong><br />'.lower(),
                      response.content.decode('ascii').lower())

        # Check form in response context is instance of UserForm
        self.assertTrue(isinstance(response.context['user_form'], UserForm))

        # Check form in response context is instance of UserProfileForm
        self.assertTrue(isinstance(
            response.context['profile_form'], UserProfileForm))

        user_form = UserForm()
        profile_form = UserProfileForm()

        # Check form is displayed correctly
        self.assertEquals(
            response.context['user_form'].as_p(), user_form.as_p())
        self.assertEquals(
            response.context['profile_form'].as_p(), profile_form.as_p())

        # Check submit button
        self.assertIn('type="submit"', response.content.decode('ascii'))
        self.assertIn('name="submit"', response.content.decode('ascii'))
        self.assertIn('value="Register"', response.content.decode('ascii'))

    @chapter9
    def test_login_form_is_displayed_correctly(self):
        #Access login page
        try:
            response = self.client.get(reverse('login'))
        except:
            try:
                response = self.client.get(reverse('rango:login'))
            except:
                return False

        #Check form display
        #Header
        self.assertIn('<h1>Login to Rango</h1>'.lower(),
                      response.content.decode('ascii').lower())

        #Username label and input text
        self.assertIn('Username:', response.content.decode('ascii'))
        self.assertIn('input type="text"', response.content.decode('ascii'))
        self.assertIn('name="username"', response.content.decode('ascii'))
        self.assertIn('size="50"', response.content.decode('ascii'))

        #Password label and input text
        self.assertIn('Password:', response.content.decode('ascii'))
        self.assertIn('input type="password"',
                      response.content.decode('ascii'))
        self.assertIn('name="password"', response.content.decode('ascii'))
        self.assertIn('value=""', response.content.decode('ascii'))
        self.assertIn('size="50"', response.content.decode('ascii'))

        #Submit button
        self.assertIn('input type="submit"', response.content.decode('ascii'))
        self.assertIn('value="submit"', response.content.decode('ascii'))

    @chapter9
    def test_login_form_is_displayed_correctly(self):
        #Access login page
        try:
            response = self.client.get(reverse('login'))
        except:
            try:
                response = self.client.get(reverse('rango:login'))
            except:
                return False

        #Check form display
        #Header
        self.assertIn('<h1>Login to Rango</h1>'.lower(),
                      response.content.decode('ascii').lower())

        #Username label and input text
        self.assertIn('Username:', response.content.decode('ascii'))
        self.assertIn('input type="text"', response.content.decode('ascii'))
        self.assertIn('name="username"', response.content.decode('ascii'))
        self.assertIn('size="50"', response.content.decode('ascii'))

        #Password label and input text
        self.assertIn('Password:', response.content.decode('ascii'))
        self.assertIn('input type="password"',
                      response.content.decode('ascii'))
        self.assertIn('name="password"', response.content.decode('ascii'))
        self.assertIn('value=""', response.content.decode('ascii'))
        self.assertIn('size="50"', response.content.decode('ascii'))

        #Submit button
        self.assertIn('input type="submit"', response.content.decode('ascii'))
        self.assertIn('value="submit"', response.content.decode('ascii'))

    @chapter9
    def test_login_provides_error_message(self):
        # Access login page
        try:
            response = self.client.post(
                reverse('login'), {'username': 'wronguser', 'password': 'wrongpass'})
        except:
            try:
                response = self.client.post(reverse('rango:login'), {
                                            'username': 'wronguser', 'password': 'wrongpass'})
            except:
                return False

        print(response.content.decode('ascii'))
        try:
            self.assertIn('wronguser', response.content.decode('ascii'))
        except:
            self.assertIn('Invalid login details supplied.',
                          response.content.decode('ascii'))

    @chapter9
    def test_login_redirects_to_index(self):
        # Create a user
        test_utils.create_user()

        # Access login page via POST with user data
        try:
            response = self.client.post(
                reverse('login'), {'username': 'testuser', 'password': 'test1234'})
        except:
            try:
                response = self.client.post(reverse('rango:login'), {
                                            'username': 'testuser', 'password': 'test1234'})
            except:
                return False

        # Check it redirects to index
        self.assertRedirects(response, reverse('index'))

    @chapter9
    def test_upload_image(self):
        # Create fake user and image to upload to register user
        image = SimpleUploadedFile(
            "testuser.jpg", b"file_content", content_type="image/jpeg")
        try:
            response = self.client.post(reverse('register'),
                                        {'username': 'testuser', 'password': 'test1234',
                                         'email': 'testuser@testuser.com',
                                         'website': 'http://www.testuser.com',
                                         'picture': image})
        except:
            try:
                response = self.client.post(reverse('rango:register'),
                                            {'username': 'testuser', 'password': 'test1234',
                                             'email': 'testuser@testuser.com',
                                             'website': 'http://www.testuser.com',
                                             'picture': image})
            except:
                return False

        # Check user was successfully registered
        self.assertIn('thank you for registering!'.lower(),
                      response.content.decode('ascii').lower())
        user = User.objects.get(username='testuser')
        user_profile = UserProfile.objects.get(user=user)
        path_to_image = './media/profile_images/testuser.jpg'

        # Check file was saved properly
        self.assertTrue(os.path.isfile(path_to_image))

        # Delete fake file created
        default_storage.delete('./media/profile_images/testuser.jpg')
