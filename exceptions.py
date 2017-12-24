from logger import logger


class Impact3Error(Exception):
    def __init__(self, *args, **kwargs):
        logger.error(self.__class__.__name__ + ': ' +  ', '.join(i for i in args), exc_info=True)


class HandlerError(Impact3Error):
    pass


class SizeError(Impact3Error):
    pass


class PluginError(Impact3Error):
    pass


class InvalidCheckMethod(Impact3Error):
    pass


class NoPageListFound(Impact3Error):
    pass

