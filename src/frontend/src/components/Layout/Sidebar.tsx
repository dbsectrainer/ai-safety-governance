import {
  Drawer,
  List,
  ListItem,
  ListItemIcon,
  ListItemText,
  ListItemButton,
  Box,
  useTheme,
  Divider,
} from '@mui/material';
import {
  Dashboard as DashboardIcon,
  People as PeopleIcon,
  Settings as SettingsIcon,
  Assessment as AssessmentIcon,
  Security as SecurityIcon,
  Gavel as GavelIcon,
} from '@mui/icons-material';
import { useLocation, useNavigate } from 'react-router-dom';

interface SidebarProps {
  isOpen: boolean;
}

const DRAWER_WIDTH = 240;

const menuItems = [
  { text: 'Dashboard', icon: <DashboardIcon />, path: '/' },
  { text: 'Users', icon: <PeopleIcon />, path: '/users' },
  { text: 'Configuration', icon: <SettingsIcon />, path: '/config' },
  { text: 'Monitoring', icon: <AssessmentIcon />, path: '/monitoring' },
  { text: 'Compliance', icon: <GavelIcon />, path: '/compliance' },
  { text: 'Security', icon: <SecurityIcon />, path: '/security' },
];

const Sidebar = ({ isOpen }: SidebarProps) => {
  const theme = useTheme();
  const navigate = useNavigate();
  const location = useLocation();

  const handleNavigation = (path: string) => {
    navigate(path);
  };

  const drawer = (
    <Box sx={{ overflow: 'auto' }}>
      <Box
        sx={{
          height: 64, // Match header height
          display: 'flex',
          alignItems: 'center',
          px: 2,
        }}
      >
        {/* Logo or branding could go here */}
      </Box>
      <Divider />
      <List>
        {menuItems.map((item) => (
          <ListItem key={item.text} disablePadding>
            <ListItemButton
              selected={location.pathname === item.path}
              onClick={() => handleNavigation(item.path)}
              sx={{
                '&.Mui-selected': {
                  backgroundColor: theme.palette.primary.light + '20',
                  '&:hover': {
                    backgroundColor: theme.palette.primary.light + '30',
                  },
                },
              }}
            >
              <ListItemIcon
                sx={{
                  color: location.pathname === item.path
                    ? theme.palette.primary.main
                    : 'inherit',
                }}
              >
                {item.icon}
              </ListItemIcon>
              <ListItemText 
                primary={item.text}
                sx={{
                  color: location.pathname === item.path
                    ? theme.palette.primary.main
                    : 'inherit',
                }}
              />
            </ListItemButton>
          </ListItem>
        ))}
      </List>
    </Box>
  );

  return (
    <Drawer
      variant="permanent"
      sx={{
        width: DRAWER_WIDTH,
        flexShrink: 0,
        '& .MuiDrawer-paper': {
          width: DRAWER_WIDTH,
          boxSizing: 'border-box',
          borderRight: `1px solid ${theme.palette.divider}`,
          ...(!isOpen && {
            width: 0,
            visibility: 'hidden',
          }),
        },
      }}
      open={isOpen}
    >
      {drawer}
    </Drawer>
  );
};

export default Sidebar;
