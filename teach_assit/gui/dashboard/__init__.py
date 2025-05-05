"""
Package pour les composants du tableau de bord amélioré.
"""

from teach_assit.gui.dashboard.dashboard_main import EnhancedDashboard
from teach_assit.gui.dashboard.stats_widget import StatsWidget
from teach_assit.gui.dashboard.performance_widget import PerformanceWidget
from teach_assit.gui.dashboard.students_widget import StudentsWidget
from teach_assit.gui.dashboard.grades_widget import GradesWidget

__all__ = [
    'EnhancedDashboard',
    'StatsWidget',
    'PerformanceWidget',
    'StudentsWidget',
    'GradesWidget'
] 