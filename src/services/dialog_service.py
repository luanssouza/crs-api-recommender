from ..util.database import session_factory
from ..models.dialog import Dialog

def insert_dialog_dict(obj_dict):
    session = session_factory()

    obj = Dialog(**obj_dict)
    session.add(obj)

    session.flush()
    obj_id = obj.id
    
    session.commit()
    session.close()

    return obj_id