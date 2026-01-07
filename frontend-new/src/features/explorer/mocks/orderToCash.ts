
import type { DFGResponse, Variant, ProcessKPIs } from '../types';

// Local ActivityDetail type for mock data (matches explorer types)
interface MockActivityDetail {
    id: string;
    name: string;
    frequency: number;
    frequencyPercent: number;
    avgDuration: number;
    minDuration: number;
    maxDuration: number;
    isStart: boolean;
    isEnd: boolean;
    resources: string[];
}

// Dataset-like mock type for logInfo fallback
export interface MockDatasetInfo {
    id: string;
    name: string;
    status: string;
    createdAt: string;
    totalCases?: number;
    totalEvents?: number;
}

/**
 * Mock data for "Order to Cash" process
 * Used for fallback when backend is unavailable or for development
 */

export const mockOrderToCashDFG: DFGResponse = {
    nodes: [
        { id: 'start', label: 'Start', frequency: 1000, isStart: true, isEnd: false },
        { id: 'receive_order', label: 'Receive Order', frequency: 1000, isStart: false, isEnd: false },
        { id: 'check_credit', label: 'Check Credit', frequency: 950, isStart: false, isEnd: false },
        { id: 'approve_order', label: 'Approve Order', frequency: 900, isStart: false, isEnd: false },
        { id: 'ship_goods', label: 'Ship Goods', frequency: 900, isStart: false, isEnd: false },
        { id: 'send_invoice', label: 'Send Invoice', frequency: 900, isStart: false, isEnd: false },
        { id: 'receive_payment', label: 'Receive Payment', frequency: 850, isStart: false, isEnd: false },
        { id: 'close_order', label: 'Close Order', frequency: 850, isStart: false, isEnd: true },
        { id: 'cancel_order', label: 'Cancel Order', frequency: 150, isStart: false, isEnd: true },
    ],
    edges: [
        { source: 'start', target: 'receive_order', frequency: 1000, probability: 1.0, avgDuration: 0 },
        { source: 'receive_order', target: 'check_credit', frequency: 950, probability: 0.95, avgDuration: 3600 },
        { source: 'receive_order', target: 'cancel_order', frequency: 50, probability: 0.05, avgDuration: 1800 },
        { source: 'check_credit', target: 'approve_order', frequency: 900, probability: 0.95, avgDuration: 7200 },
        { source: 'check_credit', target: 'cancel_order', frequency: 50, probability: 0.05, avgDuration: 3600 },
        { source: 'approve_order', target: 'ship_goods', frequency: 900, probability: 1.0, avgDuration: 172800 },
        { source: 'ship_goods', target: 'send_invoice', frequency: 900, probability: 1.0, avgDuration: 43200 },
        { source: 'send_invoice', target: 'receive_payment', frequency: 850, probability: 0.94, avgDuration: 604800 },
        { source: 'send_invoice', target: 'cancel_order', frequency: 50, probability: 0.06, avgDuration: 864000 },
        { source: 'receive_payment', target: 'close_order', frequency: 850, probability: 1.0, avgDuration: 3600 },
    ],
    stats: {
        totalCases: 1000,
        totalActivities: 7400,
        totalTransitions: 7400,
    }
};

export const mockOrderToCashVariants: Variant[] = [
    {
        key: 'v1',
        activities: ['receive_order', 'check_credit', 'approve_order', 'ship_goods', 'send_invoice', 'receive_payment', 'close_order'],
        caseCount: 800,
        frequencyPercent: 80,
        avgDuration: 831600, // ~9.6 days
        complexityScore: 1
    },
    {
        key: 'v2',
        activities: ['receive_order', 'check_credit', 'cancel_order'],
        caseCount: 50,
        frequencyPercent: 5,
        avgDuration: 5400,
        complexityScore: 0.8
    },
    {
        key: 'v3',
        activities: ['receive_order', 'cancel_order'],
        caseCount: 50,
        frequencyPercent: 5,
        avgDuration: 1800,
        complexityScore: 0.8
    }
];

export const mockOrderToCashActivities: MockActivityDetail[] = [
    { id: 'receive_order', name: 'Receive Order', frequency: 1000, frequencyPercent: 100, avgDuration: 300, minDuration: 60, maxDuration: 600, isStart: true, isEnd: false, resources: ['System'] },
    { id: 'check_credit', name: 'Check Credit', frequency: 950, frequencyPercent: 95, avgDuration: 600, minDuration: 120, maxDuration: 1200, isStart: false, isEnd: false, resources: ['Credit Officer'] },
    { id: 'approve_order', name: 'Approve Order', frequency: 900, frequencyPercent: 90, avgDuration: 300, minDuration: 60, maxDuration: 600, isStart: false, isEnd: false, resources: ['Manager'] },
    { id: 'ship_goods', name: 'Ship Goods', frequency: 900, frequencyPercent: 90, avgDuration: 3600, minDuration: 1800, maxDuration: 7200, isStart: false, isEnd: false, resources: ['Warehouse'] },
    { id: 'send_invoice', name: 'Send Invoice', frequency: 900, frequencyPercent: 90, avgDuration: 300, minDuration: 60, maxDuration: 600, isStart: false, isEnd: false, resources: ['Finance'] },
    { id: 'receive_payment', name: 'Receive Payment', frequency: 850, frequencyPercent: 85, avgDuration: 300, minDuration: 60, maxDuration: 600, isStart: false, isEnd: false, resources: ['Finance'] },
    { id: 'close_order', name: 'Close Order', frequency: 850, frequencyPercent: 85, avgDuration: 0, minDuration: 0, maxDuration: 0, isStart: false, isEnd: true, resources: ['System'] },
    { id: 'cancel_order', name: 'Cancel Order', frequency: 150, frequencyPercent: 15, avgDuration: 0, minDuration: 0, maxDuration: 0, isStart: false, isEnd: true, resources: ['System'] },
];

export const mockOrderToCashLogInfo: MockDatasetInfo = {
    id: 'mock-order-to-cash',
    name: 'Order to Cash (Demo)',
    status: 'ready',
    createdAt: new Date().toISOString(),
    totalCases: 1000,
    totalEvents: 7400,
};

export const mockOrderToCashKPIs: ProcessKPIs = {
    totalCases: 1000,
    uniqueVariants: 15,
    uniqueActivities: 8,
    avgThroughputTime: 750000,
    happyPathPercent: 80,
    reworkRate: 5
};
