'use client';

import { useEffect, useCallback } from 'react';
import { createLogger } from '@/lib/debug-logger';

const logger = createLogger('keyboard-shortcuts');

type KeyboardShortcut = {
    key: string;
    ctrl?: boolean;
    meta?: boolean;
    shift?: boolean;
    alt?: boolean;
    description: string;
    action: () => void;
};

interface UseKeyboardShortcutsOptions {
    enabled?: boolean;
}

/**
 * Hook to register keyboard shortcuts
 */
export function useKeyboardShortcuts(
    shortcuts: KeyboardShortcut[],
    options: UseKeyboardShortcutsOptions = {}
) {
    const { enabled = true } = options;

    const handleKeyDown = useCallback(
        (event: KeyboardEvent) => {
            if (!enabled) return;

            // Don't trigger shortcuts when typing in input fields
            const target = event.target as HTMLElement;
            if (
                target.tagName === 'INPUT' ||
                target.tagName === 'TEXTAREA' ||
                target.isContentEditable
            ) {
                return;
            }

            for (const shortcut of shortcuts) {
                const metaMatch = shortcut.meta ? event.metaKey : !event.metaKey;
                const ctrlMatch = shortcut.ctrl ? event.ctrlKey : !event.ctrlKey;
                const shiftMatch = shortcut.shift ? event.shiftKey : !event.shiftKey;
                const altMatch = shortcut.alt ? event.altKey : !event.altKey;
                const keyMatch = event.key.toLowerCase() === shortcut.key.toLowerCase();

                // For Mac, treat Cmd as Ctrl equivalent
                const isMac = navigator.platform.toUpperCase().indexOf('MAC') >= 0;
                const cmdCtrlMatch = isMac
                    ? (shortcut.ctrl || shortcut.meta) ? event.metaKey : !event.metaKey
                    : (shortcut.ctrl || shortcut.meta) ? event.ctrlKey : !event.ctrlKey;

                if (
                    keyMatch &&
                    (shortcut.ctrl || shortcut.meta ? cmdCtrlMatch : (metaMatch && ctrlMatch)) &&
                    shiftMatch &&
                    altMatch
                ) {
                    event.preventDefault();
                    logger.info(`⌨️ Shortcut triggered: ${shortcut.description}`);
                    shortcut.action();
                    break;
                }
            }
        },
        [shortcuts, enabled]
    );

    useEffect(() => {
        if (!enabled) return;

        document.addEventListener('keydown', handleKeyDown);
        return () => document.removeEventListener('keydown', handleKeyDown);
    }, [handleKeyDown, enabled]);
}

/**
 * Common app shortcuts - use with useKeyboardShortcuts
 */
export function useAppShortcuts({
    onToggleLogPanel,
    onOpenExport,
    onEscape,
}: {
    onToggleLogPanel?: () => void;
    onOpenExport?: () => void;
    onEscape?: () => void;
}) {
    const shortcuts: KeyboardShortcut[] = [];

    if (onToggleLogPanel) {
        shortcuts.push({
            key: 'l',
            ctrl: true,
            description: 'Toggle log panel',
            action: onToggleLogPanel,
        });
    }

    if (onOpenExport) {
        shortcuts.push({
            key: 'e',
            ctrl: true,
            description: 'Open export menu',
            action: onOpenExport,
        });
    }

    if (onEscape) {
        shortcuts.push({
            key: 'Escape',
            description: 'Close modals/panels',
            action: onEscape,
        });
    }

    useKeyboardShortcuts(shortcuts);
}
