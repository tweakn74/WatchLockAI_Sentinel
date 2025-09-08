import { type ClassValue, clsx } from "clsx";
import { twMerge } from "tailwind-merge";
import { format, formatDistanceToNow } from 'date-fns';

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs));
}

// Date formatting utilities
export function formatDate(date: string | Date) {
  return format(new Date(date), 'MMM dd, yyyy HH:mm');
}

export function formatTimeAgo(date: string | Date) {
  return formatDistanceToNow(new Date(date), { addSuffix: true });
}

// Severity color mapping
export function getSeverityColor(severity: string) {
  switch (severity) {
    case 'critical':
      return 'text-red-600 bg-red-50 border-red-200';
    case 'high':
      return 'text-orange-600 bg-orange-50 border-orange-200';
    case 'medium':
      return 'text-yellow-600 bg-yellow-50 border-yellow-200';
    case 'low':
      return 'text-blue-600 bg-blue-50 border-blue-200';
    default:
      return 'text-gray-600 bg-gray-50 border-gray-200';
  }
}

// Status color mapping
export function getStatusColor(status: string) {
  switch (status) {
    case 'online':
    case 'resolved':
    case 'completed':
      return 'text-green-600 bg-green-50 border-green-200';
    case 'offline':
    case 'open':
    case 'pending':
      return 'text-red-600 bg-red-50 border-red-200';
    case 'investigating':
    case 'in_progress':
    case 'executing':
      return 'text-yellow-600 bg-yellow-50 border-yellow-200';
    case 'false_positive':
    case 'rejected':
      return 'text-gray-600 bg-gray-50 border-gray-200';
    default:
      return 'text-blue-600 bg-blue-50 border-blue-200';
  }
}

// Agent status indicators
export function getAgentStatusIndicator(status: string) {
  switch (status) {
    case 'online':
      return '🟢';
    case 'offline':
      return '🔴';
    case 'error':
      return '🟠';
    default:
      return '⚪';
  }
}

// MITRE ATT&CK technique mapping
export function getMitreTechniqueName(technique: string) {
  const mitreMap: Record<string, string> = {
    'T1055': 'Process Injection',
    'T1059': 'Command and Scripting Interpreter',
    'T1071': 'Application Layer Protocol',
    'T1090': 'Proxy',
    'T1105': 'Ingress Tool Transfer',
    'T1204': 'User Execution',
    'T1566': 'Phishing',
    'T1583': 'Acquire Infrastructure',
    'T1588': 'Obtain Capabilities',
    'T1598': 'System Information Discovery'
  };
  
  return mitreMap[technique] || technique;
}

// Format file size
export function formatFileSize(bytes: number) {
  const sizes = ['Bytes', 'KB', 'MB', 'GB'];
  if (bytes === 0) return '0 Bytes';
  const i = Math.floor(Math.log(bytes) / Math.log(1024));
  return Math.round(bytes / Math.pow(1024, i) * 100) / 100 + ' ' + sizes[i];
}

// Calculate threat score color
export function getThreatScoreColor(score: number) {
  if (score >= 80) return 'text-red-600';
  if (score >= 60) return 'text-orange-600';
  if (score >= 40) return 'text-yellow-600';
  return 'text-green-600';
}

// Generate random ID
export function generateId() {
  return Math.random().toString(36).substr(2, 9);
}

// Truncate text
export function truncateText(text: string, maxLength: number) {
  if (text.length <= maxLength) return text;
  return text.substr(0, maxLength) + '...';
}