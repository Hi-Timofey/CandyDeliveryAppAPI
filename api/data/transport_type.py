import sqlalchemy as sa
from sqlalchemy import orm

from .db_session import SqlAlchemyBase
from .db_session import create_session


class TransportTypes(SqlAlchemyBase):
    __tablename__ = 'transport_types'

    type_id = sa.Column(sa.Integer,
                        primary_key=True, autoincrement=True, unique=True)

    type_name = sa.Column(sa.String, nullable=False, unique=True)

    type_weight = sa.Column(sa.Integer, nullable=False)

    type_earn_coefficient = sa.Column(sa.Integer, nullable=False)

    couriers_with_type = orm.relation(
        'Couriers', back_populates='courier_type')

    def create(self, db_session):
        db_session.add(self)
        db_session.commit()
        return self

    def __repr__(self):
        return f'Type(id={self.type_id},type={self.type_name})'

    def __eq__(self, other):
        return self.type_weight == other.type_weight

    def __ne__(self, other):
        return self.type_weight != other.type_weight

    @staticmethod
    def type_exist(type_name) -> bool:
        db_sess = create_session()
        query = db_sess.query(TransportTypes.type_name).all()
        return (type_name,) in query
