class UrlExistsError(BaseException):
    '''Ошибка, если url не существует или удален.'''
    pass


class AccessError(BaseException):
    '''Ошибка доступа к url.'''
    pass
