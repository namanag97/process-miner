/**
 * Process Context Builder - Utility to format process analytics data for LLM prompts
 */

import type { ProcessSummaryData } from '@/src/shared/design-system';

/**
 * Formats duration in seconds to human-readable string
 */
function formatDuration(seconds: number): string {
  if (seconds < 60) return `${Math.round(seconds)} seconds`;
  if (seconds < 3600) return `${Math.round(seconds / 60)} minutes`;
  if (seconds < 86400) return `${(seconds / 3600).toFixed(1)} hours`;
  return `${(seconds / 86400).toFixed(1)} days`;
}

/**
 * Builds a structured text context from process summary data for LLM consumption
 */
export function buildProcessContext(summary: ProcessSummaryData, processName: string): string {
  const lines: string[] = [];

  // Header
  lines.push(`## Process Analysis: ${processName}`);
  lines.push('');

  // Cycle Time Stats
  lines.push('### Cycle Time Statistics');
  lines.push(`- Average: ${formatDuration(summary.cycleTime.avgSeconds)}`);
  lines.push(`- Median: ${formatDuration(summary.cycleTime.medianSeconds)}`);
  lines.push(`- Min: ${formatDuration(summary.cycleTime.minSeconds)}`);
  lines.push(`- Max: ${formatDuration(summary.cycleTime.maxSeconds)}`);
  lines.push('');

  // Throughput
  lines.push('### Throughput Metrics');
  lines.push(`- Total Cases: ${summary.throughput.totalCases.toLocaleString()}`);
  lines.push(`- Completed Cases: ${summary.throughput.completedCases.toLocaleString()}`);
  lines.push(`- Cases per Day: ${summary.throughput.casesPerDay.toFixed(1)}`);
  lines.push(`- Cases per Week: ${summary.throughput.casesPerWeek.toFixed(1)}`);
  lines.push('');

  // Bottlenecks
  if (summary.bottlenecks.length > 0) {
    lines.push('### Identified Bottlenecks');
    const actualBottlenecks = summary.bottlenecks.filter(b => b.isBottleneck);
    if (actualBottlenecks.length > 0) {
      actualBottlenecks.forEach((b, i) => {
        lines.push(`${i + 1}. **${b.activity}** (Severity: ${b.severity})`);
        lines.push(`   - Average waiting time: ${formatDuration(b.avgWaitingTimeSeconds)}`);
      });
    } else {
      lines.push('- No significant bottlenecks detected');
    }
    lines.push('');
  }

  // Rework
  if (summary.rework.totalReworkCases > 0) {
    lines.push('### Rework Analysis');
    lines.push(`- Total cases with rework: ${summary.rework.totalReworkCases.toLocaleString()} (${summary.rework.reworkPercentage.toFixed(1)}%)`);
    if (summary.rework.activities.length > 0) {
      lines.push('- Top rework activities:');
      summary.rework.activities.slice(0, 5).forEach((r) => {
        lines.push(`  - ${r.activity}: ${r.reworkCount} occurrences (${r.reworkPercentage.toFixed(1)}%)`);
      });
    }
    lines.push('');
  }

  // Patterns
  if (summary.patterns.length > 0) {
    lines.push('### Frequent Patterns');
    summary.patterns.slice(0, 5).forEach((p, i) => {
      lines.push(`${i + 1}. ${p.pattern.join(' → ')} (Support: ${(p.support * 100).toFixed(1)}%, Frequency: ${p.frequency})`);
    });
    lines.push('');
  }

  return lines.join('\n');
}

/**
 * Builds a shorter context summary for quick LLM reference
 */
export function buildQuickContext(summary: ProcessSummaryData, processName: string): string {
  const bottleneckCount = summary.bottlenecks.filter(b => b.isBottleneck).length;
  
  return [
    `Process: ${processName}`,
    `Cases: ${summary.throughput.totalCases.toLocaleString()}`,
    `Avg Cycle Time: ${formatDuration(summary.cycleTime.avgSeconds)}`,
    `Bottlenecks: ${bottleneckCount}`,
    `Rework Rate: ${summary.rework.reworkPercentage.toFixed(1)}%`,
  ].join(' | ');
}

/**
 * Generates a system prompt for the AI assistant with process context
 */
export function buildSystemPrompt(summary: ProcessSummaryData, processName: string): string {
  const context = buildProcessContext(summary, processName);
  
  return `You are an expert process mining analyst assistant. You help users understand their business processes, identify inefficiencies, and suggest improvements.

You have access to the following process data:

${context}

When answering questions:
1. Be specific and reference the actual data provided
2. Highlight bottlenecks and inefficiencies when relevant
3. Provide actionable recommendations
4. Use clear, business-friendly language
5. If asked about something not in the data, acknowledge the limitation

Focus on practical insights that can help improve process performance.`;
}
