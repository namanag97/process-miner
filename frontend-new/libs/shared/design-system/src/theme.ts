import type { ThemeConfig } from 'antd';

/**
 * Design Tokens - Based on Design System Doc
 * All spacing, colors, typography from documented specs
 */
export const tokens = {
  // Primary Palette
  colors: {
    primary: {
      50: '#EBF5FF',
      100: '#D6EBFF',
      200: '#B3D7FF',
      400: '#4D9FFF',
      500: '#2563EB',  // Main brand blue
      600: '#1D4ED8',
      700: '#1E40AF',
    },
    success: {
      50: '#ECFDF5',
      100: '#D1FAE5',
      500: '#10B981',
      600: '#059669',
    },
    warning: {
      50: '#FFFBEB',
      100: '#FEF3C7',
      500: '#F59E0B',
      600: '#D97706',
    },
    error: {
      50: '#FEF2F2',
      100: '#FEE2E2',
      500: '#EF4444',
      600: '#DC2626',
    },
    info: {
      50: '#EFF6FF',
      500: '#3B82F6',
    },
    neutral: {
      0: '#FFFFFF',
      50: '#F9FAFB',
      100: '#F3F4F6',
      200: '#E5E7EB',
      300: '#D1D5DB',
      400: '#9CA3AF',
      500: '#6B7280',
      600: '#4B5563',
      700: '#374151',
      800: '#1F2937',
      900: '#111827',
      950: '#030712',
    },
    surface: {
      page: '#FFFFFF',
      sidebar: '#F3F4F6',
      card: '#FFFFFF',
      cardHover: '#F9FAFB',
      dark: '#1A1A2E',
    },
  },
  // Spacing (4px base unit)
  spacing: {
    0: 0,
    1: 4,
    2: 8,
    3: 12,
    4: 16,
    5: 20,
    6: 24,
    8: 32,
    10: 40,
    12: 48,
    16: 64,
  },
  // Border Radius
  radius: {
    sm: 4,
    md: 6,
    lg: 8,
    xl: 12,
    full: 9999,
  },
  // Typography
  fontSize: {
    xs: 11,
    sm: 12,
    base: 14,
    md: 15,
    lg: 16,
    xl: 18,
    '2xl': 20,
    '3xl': 24,
    '4xl': 32,
    '5xl': 40,
  },
  fontWeight: {
    regular: 400,
    medium: 500,
    semibold: 600,
    bold: 700,
  },
  // Shadows
  shadow: {
    xs: '0 1px 2px rgba(0, 0, 0, 0.04)',
    sm: '0 1px 3px rgba(0, 0, 0, 0.08)',
    md: '0 4px 6px -1px rgba(0, 0, 0, 0.1)',
    lg: '0 10px 15px -3px rgba(0, 0, 0, 0.1)',
    xl: '0 20px 25px -5px rgba(0, 0, 0, 0.15)',
    focus: '0 0 0 3px rgba(37, 99, 235, 0.2)',
  },
  // Durations
  duration: {
    fast: 100,
    normal: 150,
    moderate: 200,
    slow: 300,
  },
  // Layout
  sidebar: {
    width: 240,
    collapsedWidth: 64,
  },
} as const;

export type LuminaTokens = typeof tokens;

/**
 * Ant Design Theme Configuration - Light Theme
 * Uses compact algorithm for high-density enterprise UI
 */
export const luminaTheme: ThemeConfig = {
  token: {
    // Colors
    colorPrimary: tokens.colors.primary[500],
    colorSuccess: tokens.colors.success[500],
    colorWarning: tokens.colors.warning[500],
    colorError: tokens.colors.error[500],
    colorInfo: tokens.colors.info[500],
    
    // Typography
    fontFamily: '"Inter", -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif',
    fontSize: 14,
    
    // Border
    borderRadius: tokens.radius.md,
    borderRadiusLG: tokens.radius.lg,
    borderRadiusSM: tokens.radius.sm,
    
    // Spacing
    padding: tokens.spacing[4],
    paddingLG: tokens.spacing[6],
    paddingSM: tokens.spacing[3],
    paddingXS: tokens.spacing[2],
    
    // Layout
    controlHeight: 36,
    controlHeightLG: 40,
    controlHeightSM: 32,
  },
  components: {
    Layout: {
      siderBg: tokens.colors.surface.sidebar,
      headerBg: tokens.colors.neutral[0],
      bodyBg: tokens.colors.surface.page,
    },
    Menu: {
      itemBg: 'transparent',
      itemSelectedBg: tokens.colors.primary[100],
      itemSelectedColor: tokens.colors.primary[700],
      itemHoverBg: tokens.colors.neutral[200],
    },
    Button: {
      fontWeight: 500,
      primaryShadow: tokens.shadow.xs,
    },
    Card: {
      paddingLG: tokens.spacing[4],
      borderRadiusLG: tokens.radius.lg,
    },
    Input: {
      paddingInline: tokens.spacing[3],
    },
  },
};

/**
 * Dark Theme (Optional)
 */
export const luminaDarkTheme: ThemeConfig = {
  ...luminaTheme,
  token: {
    ...luminaTheme.token,
    colorBgContainer: tokens.colors.neutral[900],
    colorBgLayout: tokens.colors.neutral[950],
    colorText: tokens.colors.neutral[100],
  },
};
