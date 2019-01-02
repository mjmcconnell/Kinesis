# third-party imports
import testdata


class User(testdata.DictFactory):
    """Fake user details."""

    firstname = testdata.FakeDataFactory('firstName')
    lastname = testdata.FakeDataFactory('lastName')
    age = testdata.RandomInteger(10, 30)
    gender = testdata.RandomSelection(['female', 'male'])
