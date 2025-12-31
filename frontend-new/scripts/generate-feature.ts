#!/usr/bin/env npx ts-node
/**
 * Feature Generator - Scaffold new feature modules
 *
 * Usage:
 *   npx ts-node scripts/generate-feature.ts <feature-name>
 *
 * Example:
 *   npx ts-node scripts/generate-feature.ts workflows
 *   npx ts-node scripts/generate-feature.ts notifications
 *
 * This will:
 * 1. Copy the _template directory to src/features/<feature-name>
 * 2. Replace all {{FEATURE_NAME}} placeholders with the actual name
 * 3. Rename files with {{FEATURE_NAME_PASCAL}} in their names
 */

import * as fs from 'fs';
import * as path from 'path';

const TEMPLATE_DIR = path.join(__dirname, '../src/features/_template');
const FEATURES_DIR = path.join(__dirname, '../src/features');

/**
 * Convert kebab-case to PascalCase
 */
function toPascalCase(str: string): string {
  return str
    .split(/[-_]/)
    .map((word) => word.charAt(0).toUpperCase() + word.slice(1).toLowerCase())
    .join('');
}

/**
 * Convert kebab-case to camelCase
 */
function toCamelCase(str: string): string {
  const pascal = toPascalCase(str);
  return pascal.charAt(0).toLowerCase() + pascal.slice(1);
}

/**
 * Replace placeholders in file content
 */
function replacePlaceholders(content: string, featureName: string): string {
  const pascalName = toPascalCase(featureName);
  const camelName = toCamelCase(featureName);

  return content
    .replace(/\{\{FEATURE_NAME\}\}/g, featureName)
    .replace(/\{\{FEATURE_NAME_PASCAL\}\}/g, pascalName)
    .replace(/\{\{FEATURE_NAME_CAMEL\}\}/g, camelName);
}

/**
 * Replace placeholders in file path
 */
function replacePathPlaceholders(filePath: string, featureName: string): string {
  const pascalName = toPascalCase(featureName);
  return filePath.replace(/\{\{FEATURE_NAME_PASCAL\}\}/g, pascalName);
}

/**
 * Recursively copy directory with placeholder replacement
 */
function copyDirectory(src: string, dest: string, featureName: string): void {
  // Create destination directory
  if (!fs.existsSync(dest)) {
    fs.mkdirSync(dest, { recursive: true });
  }

  // Read source directory
  const entries = fs.readdirSync(src, { withFileTypes: true });

  for (const entry of entries) {
    const srcPath = path.join(src, entry.name);
    const destName = replacePathPlaceholders(entry.name, featureName);
    const destPath = path.join(dest, destName);

    if (entry.isDirectory()) {
      // Recursively copy subdirectory
      copyDirectory(srcPath, destPath, featureName);
    } else {
      // Read file, replace placeholders, write to destination
      let content = fs.readFileSync(srcPath, 'utf8');
      content = replacePlaceholders(content, featureName);
      fs.writeFileSync(destPath, content);
    }
  }
}

/**
 * Main function
 */
function generateFeature(featureName: string): void {
  // Validate feature name
  if (!featureName || !/^[a-z][a-z0-9-]*$/.test(featureName)) {
    console.error('Error: Feature name must be lowercase, start with a letter, and use hyphens for spaces.');
    console.error('Example: workflows, data-sources, ai-insights');
    process.exit(1);
  }

  const featureDir = path.join(FEATURES_DIR, featureName);

  // Check if feature already exists
  if (fs.existsSync(featureDir)) {
    console.error(`Error: Feature "${featureName}" already exists at ${featureDir}`);
    process.exit(1);
  }

  // Check if template exists
  if (!fs.existsSync(TEMPLATE_DIR)) {
    console.error(`Error: Template directory not found at ${TEMPLATE_DIR}`);
    process.exit(1);
  }

  console.log(`Creating feature: ${featureName}`);
  console.log(`  PascalCase: ${toPascalCase(featureName)}`);
  console.log(`  camelCase: ${toCamelCase(featureName)}`);
  console.log('');

  // Copy template with placeholder replacement
  copyDirectory(TEMPLATE_DIR, featureDir, featureName);

  console.log(`Feature created at: ${featureDir}`);
  console.log('');
  console.log('Next steps:');
  console.log(`  1. Update src/features/${featureName}/hooks/index.ts with actual SDK methods`);
  console.log(`  2. Add feature routes to App.tsx or FeatureRegistry`);
  console.log(`  3. Implement feature-specific components`);
  console.log(`  4. Add navigation entry if needed`);
  console.log('');
  console.log('Files created:');

  // List created files
  const listFiles = (dir: string, prefix: string = ''): void => {
    const entries = fs.readdirSync(dir, { withFileTypes: true });
    for (const entry of entries) {
      const entryPath = path.join(dir, entry.name);
      if (entry.isDirectory()) {
        console.log(`  ${prefix}${entry.name}/`);
        listFiles(entryPath, prefix + '  ');
      } else {
        console.log(`  ${prefix}${entry.name}`);
      }
    }
  };

  listFiles(featureDir);
}

// CLI execution
const featureName = process.argv[2];

if (!featureName) {
  console.log('Feature Generator');
  console.log('');
  console.log('Usage:');
  console.log('  npx ts-node scripts/generate-feature.ts <feature-name>');
  console.log('');
  console.log('Examples:');
  console.log('  npx ts-node scripts/generate-feature.ts workflows');
  console.log('  npx ts-node scripts/generate-feature.ts data-sources');
  console.log('  npx ts-node scripts/generate-feature.ts ai-insights');
  process.exit(1);
}

generateFeature(featureName);
