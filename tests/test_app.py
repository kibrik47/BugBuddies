import requests
import pytest
from flask import Flask
from app import create_app
from flask import url_for
from bson import ObjectId



from bs4 import BeautifulSoup
from urllib.parse import urljoin
import os
os.environ['FLASK_ENV'] = 'testing'

# Assuming your Flask app is created using the create_app function
app, _ = create_app()

@pytest.fixture
def client():
    with app.test_client() as client:
        yield client

def test_routes_return_200_or_302(client):
    # List of static routes to test
    static_routes = ['/', '/login', '/logout', '/register']

    # Dynamic route for the category selection page
    category_selection_route = '/' 

    # Make sure the category selection page returns a status code of 200 or 302
    response_category_selection = client.get(category_selection_route)
    assert response_category_selection.status_code in [200, 302], f"Failed for route {category_selection_route}. Status code: {response_category_selection.status_code}"

    soup = BeautifulSoup(response_category_selection.data, 'html.parser')
    category_links = [a['href'] for a in soup.find_all('a', class_='square')]

    # Test each category link
    for category_link in category_links:
        response_forum = client.get(category_link)
        response_post = client.get(category_link + '/post')

        assert response_forum.status_code in [200, 302], f"Failed for route {category_link}. Status code: {response_forum.status_code}"

        if response_post.status_code == 302:
            # Handle redirection for response_post
            redirection_location_post = response_post.headers['Location']
            print(f"Redirected to: {redirection_location_post}")
            
            # Follow the redirect for response_post
            response_follow_redirect_post = client.get(redirection_location_post)
            assert response_follow_redirect_post.status_code in [200, 302], f"Failed for route {redirection_location_post}. Status code: {response_follow_redirect_post.status_code}"
            
            # Update the response_post to the redirected response for further checks
            response_post = response_follow_redirect_post

        assert response_post.status_code in [200, 302], f"Failed for route {category_link}/post. Status code: {response_post.status_code}"

    # Test static routes
    for route in static_routes:
        response = client.get(route)
        assert response.status_code in [200, 302], f"Failed for route {route}. Status code: {response.status_code}"

def test_register_username_length_error(client):
    # Simulate a registration attempt with a username that doesn't meet the length requirement
    invalid_username = 'abc'  # Username with less than 4 letters

    # Make a POST request to register with the invalid username
    response = client.post('/register', data={'username': invalid_username, 'password': 'test_password'})

    # Check if the response status code is 200 (registration page should still be accessible)
    assert response.status_code == 200

    # Check if the response contains the error message related to username length
    assert b'Username must contain at least 4 letters (a-z or A-Z)' in response.data

def test_register_password_length_error(client):
    # Simulate a registration attempt with a password that doesn't meet the length requirement
    invalid_password = '1234'  # Password with less than 5 characters

    # Make a POST request to register with the invalid password
    response = client.post('/register', data={'username': 'test_user', 'password': invalid_password})

    # Check if the response status code is 200 (registration page should still be accessible)
    assert response.status_code == 200

    # Check if the response contains the error message related to password length
    assert b'Password must contain at least 5 characters' in response.data


def test_register_username_special_char_error(client):
    # Simulate a registration attempt with a username that contains special characters
    invalid_username = 'user@name'  # Username with special characters

    # Make a POST request to register with the invalid username
    response = client.post('/register', data={'username': invalid_username, 'password': 'test_password'})

    # Check if the response status code is 200 (registration page should still be accessible)
    assert response.status_code == 200

    # Check if the response contains the error message related to special characters in the username
    assert b'Username should not contain special characters' in response.data


def test_post_issue(client):
    # Log in first to access the post page
    login_response = client.post('/login', data={'username': 'test_user', 'password': 'test_password'}, follow_redirects=True)
    assert login_response.status_code == 200  # Check if login was successful
    
    # Test posting an issue
    issue_data = {
        'issueTopic': 'Test Issue',
        'description': 'This is a test issue description',
        'labels': 'test, issue',
        'specs': 'Test specifications',
    }
    
    post_response = client.post('/forum/test_category/post', data=issue_data, follow_redirects=True)
    assert post_response.status_code == 200  # Check if posting the issue was successful
    
    # Parse the HTML response using BeautifulSoup
    soup = BeautifulSoup(post_response.data, 'html.parser')
    
    # Find the part of the response containing the issue content
    issue_content = soup.find('div', class_='issue-content')