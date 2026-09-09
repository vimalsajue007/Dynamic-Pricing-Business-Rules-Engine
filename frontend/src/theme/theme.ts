import { createTheme } from "@mui/material/styles";

/**
 * "Nocturne Violet" — an elite, dark, editorial admin theme built for a
 * rules-and-numbers product. Deep aubergine-black surfaces, a single
 * saturated violet accent, quiet hairline borders instead of drop shadows,
 * and a display/body type pairing (Space Grotesk + Inter) that gives the
 * numbers and rule names room to read clearly.
 */

const violet = {
  50: "#F5F0FF",
  100: "#E9DEFF",
  200: "#D2BBFF",
  300: "#B594FA",
  400: "#9C6EF5",
  500: "#8B5CF6",
  600: "#7C3AED",
  700: "#6D28D9",
  800: "#5B21B6",
  900: "#3E1671",
};

const bg = {
  base: "#0D0A18",
  surface: "#141024",
  surfaceAlt: "#1A1530",
  border: "#2A2246",
  borderStrong: "#3D3164",
};

export const theme = createTheme({
  palette: {
    mode: "dark",
    primary: { main: violet[500], light: violet[300], dark: violet[700], contrastText: "#0D0A18" },
    secondary: { main: "#C4B5FD" },
    success: { main: "#34D399" },
    warning: { main: "#FBBF24" },
    error: { main: "#F87171" },
    info: { main: "#7DD3FC" },
    background: { default: bg.base, paper: bg.surface },
    text: { primary: "#F3F0FF", secondary: "#A99FCB" },
    divider: bg.border,
  },
  shape: { borderRadius: 10 },
  typography: {
    fontFamily: '"Inter", -apple-system, BlinkMacSystemFont, sans-serif',
    h1: { fontFamily: '"Space Grotesk", sans-serif', fontWeight: 600, letterSpacing: "-0.02em" },
    h2: { fontFamily: '"Space Grotesk", sans-serif', fontWeight: 600, letterSpacing: "-0.02em" },
    h3: { fontFamily: '"Space Grotesk", sans-serif', fontWeight: 600, letterSpacing: "-0.01em" },
    h4: { fontFamily: '"Space Grotesk", sans-serif', fontWeight: 600, letterSpacing: "-0.01em" },
    h5: { fontFamily: '"Space Grotesk", sans-serif', fontWeight: 600 },
    h6: { fontFamily: '"Space Grotesk", sans-serif', fontWeight: 600 },
    button: { textTransform: "none", fontWeight: 600 },
    body2: { color: "#A99FCB" },
  },
  components: {
    MuiCssBaseline: {
      styleOverrides: {
        body: {
          backgroundImage:
            "radial-gradient(circle at 15% 0%, rgba(139,92,246,0.10), transparent 40%), radial-gradient(circle at 85% 10%, rgba(124,58,237,0.08), transparent 35%)",
          backgroundAttachment: "fixed",
        },
        "::selection": { background: violet[600], color: "#fff" },
      },
    },
    MuiPaper: {
      styleOverrides: {
        root: {
          backgroundImage: "none",
          border: `1px solid ${bg.border}`,
        },
      },
    },
    MuiCard: {
      styleOverrides: {
        root: {
          backgroundColor: bg.surface,
          border: `1px solid ${bg.border}`,
          backgroundImage: "none",
        },
      },
    },
    MuiButton: {
      styleOverrides: {
        root: { borderRadius: 8, paddingInline: 18 },
        containedPrimary: {
          backgroundImage: `linear-gradient(135deg, ${violet[500]}, ${violet[700]})`,
          boxShadow: "none",
          "&:hover": { backgroundImage: `linear-gradient(135deg, ${violet[400]}, ${violet[600]})`, boxShadow: "none" },
        },
        outlined: { borderColor: bg.borderStrong },
      },
    },
    MuiChip: {
      styleOverrides: {
        root: { borderRadius: 6, fontWeight: 600 },
      },
    },
    MuiTableCell: {
      styleOverrides: {
        root: { borderColor: bg.border },
        head: { color: "#A99FCB", fontWeight: 600, fontSize: "0.75rem", letterSpacing: "0.02em", textTransform: "none" },
      },
    },
    MuiTextField: {
      defaultProps: { size: "small" },
    },
    MuiOutlinedInput: {
      styleOverrides: {
        root: { backgroundColor: "rgba(255,255,255,0.02)" },
        notchedOutline: { borderColor: bg.border },
      },
    },
    MuiDrawer: {
      styleOverrides: {
        paper: { backgroundColor: bg.surface, borderRight: `1px solid ${bg.border}` },
      },
    },
    MuiAppBar: {
      styleOverrides: {
        root: { backgroundColor: "rgba(13,10,24,0.85)", backdropFilter: "blur(10px)", boxShadow: "none", borderBottom: `1px solid ${bg.border}` },
      },
    },
  },
});

export const violetPalette = violet;
export const bgPalette = bg;
