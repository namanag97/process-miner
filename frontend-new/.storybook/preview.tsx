import type { Preview } from '@storybook/react';
import { withThemeByClassName } from '@storybook/addon-themes';
import { ConfigProvider, theme as antdTheme } from 'antd';
import { luminaTheme, luminaDarkTheme } from '../libs/shared/design-system/src/theme';
import 'antd/dist/reset.css';

// Global styles for dark mode preview
const darkModeStyles = `
  body.dark {
    background-color: #1a1a2e;
  }
`;

const preview: Preview = {
  parameters: {
    controls: {
      expanded: true,
      matchers: {
        color: /(background|color)$/i,
        date: /Date$/,
      },
      sort: 'requiredFirst',
    },
    docs: {
      toc: true,
    },
    layout: 'padded',
    backgrounds: {
      default: 'light',
      values: [
        { name: 'light', value: '#ffffff' },
        { name: 'dark', value: '#1a1a2e' },
        { name: 'gray', value: '#f3f4f6' },
      ],
    },
    viewport: {
      viewports: {
        mobile: { name: 'Mobile', styles: { width: '375px', height: '667px' } },
        tablet: { name: 'Tablet', styles: { width: '768px', height: '1024px' } },
        desktop: { name: 'Desktop', styles: { width: '1280px', height: '800px' } },
        wide: { name: 'Wide', styles: { width: '1920px', height: '1080px' } },
      },
    },
    a11y: {
      element: '#storybook-root',
      config: {},
      options: {},
      manual: false,
    },
  },
  decorators: [
    // Theme decorator for dark/light mode
    withThemeByClassName({
      themes: {
        light: '',
        dark: 'dark',
      },
      defaultTheme: 'light',
    }),
    // Ant Design ConfigProvider decorator
    (Story, context) => {
      const isDark = context.globals?.theme === 'dark' || context.parameters?.theme === 'dark';
      return (
        <>
          <style>{darkModeStyles}</style>
          <ConfigProvider 
            theme={isDark ? { 
              ...luminaDarkTheme,
              algorithm: antdTheme.darkAlgorithm,
            } : luminaTheme}
          >
            <Story />
          </ConfigProvider>
        </>
      );
    },
  ],
  globalTypes: {
    theme: {
      description: 'Global theme for components',
      toolbar: {
        title: 'Theme',
        icon: 'paintbrush',
        items: [
          { value: 'light', title: 'Light', icon: 'sun' },
          { value: 'dark', title: 'Dark', icon: 'moon' },
        ],
        dynamicTitle: true,
      },
    },
  },
  initialGlobals: {
    theme: 'light',
  },
};

export default preview;
