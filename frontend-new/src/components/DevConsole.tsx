/**
 * DevConsole - In-app developer console for debugging
 *
 * Shows API calls, errors, state changes in real-time.
 * Toggle with Ctrl+Shift+D or click the floating button.
 */
import React, { useState, useEffect, useCallback, useRef } from 'react';
import { Drawer, Badge, Button, Tabs, Tag, Typography, Space, Input, Switch, Tooltip } from 'antd';
import {
  BugOutlined,
  ApiOutlined,
  WarningOutlined,
  InfoCircleOutlined,
  ClearOutlined,
  DownloadOutlined,
  SearchOutlined,
  CloseOutlined,
} from '@ant-design/icons';
import { registerDevConsoleCallback } from '@lumina/design-system';

const { Text } = Typography;

// ============================================
// Helpers
// ============================================

function formatLogData(data: unknown): string {
  if (typeof data === 'string') return data;
  try {
    return JSON.stringify(data, null, 2);
  } catch {
    return String(data);
  }
}

// ============================================
// Types
// ============================================

type LogLevel = 'info' | 'api-req' | 'api-res' | 'error' | 'action' | 'state';

interface LogEntry {
  id: string;
  timestamp: Date;
  level: LogLevel;
  source: string;
  message: string;
  data?: unknown;
  duration?: number;
  status?: number;
}

// ============================================
// Global Log Store
// ============================================

const MAX_LOGS = 500;
let logs: LogEntry[] = [];
const listeners: Set<() => void> = new Set();
let idCounter = 0;

function notifyListeners() {
  listeners.forEach((fn) => fn());
}

export function devConsoleLog(
  level: LogLevel,
  source: string,
  message: string,
  data?: unknown,
  extra?: { duration?: number; status?: number }
) {
  const entry: LogEntry = {
    id: `log-${++idCounter}`,
    timestamp: new Date(),
    level,
    source,
    message,
    data,
    ...extra,
  };

  logs = [entry, ...logs].slice(0, MAX_LOGS);
  notifyListeners();

  // Also log to console in dev
  if (process.env.NODE_ENV === 'development') {
    const style = {
      'info': 'color: #1890ff',
      'api-req': 'color: #722ed1',
      'api-res': 'color: #13c2c2',
      'error': 'color: #ff4d4f',
      'action': 'color: #52c41a',
      'state': 'color: #fa8c16',
    }[level];
    console.log(`%c[${level.toUpperCase()}] ${source}`, style, message, data || '');
  }
}

export function clearDevConsoleLogs() {
  logs = [];
  notifyListeners();
}

// ============================================
// Convenience Loggers
// ============================================

export const devLog = {
  info: (source: string, message: string, data?: unknown) =>
    devConsoleLog('info', source, message, data),

  action: (source: string, message: string, data?: unknown) =>
    devConsoleLog('action', source, message, data),

  state: (source: string, message: string, data?: unknown) =>
    devConsoleLog('state', source, message, data),

  error: (source: string, message: string, data?: unknown) =>
    devConsoleLog('error', source, message, data),

  apiRequest: (method: string, url: string, body?: unknown) =>
    devConsoleLog('api-req', `${method} ${url}`, 'Request sent', body),

  apiResponse: (method: string, url: string, status: number, duration: number, body?: unknown) =>
    devConsoleLog('api-res', `${method} ${url}`, `${status} (${duration}ms)`, body, { duration, status }),
};

// ============================================
// Log Entry Component
// ============================================

const levelConfig: Record<LogLevel, { color: string; icon: React.ReactNode; label: string }> = {
  'info': { color: 'blue', icon: <InfoCircleOutlined />, label: 'INFO' },
  'api-req': { color: 'purple', icon: <ApiOutlined />, label: 'REQ' },
  'api-res': { color: 'cyan', icon: <ApiOutlined />, label: 'RES' },
  'error': { color: 'red', icon: <WarningOutlined />, label: 'ERROR' },
  'action': { color: 'green', icon: <BugOutlined />, label: 'ACTION' },
  'state': { color: 'orange', icon: <InfoCircleOutlined />, label: 'STATE' },
};

function LogEntryRow({ entry }: { entry: LogEntry }) {
  const [expanded, setExpanded] = useState(false);
  const config = levelConfig[entry.level];
  const time = entry.timestamp.toLocaleTimeString('en-US', { hour12: false });

  return (
    <div
      style={{
        padding: '8px 12px',
        borderBottom: '1px solid #f0f0f0',
        cursor: entry.data ? 'pointer' : 'default',
        background: expanded ? '#fafafa' : 'white',
      }}
      onClick={() => entry.data && setExpanded(!expanded)}
    >
      <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
        <Text type="secondary" style={{ fontSize: 11, fontFamily: 'monospace', width: 70 }}>
          {time}
        </Text>
        <Tag color={config.color} style={{ margin: 0, fontSize: 10 }}>
          {config.label}
        </Tag>
        <Text strong style={{ fontSize: 12, minWidth: 120 }}>
          {entry.source}
        </Text>
        <Text
          style={{ fontSize: 12, flex: 1 }}
          ellipsis={{ tooltip: entry.message }}
          type={entry.level === 'error' ? 'danger' : undefined}
        >
          {entry.message}
        </Text>
        {entry.duration && (
          <Tag color={entry.duration > 1000 ? 'red' : entry.duration > 500 ? 'orange' : 'green'}>
            {entry.duration}ms
          </Tag>
        )}
        {entry.status && (
          <Tag color={entry.status >= 400 ? 'red' : entry.status >= 300 ? 'orange' : 'green'}>
            {entry.status}
          </Tag>
        )}
      </div>
      {expanded && entry.data !== undefined && (
        <pre
          style={{
            marginTop: 8,
            marginBottom: 0,
            fontSize: 11,
            maxHeight: 200,
            overflow: 'auto',
            background: '#f5f5f5',
            padding: 8,
            borderRadius: 4,
            fontFamily: 'monospace',
            whiteSpace: 'pre-wrap',
            wordBreak: 'break-all',
          }}
        >
          {formatLogData(entry.data)}
        </pre>
      )}
    </div>
  );
}

// ============================================
// DevConsole Component
// ============================================

export function DevConsole() {
  const [open, setOpen] = useState(false);
  const [, forceUpdate] = useState(0);
  const [filter, setFilter] = useState('');
  const [activeTab, setActiveTab] = useState('all');
  const [autoScroll, setAutoScroll] = useState(true);
  const listRef = useRef<HTMLDivElement>(null);

  // Subscribe to log updates
  useEffect(() => {
    const listener = () => forceUpdate((n) => n + 1);
    listeners.add(listener);
    return () => {
      listeners.delete(listener);
    };
  }, []);

  // Register callback with design-system devLogger to capture API logs
  useEffect(() => {
    registerDevConsoleCallback((level, source, message, data, extra) => {
      devConsoleLog(level as LogLevel, source, message, data, extra);
    });
    return () => {
      registerDevConsoleCallback(null);
    };
  }, []);

  // Keyboard shortcut: Ctrl+Shift+D
  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if (e.ctrlKey && e.shiftKey && e.key === 'D') {
        e.preventDefault();
        setOpen((prev) => !prev);
      }
    };
    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, []);

  // Auto-scroll
  useEffect(() => {
    if (autoScroll && listRef.current) {
      listRef.current.scrollTop = 0;
    }
  }, [logs.length, autoScroll]);

  // Filter logs
  const filteredLogs = logs.filter((log) => {
    if (activeTab !== 'all' && log.level !== activeTab) return false;
    if (filter && !log.source.toLowerCase().includes(filter.toLowerCase()) &&
        !log.message.toLowerCase().includes(filter.toLowerCase())) {
      return false;
    }
    return true;
  });

  const errorCount = logs.filter((l) => l.level === 'error').length;
  const apiCount = logs.filter((l) => l.level === 'api-req' || l.level === 'api-res').length;

  const handleExport = useCallback(() => {
    const data = JSON.stringify(logs, null, 2);
    const blob = new Blob([data], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `dev-console-${new Date().toISOString()}.json`;
    a.click();
    URL.revokeObjectURL(url);
  }, []);

  // Don't render in production
  if (process.env.NODE_ENV !== 'development') {
    return null;
  }

  return (
    <>
      {/* Floating Toggle Button */}
      <Tooltip title="Dev Console (Ctrl+Shift+D)">
        <Button
          type="primary"
          shape="circle"
          size="large"
          icon={
            <Badge count={errorCount} size="small" offset={[-5, 5]}>
              <BugOutlined />
            </Badge>
          }
          onClick={() => setOpen(true)}
          style={{
            position: 'fixed',
            bottom: 24,
            right: 24,
            zIndex: 999,
            boxShadow: '0 4px 12px rgba(0,0,0,0.2)',
            background: errorCount > 0 ? '#ff4d4f' : '#1890ff',
          }}
        />
      </Tooltip>

      {/* Console Drawer */}
      <Drawer
        title={
          <Space>
            <BugOutlined />
            <span>Dev Console</span>
            <Tag color="blue">{logs.length} entries</Tag>
            {errorCount > 0 && <Tag color="red">{errorCount} errors</Tag>}
          </Space>
        }
        placement="bottom"
        height="50vh"
        open={open}
        onClose={() => setOpen(false)}
        extra={
          <Space>
            <Switch
              checkedChildren="Auto-scroll"
              unCheckedChildren="Manual"
              checked={autoScroll}
              onChange={setAutoScroll}
              size="small"
            />
            <Button icon={<DownloadOutlined />} size="small" onClick={handleExport}>
              Export
            </Button>
            <Button icon={<ClearOutlined />} size="small" danger onClick={clearDevConsoleLogs}>
              Clear
            </Button>
            <Button icon={<CloseOutlined />} size="small" onClick={() => setOpen(false)} />
          </Space>
        }
      >
        {/* Tabs & Filter */}
        <div style={{ marginBottom: 12, display: 'flex', gap: 12, alignItems: 'center' }}>
          <Tabs
            activeKey={activeTab}
            onChange={setActiveTab}
            size="small"
            style={{ flex: 1 }}
            items={[
              { key: 'all', label: `All (${logs.length})` },
              { key: 'api-req', label: `API Req (${logs.filter(l => l.level === 'api-req').length})` },
              { key: 'api-res', label: `API Res (${logs.filter(l => l.level === 'api-res').length})` },
              { key: 'error', label: <span style={{ color: errorCount > 0 ? '#ff4d4f' : undefined }}>Errors ({errorCount})</span> },
              { key: 'action', label: `Actions (${logs.filter(l => l.level === 'action').length})` },
              { key: 'state', label: `State (${logs.filter(l => l.level === 'state').length})` },
            ]}
          />
          <Input
            placeholder="Filter..."
            prefix={<SearchOutlined />}
            value={filter}
            onChange={(e) => setFilter(e.target.value)}
            style={{ width: 200 }}
            size="small"
            allowClear
          />
        </div>

        {/* Log List */}
        <div
          ref={listRef}
          style={{
            height: 'calc(50vh - 140px)',
            overflow: 'auto',
            border: '1px solid #f0f0f0',
            borderRadius: 4,
          }}
        >
          {filteredLogs.length === 0 ? (
            <div style={{ padding: 40, textAlign: 'center' }}>
              <Text type="secondary">No logs yet. Actions, API calls, and errors will appear here.</Text>
            </div>
          ) : (
            filteredLogs.map((entry) => <LogEntryRow key={entry.id} entry={entry} />)
          )}
        </div>
      </Drawer>
    </>
  );
}

export default DevConsole;
