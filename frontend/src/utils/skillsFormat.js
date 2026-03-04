/**
 * Format a skill or comma-separated skills string: title case per word,
 * but keep known acronyms in ALL CAPS (e.g. AWS, API, SQL).
 */
const ACRONYMS = new Set([
  'AWS', 'API', 'SQL', 'HTML', 'CSS', 'JS', 'JSON', 'XML', 'REST', 'UI', 'UX',
  'IDE', 'SDK', 'MySQL', 'PHP', 'CRM', 'ERP', 'HTTP', 'HTTPS', 'URL', 'DOM',
  'OOP', 'SaaS', 'PaaS', 'IaaS', 'CI', 'CD', 'CI/CD', 'JWT', 'REST', 'SOAP', 'MVC',
  'MVP', 'KPI', 'FAQ', 'ID', 'IT', 'QA', 'PM', 'HR', 'AI', 'ML', 'IoT',
  '.NET', 'ASP', 'ADO', 'ODBC', 'JDBC', 'JVM', 'CLI', 'GUI', 'SSO', 'LDAP',
  'OAuth', 'SAML', 'CORS', 'CSP', 'SEO', 'CMS', 'ERP', 'BI', 'ETL', 'API',
  'REST', 'GraphQL', 'gRPC', 'TCP', 'UDP', 'IP', 'DNS', 'SSL', 'TLS', 'VPN',
  'VM', 'OS', 'DB', 'NoSQL', 'MongoDB', 'Redis', 'Kafka', 'Docker', 'K8s',
  'Kubernetes', 'GCP', 'Azure', 'S3', 'EC2', 'Lambda', 'RDS', 'SQS',
  'SNS', 'IAM', 'VPC', 'CDN', 'SSH', 'FTP', 'SMTP', 'IMAP', 'POP3', 'NPM',
  'YARN', 'Git',
])

function formatWord(word) {
  if (!word || !word.trim()) return word
  const trimmed = word.trim()
  const upper = trimmed.toUpperCase()
  if (ACRONYMS.has(upper)) return upper
  if (trimmed.startsWith('.') && trimmed.length > 1) {
    return '.' + formatWord(trimmed.slice(1))
  }
  return trimmed.charAt(0).toUpperCase() + trimmed.slice(1).toLowerCase()
}

function formatSkill(skill) {
  if (!skill || typeof skill !== 'string') return ''
  return skill
    .trim()
    .split(/\s+/)
    .map(formatWord)
    .join(' ')
}

/**
 * Format a comma-separated skills string for display (title case, acronyms in caps).
 */
export function formatSkillsString(skillsStr) {
  if (!skillsStr) return ''
  if (Array.isArray(skillsStr)) {
    return skillsStr.map((s) => formatSkill(String(s.skill_name || s))).join(', ')
  }
  return skillsStr
    .split(',')
    .map((s) => formatSkill(s))
    .join(', ')
}

/**
 * Format a single skill label (e.g. for matched_skills array).
 */
export function formatSkillLabel(skill) {
  return formatSkill(String(skill || ''))
}
