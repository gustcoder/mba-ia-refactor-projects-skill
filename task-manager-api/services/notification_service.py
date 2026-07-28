import smtplib

from models.notification import Notification


class NotificationService:
    def __init__(self, db_session, smtp_host, smtp_port, smtp_user, smtp_password):
        self.db = db_session
        self.smtp_host = smtp_host
        self.smtp_port = smtp_port
        self.smtp_user = smtp_user
        self.smtp_password = smtp_password

    def send_email(self, to, subject, body):
        try:
            server = smtplib.SMTP(self.smtp_host, self.smtp_port)
            server.starttls()
            server.login(self.smtp_user, self.smtp_password)
            message = f"Subject: {subject}\n\n{body}"
            server.sendmail(self.smtp_user, to, message)
            server.quit()
            return True
        except Exception:
            return False

    def notify_task_assigned(self, user, task):
        subject = f"Nova task atribuída: {task.title}"
        body = f"Olá {user.name},\n\nA task '{task.title}' foi atribuída a você.\n\nPrioridade: {task.priority}\nStatus: {task.status}"
        self.send_email(user.email, subject, body)
        self.db.add(Notification(user_id=user.id, task_id=task.id, type='task_assigned'))
        self.db.commit()

    def notify_task_overdue(self, user, task):
        subject = f"Task atrasada: {task.title}"
        body = f"Olá {user.name},\n\nA task '{task.title}' está atrasada!\n\nData limite: {task.due_date}"
        self.send_email(user.email, subject, body)
        self.db.add(Notification(user_id=user.id, task_id=task.id, type='task_overdue'))
        self.db.commit()

    def get_notifications(self, user_id):
        notifications = Notification.query.filter_by(user_id=user_id).all()
        return [n.to_dict() for n in notifications]
