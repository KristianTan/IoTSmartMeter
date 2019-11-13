from app import db


class DailyUsage(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    date = db.Column(db.String(80), unique=True, nullable=False)
    hours = db.Column(db.Integer(120), unique=False)

    def __repr__(self):
        return '<DailyUsage %r>' % self.id
