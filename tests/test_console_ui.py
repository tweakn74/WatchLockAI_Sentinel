# File: tests/test_console_ui.py
# Purpose: Tests for minimal console UI (P4-006)

import os
import sys
import unittest
from pathlib import Path
from unittest.mock import patch, MagicMock

# Add project root to path for imports
REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if REPO_ROOT not in sys.path:
    sys.path.insert(0, REPO_ROOT)

try:
    from console.console_ui import ConsoleUI, get_console_ui, setup_console_routes, get_console_status
except ImportError:
    ConsoleUI = None


@unittest.skipIf(ConsoleUI is None, "console_ui module not available")
class TestConsoleUI(unittest.TestCase):
    """Test minimal console UI functionality"""
    
    def setUp(self):
        """Set up test environment"""
        self.env_patcher = patch.dict(os.environ, {
            'CONSOLE_UI_ENABLED': '1'
        })
        self.env_patcher.start()
        
    def tearDown(self):
        """Clean up test environment"""
        self.env_patcher.stop()
        
    def test_console_ui_init(self):
        """Test ConsoleUI initialization"""
        ui = ConsoleUI()
        
        self.assertTrue(ui.is_enabled())
        self.assertEqual(ui.static_dir.name, "static")
        
    def test_console_ui_disabled(self):
        """Test ConsoleUI when disabled"""
        with patch.dict(os.environ, {'CONSOLE_UI_ENABLED': '0'}):
            ui = ConsoleUI()
            self.assertFalse(ui.is_enabled())
            
    def test_get_static_dir(self):
        """Test static directory path"""
        ui = ConsoleUI()
        static_dir = ui.get_static_dir()
        
        self.assertIsInstance(static_dir, Path)
        self.assertEqual(static_dir.name, "static")
        
    @patch('console.console_ui.Path.exists')
    def test_setup_routes_enabled(self, mock_exists):
        """Test route setup when enabled"""
        mock_exists.return_value = True
        ui = ConsoleUI()
        
        # Mock FastAPI app
        mock_app = MagicMock()
        
        ui.setup_routes(mock_app)
        
        # Should have mounted static files and added routes
        mock_app.mount.assert_called_once()
        self.assertEqual(mock_app.get.call_count, 2)  # Dashboard and info routes
        
    def test_setup_routes_disabled(self):
        """Test route setup when disabled"""
        with patch.dict(os.environ, {'CONSOLE_UI_ENABLED': '0'}):
            ui = ConsoleUI()
            mock_app = MagicMock()
            
            ui.setup_routes(mock_app)
            
            # Should not have added any routes
            mock_app.mount.assert_not_called()
            mock_app.get.assert_not_called()
            
    def test_setup_routes_no_fastapi(self):
        """Test route setup when FastAPI not available"""
        ui = ConsoleUI()
        
        with patch.dict('sys.modules', {'fastapi': None}):
            mock_app = MagicMock()
            
            # Should not raise exception
            ui.setup_routes(mock_app)
            
    @patch('console.console_ui.Path.exists')
    def test_get_ui_status_enabled(self, mock_exists):
        """Test UI status when enabled"""
        mock_exists.return_value = True
        ui = ConsoleUI()
        
        status = ui.get_ui_status()
        
        self.assertTrue(status['enabled'])
        self.assertTrue(status['static_files_exist'])
        self.assertEqual(status['dashboard_url'], '/console/')
        
    def test_get_ui_status_disabled(self):
        """Test UI status when disabled"""
        with patch.dict(os.environ, {'CONSOLE_UI_ENABLED': '0'}):
            ui = ConsoleUI()
            
            status = ui.get_ui_status()
            
            self.assertFalse(status['enabled'])
            self.assertIsNone(status['dashboard_url'])
            
    @patch('console.console_ui.Path.exists')
    def test_get_ui_status_missing_files(self, mock_exists):
        """Test UI status with missing static files"""
        mock_exists.return_value = False
        ui = ConsoleUI()
        
        status = ui.get_ui_status()
        
        self.assertTrue(status['enabled'])
        self.assertFalse(status['static_files_exist'])
        
    def test_global_console_ui(self):
        """Test global console UI instance"""
        ui1 = get_console_ui()
        ui2 = get_console_ui()
        
        # Should return same instance
        self.assertIs(ui1, ui2)
        
    def test_setup_console_routes(self):
        """Test setup_console_routes convenience function"""
        mock_app = MagicMock()
        
        with patch('console.console_ui.get_console_ui') as mock_get_ui:
            mock_ui = MagicMock()
            mock_get_ui.return_value = mock_ui
            
            setup_console_routes(mock_app)
            
            mock_ui.setup_routes.assert_called_once_with(mock_app)
            
    def test_get_console_status(self):
        """Test get_console_status convenience function"""
        with patch('console.console_ui.get_console_ui') as mock_get_ui:
            mock_ui = MagicMock()
            mock_ui.get_ui_status.return_value = {'status': 'test'}
            mock_get_ui.return_value = mock_ui
            
            status = get_console_status()
            
            self.assertEqual(status, {'status': 'test'})
            mock_ui.get_ui_status.assert_called_once()
            
    def test_route_functions(self):
        """Test that route functions work correctly"""
        ui = ConsoleUI()
        mock_app = MagicMock()
        
        # Mock FastAPI imports
        with patch('console.console_ui.HTTPException') as mock_http_exception, \
             patch('console.console_ui.StaticFiles') as mock_static_files, \
             patch('console.console_ui.FileResponse') as mock_file_response, \
             patch('console.console_ui.HTMLResponse') as mock_html_response, \
             patch('console.console_ui.Path.exists', return_value=True):
            
            ui.setup_routes(mock_app)
            
            # Verify routes were registered
            self.assertEqual(mock_app.get.call_count, 2)
            
            # Get the registered route functions
            dashboard_route = mock_app.get.call_args_list[0][1]['endpoint']
            info_route = mock_app.get.call_args_list[1][1]['endpoint']
            
            # Test info route
            info_result = info_route()
            self.assertIn('console_ui', info_result)
            self.assertTrue(info_result['console_ui']['enabled'])


if __name__ == '__main__':
    unittest.main()
