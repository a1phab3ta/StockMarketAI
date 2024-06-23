from marshmallow import Schema, fields, validate

class StockSchema(Schema):
    ticker = fields.Str(required=True, validate=validate.Length(min=1))
    shares = fields.Int(required=True, validate=validate.Range(min=1))

class UserSchema(Schema):
    username = fields.Str(required=True, validate=validate.Length(min=1))
    password = fields.Str(required=True, validate=validate.Length(min=1))
    portfolio = fields.List(fields.Nested(StockSchema), required=True)
