import { useState } from 'react';
import { Box, useTheme } from '@mui/material';
import Sidebar from './Sidebar';
import Header from './Header';

interface LayoutProps {
  children: React.ReactNode;
}

const Layout = ({ children }: LayoutProps) => {
  const theme = useTheme();
  const [isSidebarOpen, setIsSidebarOpen] = useState(true);

  const toggleSidebar = () => {
    setIsSidebarOpen(!isSidebarOpen);
  };

  return (
    <Box sx={{ display: 'flex', minHeight: '100vh' }}>
      <Sidebar isOpen={isSidebarOpen} />
      <Box
        component="main"
        sx={{
          flexGrow: 1,
          bgcolor: theme.palette.background.default,
          display: 'flex',
          flexDirection: 'column',
          minHeight: '100vh',
          width: { sm: `calc(100% - ${isSidebarOpen ? 240 : 0}px)` },
          ml: { sm: isSidebarOpen ? '240px' : 0 },
          transition: theme.transitions.create(['margin', 'width'], {
            easing: theme.transitions.easing.sharp,
            duration: theme.transitions.duration.leavingScreen,
          }),
        }}
      >
        <Header onMenuClick={toggleSidebar} />
        <Box sx={{ p: 3, flexGrow: 1 }}>{children}</Box>
      </Box>
    </Box>
  );
};

export default Layout;
