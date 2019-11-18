from datetime import datetime, date

from sqlalchemy import desc


class DailyUsage:

    @staticmethod
    def test_me(msg):
        print(msg)

    @staticmethod
    def get_todays_usage():
        latest_entry = DailyUsage.query.order_by(desc(DailyUsage.date)).first()
        # latest_entry = db.session.query(DailyUsage).order_by(DailyUsage.date.asc()).first()
        if latest_entry:
            latest_entry_date = date(latest_entry.date.year, latest_entry.date.month, latest_entry.date.day)
            if latest_entry_date == datetime.today().date():
                return format(latest_entry.kwhUsed, '.7f')
        return 0