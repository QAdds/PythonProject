from sqlalchemy import text
from db_models.user import UserDBModel

def test_db_connection(db_session):
    result = db_session.execute(text("SELECT 1")).scalar()
    assert result == 1

def test_get_user_from_db(db_session):
    user = db_session.query(UserDBModel).first()
    assert user is not None
    assert user.id is not None
    assert user.email is not None

def test_register_user_saved_in_db(api_manager, test_user, db_helper):
    response = api_manager.auth_api.register_user(test_user, expected_status=201)
    data = response.json()

    db_user = db_helper.get_user_by_email(test_user.email)

    assert data["email"] == test_user.email
    assert db_user is not None
    assert db_user.email == test_user.email