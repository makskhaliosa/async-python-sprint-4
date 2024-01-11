from typing import Optional


class UrlTypes:
    '''Возможные типы url.'''
    PRIVATE = 'private'
    PUBLIC = 'public'


def check_url_type(url_type: Optional[str]) -> Optional[str]:
    '''Проверяет ограничения по типу url.'''
    if not url_type:
        return None

    assert url_type.lower() in (UrlTypes.PRIVATE, UrlTypes.PUBLIC), (
        f'url_type must be "{UrlTypes.PRIVATE}" or "{UrlTypes.PUBLIC}"'
    )
    return url_type
