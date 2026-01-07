/**
 * DevConsole Diagnostic - Test logging pipeline
 *
 * This component generates test logs on mount to verify the DevConsole
 * is working properly.
 */

import { useEffect } from 'react';
import { devLog } from '../DevConsole';
import { logAction, logError, logRequest, logResponse } from '@/src/shared/design-system';

export function DevConsoleDiagnostic() {
  useEffect(() => {
    console.log('[DIAGNOSTIC] Running DevConsole diagnostics...');

    // Test 1: Local devLog from DevConsole.tsx
    setTimeout(() => {
      console.log('[DIAGNOSTIC] Test 1: Local devLog.info');
      devLog.info('DIAGNOSTIC', 'Test log from local devLog');
    }, 100);

    // Test 2: Local devLog.action
    setTimeout(() => {
      console.log('[DIAGNOSTIC] Test 2: Local devLog.action');
      devLog.action('DIAGNOSTIC', 'Test action from local devLog');
    }, 200);

    // Test 3: Local devLog.error
    setTimeout(() => {
      console.log('[DIAGNOSTIC] Test 3: Local devLog.error');
      devLog.error('DIAGNOSTIC', 'Test error from local devLog', { testData: 'error context' });
    }, 300);

    // Test 4: Design-system logAction
    setTimeout(() => {
      console.log('[DIAGNOSTIC] Test 4: Design-system logAction');
      logAction('DIAGNOSTIC', 'Test action from design-system', { testData: 'action data' });
    }, 400);

    // Test 5: Design-system logError
    setTimeout(() => {
      console.log('[DIAGNOSTIC] Test 5: Design-system logError');
      logError('DIAGNOSTIC', new Error('Test error from design-system'), { testData: 'error context' });
    }, 500);

    // Test 6: Design-system API logging
    setTimeout(() => {
      console.log('[DIAGNOSTIC] Test 6: Design-system logRequest/logResponse');
      logRequest('GET', '/api/v1/test', { testPayload: 'request data' });

      setTimeout(() => {
        logResponse('GET', '/api/v1/test', 200, 150, { testData: 'response data' });
      }, 100);
    }, 600);

    // Test 7: Simulated error
    setTimeout(() => {
      console.log('[DIAGNOSTIC] Test 7: Throw and catch error');
      try {
        throw new Error('Simulated test error');
      } catch (error) {
        logError('DIAGNOSTIC', error, { context: 'simulated error test' });
      }
    }, 800);

    console.log('[DIAGNOSTIC] All diagnostic tests scheduled');
  }, []);

  return null; // This component doesn't render anything
}
