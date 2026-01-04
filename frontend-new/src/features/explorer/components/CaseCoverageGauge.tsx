/**
 * CaseCoverageGauge - Visual indicator for filtered case coverage
 *
 * Displays a circular progress gauge showing what percentage of cases
 * are currently visible based on applied filters.
 */

import { Progress, Typography } from 'antd';
import { tokens } from '@lumina/design-system';

const { Text } = Typography;

export interface CaseCoverageGaugeProps {
    /** Percentage of cases currently visible (0-100) */
    percent: number;
    /** Total number of visible cases */
    visibleCases: number;
    /** Total number of cases in dataset */
    totalCases: number;
    /** Size of the gauge circle */
    size?: number;
    /** Compact mode for smaller displays */
    compact?: boolean;
}

export function CaseCoverageGauge({
    percent,
    visibleCases,
    totalCases,
    size = 80,
    compact = false,
}: CaseCoverageGaugeProps) {
    // Color based on coverage - blue for full, amber for partial
    const strokeColor = percent >= 100
        ? tokens.colors.primary[500]
        : percent >= 50
            ? '#F59E0B'
            : '#EF4444';

    return (
        <div
            style={{
                display: 'flex',
                flexDirection: 'column',
                alignItems: 'center',
                padding: compact ? tokens.spacing[2] : tokens.spacing[4],
                background: `linear-gradient(135deg, ${tokens.colors.neutral[0]} 0%, ${tokens.colors.neutral[50]} 100%)`,
                borderRadius: tokens.radius.lg,
                border: `1px solid ${tokens.colors.neutral[200]}`,
            }}
        >
            <Progress
                type="circle"
                percent={percent}
                size={size}
                strokeColor={strokeColor}
                strokeWidth={8}
                trailColor={tokens.colors.neutral[100]}
                format={() => (
                    <div
                        style={{
                            display: 'flex',
                            flexDirection: 'column',
                            alignItems: 'center',
                            lineHeight: 1.2,
                        }}
                    >
                        <span
                            style={{
                                fontSize: compact ? 14 : 18,
                                fontWeight: 700,
                                color: tokens.colors.neutral[900],
                            }}
                        >
                            {percent.toFixed(0)}%
                        </span>
                        <span
                            style={{
                                fontSize: 10,
                                color: tokens.colors.neutral[500],
                            }}
                        >
                            of cases
                        </span>
                    </div>
                )}
            />
            <Text
                style={{
                    marginTop: tokens.spacing[2],
                    fontSize: 11,
                    color: tokens.colors.neutral[600],
                }}
            >
                {visibleCases.toLocaleString()} of {totalCases.toLocaleString()}
            </Text>
        </div>
    );
}

export default CaseCoverageGauge;
