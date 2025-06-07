from flask_rebar import ResponseSchema
from marshmallow import pre_dump
from marshmallow import pre_load

class DataEnvelopeResponse(ResponseSchema):
    @pre_dump
    @pre_load
    def envelope_in_data(self, data, **kwargs):
        if not isinstance(data, dict) or "data" not in data:
            return {"data": data}
        return data