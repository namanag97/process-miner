/**
 * DevConsole - In-app developer console for debugging
 *
 * Enhanced with:
 * - Importance scoring (1-5) for each log
 * - Focus Mode to hide noise
 * - Request flow correlation
 * - Smart export with filtering and compression
 * - Stuck request detection
 */
import React, { useState, useEffect, useCallback, useRef, useMemo } from 'react';
import {
  Drawer,
  Badge,
  Button,
  Tabs,
  Tag,
  Typography,
  Space,
  Input,
  Switch,
  Tooltip,
  Modal,
  Checkbox,
  Select,
  Collapse,
  Spin,
  Divider,
} from 'antd';
import {
  BugOutlined,
  ApiOutlined,
  WarningOutlined,
  InfoCircleOutlined,
  ClearOutlined,
  DownloadOutlined,
  SearchOutlined,
  CloseOutlined,
  AimOutlined,
  BranchesOutlined,
  ClockCircleOutlined,
  ExclamationCircleOutlined,
  ThunderboltOutlined,
  EyeInvisibleOutlined,
  CopyOutlined,
  CheckOutlined,
  ReloadOutlined,
  DatabaseOutlined,
} from '@ant-design/icons';
import { registerDevConsoleCallback } from '@/src/shared/design-system';
import { useBackendLogs } from '../../hooks/useBackendLogs';
import { BackendMetricsPanel } from '../BackendMetricsPanel';
import { DataViewer } from '../DataViewer';
import { DebugExport } from './DebugExport';

const { Text } = Typography;
const { Panel } = Collapse;

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

type LogLevel = 'info' | 'api-req' | 'api-res' | 'error' | 'action' | 'state' | 'query' | 'mutation' | 'metric' | 'perf' | 'circuit' | 'db-query' | 'cache' | 'auth';
type Importance = 1 | 2 | 3 | 4 | 5; // 1=noise, 5=critical

interface LogEntry {
  id: string;
  timestamp: Date;
  level: LogLevel;
  source: string;
  message: string;
  data?: unknown;
  duration?: number;
  status?: number;
  // Enhanced fields
  importance: Importance;
  correlationId?: string;
  requestId?: string;
  isPending?: boolean;
  pendingSince?: Date;
  // API Replay data
  replayData?: {
    method: string;
    url: string;
    headers?: Record<string, string>;
    body?: unknown;
  };
}

interface ExportOptions {
  timeRange: 'all' | '5min' | '10min' | '30min';
  minImportance: Importance;
  includeLevels: LogLevel[];
  compressRepetitive: boolean;
  includeFlowTimeline: boolean;
}

// ============================================
// Importance Scoring
// ============================================

function calculateImportance(
  level: LogLevel,
  source: string,
  message: string,
  _data?: unknown,
  extra?: { duration?: number; status?: number }
): Importance {
  // Critical: Errors and failed requests
  if (level === 'error') return 5;
  if (level === 'circuit') return 5;
  if (extra?.status && extra.status >= 400) return 5;

  // High: User actions, mutations, slow requests
  if (level === 'mutation') return 4;
  if (level === 'action') return 4;
  if (extra?.duration && extra.duration > 1000) return 4;

  // Medium: Successful API responses, state changes, metrics
  if (level === 'api-res' && extra?.status && extra.status < 400) return 3;
  if (level === 'state') return 3;
  if (level === 'query') return 3;
  if (level === 'metric') return 3;

  // Low: API requests (waiting for response), perf logs
  if (level === 'api-req') return 2;
  if (level === 'perf') return 2;

  // Noise: Heartbeats, connection logs, background polling
  const noisePatterns = [
    'heartbeat', 'connection', 'stream', 'poll', 'BE Connection',
    'Backend Observability', 'metrics'
  ];
  const sourceAndMessage = `${source} ${message}`.toLowerCase();
  if (noisePatterns.some(p => sourceAndMessage.includes(p.toLowerCase()))) {
    return 1;
  }

  return 2; // Default: Low importance
}

// ============================================
// Correlation ID Management
// ============================================

let correlationCounter = 0;
let activeCorrelation: string | null = null;

export function startCorrelation(_action: string): string {
  const id = `flow-${++correlationCounter}-${Date.now()}`;
  activeCorrelation = id;
  // Auto-expire after 30 seconds
  setTimeout(() => {
    if (activeCorrelation === id) activeCorrelation = null;
  }, 30000);
  return id;
}

export function getCurrentCorrelation(): string | null {
  return activeCorrelation;
}

// ============================================
// Global Log Store
// ============================================

const MAX_LOGS = 500;
let logs: LogEntry[] = [];
const pendingRequests: Map<string, LogEntry> = new Map();
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
  extra?: { duration?: number; status?: number; replayData?: LogEntry['replayData'] }
) {
  const importance = calculateImportance(level, source, message, extra);
  const correlationId = getCurrentCorrelation() || undefined;

  // Extract request ID from source or data for correlation
  let requestId: string | undefined;
  if (typeof data === 'object' && data !== null && 'request_id' in data) {
    requestId = (data as { request_id?: string }).request_id;
  }

  const entry: LogEntry = {
    id: `log-${++idCounter}`,
    timestamp: new Date(),
    level,
    source,
    message,
    data,
    importance,
    correlationId,
    requestId,
    ...extra,
  };

  // Track pending requests
  if (level === 'api-req') {
    const key = source; // e.g., "GET /api/v1/workspaces"
    entry.isPending = true;
    entry.pendingSince = new Date();
    pendingRequests.set(key, entry);
  }

  // Match response to request
  if (level === 'api-res') {
    const key = source;
    const pendingReq = pendingRequests.get(key);
    if (pendingReq) {
      pendingReq.isPending = false;
      pendingRequests.delete(key);
    }
  }

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
      'query': 'color: #2f54eb',
      'mutation': 'color: #eb2f96',
      'metric': 'color: #13c2c2',
      'perf': 'color: #fa8c16',
      'circuit': 'color: #ff4d4f',
      'db-query': 'color: #9254de',
      'cache': 'color: #faad14',
      'auth': 'color: #fa541c',
    }[level];
    console.log(`%c[${level.toUpperCase()}] ${source}`, style, message, data || '');
  }
}

export function clearDevConsoleLogs() {
  logs = [];
  pendingRequests.clear();
  notifyListeners();
}

// ============================================
// Convenience Loggers
// ============================================

export const devLog = {
  info: (source: string, message: string, data?: unknown) =>
    devConsoleLog('info', source, message, data),

  action: (source: string, message: string, data?: unknown) => {
    startCorrelation(source); // Start correlation for user actions
    devConsoleLog('action', source, message, data);
  },

  state: (source: string, message: string, data?: unknown) =>
    devConsoleLog('state', source, message, data),

  error: (source: string, message: string, data?: unknown) =>
    devConsoleLog('error', source, message, data),

  apiRequest: (method: string, url: string, body?: unknown, headers?: Record<string, string>) =>
    devConsoleLog('api-req', `${method} ${url}`, 'Request sent', body, {
      replayData: { method, url, body, headers }
    }),

  apiResponse: (method: string, url: string, status: number, duration: number, body?: unknown) =>
    devConsoleLog('api-res', `${method} ${url}`, `${status} (${duration}ms)`, body, { duration, status }),
};

// ============================================
// Importance Badge Component
// ============================================

function ImportanceBadge({ importance }: { importance: Importance }) {
  const config = {
    5: { color: '#ff4d4f', label: '!!', title: 'Critical' },
    4: { color: '#fa8c16', label: '!', title: 'High' },
    3: { color: '#1890ff', label: '•', title: 'Medium' },
    2: { color: '#8c8c8c', label: '○', title: 'Low' },
    1: { color: '#d9d9d9', label: '·', title: 'Noise' },
  }[importance];

  return (
    <Tooltip title={`Importance: ${config.title}`}>
      <span style={{
        width: 16,
        height: 16,
        borderRadius: '50%',
        background: config.color,
        display: 'inline-flex',
        alignItems: 'center',
        justifyContent: 'center',
        fontSize: 10,
        color: importance >= 4 ? 'white' : '#666',
        fontWeight: 'bold',
      }}>
        {config.label}
      </span>
    </Tooltip>
  );
}

// ============================================
// Level Configuration
// ============================================

const levelConfig: Record<LogLevel, { color: string; icon: React.ReactNode; label: string }> = {
  'info': { color: 'blue', icon: <InfoCircleOutlined />, label: 'INFO' },
  'api-req': { color: 'purple', icon: <ApiOutlined />, label: 'REQ' },
  'api-res': { color: 'cyan', icon: <ApiOutlined />, label: 'RES' },
  'error': { color: 'red', icon: <WarningOutlined />, label: 'ERROR' },
  'action': { color: 'green', icon: <ThunderboltOutlined />, label: 'ACTION' },
  'state': { color: 'orange', icon: <InfoCircleOutlined />, label: 'STATE' },
  'query': { color: 'geekblue', icon: <ApiOutlined />, label: 'QUERY' },
  'mutation': { color: 'magenta', icon: <ApiOutlined />, label: 'MUTATE' },
  'metric': { color: 'cyan', icon: <InfoCircleOutlined />, label: 'METRIC' },
  'perf': { color: 'gold', icon: <ThunderboltOutlined />, label: 'PERF' },
  'circuit': { color: 'red', icon: <WarningOutlined />, label: 'CIRCUIT' },
  'db-query': { color: 'lime', icon: <ApiOutlined />, label: 'DB' },
  'cache': { color: 'volcano', icon: <ThunderboltOutlined />, label: 'CACHE' },
  'auth': { color: 'purple', icon: <InfoCircleOutlined />, label: 'AUTH' },
};

// ============================================
// Log Entry Row Component
// ============================================

function LogEntryRow({ entry, showImportance }: { entry: LogEntry; showImportance: boolean }) {
  const [expanded, setExpanded] = useState(false);
  const [copied, setCopied] = useState(false);
  const config = levelConfig[entry.level];
  const time = entry.timestamp.toLocaleTimeString('en-US', { hour12: false });

  // Check if pending for too long (>5s = stuck)
  const isStuck = entry.isPending && entry.pendingSince &&
    (new Date().getTime() - entry.pendingSince.getTime()) > 5000;

  // Check if request is slow (for visual indicators)
  const isSlow = entry.duration && entry.duration > 1000;
  const isModeratelySlow = entry.duration && entry.duration > 500 && entry.duration <= 1000;

  const handleCopy = (e: React.MouseEvent) => {
    e.stopPropagation();
    const logText = JSON.stringify({
      time: entry.timestamp.toISOString(),
      level: entry.level,
      source: entry.source,
      message: entry.message,
      data: entry.data,
    }, null, 2);
    navigator.clipboard.writeText(logText);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  // API Replay handler
  const [replaying, setReplaying] = useState(false);
  const handleReplay = async (e: React.MouseEvent) => {
    e.stopPropagation();
    if (!entry.replayData) return;

    setReplaying(true);
    const { method, url, headers, body } = entry.replayData;

    try {
      const start = performance.now();
      const response = await fetch(url, {
        method,
        headers: { 'Content-Type': 'application/json', ...headers },
        body: body ? JSON.stringify(body) : undefined,
      });
      const duration = Math.round(performance.now() - start);
      const responseData = await response.json().catch(() => null);

      devConsoleLog('api-res', `↻ ${method} ${url}`, `Replayed: ${response.status}`, responseData, {
        duration,
        status: response.status
      });
    } catch (err) {
      devConsoleLog('error', `↻ ${method} ${url}`, `Replay failed: ${err}`, { error: String(err) });
    } finally {
      setReplaying(false);
    }
  };

  return (
    <div
      style={{
        padding: '8px 12px',
        borderBottom: '1px solid #f0f0f0',
        cursor: entry.data ? 'pointer' : 'default',
        background: expanded ? '#fafafa' :
          isSlow ? '#fff1f0' :
            isModeratelySlow ? '#fff7e6' :
              entry.importance >= 4 ? '#fff7e6' : 'white',
        borderLeft: entry.importance === 5 ? '3px solid #ff4d4f' :
          entry.importance === 4 ? '3px solid #fa8c16' :
            isSlow ? '3px solid #ff4d4f' :
              isModeratelySlow ? '3px solid #fa8c16' : 'none',
      }}
      onClick={() => entry.data && setExpanded(!expanded)}
    >
      <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
        {showImportance && <ImportanceBadge importance={entry.importance} />}
        <Text type="secondary" style={{ fontSize: 11, fontFamily: 'monospace', width: 70 }}>
          {time}
        </Text>
        <Tag color={config.color} style={{ margin: 0, fontSize: 10 }}>
          {config.label}
        </Tag>
        {entry.isPending && (
          <Tooltip title={isStuck ? 'Request stuck!' : 'Pending...'}>
            <Tag color={isStuck ? 'red' : 'processing'} icon={isStuck ? <ExclamationCircleOutlined /> : <Spin size="small" />}>
              {isStuck ? 'STUCK' : 'PENDING'}
            </Tag>
          </Tooltip>
        )}
        {isSlow && (
          <Tooltip title="Slow request (>1s) - consider optimization">
            <Tag color="red" icon={<ClockCircleOutlined />}>
              SLOW
            </Tag>
          </Tooltip>
        )}
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
        <Tooltip title={copied ? 'Copied!' : 'Copy log'}>
          <Button
            type="text"
            size="small"
            icon={copied ? <CheckOutlined style={{ color: '#52c41a' }} /> : <CopyOutlined />}
            onClick={handleCopy}
          />
        </Tooltip>
        {entry.replayData && (
          <Tooltip title="Replay this request">
            <Button
              type="text"
              size="small"
              loading={replaying}
              icon={<ReloadOutlined style={{ color: '#1890ff' }} />}
              onClick={handleReplay}
            />
          </Tooltip>
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
// Flow Timeline View Component
// ============================================

function FlowTimelineView({ logs }: { logs: LogEntry[] }) {
  // Group logs by correlation ID or by time proximity
  const flows = useMemo(() => {
    const flowMap = new Map<string, LogEntry[]>();

    logs.forEach(log => {
      if (log.correlationId) {
        const existing = flowMap.get(log.correlationId) || [];
        flowMap.set(log.correlationId, [...existing, log]);
      }
    });

    // Also group action -> api-req -> api-res by time proximity
    const ungrouped = logs.filter(l => !l.correlationId && l.importance >= 3);

    return {
      correlated: Array.from(flowMap.entries()).map(([id, items]) => ({
        id,
        action: items.find(i => i.level === 'action')?.source || 'Unknown Action',
        logs: items.sort((a, b) => a.timestamp.getTime() - b.timestamp.getTime()),
        hasError: items.some(i => i.level === 'error' || (i.status && i.status >= 400)),
        hasPending: items.some(i => i.isPending),
      })),
      ungrouped,
    };
  }, [logs]);

  if (flows.correlated.length === 0) {
    return (
      <div style={{ padding: 40, textAlign: 'center' }}>
        <BranchesOutlined style={{ fontSize: 32, color: '#d9d9d9' }} />
        <div style={{ marginTop: 8, color: '#888' }}>
          No correlated flows yet. User actions will appear here with their API calls.
        </div>
      </div>
    );
  }

  return (
    <Collapse accordion>
      {flows.correlated.map(flow => (
        <Panel
          key={flow.id}
          header={
            <Space>
              <ThunderboltOutlined style={{ color: '#52c41a' }} />
              <Text strong>{flow.action}</Text>
              <Tag color={flow.hasError ? 'red' : flow.hasPending ? 'orange' : 'green'}>
                {flow.hasError ? 'Error' : flow.hasPending ? 'Pending' : 'Complete'}
              </Tag>
              <Text type="secondary" style={{ fontSize: 11 }}>
                ({flow.logs.length} events)
              </Text>
            </Space>
          }
        >
          <div style={{ paddingLeft: 16, borderLeft: '2px solid #d9d9d9' }}>
            {flow.logs.map(log => (
              <div key={log.id} style={{ padding: '4px 0', display: 'flex', alignItems: 'center', gap: 8 }}>
                <Text type="secondary" style={{ fontSize: 10, fontFamily: 'monospace' }}>
                  {log.timestamp.toLocaleTimeString('en-US', { hour12: false })}
                </Text>
                <Tag color={levelConfig[log.level].color} style={{ margin: 0 }}>
                  {levelConfig[log.level].label}
                </Tag>
                <Text style={{ fontSize: 12 }}>{log.message}</Text>
                {log.duration && <Tag>{log.duration}ms</Tag>}
                {log.status && <Tag color={log.status >= 400 ? 'red' : 'green'}>{log.status}</Tag>}
              </div>
            ))}
          </div>
        </Panel>
      ))}
    </Collapse>
  );
}

// ============================================
// Export Options Modal
// ============================================

function ExportModal({
  open,
  onClose,
  onExport,
}: {
  open: boolean;
  onClose: () => void;
  onExport: (options: ExportOptions) => void;
}) {
  const [options, setOptions] = useState<ExportOptions>({
    timeRange: 'all',
    minImportance: 1,
    includeLevels: ['info', 'api-req', 'api-res', 'error', 'action', 'state', 'query', 'mutation'],
    compressRepetitive: true,
    includeFlowTimeline: true,
  });

  const quickPresets = [
    { label: 'Errors Only', options: { minImportance: 5 as Importance, includeLevels: ['error'] as LogLevel[] } },
    { label: 'Important (≥3)', options: { minImportance: 3 as Importance } },
    { label: 'API Calls', options: { includeLevels: ['api-req', 'api-res'] as LogLevel[] } },
    { label: 'User Actions', options: { includeLevels: ['action', 'mutation'] as LogLevel[] } },
  ];

  return (
    <Modal
      title={
        <Space>
          <DownloadOutlined />
          <span>Export Logs</span>
        </Space>
      }
      open={open}
      onCancel={onClose}
      onOk={() => onExport(options)}
      okText="Export"
      width={480}
    >
      <div style={{ marginBottom: 16 }}>
        <Text strong>Quick Presets:</Text>
        <div style={{ marginTop: 8, display: 'flex', gap: 8, flexWrap: 'wrap' }}>
          {quickPresets.map(preset => (
            <Button
              key={preset.label}
              size="small"
              onClick={() => setOptions(prev => ({ ...prev, ...preset.options }))}
            >
              {preset.label}
            </Button>
          ))}
        </div>
      </div>

      <Divider />

      <div style={{ display: 'flex', flexDirection: 'column', gap: 16 }}>
        <div>
          <Text strong>Time Range:</Text>
          <Select
            value={options.timeRange}
            onChange={v => setOptions(prev => ({ ...prev, timeRange: v }))}
            style={{ width: '100%', marginTop: 4 }}
            options={[
              { value: 'all', label: 'All logs' },
              { value: '5min', label: 'Last 5 minutes' },
              { value: '10min', label: 'Last 10 minutes' },
              { value: '30min', label: 'Last 30 minutes' },
            ]}
          />
        </div>

        <div>
          <Text strong>Minimum Importance:</Text>
          <Select
            value={options.minImportance}
            onChange={v => setOptions(prev => ({ ...prev, minImportance: v }))}
            style={{ width: '100%', marginTop: 4 }}
            options={[
              { value: 1, label: '1 - All (including noise)' },
              { value: 2, label: '2 - Low and above' },
              { value: 3, label: '3 - Medium and above' },
              { value: 4, label: '4 - High and above' },
              { value: 5, label: '5 - Critical only' },
            ]}
          />
        </div>

        <div>
          <Checkbox
            checked={options.compressRepetitive}
            onChange={e => setOptions(prev => ({ ...prev, compressRepetitive: e.target.checked }))}
          >
            Compress repetitive logs (heartbeats, polling, etc.)
          </Checkbox>
        </div>

        <div>
          <Checkbox
            checked={options.includeFlowTimeline}
            onChange={e => setOptions(prev => ({ ...prev, includeFlowTimeline: e.target.checked }))}
          >
            Include user flow timeline summary
          </Checkbox>
        </div>
      </div>
    </Modal>
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
  const [focusMode, setFocusMode] = useState(false);
  const [showExportModal, setShowExportModal] = useState(false);
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
    registerDevConsoleCallback((level, source, message, extra) => {
      devConsoleLog(level as LogLevel, source, message, extra);
    });
    return () => {
      registerDevConsoleCallback(null);
    };
  }, []);

  // Connect to backend SSE stream ONLY when DevConsole is open
  const backendObservability = useBackendLogs(open);

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
  const filteredLogs = useMemo(() => {
    return logs.filter((log) => {
      // Focus mode: hide low importance
      if (focusMode && log.importance < 3) return false;

      // Tab filter
      if (activeTab !== 'all' && activeTab !== 'flow' && activeTab !== 'pending') {
        if (log.level !== activeTab) return false;
      }

      // Pending tab
      if (activeTab === 'pending' && !log.isPending) return false;

      // Text filter
      if (filter && !log.source.toLowerCase().includes(filter.toLowerCase()) &&
        !log.message.toLowerCase().includes(filter.toLowerCase())) {
        return false;
      }
      return true;
    });
  }, [logs, focusMode, activeTab, filter]);

  const errorCount = logs.filter((l) => l.level === 'error').length;
  const pendingCount = Array.from(pendingRequests.values()).length;
  const stuckCount = Array.from(pendingRequests.values()).filter(
    r => r.pendingSince && (new Date().getTime() - r.pendingSince.getTime()) > 5000
  ).length;

  // Helper: Detect polling/high-frequency endpoints
  const isPollingEndpoint = useCallback((source: string): boolean => {
    const pollingPatterns = [
      '/jobs/',
      '/status',
      '/health',
      '/heartbeat',
      '/metrics',
      '/stream',
    ];
    return pollingPatterns.some(p => source.toLowerCase().includes(p.toLowerCase()));
  }, []);

  // Helper: Extract request/response bodies from log data
  const extractBodies = useCallback((log: LogEntry) => {
    const result: { requestBody?: unknown; responseBody?: unknown } = {};
    if (log.data && typeof log.data === 'object') {
      const data = log.data as Record<string, unknown>;
      if ('requestBody' in data) result.requestBody = data.requestBody;
      if ('responseBody' in data) result.responseBody = data.responseBody;
    }
    return result;
  }, []);

  const handleExport = useCallback((options: ExportOptions) => {
    const now = new Date();

    // Filter by time range
    let exportLogs = [...logs];
    if (options.timeRange !== 'all') {
      const minutes = { '5min': 5, '10min': 10, '30min': 30 }[options.timeRange] || 0;
      const cutoff = new Date(now.getTime() - minutes * 60 * 1000);
      exportLogs = exportLogs.filter(l => l.timestamp >= cutoff);
    }

    // Filter by importance
    exportLogs = exportLogs.filter(l => l.importance >= options.minImportance);

    // Filter by levels
    if (options.includeLevels.length < 8) {
      exportLogs = exportLogs.filter(l => options.includeLevels.includes(l.level));
    }

    // Compress repetitive logs
    let compressedLogs: unknown[] = [];
    const consolidationPatterns: { pattern: string; count: number; sample: string }[] = [];

    if (options.compressRepetitive) {
      const grouped = new Map<string, LogEntry[]>();
      const singles: LogEntry[] = [];

      exportLogs.forEach(log => {
        // Group noise logs AND polling endpoints
        const isRepetitive = log.importance === 1 ||
          (log.level === 'api-res' && isPollingEndpoint(log.source));

        if (isRepetitive) {
          const key = `${log.level}:${log.source}`;
          grouped.set(key, [...(grouped.get(key) || []), log]);
        } else {
          singles.push(log);
        }
      });

      // Add collapsed repetitive logs
      grouped.forEach((items, key) => {
        if (items.length > 3) {
          consolidationPatterns.push({
            pattern: key,
            count: items.length,
            sample: items[0].message,
          });
          compressedLogs.push({
            _collapsed: true,
            count: items.length,
            pattern: key,
            timeRange: {
              start: items[items.length - 1].timestamp.toISOString(),
              end: items[0].timestamp.toISOString(),
            },
            sample: {
              level: items[0].level,
              source: items[0].source,
              message: items[0].message,
            },
          });
        } else {
          singles.push(...items);
        }
      });

      // Add individual logs with extracted bodies
      compressedLogs.push(...singles.map(log => {
        const bodies = extractBodies(log);
        return {
          timestamp: log.timestamp.toISOString(),
          level: log.level,
          source: log.source,
          message: log.message,
          data: log.data,
          ...bodies,
          duration: log.duration,
          status: log.status,
          importance: log.importance,
        };
      }));
    } else {
      compressedLogs = exportLogs.map(log => {
        const bodies = extractBodies(log);
        return {
          timestamp: log.timestamp.toISOString(),
          level: log.level,
          source: log.source,
          message: log.message,
          data: log.data,
          ...bodies,
          duration: log.duration,
          status: log.status,
          importance: log.importance,
        };
      });
    }

    // Build flow timeline
    const flowTimeline: unknown[] = [];
    if (options.includeFlowTimeline) {
      const actions = exportLogs.filter(l => l.level === 'action' || l.level === 'mutation');
      actions.forEach(action => {
        const relatedLogs = exportLogs.filter(
          l => l.correlationId === action.correlationId && l.id !== action.id
        );
        flowTimeline.push({
          time: action.timestamp.toISOString(),
          action: action.source,
          message: action.message,
          result: relatedLogs.some(l => l.level === 'error') ? 'error' :
            relatedLogs.some(l => l.isPending) ? 'pending' : 'success',
          apiCalls: relatedLogs.filter(l => l.level === 'api-req' || l.level === 'api-res').length,
        });
      });
    }

    // Build session summary
    const sessionSummary = {
      export_time: now.toISOString(),
      time_range: options.timeRange,
      duration_minutes: options.timeRange === 'all' ? null :
        parseInt(options.timeRange.replace('min', '')),
      total_logs: logs.length,
      exported_logs: compressedLogs.length,
      compression_ratio: logs.length > 0 ?
        Math.round((1 - compressedLogs.length / logs.length) * 100) + '%' : '0%',
      ...(consolidationPatterns.length > 0 && {
        consolidation_summary: {
          total_before: exportLogs.length,
          total_after: compressedLogs.length,
          collapsed_patterns: consolidationPatterns,
        },
      }),
      stats: {
        errors: exportLogs.filter(l => l.level === 'error').length,
        slow_requests: exportLogs.filter(l => l.duration && l.duration > 1000).length,
        pending_requests: exportLogs.filter(l => l.isPending).length,
        user_actions: exportLogs.filter(l => l.level === 'action').length,
      },
      critical_issues: [
        ...exportLogs.filter(l => l.importance === 5).map(l => ({
          type: l.level,
          time: l.timestamp.toISOString(),
          source: l.source,
          message: l.message,
        })),
      ].slice(0, 10),
    };

    const exportData = {
      session_summary: sessionSummary,
      ...(options.includeFlowTimeline && flowTimeline.length > 0 && { user_flow_timeline: flowTimeline }),
      logs: compressedLogs,
    };

    const data = JSON.stringify(exportData, null, 2);
    const blob = new Blob([data], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `dev-console-${now.toISOString().replace(/[:.]/g, '-')}.json`;
    a.click();
    URL.revokeObjectURL(url);
    setShowExportModal(false);
  }, [logs, isPollingEndpoint, extractBodies]);

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
            <Badge count={errorCount + stuckCount} size="small" offset={[-5, 5]}>
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
            background: stuckCount > 0 ? '#fa8c16' : errorCount > 0 ? '#ff4d4f' : '#1890ff',
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
            {pendingCount > 0 && (
              <Tag color={stuckCount > 0 ? 'red' : 'orange'}>
                {pendingCount} pending {stuckCount > 0 && `(${stuckCount} stuck)`}
              </Tag>
            )}
          </Space>
        }
        placement="bottom"
        height="50vh"
        open={open}
        onClose={() => setOpen(false)}
        extra={
          <Space>
            <DebugExport logs={logs} sessionStart={new Date(Date.now() - 600000)} />
            <Tooltip title={focusMode ? 'Show all logs' : 'Hide noise (importance < 3)'}>
              <Button
                icon={focusMode ? <EyeInvisibleOutlined /> : <AimOutlined />}
                size="small"
                type={focusMode ? 'primary' : 'default'}
                onClick={() => setFocusMode(!focusMode)}
              >
                {focusMode ? 'Focus ON' : 'Focus'}
              </Button>
            </Tooltip>
            <Switch
              checkedChildren="Auto-scroll"
              unCheckedChildren="Manual"
              checked={autoScroll}
              onChange={setAutoScroll}
              size="small"
            />
            <Button icon={<DownloadOutlined />} size="small" onClick={() => setShowExportModal(true)}>
              Export
            </Button>
            <Button icon={<ClearOutlined />} size="small" danger onClick={clearDevConsoleLogs}>
              Clear
            </Button>
            <Button icon={<CloseOutlined />} size="small" onClick={() => setOpen(false)} />
          </Space>
        }
      >
        {/* Backend Metrics Panel */}
        <BackendMetricsPanel observability={backendObservability} />

        {/* Tabs & Filter */}
        <div style={{ marginBottom: 12, display: 'flex', gap: 12, alignItems: 'center' }}>
          <Tabs
            activeKey={activeTab}
            onChange={setActiveTab}
            size="small"
            style={{ flex: 1 }}
            items={[
              { key: 'all', label: `All (${logs.filter(l => !focusMode || l.importance >= 3).length})` },
              { key: 'flow', label: <span><BranchesOutlined /> Flows</span> },
              { key: 'error', label: <span style={{ color: errorCount > 0 ? '#ff4d4f' : undefined }}>Errors ({errorCount})</span> },
              { key: 'pending', label: <span style={{ color: pendingCount > 0 ? '#fa8c16' : undefined }}>Pending ({pendingCount})</span> },
              { key: 'action', label: `Actions (${logs.filter(l => l.level === 'action').length})` },
              { key: 'api-res', label: `API (${logs.filter(l => l.level === 'api-res').length})` },
              { key: 'data', label: <span><DatabaseOutlined /> Data</span> },
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

        {/* Log List or Flow View or Data Viewer */}
        {activeTab === 'data' ? (
          <DataViewer />
        ) : activeTab === 'flow' ? (
          <FlowTimelineView logs={logs} />
        ) : (
          <div
            ref={listRef}
            style={{
              height: 'calc(50vh - 200px)',
              overflow: 'auto',
              border: '1px solid #f0f0f0',
              borderRadius: 4,
            }}
          >
            {filteredLogs.length === 0 ? (
              <div style={{ padding: 40, textAlign: 'center' }}>
                <Text type="secondary">
                  {focusMode
                    ? 'No important logs yet. Disable Focus mode to see all logs.'
                    : 'No logs yet. Actions, API calls, and errors will appear here.'}
                </Text>
              </div>
            ) : (
              filteredLogs.map((entry) => (
                <LogEntryRow key={entry.id} entry={entry} showImportance={!focusMode} />
              ))
            )}
          </div>
        )}
      </Drawer>

      {/* Export Modal */}
      <ExportModal
        open={showExportModal}
        onClose={() => setShowExportModal(false)}
        onExport={handleExport}
      />
    </>
  );
}

export default DevConsole;
