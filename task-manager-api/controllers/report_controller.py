from services.errors import NotFoundError


class ReportController:
    def __init__(self, report_service):
        self.report_service = report_service

    def summary(self):
        return self.report_service.summary(), 200

    def user_report(self, user_id):
        try:
            return self.report_service.user_report(user_id), 200
        except NotFoundError as e:
            return {'error': str(e)}, 404
