from marshmallow_sqlalchemy import SQLAlchemyAutoSchema
from marshmallow_sqlalchemy.fields import Nested
from marshmallow import fields

from .couriers import Couriers
from .regions import Regions
from .transport_type import TransportTypes
from .orders import Orders


class OrdersSchema(SQLAlchemyAutoSchema):
    class Meta:
        model = Orders
        load_instance = True

class RegionsSchema(SQLAlchemyAutoSchema):
    class Meta:
        model = Regions
        load_instance = True

    regions_orders = Nested(OrdersSchema, many=True)


class TransportTypesSchema(SQLAlchemyAutoSchema):
    class Meta:
        model = TransportTypes
        load_instance = True


class CouriersSchema(SQLAlchemyAutoSchema):
    class Meta:
        model = Couriers
        load_instance = True

    regions = Nested(RegionsSchema, many=True)
    courier_type = Nested(TransportTypesSchema)
