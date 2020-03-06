# -*- coding: utf-8 -*-
"""
Simulation XBlock.
"""
from xblock.core import XBlock
from xblock.fields import Scope, String
from xblockutils.studio_editable import StudioEditableXBlockMixin

from .utils import StudentViewBlockMixin, _


class SimulationBlock(XBlock, StudioEditableXBlockMixin, StudentViewBlockMixin):
    """
    XBlock for simulations.
    """

    display_name = String(
        display_name=_('Display Name'),
        help=_('The name of the simulation.'),
        default='Simulation',
        scope=Scope.content,
    )

    simulation_url = String(
        display_name=_('Simulation URL'),
        default='',
        help=_('The url of the simulation html file.'),
        scope=Scope.content,
    )

    editable_fields = (
        'display_name',
        'simulation_url',
    )

    student_view_template = 'templates/simulation_student_view.html'
    css_resource_url = 'public/css/simulation-xblock.css'

    def student_view_data(self, context=None):
        """
        Return content and settings for student view.
        """
        return {
            'display_name': self.display_name,
            'simulation_url': self.simulation_url,
        }
