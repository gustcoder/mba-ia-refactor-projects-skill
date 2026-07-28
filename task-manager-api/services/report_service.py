from datetime import datetime, timedelta

from sqlalchemy import case, func

from database import db
from models.category import Category
from models.task import Task
from models.user import User
from services.errors import NotFoundError
from utils.helpers import VALID_STATUSES, calculate_percentage


class ReportService:
    def summary(self):
        total_tasks = Task.query.count()
        total_users = User.query.count()
        total_categories = Category.query.count()

        by_status = {
            status: Task.query.filter_by(status=status).count()
            for status in VALID_STATUSES
        }

        by_priority = {
            label: Task.query.filter_by(priority=priority).count()
            for priority, label in enumerate(['critical', 'high', 'medium', 'low', 'minimal'], start=1)
        }

        overdue_tasks = [
            t for t in Task.query.filter(Task.due_date.isnot(None)).all()
            if t.is_overdue()
        ]
        overdue_list = [
            {
                'id': t.id,
                'title': t.title,
                'due_date': str(t.due_date),
                'days_overdue': (datetime.utcnow() - t.due_date).days,
            }
            for t in overdue_tasks
        ]

        seven_days_ago = datetime.utcnow() - timedelta(days=7)
        recent_tasks = Task.query.filter(Task.created_at >= seven_days_ago).count()
        recent_done = Task.query.filter(
            Task.status == 'done', Task.updated_at >= seven_days_ago
        ).count()

        productivity = {
            user_id: (total, completed)
            for user_id, total, completed in (
                db.session.query(
                    Task.user_id,
                    func.count(Task.id),
                    func.sum(case((Task.status == 'done', 1), else_=0)),
                )
                .group_by(Task.user_id)
                .all()
            )
        }

        user_stats = []
        for u in User.query.all():
            total, completed = productivity.get(u.id, (0, 0))
            completed = completed or 0
            user_stats.append({
                'user_id': u.id,
                'user_name': u.name,
                'total_tasks': total,
                'completed_tasks': completed,
                'completion_rate': calculate_percentage(completed, total),
            })

        return {
            'generated_at': str(datetime.utcnow()),
            'overview': {
                'total_tasks': total_tasks,
                'total_users': total_users,
                'total_categories': total_categories,
            },
            'tasks_by_status': by_status,
            'tasks_by_priority': by_priority,
            'overdue': {
                'count': len(overdue_list),
                'tasks': overdue_list,
            },
            'recent_activity': {
                'tasks_created_last_7_days': recent_tasks,
                'tasks_completed_last_7_days': recent_done,
            },
            'user_productivity': user_stats,
        }

    def user_report(self, user_id):
        user = User.query.get(user_id)
        if not user:
            raise NotFoundError('Usuário não encontrado')

        tasks = Task.query.filter_by(user_id=user_id).all()
        total = len(tasks)
        by_status = {status: 0 for status in VALID_STATUSES}
        overdue = 0
        high_priority = 0

        for t in tasks:
            by_status[t.status] = by_status.get(t.status, 0) + 1
            if t.priority <= 2:
                high_priority += 1
            if t.is_overdue():
                overdue += 1

        return {
            'user': {
                'id': user.id,
                'name': user.name,
                'email': user.email,
            },
            'statistics': {
                'total_tasks': total,
                'done': by_status['done'],
                'pending': by_status['pending'],
                'in_progress': by_status['in_progress'],
                'cancelled': by_status['cancelled'],
                'overdue': overdue,
                'high_priority': high_priority,
                'completion_rate': calculate_percentage(by_status['done'], total),
            },
        }
