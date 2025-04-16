import json

import pytest
from django.urls import reverse

from bot.models import User
from conftest import update_callback_data


@pytest.mark.django_db
@pytest.mark.parametrize("payload", ["confirm"], indirect=True)
def test_telegram_webhook(client, payload):
    initial_count = User.objects.count()

    # Example payload from Telegram
    url = reverse("webhook")
    response = client.post(url, json.dumps(payload), content_type="application/json")

    # Check if the response is what you expect
    assert response.status_code == 200

    # Check that a new News item has been added
    assert User.objects.count() == initial_count + 1

    # Optionally, check that the last item added has correct content
    # last_news = User.objects.latest("id")
    # assert last_news.url == "https://leviathannews.xyz/"
