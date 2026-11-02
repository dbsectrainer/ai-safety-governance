const AUDIT_MESSAGES: Record<string, string> = {
  'run_checks:compliance_check': 'Ran compliance checks',
  'create:compliance_record': 'Created compliance record',
  'update:compliance_record': 'Updated compliance record',
  'delete:compliance_record': 'Deleted compliance record',
  'create:model_version': 'Registered model version',
  'update:model_version': 'Updated model version',
  'delete:model_version': 'Deleted model version',
  'create:user': 'Created user',
  'update:user': 'Updated user',
  'delete:user': 'Deleted user',
  'update:settings': 'Updated platform settings',
};

/** Turn raw audit action/resource pairs into a readable sentence fragment. */
export function formatAuditAction(action: string, resourceType: string): string {
  const known = AUDIT_MESSAGES[`${action}:${resourceType}`];
  if (known) {
    return known;
  }
  const fallback = `${action.replace(/_/g, ' ')} ${resourceType.replace(/_/g, ' ')}`;
  return fallback.charAt(0).toUpperCase() + fallback.slice(1);
}
