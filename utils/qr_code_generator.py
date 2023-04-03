from uuid import uuid4


def get_uid(section_name):
    return f'{section_name}{uuid4().hex[:10]}'
