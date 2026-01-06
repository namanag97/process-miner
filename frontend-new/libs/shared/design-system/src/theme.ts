import type { ThemeConfig } from 'antd';

/**
 * Design Tokens - Based on Design System Doc
 * All spacing, colors, typography from documented specs
 */
export const tokens = {
  // Primary Palette
  colors: {
    primary: {
      50: '#F0F7FF',
      100: '#E0EFFF',
      200: '#BADAFF',
      400: '#4D96FF',
      500: '#0F52FF',  // Precision Cobalt
      600: '#0041E6',
      700: '#0031B3',
    },
    success: {
      50: '#ECFDF5',
      100: '#D1FAE5',
      200: '#A7F3D0',
      300: '#6EE7B7',
      500: '#10B981',
      600: '#059669',
      700: '#047857',
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
      200: '#FECACA',
      300: '#FCA5A5',
      500: '#EF4444',
      600: '#DC2626',
      700: '#B91C1C',
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
    // Status colors for object lifecycle states
    status: {
      pending: '#FCD34D',    // Awaiting action
      running: '#60A5FA',    // In progress
      completed: '#34D399',  // Successfully done
      failed: '#F87171',     // Error state
      stale: '#9CA3AF',      // Outdated/needs refresh
      active: '#10B981',     // Currently active
      archived: '#6B7280',   // Archived/inactive
      draft: '#A78BFA',      // Not yet activated
    },
    // Severity colors for alerts and deviations
    severity: {
      critical: '#DC2626',   // Immediate action required
      high: '#F59E0B',       // High priority
      medium: '#3B82F6',     // Normal priority
      low: '#10B981',        // Low priority
      info: '#6B7280',       // Informational
    },
    // Process node type colors for DFG/BPMN visualization
    nodeType: {
      activity: '#0F52FF',   // Standard activity
      gateway: '#F59E0B',    // Decision point
      event: '#10B981',      // Start/end/intermediate event
      placeholder: '#D1D5DB',// Unknown/pending
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
    none: 0,
    xs: 2,   // Architectural precision
    sm: 4,
    md: 8,   // Standard container
    lg: 16,  // Page surface
    xl: 24,
    full: 9999,
  },
  // Typography
  fontSize: {
    xs: 11,
    sm: 12,
    base: 14,
    md: 18.66,   // 14 * 1.333
    lg: 24.88,   // 18.66 * 1.333
    xl: 33.17,   // 24.88 * 1.333
    '2xl': 44.22,
    '3xl': 58.95,
    '4xl': 78.58,
    '5xl': 104.75,
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
  // Easing Curves
  easing: {
    default: 'cubic-bezier(0.4, 0, 0.2, 1)',
    in: 'cubic-bezier(0.4, 0, 1, 1)',
    out: 'cubic-bezier(0, 0, 0.2, 1)',
    inOut: 'cubic-bezier(0.4, 0, 0.2, 1)',
    bounce: 'cubic-bezier(0.68, -0.55, 0.265, 1.55)',
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
    controlHeight: 40,   // More breathing room
    controlHeightLG: 48,
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
      fontWeight: 600,
      primaryShadow: '0 4px 12px rgba(15, 82, 255, 0.2)',
      borderRadius: tokens.radius.xs, // Precise sharp buttons
    },
    Card: {
      paddingLG: tokens.spacing[6],
      borderRadiusLG: tokens.radius.lg,
      boxShadow: tokens.shadow.md,
    },
    Input: {
      paddingInline: tokens.spacing[4],
      borderRadius: tokens.radius.xs,
    },
    Table: {
      borderRadius: tokens.radius.none,
      fontSize: tokens.fontSize.base,
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
