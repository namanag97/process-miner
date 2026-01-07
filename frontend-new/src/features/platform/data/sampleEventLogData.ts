/**
 * Sample Event Log Data for Process Mining Showcase
 * 
 * Generates realistic "Order-to-Cash" process data with:
 * - ~250 cases with 6-12 activities each
 * - Realistic activity sequences, timestamps, and resources
 */

// Types for sample data
export interface SampleEvent {
    caseId: string;
    activity: string;
    timestamp: Date;
    resource: string;
}

export interface SampleCase {
    caseId: string;
    events: SampleEvent[];
    variant: string;
}

// Activity definitions
export const ACTIVITIES = [
    'Order Received',
    'Validate Order',
    'Credit Check',
    'Order Approved',
    'Order Rejected',
    'Prepare Shipment',
    'Ship Order',
    'Deliver Order',
    'Receive Payment',
    'Close Case',
] as const;

export type Activity = typeof ACTIVITIES[number];

// Resources (employees)
export const RESOURCES = [
    'Sarah Chen',
    'Mike Johnson',
    'Emma Williams',
    'David Brown',
    'Lisa Garcia',
    'James Wilson',
    'Maria Martinez',
    'Robert Taylor',
] as const;

// Common process variants (activity sequences)
const HAPPY_PATH = ['Order Received', 'Validate Order', 'Credit Check', 'Order Approved', 'Prepare Shipment', 'Ship Order', 'Deliver Order', 'Receive Payment', 'Close Case'];
const REJECTED_PATH = ['Order Received', 'Validate Order', 'Credit Check', 'Order Rejected', 'Close Case'];
const REWORK_PATH = ['Order Received', 'Validate Order', 'Order Received', 'Validate Order', 'Credit Check', 'Order Approved', 'Prepare Shipment', 'Ship Order', 'Deliver Order', 'Receive Payment', 'Close Case'];
const FAST_TRACK = ['Order Received', 'Order Approved', 'Prepare Shipment', 'Ship Order', 'Deliver Order', 'Receive Payment', 'Close Case'];
const DELAYED_PAYMENT = ['Order Received', 'Validate Order', 'Credit Check', 'Order Approved', 'Prepare Shipment', 'Ship Order', 'Deliver Order', 'Receive Payment', 'Receive Payment', 'Close Case'];

const VARIANTS: { path: string[]; weight: number }[] = [
    { path: HAPPY_PATH, weight: 45 },
    { path: REJECTED_PATH, weight: 15 },
    { path: REWORK_PATH, weight: 10 },
    { path: FAST_TRACK, weight: 20 },
    { path: DELAYED_PAYMENT, weight: 10 },
];

// Generate random timestamp within business hours
function generateTimestamp(baseDate: Date, hoursOffset: number): Date {
    const date = new Date(baseDate);
    date.setHours(date.getHours() + hoursOffset + Math.random() * 4);
    return date;
}

// Generate a single case
function generateCase(caseNumber: number, baseDate: Date): SampleCase {
    // Select variant based on weights
    const totalWeight = VARIANTS.reduce((sum, v) => sum + v.weight, 0);
    let random = Math.random() * totalWeight;
    let selectedVariant = VARIANTS[0];

    for (const variant of VARIANTS) {
        random -= variant.weight;
        if (random <= 0) {
            selectedVariant = variant;
            break;
        }
    }

    const events: SampleEvent[] = [];
    let currentTime = new Date(baseDate);
    currentTime.setDate(currentTime.getDate() + Math.floor(caseNumber / 5));

    for (const activity of selectedVariant.path) {
        events.push({
            caseId: `CASE-${String(caseNumber).padStart(4, '0')}`,
            activity,
            timestamp: generateTimestamp(currentTime, 0),
            resource: RESOURCES[Math.floor(Math.random() * RESOURCES.length)],
        });
        // Add random delay between activities (1-24 hours)
        currentTime = new Date(currentTime.getTime() + (1 + Math.random() * 23) * 60 * 60 * 1000);
    }

    return {
        caseId: `CASE-${String(caseNumber).padStart(4, '0')}`,
        events,
        variant: selectedVariant.path.join(' → '),
    };
}

// Generate full sample dataset
export function generateSampleEventLog(numCases: number = 250): SampleCase[] {
    const baseDate = new Date('2025-01-01T08:00:00');
    const cases: SampleCase[] = [];

    for (let i = 1; i <= numCases; i++) {
        cases.push(generateCase(i, baseDate));
    }

    return cases;
}

// Pre-generated sample data (for consistent results)
export const SAMPLE_EVENT_LOG = generateSampleEventLog(250);

// Aggregated statistics
export const SAMPLE_STATISTICS = {
    totalCases: SAMPLE_EVENT_LOG.length,
    totalEvents: SAMPLE_EVENT_LOG.reduce((sum, c) => sum + c.events.length, 0),
    uniqueActivities: ACTIVITIES.length,
    uniqueResources: RESOURCES.length,
    uniqueVariants: new Set(SAMPLE_EVENT_LOG.map(c => c.variant)).size,
    startActivities: { 'Order Received': SAMPLE_EVENT_LOG.length },
    endActivities: {
        'Close Case': SAMPLE_EVENT_LOG.length,
    },
} as const;
