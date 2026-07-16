from skime.env import Environment, Undef


def test_undef_is_a_singleton_object():
    assert Undef() is Undef()
    assert Undef() is not None


def test_alloc_local_can_replace_a_value_with_none():
    env = Environment()
    idx = env.alloc_local("value", 1)

    env.alloc_local("value", None)

    assert env.read_local(idx) is None
