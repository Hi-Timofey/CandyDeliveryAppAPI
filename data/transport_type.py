import sqlalchemy as sa
from sqlalchemy import orm

from .db_session import SqlAlchemyBase


class TransportTypes(SqlAlchemyBase):
    __tablename__ = 'transport_types'

    type_id = sa.Column(sa.Integer,
                        primary_key=True, autoincrement=True, unique=True)

    type_name = sa.Column(sa.String, nullable=False)

    type_weight = sa.Column(sa.Integer, nullable=False)

    couriers_with_type = orm.relation('Couriers', back_populates='courier_type')


    def __init__(self, type_name, type_weight):
        self.type_name = type_name
        self.type_weight = type_weight

    def create(self, db_session):
        db_session.add(self)
        db_session.commit()
        return self

    def __repr__(self):
        return f'Type<id {self.type_id}>: {self.type_name} ({type_weight})'


# class RegionsSchema(SQLAlchemyAutoSchema):
#     class Meta:
#         model = Regions
#         include_relationships = True
#         load_instance = True
