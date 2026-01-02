# Bug List

## 2026-01-02

### Frontend White Screen - Environment Variables Not Injected
- **Error**: `Cannot read properties of undefined (reading 'VITE_API_BASE_URL')` at env.ts:71
- **Root Cause**: Rspack (not Vite) doesn't auto-inject `import.meta.env` - needs explicit DefinePlugin config
- **Why Blocking**: Code uses `import.meta.env.VITE_*` but bundler wasn't replacing these at build time
- **Fix**:
  1. Created `.env` from `.env.example`
  2. Added `dotenv` loading to `rspack.config.js`
  3. Configured `rspack.DefinePlugin` to replace all `import.meta.env.*` references
  4. Moved DefinePlugin to first position in plugins array
  5. Clear browser cache (Cmd+Shift+R) after build
- **Files**: `rspack.config.js`, `.env`
- **Note**: Browser hard refresh required after config changes
- **Status**: ✅ Resolved
