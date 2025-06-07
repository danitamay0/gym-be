from flask_sqlalchemy import BaseQuery

class SoftDeleteQuery(BaseQuery):
    def alive(self):
        return self.filter_by(deleted_at=None)