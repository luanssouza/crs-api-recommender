from ..util.database import session_factory
from ..models.recommendation import Recommendation

def insert_recommendation_dict(obj_dict):
    session = session_factory()

    obj = Recommendation.fromdict(**obj_dict)
    session.add(obj)

    session.flush()
    obj_id = obj.id
    
    session.commit()
    session.close()

    return obj_id