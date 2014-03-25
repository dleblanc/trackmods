from makenew import foo

def get_maven_modules(dirData):
    pass

def test_get_module_dirs():

    dirData = {
        "d1": {},
        "d2": {},
        "d3": "d3"
    }

    maven_modules = get_maven_modules(dirData)

    assert len(maven_modules) == 3
    assert foo() == "bar"