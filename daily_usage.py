from app import db


class DailyUsage(db.Model):
    __tablename__ = 'daily_usage'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    date = db.Column(db.DateTime, unique=True, nullable=False)
    kwhUsed = db.Column(db.Float, unique=False)

    def __init__(self, date, kwhUsed):
        self.date = date
        self.kwhUsed = kwhUsed

    def __repr__(self):
        return '<DailyUsage %r, %r, %r>' % (self.id, self.date, self.kwhUsed)