import {
  Box,
  Divider,
  Drawer,
  List,
  ListItem,
  ListItemButton,
  ListItemIcon,
  ListItemText,
  Typography,
  useTheme,
} from "@mui/material";
import {
  Assessment as AssessmentIcon,
  Dashboard as DashboardIcon,
  Gavel as GavelIcon,
  Home as HomeIcon,
  People as PeopleIcon,
  Security as SecurityIcon,
  Settings as SettingsIcon,
} from "@mui/icons-material";
import { useEffect, useState } from "react";
import { useLocation, useNavigate } from "react-router-dom";
import { authService } from "../../services/auth";
import type { AuthUser } from "../../config/security";
import { isAdministrator } from "../../config/security";

interface SidebarProps {
  isOpen: boolean;
  isMobile: boolean;
  onClose: () => void;
}

const DRAWER_WIDTH = 240;

const menuItems = [
  { text: "Home", icon: <HomeIcon />, path: "/", roles: [] as string[] },
  {
    text: "Dashboard",
    icon: <DashboardIcon />,
    path: "/dashboard",
    roles: [] as string[],
  },
  { text: "Users", icon: <PeopleIcon />, path: "/users", roles: ["admin"] },
  {
    text: "Configuration",
    icon: <SettingsIcon />,
    path: "/config",
    roles: ["admin"],
  },
  {
    text: "Monitoring",
    icon: <AssessmentIcon />,
    path: "/monitoring",
    roles: [] as string[],
  },
  {
    text: "Compliance",
    icon: <GavelIcon />,
    path: "/compliance",
    roles: ["admin", "compliance-officer"],
  },
  {
    text: "Security",
    icon: <SecurityIcon />,
    path: "/security",
    roles: ["admin", "security-officer"],
  },
];

const Sidebar = ({ isOpen, isMobile, onClose }: SidebarProps) => {
  const theme = useTheme();
  const navigate = useNavigate();
  const location = useLocation();
  const [user, setUser] = useState<AuthUser | null>(null);

  useEffect(() => {
    let cancelled = false;
    if (!authService.isAuthenticated()) {
      setUser(null);
      return () => {
        cancelled = true;
      };
    }
    void authService.getCurrentUser().then((current) => {
      if (!cancelled) {
        setUser(current);
      }
    });
    return () => {
      cancelled = true;
    };
  }, []);

  const canAccess = (roles: string[]) => {
    if (roles.length === 0) {
      return true;
    }
    if (isAdministrator(user)) {
      return true;
    }
    return roles.some((role) => user?.roles?.includes(role));
  };

  const handleNavigation = (path: string) => {
    navigate(path);
    if (isMobile) {
      onClose();
    }
  };

  const drawer = (
    <Box
      sx={{
        overflow: "auto",
        display: "flex",
        flexDirection: "column",
        height: "100%",
      }}
    >
      <Box
        sx={{
          height: 64,
          display: "flex",
          alignItems: "center",
          px: 2,
        }}
      >
        <Typography variant="subtitle1" fontWeight={700} color="primary">
          AI Safety
        </Typography>
      </Box>
      <Divider />
      <List component="nav" aria-label="Main navigation">
        {menuItems
          .filter((item) => canAccess(item.roles))
          .map((item) => (
            <ListItem key={item.text} disablePadding>
              <ListItemButton
                selected={location.pathname === item.path}
                onClick={() => handleNavigation(item.path)}
                sx={{
                  "&.Mui-selected": {
                    backgroundColor: `${theme.palette.primary.light}20`,
                    "&:hover": {
                      backgroundColor: `${theme.palette.primary.light}30`,
                    },
                  },
                }}
              >
                <ListItemIcon
                  sx={{
                    color:
                      location.pathname === item.path
                        ? theme.palette.primary.main
                        : "inherit",
                  }}
                >
                  {item.icon}
                </ListItemIcon>
                <ListItemText
                  primary={item.text}
                  sx={{
                    color:
                      location.pathname === item.path
                        ? theme.palette.primary.main
                        : "inherit",
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
      variant={isMobile ? "temporary" : "permanent"}
      sx={{
        width: isMobile ? 0 : isOpen ? DRAWER_WIDTH : 0,
        flexShrink: 0,
        "& .MuiDrawer-paper": {
          width: DRAWER_WIDTH,
          boxSizing: "border-box",
          borderRight: `1px solid ${theme.palette.divider}`,
          ...(!isMobile &&
            !isOpen && {
              width: 0,
              visibility: "hidden",
            }),
        },
      }}
      open={isMobile ? isOpen : true}
      onClose={onClose}
      ModalProps={{ keepMounted: true }}
    >
      {drawer}
    </Drawer>
  );
};

export default Sidebar;
