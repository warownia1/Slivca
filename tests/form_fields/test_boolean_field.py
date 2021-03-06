from nose.tools import assert_is, raises, assert_true

from slivka.server.forms.fields import BooleanField, ValidationError


def test_bool_conversion():
    field = BooleanField('name', required=False)
    assert_is(field.run_validation(True), True)
    assert_is(field.run_validation(False), None)


def test_int_conversion():
    field = BooleanField('name', required=False)
    assert_is(field.run_validation(1), True)
    assert_is(field.run_validation(0), None)


def test_text_conversion():
    field = BooleanField('name', required=False)
    for text in ('false', 'FALSE', 'False', 'off', '0', 'no', 'NULL', 'NONE', ''):
        assert_is(field.run_validation(text), None)
    for text in ('true', 'TRUE', 'T', 'on', 'yes', 'Y'):
        assert_is(field.run_validation(text), True)
    assert_is(field.run_validation('foobar'), True)


def test_none_conversion():
    field = BooleanField('name', required=False)
    assert_is(field.run_validation(None), None)


# empty value validation

@raises(ValidationError)
def test_validate_none():
    field = BooleanField('name')
    field.validate(None)


@raises(ValidationError)
def test_validate_none_required():
    field = BooleanField('name', required=True)
    field.validate(None)


def test_validation_none_not_required():
    field = BooleanField('name', required=False)
    assert_is(field.validate(None), None)


# validation with default provided

def test_validate_none_with_default():
    field = BooleanField('name', default=True)
    assert_is(field.validate(None), True)
    field = BooleanField('name', default=False)
    assert_is(field.validate(None), None)


def test_validate_empty_with_default():
    field = BooleanField('name', default=True)
    assert_is(field.validate({}), True)
    assert_is(field.validate(''), True)


def test_true_to_cmd_parameter():
    field = BooleanField('name', required=False)
    assert_true(field.to_cmd_parameter(True))


def test_none_to_cmd_parameter():
    field = BooleanField('name', required=False)
    assert_is(field.to_cmd_parameter(None), None)
