import { useCallback, useEffect, useState } from 'react';
import { Helmet } from 'react-helmet-async';
import {
  Alert,
  Avatar,
  Box,
  Button,
  Chip,
  CircularProgress,
  Dialog,
  DialogActions,
  DialogContent,
  DialogContentText,
  DialogTitle,
  FormControl,
  FormControlLabel,
  InputLabel,
  MenuItem,
  Paper,
  Select,
  Switch,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  TextField,
  Tooltip,
  Typography,
  IconButton,
  useTheme,
} from '@mui/material';
import {
  Add as AddIcon,
  Block as BlockIcon,
  CheckCircle as CheckCircleIcon,
  Delete as DeleteIcon,
  Edit as EditIcon,
  Refresh as RefreshIcon,
  Warning as WarningIcon,
} from '@mui/icons-material';
import { format } from 'date-fns';
import { useSnackbar } from 'notistack';
import { usersService } from '../../services/users';
import type { ApiUser, CreateUserPayload, UpdateUserPayload } from '../../services/users';
import { getErrorMessage } from '../../services/api';

interface UserFormData {
  username: string;
  email: string;
  full_name: string;
  password: string;
  role: 'Admin' | 'User';
  is_active: boolean;
}

const EMPTY_FORM: UserFormData = {
  username: '',
  email: '',
  full_name: '',
  password: '',
  role: 'User',
  is_active: true,
};

const Users = () => {
  const theme = useTheme();
  const { enqueueSnackbar } = useSnackbar();
  const [users, setUsers] = useState<ApiUser[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [isRefreshing, setIsRefreshing] = useState(false);
  const [error, setError] = useState('');
  const [dialogOpen, setDialogOpen] = useState(false);
  const [selectedUser, setSelectedUser] = useState<ApiUser | null>(null);
  const [deleteTarget, setDeleteTarget] = useState<ApiUser | null>(null);
  const [isSaving, setIsSaving] = useState(false);
  const [formError, setFormError] = useState('');
  const [formData, setFormData] = useState<UserFormData>(EMPTY_FORM);

  const loadUsers = useCallback(async (background = false) => {
    if (background) {
      setIsRefreshing(true);
    } else {
      setIsLoading(true);
    }
    try {
      const data = await usersService.listUsers();
      setUsers(data);
      setError('');
    } catch (err) {
      setError(getErrorMessage(err));
    } finally {
      setIsLoading(false);
      setIsRefreshing(false);
    }
  }, []);

  useEffect(() => {
    void loadUsers();
  }, [loadUsers]);

  const openCreateDialog = () => {
    setSelectedUser(null);
    setFormData(EMPTY_FORM);
    setFormError('');
    setDialogOpen(true);
  };

  const openEditDialog = (user: ApiUser) => {
    setSelectedUser(user);
    setFormData({
      username: user.username,
      email: user.email,
      full_name: user.full_name || '',
      password: '',
      role: user.is_superuser ? 'Admin' : 'User',
      is_active: user.is_active,
    });
    setFormError('');
    setDialogOpen(true);
  };

  const handleSubmit = async () => {
    if (!formData.username.trim() || !formData.email.trim()) {
      setFormError('Username and email are required');
      return;
    }
    if (!selectedUser && formData.password.length < 8) {
      setFormError('Password must be at least 8 characters');
      return;
    }

    setIsSaving(true);
    setFormError('');
    try {
      if (selectedUser) {
        const payload: UpdateUserPayload = {
          username: formData.username.trim(),
          email: formData.email.trim(),
          full_name: formData.full_name.trim() || null,
          is_superuser: formData.role === 'Admin',
          is_active: formData.is_active,
        };
        if (formData.password) {
          payload.password = formData.password;
        }
        await usersService.updateUser(selectedUser.id, payload);
        enqueueSnackbar('User updated', { variant: 'success' });
      } else {
        const payload: CreateUserPayload = {
          username: formData.username.trim(),
          email: formData.email.trim(),
          full_name: formData.full_name.trim() || null,
          password: formData.password,
          is_superuser: formData.role === 'Admin',
          is_active: formData.is_active,
        };
        await usersService.createUser(payload);
        enqueueSnackbar('User created', { variant: 'success' });
      }
      setDialogOpen(false);
      await loadUsers(true);
    } catch (err) {
      setFormError(getErrorMessage(err));
    } finally {
      setIsSaving(false);
    }
  };

  const handleToggleStatus = async (user: ApiUser) => {
    try {
      await usersService.updateUser(user.id, { is_active: !user.is_active });
      enqueueSnackbar(`User ${user.is_active ? 'deactivated' : 'activated'}`, {
        variant: 'success',
      });
      await loadUsers(true);
    } catch (err) {
      enqueueSnackbar(getErrorMessage(err), { variant: 'error' });
    }
  };

  const handleDelete = async () => {
    if (!deleteTarget) {
      return;
    }
    try {
      await usersService.deleteUser(deleteTarget.id);
      enqueueSnackbar('User deleted', { variant: 'success' });
      setDeleteTarget(null);
      await loadUsers(true);
    } catch (err) {
      enqueueSnackbar(getErrorMessage(err), { variant: 'error' });
    }
  };

  if (isLoading) {
    return (
      <Box display="flex" justifyContent="center" alignItems="center" minHeight="400px" role="status">
        <CircularProgress />
      </Box>
    );
  }

  return (
    <>
      <Helmet>
        <title>User Management - AI Safety Governance Platform</title>
        <meta
          name="description"
          content="Manage users, roles, and permissions for the AI Safety Governance Platform"
        />
      </Helmet>

      <Box sx={{ pb: 4 }}>
        <Box display="flex" justifyContent="space-between" alignItems="center" mb={4} gap={2}>
          <Typography variant="h4" component="h1">
            User Management
          </Typography>
          <Box display="flex" alignItems="center" gap={1}>
            <Tooltip title="Refresh users">
              <IconButton
                onClick={() => void loadUsers(true)}
                disabled={isRefreshing}
                aria-label="Refresh users"
              >
                <RefreshIcon />
              </IconButton>
            </Tooltip>
            <Button variant="contained" startIcon={<AddIcon />} onClick={openCreateDialog}>
              Add User
            </Button>
          </Box>
        </Box>

        {error && (
          <Alert severity="error" sx={{ mb: 2 }} action={
            <Button color="inherit" size="small" onClick={() => void loadUsers()}>
              Retry
            </Button>
          }>
            {error}
          </Alert>
        )}

        <TableContainer component={Paper} sx={{ overflowX: 'auto' }}>
          <Table aria-label="Users">
            <TableHead>
              <TableRow>
                <TableCell>User</TableCell>
                <TableCell>Role</TableCell>
                <TableCell>Status</TableCell>
                <TableCell>Created</TableCell>
                <TableCell align="right">Actions</TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {users.length === 0 ? (
                <TableRow>
                  <TableCell colSpan={5} align="center">
                    <Typography variant="body2" color="text.secondary" sx={{ py: 3 }}>
                      No users found. Create the first user to get started.
                    </Typography>
                  </TableCell>
                </TableRow>
              ) : (
                users.map((user) => {
                  const displayName = user.full_name || user.username;
                  return (
                    <TableRow key={user.id} hover>
                      <TableCell>
                        <Box display="flex" alignItems="center" gap={2}>
                          <Avatar sx={{ bgcolor: theme.palette.primary.main }}>
                            {displayName.charAt(0).toUpperCase()}
                          </Avatar>
                          <Box>
                            <Typography variant="body1">{displayName}</Typography>
                            <Typography variant="body2" color="text.secondary">
                              {user.email}
                            </Typography>
                            <Typography variant="caption" color="text.secondary">
                              @{user.username}
                            </Typography>
                          </Box>
                        </Box>
                      </TableCell>
                      <TableCell>
                        <Chip
                          label={user.is_superuser ? 'Admin' : 'User'}
                          color={user.is_superuser ? 'error' : 'default'}
                          size="small"
                        />
                      </TableCell>
                      <TableCell>
                        <Chip
                          icon={user.is_active ? <CheckCircleIcon /> : <WarningIcon />}
                          label={user.is_active ? 'Active' : 'Inactive'}
                          color={user.is_active ? 'success' : 'warning'}
                          size="small"
                        />
                      </TableCell>
                      <TableCell>{format(new Date(user.created_at), 'MMM d, yyyy')}</TableCell>
                      <TableCell align="right">
                        <Tooltip title="Edit user">
                          <IconButton
                            size="small"
                            onClick={() => openEditDialog(user)}
                            aria-label={`Edit ${user.username}`}
                            sx={{ mr: 1 }}
                          >
                            <EditIcon />
                          </IconButton>
                        </Tooltip>
                        <Tooltip
                          title={`${user.is_active ? 'Deactivate' : 'Activate'} user`}
                        >
                          <IconButton
                            size="small"
                            onClick={() => void handleToggleStatus(user)}
                            aria-label={`${user.is_active ? 'Deactivate' : 'Activate'} ${user.username}`}
                            sx={{ mr: 1 }}
                          >
                            <BlockIcon />
                          </IconButton>
                        </Tooltip>
                        <Tooltip title="Delete user">
                          <IconButton
                            size="small"
                            onClick={() => setDeleteTarget(user)}
                            aria-label={`Delete ${user.username}`}
                            color="error"
                          >
                            <DeleteIcon />
                          </IconButton>
                        </Tooltip>
                      </TableCell>
                    </TableRow>
                  );
                })
              )}
            </TableBody>
          </Table>
        </TableContainer>

        <Dialog open={dialogOpen} onClose={() => setDialogOpen(false)} maxWidth="sm" fullWidth>
          <DialogTitle>{selectedUser ? 'Edit User' : 'Add New User'}</DialogTitle>
          <DialogContent>
            {formError && (
              <Alert severity="error" sx={{ mt: 1, mb: 1 }}>
                {formError}
              </Alert>
            )}
            <Box sx={{ pt: 1, display: 'flex', flexDirection: 'column', gap: 2 }}>
              <TextField
                fullWidth
                required
                label="Username"
                value={formData.username}
                onChange={(e) => setFormData({ ...formData, username: e.target.value })}
                disabled={isSaving}
              />
              <TextField
                fullWidth
                required
                label="Email"
                type="email"
                value={formData.email}
                onChange={(e) => setFormData({ ...formData, email: e.target.value })}
                disabled={isSaving}
              />
              <TextField
                fullWidth
                label="Full Name"
                value={formData.full_name}
                onChange={(e) => setFormData({ ...formData, full_name: e.target.value })}
                disabled={isSaving}
              />
              <TextField
                fullWidth
                label={selectedUser ? 'New Password (optional)' : 'Password'}
                type="password"
                value={formData.password}
                onChange={(e) => setFormData({ ...formData, password: e.target.value })}
                helperText="At least 8 characters with uppercase, lowercase, number and special character"
                disabled={isSaving}
              />
              <FormControl fullWidth>
                <InputLabel id="role-label">Role</InputLabel>
                <Select
                  labelId="role-label"
                  label="Role"
                  value={formData.role}
                  onChange={(e) =>
                    setFormData({ ...formData, role: e.target.value as 'Admin' | 'User' })
                  }
                  disabled={isSaving}
                >
                  <MenuItem value="User">User</MenuItem>
                  <MenuItem value="Admin">Admin</MenuItem>
                </Select>
              </FormControl>
              <FormControlLabel
                control={
                  <Switch
                    checked={formData.is_active}
                    onChange={(e) => setFormData({ ...formData, is_active: e.target.checked })}
                    disabled={isSaving}
                  />
                }
                label="Active"
              />
            </Box>
          </DialogContent>
          <DialogActions>
            <Button onClick={() => setDialogOpen(false)} disabled={isSaving}>
              Cancel
            </Button>
            <Button variant="contained" onClick={() => void handleSubmit()} disabled={isSaving}>
              {isSaving ? 'Saving...' : selectedUser ? 'Save Changes' : 'Add User'}
            </Button>
          </DialogActions>
        </Dialog>

        <Dialog open={Boolean(deleteTarget)} onClose={() => setDeleteTarget(null)}>
          <DialogTitle>Delete user?</DialogTitle>
          <DialogContent>
            <DialogContentText>
              This permanently deletes {deleteTarget?.email}. This action cannot be undone.
            </DialogContentText>
          </DialogContent>
          <DialogActions>
            <Button onClick={() => setDeleteTarget(null)}>Cancel</Button>
            <Button color="error" variant="contained" onClick={() => void handleDelete()}>
              Delete
            </Button>
          </DialogActions>
        </Dialog>
      </Box>
    </>
  );
};

export default Users;
