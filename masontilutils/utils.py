from multiprocessing import Manager


def create_shared_data():
    manager = Manager()
    shared_data = manager.dict({
        'counter': 0,
        'processes': manager.dict(),
        'queries': manager.list(),
    })
    return shared_data

def create_query(query: str, **kwargs):
    return query.format(**kwargs)
