import requests
import pytest
from flask import Flask
from app import create_app
from bs4 import BeautifulSoup
from urllib.parse import urljoin

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
    category_selection_route = '/'  # Adjust this if the category links are in a different route

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
