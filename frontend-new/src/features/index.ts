/**
 * Feature Registration Index
 * 
 * Import each feature module to trigger auto-registration via FeatureRegistry.
 * Order matters for route precedence (first match wins).
 * 
 * Adding a new feature:
 * 1. Create feature in features/{feature-name}/
 * 2. Add FeatureRegistry.register() call in index.ts
 * 3. Add import here
 */

// Core workspace features
import './projects';
import './upload-wizard';

// Process analysis features
import './explorer';
import './discovery';
import './kpi';
import './analytics';
import './ai';

// Platform features (settings, notifications, etc.)
import './platform';

console.debug('[Features] All features registered');
