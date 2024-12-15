import { BrowserRouter, useLocation } from 'react-router-dom';
import { ThemeProvider, CssBaseline } from '@mui/material';
import { SnackbarProvider } from 'notistack';
import { createTheme } from '@mui/material/styles';
import AppRoutes from './routes';
import Layout from './components/Layout';

// Create theme instance
const theme = createTheme({
  palette: {
    primary: {
      main: '#1976d2',
      light: '#42a5f5',
      dark: '#1565c0',
    },
    secondary: {
      main: '#9c27b0',
      light: '#ba68c8',
      dark: '#7b1fa2',
    },
    background: {
      default: '#f5f5f5',
      paper: '#ffffff',
    },
  },
  components: {
    MuiButton: {
      styleOverrides: {
        root: {
          textTransform: 'none',
        },
      },
    },
    MuiPaper: {
      styleOverrides: {
        root: {
          boxShadow: '0 2px 4px rgba(0,0,0,0.1)',
        },
      },
    },
  },
});

// Wrapper component to conditionally render Layout
const AppContent = () => {
  const location = useLocation();
  const publicPaths = ['/', '/login', '/register', '/unauthorized'];
  const isPublicPath = publicPaths.includes(location.pathname);

  return isPublicPath ? (
    <AppRoutes />
  ) : (
    <Layout>
      <AppRoutes />
    </Layout>
  );
};

function App() {
  return (
    <ThemeProvider theme={theme}>
      <CssBaseline />
      <SnackbarProvider 
        maxSnack={3} 
        anchorOrigin={{
          vertical: 'bottom',
          horizontal: 'right',
        }}
      >
        <BrowserRouter>
          <AppContent />
        </BrowserRouter>
      </SnackbarProvider>
    </ThemeProvider>
  );
}

export default App;
