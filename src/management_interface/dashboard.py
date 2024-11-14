import typing
from dataclasses import dataclass, field
from datetime import datetime
import json
import logging
import uuid

@dataclass
class DashboardWidget:
    """Represents a configurable dashboard widget."""
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    title: str = 'Untitled Widget'
    type: str = 'metric'  # e.g., 'metric', 'chart', 'log'
    data_source: typing.Optional[typing.Callable] = None
    data: dict = field(default_factory=dict)
    last_updated: datetime = field(default_factory=datetime.now)
    refresh_interval: int = 300  # Default 5 minutes
    config: dict = field(default_factory=dict)

class Dashboard:
    """
    Manages a comprehensive dashboard for system monitoring and insights.
    Supports dynamic widget configuration and data retrieval.
    """
    
    def __init__(self):
        """Initialize the dashboard with core monitoring capabilities."""
        self.logger = logging.getLogger('dashboard')
        self._widgets: dict[str, DashboardWidget] = {}
        self._data_sources: dict[str, typing.Callable] = {}
    
    def add_widget(self, widget: DashboardWidget) -> bool:
        """
        Add a new widget to the dashboard.
        
        :param widget: DashboardWidget to add
        :return: True if widget added successfully, False if widget with ID already exists
        """
        if widget.id in self._widgets:
            self.logger.warning(f"Widget with ID {widget.id} already exists")
            return False
        
        self._widgets[widget.id] = widget
        self.logger.info(f"Added widget: {widget.title} (ID: {widget.id})")
        return True
    
    def remove_widget(self, widget_id: str) -> bool:
        """
        Remove a widget from the dashboard.
        
        :param widget_id: ID of the widget to remove
        :return: True if widget removed successfully, False if widget not found
        """
        if widget_id not in self._widgets:
            self.logger.warning(f"Widget with ID {widget_id} not found")
            return False
        
        del self._widgets[widget_id]
        self.logger.info(f"Removed widget: {widget_id}")
        return True
    
    def update_widget(self, widget_id: str, updates: dict) -> bool:
        """
        Update an existing widget's configuration.
        
        :param widget_id: ID of the widget to update
        :param updates: Dictionary of updates to apply
        :return: True if update successful, False otherwise
        """
        if widget_id not in self._widgets:
            self.logger.warning(f"Widget with ID {widget_id} not found")
            return False
        
        widget = self._widgets[widget_id]
        
        # Update widget properties
        for key, value in updates.items():
            if hasattr(widget, key):
                setattr(widget, key, value)
        
        # Update last updated timestamp
        widget.last_updated = datetime.now()
        
        self.logger.info(f"Updated widget: {widget_id}")
        return True
    
    def register_data_source(self, name: str, data_source: typing.Callable) -> bool:
        """
        Register a data source for widgets to use.
        
        :param name: Name of the data source
        :param data_source: Callable that returns data
        :return: True if registration successful
        """
        self._data_sources[name] = data_source
        self.logger.info(f"Registered data source: {name}")
        return True
    
    def refresh_widget(self, widget_id: str) -> typing.Optional[dict]:
        """
        Refresh a specific widget's data by calling its data source.
        
        :param widget_id: ID of the widget to refresh
        :return: Updated widget data or None if refresh fails
        """
        if widget_id not in self._widgets:
            self.logger.warning(f"Widget with ID {widget_id} not found")
            return None
        
        widget = self._widgets[widget_id]
        
        if not widget.data_source:
            self.logger.warning(f"No data source configured for widget {widget_id}")
            return None
        
        try:
            # Call the data source function
            widget.data = widget.data_source()
            widget.last_updated = datetime.now()
            
            self.logger.info(f"Refreshed widget: {widget_id}")
            return widget.data
        except Exception as e:
            self.logger.error(f"Error refreshing widget {widget_id}: {e}")
            return None
    
    def refresh_all_widgets(self) -> dict:
        """
        Refresh all widgets in the dashboard.
        
        :return: Dictionary of widget IDs and their refresh results
        """
        refresh_results = {}
        for widget_id in self._widgets:
            refresh_results[widget_id] = self.refresh_widget(widget_id)
        
        return refresh_results
    
    def get_widget(self, widget_id: str) -> typing.Optional[DashboardWidget]:
        """
        Retrieve a specific widget.
        
        :param widget_id: ID of the widget to retrieve
        :return: Widget or None if not found
        """
        return self._widgets.get(widget_id)
    
    def list_widgets(self) -> list[DashboardWidget]:
        """
        List all widgets in the dashboard.
        
        :return: List of dashboard widgets
        """
        return list(self._widgets.values())
    
    def export_dashboard_config(self) -> dict:
        """
        Export the current dashboard configuration.
        
        :return: Dictionary representing dashboard configuration
        """
        return {
            'widgets': [
                {
                    'id': widget.id,
                    'title': widget.title,
                    'type': widget.type,
                    'config': widget.config,
                    'last_updated': widget.last_updated.isoformat()
                }
                for widget in self._widgets.values()
            ]
        }
    
    def import_dashboard_config(self, config: dict) -> bool:
        """
        Import a dashboard configuration.
        
        :param config: Dashboard configuration to import
        :return: True if import successful, False otherwise
        """
        try:
            for widget_config in config.get('widgets', []):
                widget = DashboardWidget(
                    id=widget_config['id'],
                    title=widget_config['title'],
                    type=widget_config['type'],
                    config=widget_config.get('config', {}),
                    last_updated=datetime.fromisoformat(widget_config['last_updated'])
                )
                self.add_widget(widget)
            
            self.logger.info("Dashboard configuration imported successfully")
            return True
        except Exception as e:
            self.logger.error(f"Error importing dashboard configuration: {e}")
            return False

def main():
    """Example usage of Dashboard."""
    # Setup logging
    logging.basicConfig(level=logging.INFO)
    
    # Create dashboard
    dashboard = Dashboard()
    
    # Example data source
    def system_metrics_source():
        return {
            'cpu_usage': 45.5,
            'memory_usage': 62.3,
            'disk_usage': 78.1
        }
    
    # Register data source
    dashboard.register_data_source('system_metrics', system_metrics_source)
    
    # Create a widget
    system_metrics_widget = DashboardWidget(
        title='System Performance',
        type='metric',
        data_source=system_metrics_source
    )
    
    # Add widget to dashboard
    dashboard.add_widget(system_metrics_widget)
    
    # Refresh widget
    metrics = dashboard.refresh_widget(system_metrics_widget.id)
    print("System Metrics:", metrics)
    
    # Export and import dashboard configuration
    config = dashboard.export_dashboard_config()
    print("Dashboard Config:", json.dumps(config, indent=2))

if __name__ == '__main__':
    main()
