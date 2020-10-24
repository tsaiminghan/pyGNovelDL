NAME = 'command_name'


class Command(object):
    """ this is a sample """
    name = NAME

    def __call__(self, *args, **kwargs):
        raise NotImplementedError
