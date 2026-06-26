import { createTheme } from '@mui/material/styles';

export const theme = createTheme({
  palette: {
    mode: 'dark',
    primary: { main: '#c2f23a', contrastText: '#0a0c08' },
    secondary: { main: '#86efac' },
    background: { default: '#0a0c0a', paper: '#141815' },
    error: { main: '#ff6b6b' },
    success: { main: '#86efac' },
    warning: { main: '#e0c84a' },
    text: { primary: '#eef3ea', secondary: '#8b948a' },
    divider: '#242a20',
  },
  shape: { borderRadius: 12 },
  typography: {
    fontFamily: 'system-ui, -apple-system, "Segoe UI", Roboto, sans-serif',
  },
  components: {
    MuiPaper: { styleOverrides: { root: { backgroundImage: 'none' } } },
    MuiButton: {
      defaultProps: { disableElevation: true },
      styleOverrides: { root: { fontWeight: 600 } },
    },
  },
});
