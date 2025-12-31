import {
  BarChartOutlined,
  ClockCircleOutlined,
  CalendarOutlined,
  WarningOutlined,
  RobotOutlined,
  BulbOutlined,
} from '@ant-design/icons';

export interface ProcessQuestion {
  id: string;
  icon: typeof BarChartOutlined;
  title: string;
  description: string;
  route?: (projectId: string, logId: string) => string;
  action?: 'feedback';
}

export const PROCESS_QUESTIONS: ProcessQuestion[] = [
  {
    id: 'process-overview',
    icon: BarChartOutlined,
    title: 'What does your process look like?',
    description: 'Get a comprehensive overview of your process with an interactive flow diagram.',
    route: (projectId, logId) => `/workspace/${projectId}/data/${logId}/explorer`,
  },
  {
    id: 'duration',
    icon: ClockCircleOutlined,
    title: 'How long does your process take?',
    description: 'Explore how inefficiencies affect your throughput time and cycle times.',
    route: (projectId, logId) => `/workspace/${projectId}/data/${logId}/kpi?tab=performance`,
  },
  {
    id: 'deadlines',
    icon: CalendarOutlined,
    title: 'Are you meeting your deadlines?',
    description: 'Analyze SLA compliance and maintain great relationships with customers.',
    route: (projectId, logId) => `/workspace/${projectId}/data/${logId}/kpi?tab=deadlines`,
  },
  {
    id: 'unwanted',
    icon: WarningOutlined,
    title: 'How many unwanted activities are in your process?',
    description: 'Find out how rework and exceptions affect your throughput time.',
    route: (projectId, logId) => `/workspace/${projectId}/data/${logId}/kpi?tab=unwanted`,
  },
  {
    id: 'automation',
    icon: RobotOutlined,
    title: 'How automated is your process?',
    description: 'Discover time savings potential from automation opportunities.',
    route: (projectId, logId) => `/workspace/${projectId}/data/${logId}/kpi?tab=automation`,
  },
  {
    id: 'custom',
    icon: BulbOutlined,
    title: 'Want to look into something else?',
    description: 'Tell us what other questions you have about your process.',
    action: 'feedback',
  },
];
