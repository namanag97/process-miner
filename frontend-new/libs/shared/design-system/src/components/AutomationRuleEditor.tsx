/**
 * AutomationRuleEditor - Rule configuration for process automation
 *
 * Enables users to create and edit automation rules with conditions,
 * triggers, and actions for process mining alerts and interventions.
 *
 * @example
 * <AutomationRuleEditor
 *   rule={existingRule}
 *   onSave={handleSaveRule}
 *   onCancel={() => setEditorOpen(false)}
 * />
 */

import React, { useState, useCallback } from 'react';
import {
  Card,
  Button,
  Space,
  Typography,
  Form,
  Input,
  Select,
  Switch,
  InputNumber,
  Row,
  Col,
  Divider,
  Tag,
  Alert,
  Steps,
  Tooltip,
} from 'antd';
import {
  PlusOutlined,
  DeleteOutlined,
  ThunderboltOutlined,
  BellOutlined,
  MailOutlined,
  ApiOutlined,
  ClockCircleOutlined,
  FilterOutlined,
  PlayCircleOutlined,
  CheckCircleOutlined,
  InfoCircleOutlined,
} from '@ant-design/icons';
import { SeverityBadge, type SeverityLevel } from './StatusBadge';
import { tokens } from '../theme';

const { Text, Title, Paragraph } = Typography;
const { Option } = Select;

// ============================================
// Types
// ============================================

export type TriggerType =
  | 'threshold_exceeded'
  | 'sla_approaching'
  | 'bottleneck_detected'
  | 'deviation_found'
  | 'prediction_alert'
  | 'scheduled'
  | 'manual';

export type ActionType =
  | 'send_email'
  | 'send_slack'
  | 'send_webhook'
  | 'create_ticket'
  | 'update_priority'
  | 'assign_resource'
  | 'trigger_workflow';

export type ConditionOperator =
  | 'equals'
  | 'not_equals'
  | 'greater_than'
  | 'less_than'
  | 'contains'
  | 'not_contains'
  | 'in'
  | 'not_in';

export interface RuleCondition {
  id: string;
  field: string;
  operator: ConditionOperator;
  value: any;
}

export interface RuleAction {
  id: string;
  type: ActionType;
  config: Record<string, any>;
}

export interface AutomationRule {
  id?: string;
  name: string;
  description?: string;
  enabled: boolean;
  trigger: TriggerType;
  triggerConfig?: Record<string, any>;
  conditions: RuleCondition[];
  conditionLogic: 'and' | 'or';
  actions: RuleAction[];
  severity: SeverityLevel;
  cooldownMinutes?: number;
  createdAt?: Date;
  updatedAt?: Date;
}

export interface AutomationRuleEditorProps {
  /** Existing rule to edit (undefined for new) */
  rule?: AutomationRule;
  /** Save handler */
  onSave: (rule: AutomationRule) => void;
  /** Cancel handler */
  onCancel: () => void;
  /** Available fields for conditions */
  availableFields?: Array<{ value: string; label: string }>;
  /** Loading state */
  loading?: boolean;
}

// ============================================
// Configuration
// ============================================

const TRIGGER_OPTIONS: Array<{ value: TriggerType; label: string; icon: React.ReactNode }> = [
  { value: 'threshold_exceeded', label: 'Threshold Exceeded', icon: <ThunderboltOutlined /> },
  { value: 'sla_approaching', label: 'SLA Approaching', icon: <ClockCircleOutlined /> },
  { value: 'bottleneck_detected', label: 'Bottleneck Detected', icon: <FilterOutlined /> },
  { value: 'deviation_found', label: 'Deviation Found', icon: <BellOutlined /> },
  { value: 'prediction_alert', label: 'Prediction Alert', icon: <ThunderboltOutlined /> },
  { value: 'scheduled', label: 'Scheduled', icon: <ClockCircleOutlined /> },
  { value: 'manual', label: 'Manual Trigger', icon: <PlayCircleOutlined /> },
];

const ACTION_OPTIONS: Array<{ value: ActionType; label: string; icon: React.ReactNode }> = [
  { value: 'send_email', label: 'Send Email', icon: <MailOutlined /> },
  { value: 'send_slack', label: 'Send to Slack', icon: <ApiOutlined /> },
  { value: 'send_webhook', label: 'Call Webhook', icon: <ApiOutlined /> },
  { value: 'create_ticket', label: 'Create Ticket', icon: <PlusOutlined /> },
  { value: 'update_priority', label: 'Update Priority', icon: <ThunderboltOutlined /> },
  { value: 'assign_resource', label: 'Assign Resource', icon: <PlayCircleOutlined /> },
  { value: 'trigger_workflow', label: 'Trigger Workflow', icon: <PlayCircleOutlined /> },
];

const OPERATOR_OPTIONS: Array<{ value: ConditionOperator; label: string }> = [
  { value: 'equals', label: 'Equals' },
  { value: 'not_equals', label: 'Not Equals' },
  { value: 'greater_than', label: 'Greater Than' },
  { value: 'less_than', label: 'Less Than' },
  { value: 'contains', label: 'Contains' },
  { value: 'not_contains', label: 'Not Contains' },
];

const DEFAULT_FIELDS = [
  { value: 'case_duration', label: 'Case Duration' },
  { value: 'activity_name', label: 'Activity Name' },
  { value: 'resource', label: 'Resource' },
  { value: 'case_value', label: 'Case Value' },
  { value: 'wait_time', label: 'Wait Time' },
  { value: 'rework_count', label: 'Rework Count' },
];

// ============================================
// Helper functions
// ============================================

function generateId(): string {
  return `${Date.now()}-${Math.random().toString(36).substr(2, 9)}`;
}

const DEFAULT_RULE: AutomationRule = {
  name: '',
  description: '',
  enabled: true,
  trigger: 'threshold_exceeded',
  conditions: [],
  conditionLogic: 'and',
  actions: [],
  severity: 'medium',
  cooldownMinutes: 60,
};

// ============================================
// AutomationRuleEditor Component
// ============================================

export function AutomationRuleEditor({
  rule,
  onSave,
  onCancel,
  availableFields = DEFAULT_FIELDS,
  loading = false,
}: AutomationRuleEditorProps) {
  const [form] = Form.useForm();
  const [currentStep, setCurrentStep] = useState(0);
  const [ruleState, setRuleState] = useState<AutomationRule>(rule || DEFAULT_RULE);

  // Add condition
  const handleAddCondition = useCallback(() => {
    setRuleState((prev) => ({
      ...prev,
      conditions: [
        ...prev.conditions,
        { id: generateId(), field: '', operator: 'equals', value: '' },
      ],
    }));
  }, []);

  // Remove condition
  const handleRemoveCondition = useCallback((id: string) => {
    setRuleState((prev) => ({
      ...prev,
      conditions: prev.conditions.filter((c) => c.id !== id),
    }));
  }, []);

  // Update condition
  const handleUpdateCondition = useCallback(
    (id: string, updates: Partial<RuleCondition>) => {
      setRuleState((prev) => ({
        ...prev,
        conditions: prev.conditions.map((c) =>
          c.id === id ? { ...c, ...updates } : c
        ),
      }));
    },
    []
  );

  // Add action
  const handleAddAction = useCallback(() => {
    setRuleState((prev) => ({
      ...prev,
      actions: [...prev.actions, { id: generateId(), type: 'send_email', config: {} }],
    }));
  }, []);

  // Remove action
  const handleRemoveAction = useCallback((id: string) => {
    setRuleState((prev) => ({
      ...prev,
      actions: prev.actions.filter((a) => a.id !== id),
    }));
  }, []);

  // Update action
  const handleUpdateAction = useCallback(
    (id: string, updates: Partial<RuleAction>) => {
      setRuleState((prev) => ({
        ...prev,
        actions: prev.actions.map((a) => (a.id === id ? { ...a, ...updates } : a)),
      }));
    },
    []
  );

  // Save rule
  const handleSave = useCallback(() => {
    onSave(ruleState);
  }, [ruleState, onSave]);

  // Validation
  const isValid = ruleState.name.trim() !== '' && ruleState.actions.length > 0;

  const steps = [
    { title: 'Basic Info', icon: <InfoCircleOutlined /> },
    { title: 'Trigger', icon: <ThunderboltOutlined /> },
    { title: 'Conditions', icon: <FilterOutlined /> },
    { title: 'Actions', icon: <PlayCircleOutlined /> },
  ];

  return (
    <Card
      title={
        <Space>
          <ThunderboltOutlined style={{ color: tokens.colors.primary[500] }} />
          <span>{rule ? 'Edit Automation Rule' : 'Create Automation Rule'}</span>
        </Space>
      }
      extra={
        <Space>
          <Button onClick={onCancel}>Cancel</Button>
          <Button type="primary" onClick={handleSave} disabled={!isValid} loading={loading}>
            Save Rule
          </Button>
        </Space>
      }
    >
      <Steps
        current={currentStep}
        items={steps}
        style={{ marginBottom: tokens.spacing[6] }}
        onChange={setCurrentStep}
      />

      <Divider />

      {/* Step 1: Basic Info */}
      {currentStep === 0 && (
        <div style={{ maxWidth: 600 }}>
          <Form layout="vertical">
            <Form.Item label="Rule Name" required>
              <Input
                placeholder="e.g., SLA Breach Alert"
                value={ruleState.name}
                onChange={(e) => setRuleState((prev) => ({ ...prev, name: e.target.value }))}
              />
            </Form.Item>
            <Form.Item label="Description">
              <Input.TextArea
                rows={3}
                placeholder="Describe what this rule does..."
                value={ruleState.description}
                onChange={(e) => setRuleState((prev) => ({ ...prev, description: e.target.value }))}
              />
            </Form.Item>
            <Row gutter={16}>
              <Col span={12}>
                <Form.Item label="Severity">
                  <Select
                    value={ruleState.severity}
                    onChange={(value) => setRuleState((prev) => ({ ...prev, severity: value }))}
                  >
                    <Option value="critical">Critical</Option>
                    <Option value="high">High</Option>
                    <Option value="medium">Medium</Option>
                    <Option value="low">Low</Option>
                    <Option value="info">Info</Option>
                  </Select>
                </Form.Item>
              </Col>
              <Col span={12}>
                <Form.Item label="Cooldown (minutes)">
                  <InputNumber
                    min={0}
                    value={ruleState.cooldownMinutes}
                    onChange={(value) =>
                      setRuleState((prev) => ({ ...prev, cooldownMinutes: value || 0 }))
                    }
                    style={{ width: '100%' }}
                  />
                </Form.Item>
              </Col>
            </Row>
            <Form.Item label="Enabled">
              <Switch
                checked={ruleState.enabled}
                onChange={(checked) => setRuleState((prev) => ({ ...prev, enabled: checked }))}
              />
            </Form.Item>
          </Form>
        </div>
      )}

      {/* Step 2: Trigger */}
      {currentStep === 1 && (
        <div>
          <Paragraph type="secondary" style={{ marginBottom: tokens.spacing[4] }}>
            Select when this rule should be triggered.
          </Paragraph>
          <Row gutter={[16, 16]}>
            {TRIGGER_OPTIONS.map((trigger) => (
              <Col xs={12} sm={8} md={6} key={trigger.value}>
                <Card
                  hoverable
                  onClick={() => setRuleState((prev) => ({ ...prev, trigger: trigger.value }))}
                  className="card-hover-lift"
                  style={{
                    textAlign: 'center',
                    border:
                      ruleState.trigger === trigger.value
                        ? `2px solid ${tokens.colors.primary[500]}`
                        : undefined,
                    backgroundColor:
                      ruleState.trigger === trigger.value
                        ? tokens.colors.primary[50]
                        : undefined,
                  }}
                  styles={{ body: { padding: tokens.spacing[4] } }}
                >
                  <div
                    style={{
                      fontSize: 24,
                      color: tokens.colors.primary[500],
                      marginBottom: tokens.spacing[2],
                    }}
                  >
                    {trigger.icon}
                  </div>
                  <Text strong style={{ fontSize: tokens.fontSize.sm }}>
                    {trigger.label}
                  </Text>
                </Card>
              </Col>
            ))}
          </Row>
        </div>
      )}

      {/* Step 3: Conditions */}
      {currentStep === 2 && (
        <div>
          <div
            style={{
              display: 'flex',
              justifyContent: 'space-between',
              alignItems: 'center',
              marginBottom: tokens.spacing[4],
            }}
          >
            <Space>
              <Text>Match</Text>
              <Select
                value={ruleState.conditionLogic}
                onChange={(value) => setRuleState((prev) => ({ ...prev, conditionLogic: value }))}
                style={{ width: 100 }}
              >
                <Option value="and">ALL</Option>
                <Option value="or">ANY</Option>
              </Select>
              <Text>of the following conditions</Text>
            </Space>
            <Button icon={<PlusOutlined />} onClick={handleAddCondition}>
              Add Condition
            </Button>
          </div>

          {ruleState.conditions.length === 0 ? (
            <Alert
              message="No conditions defined"
              description="Rules without conditions will trigger for all events matching the trigger type."
              type="info"
              showIcon
            />
          ) : (
            <Space direction="vertical" style={{ width: '100%' }}>
              {ruleState.conditions.map((condition, index) => (
                <Card key={condition.id} size="small">
                  <Row gutter={12} align="middle">
                    <Col flex="1">
                      <Select
                        placeholder="Select field"
                        value={condition.field || undefined}
                        onChange={(value) => handleUpdateCondition(condition.id, { field: value })}
                        style={{ width: '100%' }}
                      >
                        {availableFields.map((f) => (
                          <Option key={f.value} value={f.value}>
                            {f.label}
                          </Option>
                        ))}
                      </Select>
                    </Col>
                    <Col flex="1">
                      <Select
                        value={condition.operator}
                        onChange={(value) =>
                          handleUpdateCondition(condition.id, { operator: value })
                        }
                        style={{ width: '100%' }}
                      >
                        {OPERATOR_OPTIONS.map((op) => (
                          <Option key={op.value} value={op.value}>
                            {op.label}
                          </Option>
                        ))}
                      </Select>
                    </Col>
                    <Col flex="1">
                      <Input
                        placeholder="Value"
                        value={condition.value}
                        onChange={(e) =>
                          handleUpdateCondition(condition.id, { value: e.target.value })
                        }
                      />
                    </Col>
                    <Col>
                      <Button
                        type="text"
                        danger
                        icon={<DeleteOutlined />}
                        onClick={() => handleRemoveCondition(condition.id)}
                      />
                    </Col>
                  </Row>
                </Card>
              ))}
            </Space>
          )}
        </div>
      )}

      {/* Step 4: Actions */}
      {currentStep === 3 && (
        <div>
          <div
            style={{
              display: 'flex',
              justifyContent: 'space-between',
              alignItems: 'center',
              marginBottom: tokens.spacing[4],
            }}
          >
            <Text>Actions to perform when rule triggers:</Text>
            <Button icon={<PlusOutlined />} onClick={handleAddAction}>
              Add Action
            </Button>
          </div>

          {ruleState.actions.length === 0 ? (
            <Alert
              message="At least one action is required"
              description="Add an action to specify what happens when this rule triggers."
              type="warning"
              showIcon
            />
          ) : (
            <Space direction="vertical" style={{ width: '100%' }}>
              {ruleState.actions.map((action, index) => {
                const actionOption = ACTION_OPTIONS.find((a) => a.value === action.type);
                return (
                  <Card key={action.id} size="small">
                    <Row gutter={12} align="middle">
                      <Col flex="0 0 40px">
                        <div
                          style={{
                            width: 32,
                            height: 32,
                            borderRadius: tokens.radius.sm,
                            backgroundColor: tokens.colors.primary[50],
                            display: 'flex',
                            alignItems: 'center',
                            justifyContent: 'center',
                            color: tokens.colors.primary[500],
                          }}
                        >
                          {actionOption?.icon}
                        </div>
                      </Col>
                      <Col flex="1">
                        <Select
                          value={action.type}
                          onChange={(value) => handleUpdateAction(action.id, { type: value })}
                          style={{ width: '100%' }}
                        >
                          {ACTION_OPTIONS.map((a) => (
                            <Option key={a.value} value={a.value}>
                              <Space>
                                {a.icon}
                                {a.label}
                              </Space>
                            </Option>
                          ))}
                        </Select>
                      </Col>
                      <Col flex="2">
                        {action.type === 'send_email' && (
                          <Input
                            placeholder="Recipient email"
                            value={action.config.email}
                            onChange={(e) =>
                              handleUpdateAction(action.id, {
                                config: { ...action.config, email: e.target.value },
                              })
                            }
                          />
                        )}
                        {action.type === 'send_webhook' && (
                          <Input
                            placeholder="Webhook URL"
                            value={action.config.url}
                            onChange={(e) =>
                              handleUpdateAction(action.id, {
                                config: { ...action.config, url: e.target.value },
                              })
                            }
                          />
                        )}
                        {action.type === 'send_slack' && (
                          <Input
                            placeholder="Slack channel"
                            value={action.config.channel}
                            onChange={(e) =>
                              handleUpdateAction(action.id, {
                                config: { ...action.config, channel: e.target.value },
                              })
                            }
                          />
                        )}
                      </Col>
                      <Col>
                        <Button
                          type="text"
                          danger
                          icon={<DeleteOutlined />}
                          onClick={() => handleRemoveAction(action.id)}
                        />
                      </Col>
                    </Row>
                  </Card>
                );
              })}
            </Space>
          )}
        </div>
      )}

      {/* Navigation */}
      <Divider />
      <div style={{ display: 'flex', justifyContent: 'space-between' }}>
        <Button disabled={currentStep === 0} onClick={() => setCurrentStep((s) => s - 1)}>
          Previous
        </Button>
        {currentStep < steps.length - 1 ? (
          <Button type="primary" onClick={() => setCurrentStep((s) => s + 1)}>
            Next
          </Button>
        ) : (
          <Button type="primary" onClick={handleSave} disabled={!isValid} loading={loading}>
            <CheckCircleOutlined /> Save Rule
          </Button>
        )}
      </div>
    </Card>
  );
}

export default AutomationRuleEditor;
