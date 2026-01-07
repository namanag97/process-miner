/**
 * CreateProjectModal - Modal for creating a new project
 */

import { Modal, Form, Input, Button } from 'antd';
import type { FormInstance } from 'antd';
import { tokens } from '@lumina/design-system';
import type { CreateProjectInput } from '../types';

interface CreateProjectModalProps {
  open: boolean;
  onCancel: () => void;
  onSubmit: (values: CreateProjectInput) => void;
  loading?: boolean;
  form: FormInstance<CreateProjectInput>;
}

export function CreateProjectModal({
  open,
  onCancel,
  onSubmit,
  loading = false,
  form,
}: CreateProjectModalProps) {
  return (
    <Modal
      title="Create New Project"
      open={open}
      onCancel={onCancel}
      footer={null}
      destroyOnClose
    >
      <Form
        form={form}
        layout="vertical"
        onFinish={onSubmit}
        style={{ marginTop: tokens.spacing[4] }}
      >
        <Form.Item
          name="name"
          label="Project Name"
          rules={[{ required: true, message: 'Please enter a project name' }]}
        >
          <Input placeholder="e.g., Q4 Process Analysis" autoFocus />
        </Form.Item>

        <Form.Item name="description" label="Description (optional)">
          <Input.TextArea
            rows={3}
            placeholder="Brief description of the project"
          />
        </Form.Item>

        <Form.Item style={{ marginBottom: 0, textAlign: 'right' }}>
          <Button onClick={onCancel} style={{ marginRight: 8 }}>
            Cancel
          </Button>
          <Button type="primary" htmlType="submit" loading={loading}>
            Create Project
          </Button>
        </Form.Item>
      </Form>
    </Modal>
  );
}

export default CreateProjectModal;
