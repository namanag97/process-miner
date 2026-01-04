/**
 * Backend Metrics Panel for DevConsole
 * 
 * Beautiful real-time visualization of backend observability:
 * - System metrics (CPU, Memory, RPS)
 * - Circuit breaker status indicators
 * - Request waterfall and timing
 * - Error rate tracking
 */
import { Card, Progress, Tag, Space, Statistic, Row, Col, Tooltip, Badge } from 'antd';
import {
  ThunderboltOutlined,
  CloudServerOutlined,
  ApiOutlined,
  SafetyCertificateOutlined,
  WarningOutlined,
  CheckCircleOutlined,
  CloseCircleOutlined,
  ClockCircleOutlined,
} from '@ant-design/icons';
import { BackendObservability } from '../hooks/useBackendLogs';

interface MetricsPanelProps {
  observability: BackendObservability;
}

// Circuit breaker state colors and icons
const circuitStateConfig = {
  closed: { color: '#52c41a', icon: <CheckCircleOutlined />, label: 'Healthy' },
  open: { color: '#ff4d4f', icon: <CloseCircleOutlined />, label: 'Open' },
  half_open: { color: '#faad14', icon: <ClockCircleOutlined />, label: 'Recovering' },
};

export function BackendMetricsPanel({ observability }: MetricsPanelProps) {
  const { connected, metrics, circuitBreakers, errorCount, slowRequests, lastHeartbeat } = observability;

  if (!connected || !metrics) {
    return (
      <Card
        size="small"
        style={{
          background: 'linear-gradient(135deg, #1a1a2e 0%, #16213e 100%)',
          border: 'none',
          borderRadius: 8,
        }}
      >
        <div style={{ textAlign: 'center', padding: 16, color: '#888' }}>
          <CloudServerOutlined style={{ fontSize: 24, marginBottom: 8 }} />
          <div>Connecting to backend...</div>
        </div>
      </Card>
    );
  }

  const isHealthy = metrics.error_rate_percent < 5 && metrics.avg_response_time_ms < 500;
  const cpuColor = metrics.cpu_percent > 80 ? '#ff4d4f' : metrics.cpu_percent > 60 ? '#faad14' : '#52c41a';
  const memColor = metrics.memory_percent > 80 ? '#ff4d4f' : metrics.memory_percent > 60 ? '#faad14' : '#52c41a';

  return (
    <div style={{
      background: 'linear-gradient(135deg, #0d0d1a 0%, #1a1a2e 50%, #16213e 100%)',
      borderRadius: 12,
      padding: 16,
      marginBottom: 12,
      border: '1px solid rgba(255,255,255,0.1)',
    }}>
      {/* Header */}
      <div style={{
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'space-between',
        marginBottom: 16,
      }}>
        <Space>
          <Badge status={connected ? 'success' : 'error'} />
          <span style={{ color: '#fff', fontWeight: 600, fontSize: 14 }}>
            Backend Observability
          </span>
        </Space>
        <Space size="small">
          {isHealthy ? (
            <Tag color="success" icon={<CheckCircleOutlined />}>Healthy</Tag>
          ) : (
            <Tag color="warning" icon={<WarningOutlined />}>Degraded</Tag>
          )}
          <Tag color="blue">{metrics.active_requests} active</Tag>
        </Space>
      </div>

      {/* Main Metrics Grid */}
      <Row gutter={[12, 12]}>
        {/* RPS */}
        <Col span={6}>
          <div style={{
            background: 'rgba(24, 144, 255, 0.1)',
            borderRadius: 8,
            padding: 12,
            border: '1px solid rgba(24, 144, 255, 0.2)',
          }}>
            <div style={{ color: '#888', fontSize: 11, marginBottom: 4 }}>
              <ThunderboltOutlined style={{ marginRight: 4 }} />
              REQUESTS/SEC
            </div>
            <div style={{ color: '#1890ff', fontSize: 24, fontWeight: 700 }}>
              {metrics.requests_per_second.toFixed(1)}
            </div>
          </div>
        </Col>

        {/* Response Time */}
        <Col span={6}>
          <div style={{
            background: metrics.avg_response_time_ms > 500
              ? 'rgba(255, 77, 79, 0.1)'
              : 'rgba(82, 196, 26, 0.1)',
            borderRadius: 8,
            padding: 12,
            border: `1px solid ${metrics.avg_response_time_ms > 500
              ? 'rgba(255, 77, 79, 0.2)'
              : 'rgba(82, 196, 26, 0.2)'}`,
          }}>
            <div style={{ color: '#888', fontSize: 11, marginBottom: 4 }}>
              <ClockCircleOutlined style={{ marginRight: 4 }} />
              AVG RESPONSE
            </div>
            <div style={{
              color: metrics.avg_response_time_ms > 500 ? '#ff4d4f' : '#52c41a',
              fontSize: 24,
              fontWeight: 700
            }}>
              {metrics.avg_response_time_ms.toFixed(0)}
              <span style={{ fontSize: 12, fontWeight: 400 }}>ms</span>
            </div>
          </div>
        </Col>

        {/* Error Rate */}
        <Col span={6}>
          <div style={{
            background: metrics.error_rate_percent > 5
              ? 'rgba(255, 77, 79, 0.1)'
              : 'rgba(82, 196, 26, 0.1)',
            borderRadius: 8,
            padding: 12,
            border: `1px solid ${metrics.error_rate_percent > 5
              ? 'rgba(255, 77, 79, 0.2)'
              : 'rgba(82, 196, 26, 0.2)'}`,
          }}>
            <div style={{ color: '#888', fontSize: 11, marginBottom: 4 }}>
              <WarningOutlined style={{ marginRight: 4 }} />
              ERROR RATE
            </div>
            <div style={{
              color: metrics.error_rate_percent > 5 ? '#ff4d4f' : '#52c41a',
              fontSize: 24,
              fontWeight: 700
            }}>
              {metrics.error_rate_percent.toFixed(1)}
              <span style={{ fontSize: 12, fontWeight: 400 }}>%</span>
            </div>
          </div>
        </Col>

        {/* Memory */}
        <Col span={6}>
          <div style={{
            background: 'rgba(114, 46, 209, 0.1)',
            borderRadius: 8,
            padding: 12,
            border: '1px solid rgba(114, 46, 209, 0.2)',
          }}>
            <div style={{ color: '#888', fontSize: 11, marginBottom: 4 }}>
              <CloudServerOutlined style={{ marginRight: 4 }} />
              MEMORY
            </div>
            <div style={{ color: '#722ed1', fontSize: 24, fontWeight: 700 }}>
              {metrics.memory_mb.toFixed(0)}
              <span style={{ fontSize: 12, fontWeight: 400 }}>MB</span>
            </div>
          </div>
        </Col>
      </Row>

      {/* CPU & Memory Bars */}
      <div style={{ marginTop: 16, display: 'flex', gap: 24 }}>
        <div style={{ flex: 1 }}>
          <div style={{ color: '#888', fontSize: 11, marginBottom: 4 }}>CPU Usage</div>
          <Progress
            percent={metrics.cpu_percent}
            strokeColor={cpuColor}
            trailColor="rgba(255,255,255,0.1)"
            size="small"
            format={p => <span style={{ color: cpuColor }}>{p}%</span>}
          />
        </div>
        <div style={{ flex: 1 }}>
          <div style={{ color: '#888', fontSize: 11, marginBottom: 4 }}>Memory Usage</div>
          <Progress
            percent={metrics.memory_percent}
            strokeColor={memColor}
            trailColor="rgba(255,255,255,0.1)"
            size="small"
            format={p => <span style={{ color: memColor }}>{p}%</span>}
          />
        </div>
      </div>

      {/* Circuit Breakers */}
      {Object.keys(circuitBreakers).length > 0 && (
        <div style={{ marginTop: 16 }}>
          <div style={{ color: '#888', fontSize: 11, marginBottom: 8 }}>
            <SafetyCertificateOutlined style={{ marginRight: 4 }} />
            CIRCUIT BREAKERS
          </div>
          <Space wrap size="small">
            {Object.entries(circuitBreakers).map(([name, state]) => {
              const config = circuitStateConfig[state] || circuitStateConfig.closed;
              return (
                <Tooltip key={name} title={`${name}: ${config.label}`}>
                  <Tag
                    color={config.color}
                    icon={config.icon}
                    style={{
                      margin: 0,
                      background: `${config.color}20`,
                      border: `1px solid ${config.color}40`,
                    }}
                  >
                    {name}
                  </Tag>
                </Tooltip>
              );
            })}
          </Space>
        </div>
      )}

      {/* Footer Stats */}
      <div style={{
        marginTop: 16,
        paddingTop: 12,
        borderTop: '1px solid rgba(255,255,255,0.1)',
        display: 'flex',
        justifyContent: 'space-between',
        fontSize: 11,
        color: '#666',
      }}>
        <span>
          Errors: <span style={{ color: errorCount > 0 ? '#ff4d4f' : '#52c41a' }}>{errorCount}</span>
        </span>
        <span>
          Slow Requests: <span style={{ color: slowRequests > 0 ? '#faad14' : '#52c41a' }}>{slowRequests}</span>
        </span>
        <span>
          Last update: {lastHeartbeat ? new Date(lastHeartbeat).toLocaleTimeString() : '-'}
        </span>
      </div>
    </div>
  );
}

export default BackendMetricsPanel;
