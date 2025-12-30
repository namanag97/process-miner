import { theme } from 'antd';
import type { ThemeConfig } from 'antd';

/**
 * Celonis-inspired design tokens
 */
export const tokens = {
  // Primary Blue - Celonis brand (updated to match reference)
  colorPrimary: '#0066FF',
  colorPrimaryHover: '#338FFF',
  colorPrimaryActive: '#0052CC',

  // Semantic colors
  colorSuccess: '#36B37E',
  colorWarning: '#FAAD14',
  colorError: '#DE350B',
  colorInfo: '#0066FF',

  // Text colors
  colorText: '#172B4D',
  colorTextSecondary: '#5E6C84',
  colorTextTertiary: '#97A0AF',
  colorTextQuaternary: '#B3BAC5',

  // Background colors
  colorBgLayout: '#F4F5F7',
  colorBgContainer: '#FFFFFF',
  colorBgElevated: '#FFFFFF',
  colorBgSpotlight: '#FAFBFC',

  // Border colors
  colorBorder: '#DFE1E6',
  colorBorderSecondary: '#EBECF0',

  // Typography
  fontFamily: 'Inter, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif',
  fontSize: 14,
  fontSizeSM: 12,
  fontSizeLG: 16,
  fontSizeXL: 20,

  // Spacing (compact 8-12-16 scale)
  padding: 16,
  paddingXS: 8,
  paddingSM: 12,
  paddingLG: 24,

  // Border radius (6px default - softer per reference)
  borderRadius: 6,
  borderRadiusSM: 4,
  borderRadiusLG: 12,

  // Shadows
  boxShadow: '0 1px 3px rgba(9, 30, 66, 0.08), 0 1px 2px rgba(9, 30, 66, 0.06)',
  boxShadowSecondary: '0 4px 8px rgba(9, 30, 66, 0.1), 0 2px 4px rgba(9, 30, 66, 0.06)',
} as const;

/**
 * Light theme configuration with compact algorithm for high-density enterprise UIs
 */
export const luminaTheme: ThemeConfig = {
  algorithm: theme.compactAlgorithm,
  token: {
    colorPrimary: tokens.colorPrimary,
    colorSuccess: tokens.colorSuccess,
    colorWarning: tokens.colorWarning,
    colorError: tokens.colorError,
    colorInfo: tokens.colorInfo,
    colorText: tokens.colorText,
    colorTextSecondary: tokens.colorTextSecondary,
    colorTextTertiary: tokens.colorTextTertiary,
    colorBgLayout: tokens.colorBgLayout,
    colorBgContainer: tokens.colorBgContainer,
    colorBorder: tokens.colorBorder,
    colorBorderSecondary: tokens.colorBorderSecondary,
    fontFamily: tokens.fontFamily,
    fontSize: tokens.fontSize,
    borderRadius: tokens.borderRadius,
    padding: tokens.padding,
  },
  components: {
    Layout: {
      headerBg: '#FFFFFF',
      siderBg: '#1B2838',
      bodyBg: tokens.colorBgLayout,
      headerHeight: 56,
    },
    Menu: {
      darkItemBg: '#1B2838',
      darkItemSelectedBg: '#0066FF',
      darkItemHoverBg: 'rgba(255, 255, 255, 0.1)',
      itemHeight: 40,
      iconSize: 16,
    },
    Card: {
      paddingLG: 24,
      headerFontSize: 14,
      borderRadiusLG: 12,
    },
    Table: {
      headerBg: '#FAFBFC',
      rowHoverBg: '#F4F5F7',
      cellPaddingBlock: 8,
      cellPaddingInline: 12,
    },
    Button: {
      controlHeight: 32,
      contentFontSize: 14,
      paddingInline: 12,
    },
    Input: {
      controlHeight: 32,
    },
    Select: {
      controlHeight: 32,
    },
    Statistic: {
      contentFontSize: 24,
      titleFontSize: 12,
    },
  },
};

/**
 * Dark theme configuration
 */
export const luminaDarkTheme: ThemeConfig = {
  algorithm: [theme.compactAlgorithm, theme.darkAlgorithm],
  token: {
    colorPrimary: tokens.colorPrimary,
    colorSuccess: tokens.colorSuccess,
    colorWarning: tokens.colorWarning,
    colorError: tokens.colorError,
    colorInfo: tokens.colorInfo,
    colorBgLayout: '#0A0A0F',
    colorBgContainer: '#141419',
    colorBgElevated: '#1E1E26',
    colorText: '#FAFAFA',
    colorTextSecondary: '#A1A1AA',
    colorTextTertiary: '#71717A',
    colorBorder: '#27272A',
    colorBorderSecondary: '#3F3F46',
    fontFamily: tokens.fontFamily,
    fontSize: tokens.fontSize,
    borderRadius: tokens.borderRadius,
    padding: tokens.padding,
  },
  components: {
    Layout: {
      siderBg: '#0A0A0F',
      bodyBg: '#0A0A0F',
      headerBg: '#141419',
    },
    Menu: {
      darkItemBg: 'transparent',
      darkItemSelectedBg: '#0052CC',
      darkItemHoverBg: 'rgba(255, 255, 255, 0.08)',
    },
    Card: {
      colorBgContainer: '#141419',
    },
    Table: {
      headerBg: '#1E1E26',
      rowHoverBg: '#252530',
    },
  },
};

export type LuminaTokens = typeof tokens;
