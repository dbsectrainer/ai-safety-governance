import {
  AppBar,
  Avatar,
  Box,
  Divider,
  IconButton,
  Menu,
  MenuItem,
  Toolbar,
  Tooltip,
  Typography,
} from "@mui/material";
import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import MenuIcon from "@mui/icons-material/Menu";
import AccountCircle from "@mui/icons-material/AccountCircle";
import NotificationsIcon from "@mui/icons-material/Notifications";
import { authService } from "../../services/auth";
import type { AuthUser } from "../../config/security";
import { isAdministrator } from "../../config/security";

interface HeaderProps {
  onMenuClick: () => void;
}

const Header = ({ onMenuClick }: HeaderProps) => {
  const navigate = useNavigate();
  const [anchorEl, setAnchorEl] = useState<null | HTMLElement>(null);
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

  const handleMenu = (event: React.MouseEvent<HTMLElement>) => {
    setAnchorEl(event.currentTarget);
  };

  const handleClose = () => {
    setAnchorEl(null);
  };

  const handleLogout = async () => {
    setAnchorEl(null);
    await authService.logout();
    navigate("/login", { replace: true });
  };

  const displayName = user?.full_name || user?.username || "Account";
  const initial = displayName.charAt(0).toUpperCase();

  return (
    <AppBar
      position="sticky"
      sx={{
        zIndex: (theme) => theme.zIndex.drawer + 1,
        bgcolor: "background.paper",
        color: "text.primary",
        boxShadow: 1,
      }}
    >
      <Toolbar>
        <IconButton
          edge="start"
          color="inherit"
          aria-label="Toggle navigation"
          onClick={onMenuClick}
          sx={{ mr: 2 }}
        >
          <MenuIcon />
        </IconButton>

        <Typography
          variant="h6"
          component="div"
          sx={{ flexGrow: 1, fontSize: { xs: "1rem", sm: "1.25rem" } }}
        >
          AI Safety Governance Platform
        </Typography>

        <Box
          sx={{
            display: "flex",
            alignItems: "center",
            gap: { xs: 0.5, sm: 2 },
          }}
        >
          <Tooltip title="View monitoring">
            <IconButton
              color="inherit"
              aria-label="View monitoring"
              onClick={() => navigate("/monitoring")}
            >
              <NotificationsIcon />
            </IconButton>
          </Tooltip>

          <Tooltip title="Account settings">
            <IconButton
              onClick={handleMenu}
              color="inherit"
              aria-label="Open account menu"
            >
              <Avatar sx={{ width: 32, height: 32 }}>
                {user ? initial : <AccountCircle />}
              </Avatar>
            </IconButton>
          </Tooltip>
        </Box>

        <Menu
          id="menu-appbar"
          anchorEl={anchorEl}
          anchorOrigin={{ vertical: "bottom", horizontal: "right" }}
          keepMounted
          transformOrigin={{ vertical: "top", horizontal: "right" }}
          open={Boolean(anchorEl)}
          onClose={handleClose}
        >
          <MenuItem disabled sx={{ opacity: 1 }}>
            <Box>
              <Typography variant="body2" fontWeight={600}>
                {displayName}
              </Typography>
              <Typography variant="caption" color="text.secondary">
                {user?.email || ""}
              </Typography>
            </Box>
          </MenuItem>
          <Divider />
          {isAdministrator(user) && (
            <MenuItem
              onClick={() => {
                handleClose();
                navigate("/config");
              }}
            >
              Settings
            </MenuItem>
          )}
          <MenuItem onClick={handleLogout}>Sign out</MenuItem>
        </Menu>
      </Toolbar>
    </AppBar>
  );
};

export default Header;
