/**
 * Jest Configuration
 *
 * @see https://jestjs.io/docs/configuration
 */

module.exports = {
  displayName: 'frontend-new',
  preset: './jest.preset.js',
  testEnvironment: 'jsdom',
  transform: {
    '^(?!.*\\.(js|jsx|ts|tsx|css|json)$)': '@nx/react/plugins/jest',
    '^.+\\.[tj]sx?$': ['babel-jest', { presets: ['@nx/react/babel'] }],
  },
  moduleFileExtensions: ['ts', 'tsx', 'js', 'jsx'],
  coverageDirectory: './coverage/frontend-new',
  testMatch: [
    '<rootDir>/src/**/__tests__/**/*.[jt]s?(x)',
    '<rootDir>/src/**/*(*.)@(spec|test).[jt]s?(x)',
  ],
  setupFilesAfterEnv: ['<rootDir>/src/test/setup.ts'],
  moduleNameMapper: {
    // Path aliases matching tsconfig
    '^@/(.*)$': '<rootDir>/src/$1',
    '^@lumina/design-system$': '<rootDir>/libs/shared/design-system/src/index.ts',
    // Handle CSS modules
    '\\.css$': 'identity-obj-proxy',
    // Handle static assets
    '\\.(jpg|jpeg|png|gif|svg)$': '<rootDir>/src/test/__mocks__/fileMock.js',
  },
  collectCoverageFrom: [
    'src/**/*.{ts,tsx}',
    '!src/**/*.d.ts',
    '!src/**/*.stories.{ts,tsx}',
    '!src/**/index.{ts,tsx}',
    '!src/test/**/*',
    '!src/main.tsx',
  ],
  coverageThreshold: {
    global: {
      statements: 30,
      branches: 20,
      functions: 30,
      lines: 30,
    },
  },
  testTimeout: 10000,
  verbose: true,
};
