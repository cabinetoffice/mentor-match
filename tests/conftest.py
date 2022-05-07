import os
import pathlib
import pytest as pytest
import app.helpers
from app import create_app
from app.config import TestConfig
from matching.process import create_participant_list_from_path
from app.classes import CSMentee, CSMentor
from app.helpers import known_file as kf


@pytest.fixture(scope="function")
def base_data() -> dict:
    return {
        "first name": "Test",
        "last name": "Data",
        "email address": "test@data.com",
        "job title": "N/A",
        "organisation": "Department of Fun",
        "grade": "Grade 7",
        "profession": "Policy",
        "biography": "Test biography",
    }


@pytest.fixture
def base_mentor_data(base_data):
    base_data["grade"] = "Grade 6"
    base_data["department"] = "Ministry of Silly Walks"
    base_data["characteristics"] = "bisexual, transgender"
    return base_data


@pytest.fixture
def base_mentee_data(base_data):
    base_data["target profession"] = "Policy"
    base_data["match with similar identity"] = "yes"
    base_data["identity to match"] = "bisexual"
    return base_data


@pytest.fixture(scope="function")
def base_mentee(base_mentee_data):
    return CSMentee(**base_mentee_data)


@pytest.fixture(scope="function")
def base_mentor(base_mentor_data):
    return CSMentor(**base_mentor_data)


@pytest.fixture(scope="function")
def known_file(base_data):
    return kf


@pytest.fixture(scope="function")
def test_data_path(tmpdir_factory):
    return tmpdir_factory.mktemp("data")


@pytest.fixture
def client(test_data_path):
    test_app = create_app(TestConfig)
    test_app.config["UPLOAD_FOLDER"] = test_data_path
    test_app_context = test_app.test_request_context()
    test_app_context.push()
    with test_app.test_client() as client:
        client.set_cookie(server_name="localhost", key="logged-in", value="true")
        yield client


@pytest.fixture(scope="function")
def test_participants(test_data_path, known_file):
    known_file(test_data_path, "mentee", 50)
    known_file(test_data_path, "mentor", 50)
    create_participant_list_from_path(CSMentee, test_data_path)
    create_participant_list_from_path(CSMentor, test_data_path)
    yield


@pytest.fixture(autouse=True)
def predictable_random_string(monkeypatch):
    def predictable_string():
        return "abcdef"

    monkeypatch.setattr(app.helpers, "random_string", predictable_string)


@pytest.fixture
def write_test_file(test_data_path):
    def _write_test_file(filename):
        filepath = pathlib.Path(test_data_path, "12345", filename)
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        f = open(filepath, "w")
        f.write("Fake data")
        f.close()

    return _write_test_file
